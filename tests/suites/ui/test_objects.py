"""Vue Objets & références (généralise travaux/test-objets, auto-contenu)."""
import pytest

pytestmark = pytest.mark.ui


def test_object_types_and_instances(app):
    app.load("ebios-objets.rae.json")
    app.goto("objects")
    assert app.js("(analyse.object_types||[]).length") > 0
    assert app.js("(analyse.objects||[]).length") > 0
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
