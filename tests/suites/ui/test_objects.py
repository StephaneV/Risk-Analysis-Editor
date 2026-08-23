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
