"""Filtres, tri et colonnes des registres."""
import pytest

pytestmark = pytest.mark.ui


def test_category_filter_reduces_rows(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    total = app.js("document.querySelectorAll('#risksTable tr').length")
    cat = app.js("analyse.risks[0].category")
    app.js("c=>{listState.risks.cat=c; renderRisks();}", cat)
    filtered = app.js("document.querySelectorAll('#risksTable tr').length")
    assert 0 < filtered <= total
    # tous les risques d'une seule catégorie
    with_cat = app.js("c=>analyse.risks.filter(r=>r.category===c).length", cat)
    assert filtered == with_cat


def test_search_filters_rows(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    label = app.js("analyse.risks[0].label")
    app.js("q=>{listState.risks.q=q; renderRisks();}", label[:6])
    filtered = app.js("document.querySelectorAll('#risksTable tr').length")
    assert filtered >= 1


def test_column_menu_opens(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    gear = app.js("()=>{const b=document.querySelector('#view-risks .colgear'); if(b){b.click(); return true;} return false;}")
    assert gear is True
    assert not app.console_errors()
