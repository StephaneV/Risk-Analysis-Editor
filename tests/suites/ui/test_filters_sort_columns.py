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


SELECT_SETUP = r"""
() => {
  analyse.object_types=[]; analyse.objects=[];
  analyse.custom_fields=[{code:'zone',target:'risk',type:'select',filterable:true,label:{fr:'Zone'},
    items:[{code:'nord',label:{fr:'Nord'}},{code:'sud',label:{fr:'Sud'}}]}];
  analyse.risks=[
    {id:'R1',label:'r1',initial_assessment:{probability:1,severity:1},custom:{zone:'nord'}},
    {id:'R2',label:'r2',initial_assessment:{probability:1,severity:1},custom:{zone:'sud'}},
    {id:'R3',label:'r3',initial_assessment:{probability:1,severity:1},custom:{zone:'nord'}}];
  analyse.measures=[]; analyse.treatments=[];
}
"""


def test_select_field_filter(app):
    """Filtre UI sur un champ perso de type « select » (fermé) — D07."""
    app.load("ebios.rae.json")
    app.js(SELECT_SETUP)
    app.goto("risks")
    assert app.js("cfFilterableFields('risk').map(f=>f.code).indexOf('zone')>=0"), "champ select non filtrable"
    app.js("()=>{cfFilters={zone:'nord'}; renderRisks();}")
    ids = sorted(app.js("visibleRisks().map(r=>r.id)"))
    app.js("()=>{cfFilters={}; renderRisks();}")
    assert ids == ["R1", "R3"], f"filtre select nord → {ids}"
    assert not app.console_errors()


def test_column_menu_opens(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    gear = app.js("()=>{const b=document.querySelector('#view-risks .colgear'); if(b){b.click(); return true;} return false;}")
    assert gear is True
    assert not app.console_errors()


def _risk_ids(app):
    return app.js("[...document.querySelectorAll('#risksTable tr .id-badge')].map(e=>e.textContent)")


def test_column_sort_three_states(app):
    """Tri de colonne à 3 états : croissant → décroissant → ordre du fichier."""
    app.load("ebios.rae.json")
    app.goto("risks")
    app.click('#risksTableEl th[data-sort="risk"]')      # 1er clic : croissant
    st_asc = app.js("[listState.risks.sort, listState.risks.dir]")
    asc = _risk_ids(app)
    app.click('#risksTableEl th[data-sort="risk"]')      # 2e clic : décroissant
    st_desc = app.js("[listState.risks.sort, listState.risks.dir]")
    desc = _risk_ids(app)
    app.click('#risksTableEl th[data-sort="risk"]')      # 3e clic : plus de tri
    st_none = app.js("[listState.risks.sort, listState.risks.dir]")
    assert st_asc == ["risk", 1] and st_desc == ["risk", -1] and st_none == ["", 1]
    assert asc == list(reversed(desc)), "croissant devrait être l'inverse de décroissant"
    assert not app.console_errors()


def test_object_sort_three_states(app):
    """Tri d'objets à 3 états (objSortToggle) : croissant → décroissant → ordre du fichier."""
    app.load("ebios-objets.rae.json")
    code = app.js("analyse.object_types[0].code")

    def ids():
        return app.js("c=>objSortedInstances(objectTypeByCode(c)).map(o=>o.id)", code)

    file_order = ids()
    app.js("c=>objSortToggle(c,'id')", code); asc = ids()
    app.js("c=>objSortToggle(c,'id')", code); desc = ids()
    app.js("c=>objSortToggle(c,'id')", code); none = ids()
    assert asc == list(reversed(desc)), "tri objets : croissant ≠ inverse du décroissant"
    assert none == file_order, "3e état : retour à l'ordre du fichier"
