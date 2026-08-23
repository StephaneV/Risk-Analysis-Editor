"""Colonnes personnalisables des registres : visibilité et ordre."""
import pytest

pytestmark = pytest.mark.ui


def test_toggle_column_visibility(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    assert app.js("colOrder('risks').indexOf('cat')>=0")
    app.js("()=>{toggleColumn('risks','cat',false); renderRisks();}")   # masquer + rafraîchir
    assert app.js("colOrder('risks').indexOf('cat')<0")
    assert app.js("!document.querySelector('#risksTableEl th[data-sort=\"cat\"]')"), "colonne encore dans le DOM"
    app.js("()=>{toggleColumn('risks','cat',true); renderRisks();}")    # réafficher
    assert app.js("colOrder('risks').indexOf('cat')>=0")


def test_move_column_order(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    before = app.js("colOrder('risks')")
    r = app.js("""()=>{
      const first = pinnedFirstKey('risks');
      const mids = colOrder('risks').filter(k=>k!==first && k!=='__act');
      if (mids.length < 2) return null;
      moveColumnStep('risks', mids[0], 1);
      return colOrder('risks');
    }""")
    assert r is not None and r != before, "l'ordre des colonnes n'a pas changé"
