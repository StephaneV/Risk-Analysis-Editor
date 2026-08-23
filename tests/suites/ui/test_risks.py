"""Vue Risques : registre, ouverture de fiche, création via modale."""
import pytest

pytestmark = pytest.mark.ui


def test_registry_row_count_matches_model(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    n = app.js("(analyse.risks||[]).length")
    rows = app.js("document.querySelectorAll('#risksTable tr').length")
    assert n > 0 and rows == n


def test_open_risk_modal_prefilled(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    app.js("openRiskModal('R1', null, null)")
    assert app.modal_open()
    assert app.js("document.getElementById('f_label').value")  # libellé pré-rempli


def test_create_risk_via_modal(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    before = app.js("analyse.risks.length")
    app.js("openRiskModal(null)")
    app.set_input("#f_label", "Nouveau risque de test")
    app.click("#modalOk")   # « Créer »
    assert app.js("analyse.risks.length") == before + 1
    assert not app.console_errors()
