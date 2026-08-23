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


def test_markdown_preview_toggle(app):
    app.load("ebios.rae.json")
    app.goto("presentation")
    app.js("()=>{const ta=document.getElementById('mDesc'); ta.value='# Titre\\n\\n**gras** et *italique*';}")
    # activer l'aperçu
    app.js("()=>document.getElementById('mDesc')._mdSetMode(true)")
    assert app.js("()=>document.getElementById('mDesc')._mdPreview()") is True
    html = app.js("()=>document.getElementById('mDesc').closest('.md-wrap').querySelector('.md-preview').innerHTML")
    assert "<strong>" in html or "<h1" in html, "l'aperçu Markdown n'est pas rendu"
    # revenir en édition
    app.js("()=>document.getElementById('mDesc')._mdSetMode(false)")
    assert app.js("()=>document.getElementById('mDesc')._mdPreview()") is False
    assert not app.console_errors()
