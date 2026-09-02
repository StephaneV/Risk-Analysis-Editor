"""Validateur .rae.json autonome (tools/rae-validator/index.html).

On charge la page de l'outil et on appelle sa fonction pure `validate(json, nom)` via
Playwright, puis on vérifie les résultats (sévérité, catégorie, règle C1–C10, chemin).
Le validateur est indépendant de l'application : ces tests garantissent qu'il reste
aligné sur le format et n'introduit pas de faux positifs sur les fichiers valides.
"""
import copy
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.ui

FIX = Path(__file__).resolve().parents[2] / "fixtures" / "analyses"


# ------------------------------------------------------------------ fixture outil
@pytest.fixture
def validate(browser, base_url):
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(base_url + "/tools/rae-validator/index.html", wait_until="load")
    page.wait_for_function("typeof validate === 'function'")
    yield lambda obj: page.evaluate("(o)=>validate(o, 'test')", obj)
    ctx.close()


# ------------------------------------------------------------------ aides
def errs(F):
    return [f for f in F if f["sev"] == "error"]


def warns(F):
    return [f for f in F if f["sev"] == "warning"]


def rules(F, sev=None):
    return [f["rule"] for f in F if sev is None or f["sev"] == sev]


def has(F, sev, rule, path_sub=None):
    """Vrai s'il existe un résultat de cette sévérité + règle (et chemin contenant path_sub)."""
    return any(f["sev"] == sev and f["rule"] == rule and (path_sub is None or path_sub in f["path"]) for f in F)


def base():
    """Fichier minimal VALIDE (2×2, criticité couvrante) — mutable par chaque test."""
    return {
        "format": "risk-analysis-editor", "version": "1.0",
        "metadata": {"status": "draft", "language": "fr"},
        "grid": {
            "vertical_axis": {"label": "V", "levels": [{"value": 1, "label": "a"}, {"value": 2, "label": "b"}]},
            "horizontal_axis": {"label": "H", "levels": [{"value": 1, "label": "x"}, {"value": 2, "label": "y"}]},
            "score": {"method": "product"},
            "criticality_levels": [
                {"code": "lo", "label": "Lo", "score_min": 1, "score_max": 2, "color": "#00ff00"},
                {"code": "hi", "label": "Hi", "score_min": 3, "score_max": 4, "color": "#ff0000"}],
        },
        "risks": [{"id": "R1", "label": "A", "initial_assessment": {"probability": 1, "severity": 1}}],
        "measures": [{"id": "M1", "label": "m", "status": "proposed"}],
        "treatments": [],
        "custom_fields": [], "object_types": [], "objects": [],
    }


# ------------------------------------------------------------------ tests
def test_base_is_valid(validate):
    """Le fichier minimal de référence ne produit aucune erreur (base saine des mutations)."""
    F = validate(base())
    assert errs(F) == [], f"faux positifs sur le fichier minimal : {[ (f['rule'], f['path']) for f in errs(F) ]}"


@pytest.mark.parametrize("name", [
    "ebios.rae.json", "ebios-objets.rae.json", "tous-types-champs.rae.json", "aipd-objets.rae.json",
])
def test_real_fixtures_have_no_errors(validate, name):
    """Aucun fichier de fixture valide ne doit remonter d'erreur (zéro faux positif)."""
    data = json.loads((FIX / name).read_text(encoding="utf-8"))
    F = validate(data)
    assert errs(F) == [], f"{name} : erreurs inattendues " + str([(f["rule"], f["path"]) for f in errs(F)])


def test_bad_root_and_missing_keys(validate):
    assert has(validate("pas un objet"), "error", "C1")
    F = validate({"format": "autre-chose"})
    assert has(F, "error", "C1", "format")
    assert has(F, "error", "C1", "risks")
    assert has(F, "error", "C1", "grid")


def test_duplicate_ids_C2(validate):
    d = base()
    d["risks"].append({"id": "R1", "label": "B", "initial_assessment": {"probability": 1, "severity": 1}})
    d["measures"].append({"id": "M1", "label": "m2", "status": "proposed"})
    F = validate(d)
    assert has(F, "error", "C2", "risks[1].id")
    assert has(F, "error", "C2", "measures[1].id")


def test_duplicate_field_code_C2(validate):
    d = base()
    d["custom_fields"] = [
        {"code": "p", "target": "risk", "type": "integer", "label": "P"},
        {"code": "p", "target": "risk", "type": "text", "label": "P2"},
    ]
    assert has(validate(d), "error", "C2", "custom_fields[1].code")


def test_broken_links_and_duplicate_C6(validate):
    d = base()
    d["treatments"] = [
        {"risk": "R1", "measure": "M1"},
        {"risk": "R1", "measure": "M1"},   # doublon
        {"risk": "R9", "measure": "M9"},   # inexistants
    ]
    F = validate(d)
    assert has(F, "error", "C6", "treatments[2].risk")
    assert has(F, "error", "C6", "treatments[2].measure")
    assert has(F, "warning", "C6", "treatments[1]")  # doublon = avertissement


def test_assessment_out_of_axis_C4(validate):
    d = base()
    d["risks"][0]["initial_assessment"] = {"probability": 9, "severity": 1}
    assert has(validate(d), "error", "C4", "risks[0].initial_assessment.probability")


def test_residual_over_initial_C9(validate):
    d = base()
    d["risks"][0]["initial_assessment"] = {"probability": 1, "severity": 1}
    d["risks"][0]["residual_assessment"] = {"probability": 2, "severity": 2}
    assert has(validate(d), "warning", "C9", "risks[0]")


def test_grid_axis_C3_and_criticality_C5(validate):
    d = base()
    d["grid"]["vertical_axis"]["levels"] = [{"value": 1, "label": "a"}, {"value": 1, "label": "b"}]
    d["grid"]["criticality_levels"] = [
        {"code": "lo", "label": "Lo", "score_min": 1, "score_max": 6, "color": "#00ff00"},
        {"code": "hi", "label": "Hi", "score_min": 5, "score_max": 16, "color": "#ff0000"}]
    F = validate(d)
    assert has(F, "error", "C3", "grid.vertical_axis")
    assert has(F, "error", "C5", "grid.criticality_levels")


def test_matrix_dimensions_C7(validate):
    d = base()
    d["grid"]["score"] = {"method": "matrix", "matrix": [[1, 2]]}   # 1 ligne pour 2 niveaux V
    assert has(validate(d), "error", "C7", "grid.score.matrix")


def test_object_unknown_type_and_orphan_ref_C8_C10(validate):
    d = base()
    d["object_types"] = [{"code": "srv", "label": "Srv", "id_prefix": "S",
                          "attributes": [{"code": "n", "type": "text", "label": "N"}]}]
    d["objects"] = [{"id": "Z1", "type": "absent", "values": {}}]     # type inconnu (C8)
    d["custom_fields"] = [{"code": "vm", "target": "risk", "type": "reference", "label": "VM",
                           "object_type": "srv", "multiple": True}]
    d["risks"][0]["custom"] = {"vm": ["OBJX"]}                        # référence orpheline (C10)
    F = validate(d)
    assert has(F, "error", "C8", "objects[0].type")
    assert has(F, "warning", "C10")


def test_orphan_and_required_custom(validate):
    d = base()
    d["custom_fields"] = [{"code": "prio", "target": "risk", "type": "integer",
                           "label": "P", "required": True, "min": 1, "max": 5}]
    d["risks"][0]["custom"] = {"ghost": "x"}   # valeur orpheline + obligatoire manquant
    F = validate(d)
    assert any(f["sev"] == "warning" and "orphelin" in f["cat"].lower() for f in F)
    assert any(f["sev"] == "warning" and f["cat"] == "Obligatoires" for f in F)


def test_value_out_of_bounds(validate):
    d = base()
    d["custom_fields"] = [{"code": "prio", "target": "risk", "type": "integer",
                           "label": "P", "min": 1, "max": 5}]
    d["risks"][0]["custom"] = {"prio": 99}
    assert any(f["sev"] == "warning" and f["cat"] == "Valeurs" for f in validate(d))


def test_formula_syntax_unknown_ref_and_cycle(validate):
    d = base()
    d["custom_fields"] = [
        {"code": "c1", "target": "risk", "type": "computed", "label": "C1", "expression": "=cf.c2 + cf.nope"},
        {"code": "c2", "target": "risk", "type": "computed", "label": "C2", "expression": "=cf.c1 * 2"},
        {"code": "bad", "target": "risk", "type": "computed", "label": "B", "expression": "=SUM(cf.c1, "},
    ]
    F = validate(d)
    formulas = [f for f in F if f["cat"] == "Formules" and f["sev"] == "error"]
    joined = " ".join(f["msg"] for f in formulas)
    assert "cf.nope" in joined, "référence inexistante non détectée"
    assert any("syntaxe" in f["msg"] for f in formulas), "erreur de syntaxe non détectée"
    assert any("ycle" in f["msg"] for f in formulas), "cycle non détecté"


def test_missing_object_type_definitions(validate):
    """Types select/reference/computed sans leur propriété obligatoire."""
    d = base()
    d["custom_fields"] = [
        {"code": "s", "target": "risk", "type": "select", "label": "S"},          # sans items
        {"code": "r", "target": "risk", "type": "reference", "label": "R"},        # sans object_type
        {"code": "k", "target": "risk", "type": "computed", "label": "K"},         # sans expression
    ]
    F = validate(d)
    assert has(F, "error", "C1", "custom_fields[0].items")
    assert has(F, "error", "C1", "custom_fields[1].object_type")
    assert has(F, "error", "C1", "custom_fields[2].expression")
