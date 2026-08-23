"""Vue Statistiques : blocs rendus, contenu non vide."""
import pytest

pytestmark = pytest.mark.ui


def test_stats_render(app):
    app.load("ebios.rae.json")
    app.goto("stats")
    # au moins quelques éléments rendus dans la vue
    assert app.js("document.getElementById('view-stats').querySelectorAll('*').length") > 20
    assert not app.console_errors()


def test_stats_on_objects_fixture(app):
    app.load("ebios-objets.rae.json")
    app.goto("stats")
    assert not app.console_errors()
    assert app.js("document.getElementById('view-stats').querySelectorAll('*').length") > 20
