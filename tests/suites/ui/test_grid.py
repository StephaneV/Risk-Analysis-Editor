"""Paramètres › Grille de cotation : édition des niveaux d'axe, méthode de score, criticité."""
import pytest

pytestmark = pytest.mark.ui


def test_add_and_delete_axis_level(app):
    app.load("ebios.rae.json")
    app.settings_subtab("grid")
    n = app.js("analyse.grid.vertical_axis.levels.length")
    app.click('[data-addlevel="prob"]')
    assert app.js("analyse.grid.vertical_axis.levels.length") == n + 1
    app.js("()=>{const dels=document.querySelectorAll('#axisProb [data-axis-del]'); dels[dels.length-1].click();}")
    if app.js("!!document.querySelector('body > .modal-bg.open')"):
        app.top_modal_confirm()                     # confirmer la suppression du niveau
    assert app.js("analyse.grid.vertical_axis.levels.length") == n


def test_edit_level_label(app):
    app.load("ebios.rae.json")
    app.settings_subtab("grid")
    app.set_input('#axisProb [data-axis="prob"][data-i="0"][data-f="label"]', "NiveauX")
    assert app.js("analyse.grid.vertical_axis.levels[0].label") == "NiveauX"


def test_score_method_change(app):
    app.load("ebios.rae.json")
    app.settings_subtab("grid")
    app.set_input("#scoreMethode", "sum")
    assert app.js("analyse.grid.score.method") == "sum"
    assert app.js("scoreOf(3,4)") == 7          # somme
    app.set_input("#scoreMethode", "product")
    assert app.js("scoreOf(3,4)") == 12         # produit


def test_add_and_delete_criticality(app):
    app.load("ebios.rae.json")
    app.settings_subtab("grid")
    n = app.js("analyse.grid.criticality_levels.length")
    app.click("#btnAddCrit")
    assert app.js("analyse.grid.criticality_levels.length") == n + 1
    # supprimer le niveau ajouté (l'index est porté par data-crit-del ; vide → suppression directe)
    app.js("()=>{const i=analyse.grid.criticality_levels.length-1;"
           " document.querySelector('#critBody [data-crit-del=\"'+i+'\"]').click();}")
    if app.js("!!document.querySelector('body > .modal-bg.open')"):
        app.top_modal_confirm()
    assert app.js("analyse.grid.criticality_levels.length") == n
    assert not app.console_errors()
