"""Paramètres : rendu des 7 sous-onglets + création d'un champ personnalisé."""
import pytest

from harness.app import SETTINGS_SUBTABS

pytestmark = pytest.mark.ui


@pytest.mark.parametrize("pmode", SETTINGS_SUBTABS)
def test_subtab_renders(app, pmode):
    app.load("ebios.rae.json")
    app.settings_subtab(pmode)
    # le panneau du sous-onglet existe et la vue a du contenu
    assert app.js("m=>!!document.querySelector('#view-settings [data-pmode=\"'+m+'\"]')", pmode)
    assert app.js("document.getElementById('view-settings').querySelectorAll('*').length") > 15
    assert not app.console_errors()


def test_contrast_mode_apply(app):
    app.load("ebios.rae.json")
    app.settings_subtab("display")
    app.set_input("#cfgContraste", "wcag")
    assert app.js("document.documentElement.getAttribute('data-contrast')") == "wcag"
    assert app.js("labelContrast()") == "wcag"
    app.set_input("#cfgContraste", "classic")
    assert app.js("document.documentElement.getAttribute('data-contrast')") == "classic"
    assert not app.console_errors()


def test_create_object_type_via_modal(app):
    """S04 : création d'un type d'objet via la modale (code + libellé + préfixe)."""
    app.load("ebios-objets.rae.json")
    app.settings_subtab("objtypes")
    before = app.js("objectTypes().length")
    app.js("()=>openObjectTypeModal(null)")     # modale empilée (dyn)
    app.set_input("#otLabel", "Nouveau type")
    app.set_input("#otCode", "nouveau_type")
    app.set_input("#otPrefix", "NT")
    app.top_modal_confirm()                     # « Créer »
    assert app.js("objectTypes().length") == before + 1
    assert app.js("!!objectTypeByCode('nouveau_type')"), "type créé introuvable"
    assert not app.console_errors()


def test_add_custom_field_via_modal(app):
    app.load("ebios.rae.json")
    app.settings_subtab("fields")
    before = app.js("(analyse.custom_fields||[]).length")
    app.js("openCustomFieldModal(null)")
    app.set_input("#cfLab", "Champ de test")
    app.set_input("#cfCode", "champ_de_test")
    app.click("#modalOk")   # « Créer »
    assert app.js("(analyse.custom_fields||[]).length") == before + 1
    assert not app.console_errors()
