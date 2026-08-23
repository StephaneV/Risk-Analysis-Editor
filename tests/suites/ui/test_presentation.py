"""Vue Présentation : métadonnées + champs perso d'analyse."""
import pytest

pytestmark = pytest.mark.ui


def test_metadata_shown(app):
    app.load("ebios.rae.json")
    app.goto("presentation")
    assert app.js("document.getElementById('mTitle').value") == app.js("analyse.metadata.title")


def test_edit_title_applies(app):
    app.load("ebios.rae.json")
    app.goto("presentation")
    app.set_input("#mTitle", "Titre modifié par test")
    app.click("#presSave")
    assert app.js("analyse.metadata.title") == "Titre modifié par test"
    assert not app.console_errors()


def test_analysis_custom_fields_render(app):
    # la fixture kitchen-sink porte un champ perso d'analyse
    app.load("tous-types-champs.rae.json")
    app.goto("presentation")
    assert app.js("document.querySelectorAll('#cfAnalysisValues [data-cf]').length") >= 1
