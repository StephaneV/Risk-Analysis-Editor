"""Vue Objets & références (généralise travaux/test-objets, auto-contenu)."""
import pytest

pytestmark = pytest.mark.ui


def test_object_types_and_instances(app):
    app.load("ebios-objets.rae.json")
    app.goto("objects")
    assert app.js("(analyse.object_types||[]).length") > 0
    assert app.js("(analyse.objects||[]).length") > 0
    assert not app.console_errors()


OBJ_ROUNDTRIP = r"""
code => {
  const q = s => { s = String(s==null?'':s); return /[",;\n]/.test(s) ? '"'+s.replace(/"/g,'""')+'"' : s; };
  const ids0 = objectsOfType(code).map(o=>o.id).sort();
  let cap=null; const dl=window.downloadCSV; window.downloadCSV=(rows)=>{cap={rows};};
  exportObjectTypeCSV(code); window.downloadCSV=dl;
  const text = cap.rows.map(r=>r.map(q).join(',')).join('\n');
  analyse.objects = objectsAll().filter(o=>o.type!==code);   // vide les instances de ce type
  const an = analyzeObjectsCSV(code, text);
  const res = commitObjectImport(code, an.items);
  return { ids0, ids1: objectsOfType(code).map(o=>o.id).sort(), errors: an.errors, added: res.added };
}
"""


def test_object_type_csv_roundtrip(app):
    """Export CSV d'un type d'objet → réimport : les instances (ids) sont préservées (T05)."""
    app.load("ebios-objets.rae.json")
    code = app.js("analyse.object_types[0].code")
    r = app.js(OBJ_ROUNDTRIP, code)
    assert r["ids0"], "le type choisi n'a aucune instance"
    assert not r["errors"], f"erreurs d'import objets : {r['errors']}"
    assert r["ids1"] == r["ids0"], "aller-retour CSV objets : instances altérées"
    assert not app.console_errors()


def test_open_instance_modal(app):
    app.load("ebios-objets.rae.json")
    code = app.js("analyse.object_types[0].code")
    app.js("c=>openObjectModal(c, null)", code)
    # une modale empilée avec des contrôles d'attribut
    assert app.js("!!document.querySelector('body > .modal-bg.open')")
    assert app.js("document.querySelectorAll('body > .modal-bg.open [data-cf]').length") >= 1
    app.close_modals()


def test_open_object_type_editor(app):
    app.load("ebios-objets.rae.json")
    app.js("openObjectTypeModal(0)")   # index dans object_types, pas le code
    assert app.js("!!document.querySelector('body > .modal-bg.open')")
    assert app.js("!!document.getElementById('otLabel')")
    app.close_modals()


def test_reference_field_present(app):
    # kitchen-sink : un champ 'reference' sur les risques pointant vers des objets
    app.load("tous-types-champs.rae.json")
    refs = app.js("analyse.risks[0].custom.f_ref")
    assert isinstance(refs, list) and len(refs) == 2


def test_create_instance_via_modal(app):
    app.load("tous-types-champs.rae.json")
    before = app.js("(analyse.objects||[]).length")
    app.js("openObjectModal('srv', null)")
    # remplir l'attribut texte « nom » puis créer
    app.js("()=>{const i=document.querySelector('body > .modal-bg.open [data-cf=\"nom\"] [data-cfv]');"
           " if(!i)throw new Error('champ nom absent'); i.value='Serveur créé par test';"
           " i.dispatchEvent(new Event('input',{bubbles:true}));}")
    app.top_modal_confirm()   # « Créer »
    assert app.js("(analyse.objects||[]).length") == before + 1
    assert not app.console_errors()


def test_type_cascade_delete_referential_integrity(app):
    """Suppression d'un type d'objet : cascade sur ses instances ET purge des champs de référence
    qui le ciblent (intégrité référentielle)."""
    app.load("tous-types-champs.rae.json")   # type 'srv' + objets SRV1/SRV2 + champ ref 'f_ref' -> srv
    assert app.js("analyse.objects.filter(o=>o.type==='srv').length") == 2
    assert app.js("!!analyse.custom_fields.find(f=>f.code==='f_ref')")
    app.js("()=>{const i=analyse.object_types.findIndex(t=>t.code==='srv'); deleteObjectType(i);}")
    app.top_modal_confirm()   # confirmer la cascade
    assert app.js("!analyse.object_types.find(t=>t.code==='srv')"), "type non supprimé"
    assert app.js("analyse.objects.filter(o=>o.type==='srv').length") == 0, "instances non supprimées"
    assert app.js("!analyse.custom_fields.find(f=>f.code==='f_ref')"), "champ de référence non purgé"
    assert not app.console_errors()


def test_modal_cleanup_no_phantom(app):
    """Contexte fantôme : l'éditeur de type (id #otLabel/#cfCode) ne doit pas laisser de résidu DOM
    qui entrerait en collision avec la modale d'instance ouverte ensuite."""
    app.load("ebios-objets.rae.json")
    app.js("openObjectTypeModal(0)")
    assert app.js("!!document.getElementById('otLabel')")
    app.close_modals()
    assert app.js("!document.getElementById('otLabel')"), "résidu DOM de la modale de type"
    code = app.js("analyse.object_types[0].code")
    app.js("c=>openObjectModal(c, null)", code)
    assert app.js("!!document.querySelector('body > .modal-bg.open')")
    # aucun champ fantôme de l'éditeur de type dans la modale d'instance
    assert app.js("!document.getElementById('otLabel')")
    app.close_modals()
