"""Modale d'import CSV (risques / mesures / liens / objets)."""
import pytest

pytestmark = pytest.mark.ui


def test_import_risks_via_modal(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    before = app.js("analyse.risks.length")
    csv = "id,label,category,initial_probability,initial_severity\nRX1,Risque importé,Test,3,4"
    app.js("openImportModal('risks')")
    assert app.modal_open()
    app.set_input("#impText", csv)         # déclenche l'aperçu
    app.click("#modalOk")                  # « Importer »
    assert app.js("!!riskById('RX1')"), "risque importé absent"
    assert app.js("riskById('RX1').label") == "Risque importé"
    assert app.js("analyse.risks.length") == before + 1
    assert not app.console_errors()


def test_import_measures_via_modal(app):
    app.load("ebios.rae.json")
    app.goto("measures")
    before = app.js("analyse.measures.length")
    csv = "id,label,type,status\nMX1,Mesure importée,preventive,planned"
    app.js("openImportModal('measures')")
    app.set_input("#impText", csv)
    app.click("#modalOk")
    assert app.js("!!measureById('MX1')")
    assert app.js("analyse.measures.length") == before + 1


def test_import_column_mapping_by_header(app):
    """D06 : mappage des colonnes par en-tête (ordre libre) via analyzeRisksCSV."""
    app.load("ebios.rae.json")
    # colonnes dans le désordre + libellés reconnus
    csv = "label,id,initial_severity,initial_probability\nRisque A,RA1,4,2"
    res = app.js("t=>analyzeRisksCSV(t)", csv)
    ok = [it for it in res["items"] if not it.get("errors")]
    assert ok and ok[0]["id"] == "RA1", "mappage par en-tête (ordre libre) échoué"


def test_import_risks_reports_line_errors(app):
    """D06 : une valeur hors échelle produit une erreur portée par la ligne concernée."""
    app.load("ebios.rae.json")
    csv = "id,label,initial_probability,initial_severity\nRB1,Bonne ligne,1,1\nRB2,Mauvaise,99,1"
    res = app.js("t=>analyzeRisksCSV(t)", csv)
    bad = [it for it in res["items"] if it.get("errors")]
    assert bad, "aucune erreur par ligne détectée pour une valeur hors échelle"
    # la bonne ligne reste importable
    good = [it for it in res["items"] if not it.get("errors")]
    assert any(it["id"] == "RB1" for it in good)


def test_import_maps_italian_custom_label(app):
    """Régression 0.3 : une colonne nommée par le libellé ITALIEN d'un champ perso est mappée
    (cfImportCols incluait fr/en mais omettait it)."""
    app.load("ebios.rae.json")
    app.goto("risks")
    app.js("""()=>{ analyse.custom_fields=[{code:'lvl', target:'risk', type:'text',
        label:{fr:'Niveau FR', en:'Level EN', it:'Livello IT'}}]; }""")
    app.js("openImportModal('risks')")
    app.set_input("#impText", "id,Livello IT\nRZ1,haut")   # en-tête = libellé italien
    app.click("#modalOk")
    r = app.js("riskById('RZ1')")
    assert r and (r.get("custom") or {}).get("lvl") == "haut", \
        f"colonne au libellé italien non mappée à l'import : {r and r.get('custom')}"


def test_import_links_unknown_refs(app):
    """D06 : import de liens signalant risque/mesure inconnu(e)."""
    app.load("ebios.rae.json")
    csv = "risk,measure\nR1,M1\nZZ,M1"
    res = app.js("t=>analyzeLinksCSV(t)", csv)
    has_err = bool(res.get("errors")) or any(it.get("errors") for it in res["items"])
    assert has_err, "référence inconnue non signalée à l'import de liens"
