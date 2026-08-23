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


REF_SETUP = r"""
() => {
  analyse.object_types=[{code:'vm',label:{fr:'VM'},attributes:[{code:'n',type:'text',label:{fr:'N'}}]}];
  analyse.objects=[{id:'O1',type:'vm',values:{n:'A'}},{id:'O2',type:'vm',values:{n:'B'}}];
  analyse.custom_fields=[{code:'vmref',target:'risk',type:'reference',object_type:'vm',filterable:true,label:{fr:'VM'}}];
  analyse.risks=[
    {id:'R1',label:'r1',initial_assessment:{probability:1,severity:1},custom:{vmref:['O1']}},
    {id:'R2',label:'r2',initial_assessment:{probability:1,severity:1},custom:{vmref:['O2']}},
    {id:'R3',label:'r3',initial_assessment:{probability:1,severity:1},custom:{vmref:['O1','O2']}}];
  analyse.measures=[];analyse.treatments=[];
}
"""


def test_reference_field_filter(app):
    """Filtre UI sur un champ de référence : ne retient que les risques référençant l'objet choisi
    (porté de test-objets, lot 6 « filtres sur références »)."""
    app.load("ebios-objets.rae.json")
    app.js(REF_SETUP)
    app.goto("risks")   # rend le registre + les barres de filtre
    assert app.js("cfFilterableFields('risk').map(f=>f.code).indexOf('vmref')>=0"), "champ référence non filtrable"
    # filtrer sur l'objet O1 → R1 et R3
    app.js("()=>{cfFilters={vmref:'O1'}; renderRisks();}")
    rows = app.js("document.querySelectorAll('#risksTable tr').length")
    ids = sorted(app.js("visibleRisks().map(r=>r.id)"))
    app.js("()=>{cfFilters={}; renderRisks();}")
    assert rows == 2 and ids == ["R1", "R3"], f"filtre référence O1 → rows={rows} ids={ids}"
    assert not app.console_errors()


def test_column_menu_opens(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    gear = app.js("()=>{const b=document.querySelector('#view-risks .colgear'); if(b){b.click(); return true;} return false;}")
    assert gear is True
    assert not app.console_errors()
