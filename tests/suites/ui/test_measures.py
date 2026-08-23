"""Vue Mesures : registre, ouverture de fiche, création via modale."""
import pytest

pytestmark = pytest.mark.ui


def test_registry_row_count_matches_model(app):
    app.load("ebios.rae.json")
    app.goto("measures")
    n = app.js("(analyse.measures||[]).length")
    rows = app.js("document.querySelectorAll('#measuresTable tr').length")
    assert n > 0 and rows == n


def test_open_measure_modal_prefilled(app):
    app.load("ebios.rae.json")
    app.goto("measures")
    mid = app.js("analyse.measures[0].id")
    app.js("id=>openMeasureModal(id, null, null)", mid)
    assert app.modal_open()
    assert app.js("document.getElementById('f_label').value")


def test_create_measure_via_modal(app):
    app.load("ebios.rae.json")
    app.goto("measures")
    before = app.js("analyse.measures.length")
    app.js("openMeasureModal(null)")
    app.set_input("#f_label", "Nouvelle mesure de test")
    app.click("#modalOk")
    assert app.js("analyse.measures.length") == before + 1
    assert not app.console_errors()
