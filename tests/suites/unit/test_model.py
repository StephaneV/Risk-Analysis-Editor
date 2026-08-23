"""Modèle & grille : score, criticité, résiduel, transposition, validation de structure."""
import pytest

pytestmark = pytest.mark.unit


def test_score_is_product(app):
    app.load("ebios.rae.json")
    assert app.js("scoreOf(4,4)") == 16
    assert app.js("scoreOf(2,3)") == 6


def test_crit_for_thresholds(app):
    app.load("ebios.rae.json")
    # grille 4×4 : score 16 = plus haut niveau ; score 1 = plus bas
    hi = app.js("critFor(16)")
    lo = app.js("critFor(1)")
    assert hi and lo and hi["label"] != lo["label"]
    assert hi["score_max"] >= 16 and lo["score_min"] <= 1


def test_residual_falls_back_to_initial(app):
    app.load("ebios.rae.json")
    res = app.js("""() => {
      const r = {initial_assessment:{probability:3,severity:3}};
      return residual(r);
    }""")
    assert res["probability"] == 3 and res["severity"] == 3


def test_transpose_swaps_axes(app):
    app.load("ebios.rae.json")
    before = app.js("[analyse.grid.vertical_axis.label, analyse.grid.horizontal_axis.label]")
    app.js("transposeAxes()")
    after = app.js("[analyse.grid.vertical_axis.label, analyse.grid.horizontal_axis.label]")
    assert after[0] == before[1] and after[1] == before[0]


def test_validate_structure(app):
    app.load("ebios.rae.json")
    assert app.js("!!validateStructure(analyse)") is False  # valide -> pas d'erreur
    assert app.js("!!validateStructure({})") is True        # vide -> erreur
    assert app.js("!!validateStructure({format:'risk-analysis-editor',version:'1.0',metadata:{title:'x'}})") is True
