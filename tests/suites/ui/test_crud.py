"""CRUD complet : risques, mesures, champs personnalisés, types & instances d'objet, blocs stats."""
import pytest

pytestmark = pytest.mark.ui


# ---------------------------------------------------------------- Risques
def test_risk_duplicate(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    before = app.js("analyse.risks.length")
    app.click('#risksTable [data-dup-r="R1"]')     # ouvre une modale de création pré-remplie
    assert app.modal_open()
    app.click("#modalOk")                           # « Créer »
    assert app.js("analyse.risks.length") == before + 1
    assert not app.console_errors()


def test_risk_edit(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    app.click('#risksTable [data-edit-r="R1"]')
    assert app.modal_open()
    app.set_input("#f_label", "Libellé modifié par test")
    app.click("#modalOk")                           # « Valider »
    assert app.js("riskById('R1').label") == "Libellé modifié par test"


def test_risk_delete_and_undo(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    before = app.js("analyse.risks.length")
    app.click('#risksTable [data-del-r="R1"]')
    app.top_modal_confirm()                         # confirmer la suppression
    assert app.js("analyse.risks.length") == before - 1
    assert app.js("!riskById('R1')")
    app.click("#toast .t-act")                      # annuler (filet toast)
    assert app.js("analyse.risks.length") == before
    assert app.js("!!riskById('R1')")


# ---------------------------------------------------------------- Mesures
def test_measure_duplicate(app):
    app.load("ebios.rae.json")
    app.goto("measures")
    mid = app.js("analyse.measures[0].id")
    before = app.js("analyse.measures.length")
    app.click(f'#measuresTable [data-dup-m="{mid}"]')
    assert app.modal_open()
    app.click("#modalOk")
    assert app.js("analyse.measures.length") == before + 1


def test_measure_delete_and_undo(app):
    app.load("ebios.rae.json")
    app.goto("measures")
    mid = app.js("analyse.measures[0].id")
    before = app.js("analyse.measures.length")
    app.click(f'#measuresTable [data-del-m="{mid}"]')
    app.top_modal_confirm()
    assert app.js("analyse.measures.length") == before - 1
    app.click("#toast .t-act")
    assert app.js("analyse.measures.length") == before


# ---------------------------------------------------------------- Champs personnalisés
def test_custom_field_edit_reorder_delete(app):
    app.load("ebios.rae.json")
    app.settings_subtab("fields")
    assert app.js("customFields().length") >= 2
    # éditer le libellé du 1er champ
    app.js("openCustomFieldModal(0)")
    app.set_input("#cfLab", "Champ édité")
    app.click("#modalOk")
    assert app.js("customFields().some(f=>(f.label[lang]||f.label.fr)==='Champ édité')")
    # réordonner : descendre le 1er
    app.settings_subtab("fields")
    first = app.js("customFields()[0].code")
    app.click('#cfTable [data-cf-down="0"]')
    assert app.js("customFields()[1].code") == first
    # supprimer le 1er
    app.settings_subtab("fields")
    n = app.js("customFields().length")
    app.click('#cfTable [data-cf-del="0"]')
    app.top_modal_confirm()
    assert app.js("customFields().length") == n - 1
    assert not app.console_errors()


# ---------------------------------------------------------------- Types & instances d'objet
def test_object_type_reorder(app):
    app.load("ebios-objets.rae.json")
    app.settings_subtab("objtypes")
    assert app.js("objectTypes().length") >= 2
    first = app.js("objectTypes()[0].code")
    app.click('#otTable [data-ot-down="0"]')
    assert app.js("objectTypes()[1].code") == first


def test_object_instance_edit_and_delete(app):
    app.load("ebios-objets.rae.json")
    app.goto("objects")
    inst = app.js("analyse.objects[0]")
    # édition : ouvrir la fiche, modifier un attribut, enregistrer
    app.js("([c,i])=>openObjectModal(c, i)", [inst["type"], inst["id"]])
    app.js("""() => { const el=document.querySelector('body > .modal-bg.open [data-cfv]');
             if(el){el.value='Modif test'; el.dispatchEvent(new Event('input',{bubbles:true}));} }""")
    n0 = app.js("analyse.objects.length")
    app.top_modal_confirm()                          # enregistrer (édition -> pas de création)
    assert app.js("analyse.objects.length") == n0, "l'édition ne doit pas créer d'instance"
    # suppression
    app.goto("objects")
    before = app.js("analyse.objects.length")
    app.click('#view-objects [data-obj-del]')
    app.top_modal_confirm()
    assert app.js("analyse.objects.length") == before - 1
    assert not app.console_errors()


# ---------------------------------------------------------------- Blocs de statistiques
def test_stat_block_add_and_remove(app):
    app.load("ebios.rae.json")
    app.goto("stats")
    before = app.js("statsCfg().length")
    # ajout d'un bloc « champ personnalisé » (ebios porte des champs perso)
    added = app.js("""() => {
      if (typeof statCustomCandidates==='function' && statCustomCandidates().length) { statsAddCustom(); }
      return statsCfg().length;
    }""")
    assert added == before + 1, "aucun bloc ajouté"
    # suppression du dernier bloc ajouté
    app.js("() => { const bl=statsCfg(); statsSetBlocks(bl.slice(0,-1)); }")
    assert app.js("statsCfg().length") == before
    assert not app.console_errors()
