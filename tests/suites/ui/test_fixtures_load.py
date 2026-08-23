"""Vérifie que chaque fixture d'analyse valide se charge sans erreur console,
et que les fixtures malformées sont rejetées proprement (pas de plantage).
"""
import json
from pathlib import Path

import pytest

from harness.browser import FIXTURES

pytestmark = pytest.mark.ui

VALID = sorted((FIXTURES / "analyses").glob("*.rae.json"))
MALFORMES_STRUCT = sorted((FIXTURES / "analyses" / "malformes").glob("*.rae.json"))


@pytest.mark.parametrize("path", VALID, ids=[p.stem for p in VALID])
def test_valid_fixture_loads(app, path):
    app.clear_errors()
    app.load(str(path))
    assert app.js("(analyse&&analyse.format)||''") == "risk-analysis-editor"
    errs = app.console_errors()
    assert not errs, f"{path.name} — erreurs console au chargement : {errs}"


@pytest.mark.parametrize("path", MALFORMES_STRUCT, ids=[p.stem for p in MALFORMES_STRUCT])
def test_malformed_fixture_rejected(app, path):
    obj = json.loads(path.read_text(encoding="utf-8"))
    # applyLoadedData renvoie false et affiche une alerte pour une structure invalide
    rejected = app.js("o => applyLoadedData(o, 'malforme', false) === false", obj)
    assert rejected is True, f"{path.name} aurait dû être rejetée par validateStructure"


def test_broken_json_is_invalid():
    # le fichier .txt n'est pas du JSON parsable (chemin d'erreur du lecteur de fichier)
    raw = (FIXTURES / "analyses" / "malformes" / "json-casse.txt").read_text(encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        json.loads(raw)
