"""Vue Liens : sous-onglets Associations (tableau croisé) / Détails."""
import pytest

pytestmark = pytest.mark.ui


def test_cross_grid_renders(app):
    app.load("ebios.rae.json")
    app.goto("links")
    app.js("()=>{linkMode='grid'; renderLinks();}")
    assert app.js("document.querySelectorAll('#crossArea tbody tr').length") > 0
    assert not app.console_errors()


def test_details_subtab(app):
    app.load("ebios.rae.json")
    app.goto("links")
    app.js("()=>{linkMode='details'; renderLinks();}")
    assert not app.console_errors()
    assert app.js("document.getElementById('view-links').querySelectorAll('*').length") > 10
