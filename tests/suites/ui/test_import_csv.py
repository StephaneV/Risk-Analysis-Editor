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
