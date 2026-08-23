"""Vue Matrices : rendu des grilles, trajectoire, titre long."""
import pytest

pytestmark = pytest.mark.ui


def _cells(app):
    return app.js("document.querySelectorAll('#view-matrices .cell').length")


def test_matrices_render(app):
    app.load("ebios.rae.json")
    app.goto("matrices")
    assert _cells(app) > 0


def test_trajectory_mode(app):
    app.load("ebios.rae.json")
    app.goto("matrices")
    app.js("matrixMode='traj'; renderMatrices();")
    assert _cells(app) > 0
    assert not app.console_errors()


def test_long_title_renders(app):
    app.load("titre-long.rae.json")
    app.goto("matrices")
    assert _cells(app) > 0
    assert not app.console_errors()


def test_grid_3x3_and_5x5(app):
    for fx in ("grille-3x3.rae.json", "grille-5x5.rae.json"):
        app.load(fx)
        app.goto("matrices")
        assert _cells(app) > 0, f"{fx} : aucune cellule"
        assert not app.console_errors()
