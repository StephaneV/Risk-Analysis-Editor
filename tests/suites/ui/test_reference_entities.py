"""Champs « référence à un objet » ciblant les éléments de l'analyse : risques et mesures.

Couvre l'évolution : un champ de type reference peut cibler un risque ou une mesure
(pseudo-types REF_RISK / REF_MEASURE) en plus des types d'objets. Vérifie l'abstraction
(refCandidates / refLabel), le sélecteur de type ciblé, le contrôle (picker), l'affichage,
et un aller-retour de bout en bout dans une fiche mesure.
"""
import pytest

pytestmark = pytest.mark.ui


def test_field_def_offers_risks_and_measures(app):
    """La modale de champ perso (type reference) propose Risques et Mesures comme cibles."""
    app.load("ebios.rae.json")
    app.settings_subtab("fields")
    app.js("openCustomFieldModal(null)")
    app.set_input("#cfType", "reference")   # déclenche le rendu des options du type
    opts = app.js("[...document.querySelectorAll('#cfObjectType option')].map(o=>o.value)")
    assert "@risks" in opts and "@measures" in opts, f"cibles risque/mesure absentes : {opts}"
    app.close_modals()


@pytest.mark.parametrize("sentinel,coll", [("REF_RISK", "risks"), ("REF_MEASURE", "measures")])
def test_ref_entity_candidates_and_label(app, sentinel, coll):
    """refCandidates renvoie tous les risques/mesures ; refLabel résout l'id en libellé."""
    app.load("ebios.rae.json")
    n = app.js(f"refCandidates({sentinel}).length")
    assert n == app.js(f"analyse.{coll}.length") and n > 0
    r = app.js(f"""()=>{{
      const e = analyse.{coll}[0];
      return {{ lbl: refLabel({sentinel}, e.id), exp: (e.label||e.id) }};
    }}""")
    assert r["lbl"] == r["exp"], f"refLabel != libellé ({r})"


@pytest.mark.parametrize("sentinel,coll,openattr", [
    ("REF_RISK", "risks", "data-open-r"), ("REF_MEASURE", "measures", "data-open-m")])
def test_ref_entity_control_and_display(app, sentinel, coll, openattr):
    """Le contrôle liste l'entité et masque « créer » ; l'affichage est une pastille Rn/Mn
    (code + infobulle du libellé via aria/tooltip), comme dans les registres."""
    app.load("ebios.rae.json")
    eid = app.js(f"analyse.{coll}[0].id")
    label = app.js(f"analyse.{coll}[0].label")
    ctrl = app.js(f"()=>cfControlHTML({{type:'reference',object_type:{sentinel},multiple:true,code:'rr'}}, [])")
    assert label in ctrl, "l'entité n'apparaît pas dans le picker"
    assert "cf-ref-create" not in ctrl, "le bouton « créer » ne doit pas être proposé pour une entité"
    disp = app.js(f"()=>cfDisplayHTML({{type:'reference',object_type:{sentinel},multiple:true,code:'rr'}}, [analyse.{coll}[0].id], true)")
    assert 'class="pill"' in disp, "l'affichage doit utiliser une pastille"
    assert f'{openattr}="{eid}"' in disp, f"pastille sans {openattr} (navigation transversale)"
    assert f">{eid}<" in disp, "le code (Rn/Mn) doit être affiché"
    assert label in disp, "le libellé (infobulle/aria) doit rester disponible"


def test_measure_field_references_risks_end_to_end(app):
    """Un champ reference (target=mesure, object_type=@risks) : sélection d'un risque, persistance, affichage."""
    app.load("ebios.rae.json")
    rid = app.js("analyse.risks[0].id")
    rlabel = app.js("analyse.risks[0].label")
    mid = app.js("analyse.measures[0].id")
    # champ perso « risques traités » sur les mesures, pointant vers les risques
    app.js("""()=>{ analyse.custom_fields.push({code:'risques_traites', target:'measure', type:'reference',
        object_type:REF_RISK, multiple:true, label:{fr:'Risques traités'}}); }""")
    app.goto("measures")
    app.js("id=>openMeasureModal(id)", mid)
    # le picker (select d'ajout) liste les risques
    assert app.js("""()=>{const o=document.querySelector('#modalBody [data-cf=\"risques_traites\"] .cf-ref-add');
        return !!o && [...o.options].some(x=>x.value && analyse.risks.some(r=>r.id===x.value));}"""), "picker sans risques"
    # sélectionne le 1er risque dans le picker puis enregistre
    app.js("""()=>{const box=document.querySelector('#modalBody [data-cf=\"risques_traites\"]');
        const add=box.querySelector('.cf-ref-add'); add.value=analyse.risks[0].id;
        add.dispatchEvent(new Event('change',{bubbles:true}));}""")
    app.click("#modalOk")
    val = app.js("id=>(measureById(id).custom||{}).risques_traites", mid)
    assert val == [rid], f"référence non persistée : {val}"
    # affichage résout le libellé du risque
    disp = app.js("""id=>{const f=analyse.custom_fields.find(f=>f.code==='risques_traites');
        return cfDisplayHTML(f,(measureById(id).custom||{}).risques_traites,true);}""", mid)
    assert rlabel in disp
    assert not app.console_errors()


@pytest.mark.parametrize("sentinel,coll", [("REF_RISK", "risks"), ("REF_MEASURE", "measures")])
def test_ref_entity_filter_choices(app, sentinel, coll):
    """Les choix de filtre d'un champ reference→entité listent les risques/mesures."""
    app.load("ebios.rae.json")
    ch = app.js(f"()=>cfFilterChoices({{type:'reference',object_type:{sentinel},code:'rr'}}).map(c=>c[0])")
    ids = app.js(f"analyse.{coll}.map(e=>e.id)")
    assert sorted(ch) == sorted(ids), "les choix de filtre ne correspondent pas aux entités"
