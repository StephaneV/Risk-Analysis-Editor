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


# Pleine largeur (piste 5) : bouton de bascule dans l'en-tête ; retire la largeur max du contenu
# (main), booléen global extensions.display.full_width, appliqué à l'ouverture.
FULL_WIDTH = r"""
() => {
  const btn = document.getElementById('btnFullWidth');
  const main = document.querySelector('main');
  const out = { present: !!btn, before: getComputedStyle(main).maxWidth };
  btn.click();
  out.on = {
    hasClass: main.classList.contains('full-width'),
    maxW: getComputedStyle(main).maxWidth,
    aria: btn.getAttribute('aria-pressed'),
    stored: (analyse.extensions.display || {}).full_width
  };
  btn.click();
  out.off = { hasClass: main.classList.contains('full-width'), stored: (analyse.extensions.display || {}).full_width };
  // persistance à l'ouverture : recharger des données avec full_width déjà actif
  const cur = JSON.parse(JSON.stringify(analyse));
  cur.extensions = cur.extensions || {}; cur.extensions.display = cur.extensions.display || {};
  cur.extensions.display.full_width = true;
  applyLoadedData(cur, 'x.rae.json', false);
  out.afterLoad = { hasClass: main.classList.contains('full-width'), active: btn.classList.contains('active') };
  return out;
}
"""


def test_full_width_toggle(app):
    app.load("ebios.rae.json")
    r = app.js(FULL_WIDTH)
    assert r["present"], "bouton pleine largeur absent de l'en-tête"
    assert r["before"] != "none", "le contenu devrait être borné par défaut"
    # Activé : classe + max-width levée + aria + stockage.
    assert r["on"]["hasClass"] and r["on"]["maxW"] == "none"
    assert r["on"]["aria"] == "true" and r["on"]["stored"] is True
    # Désactivé : classe retirée + clé purgée (pas de config vide).
    assert not r["off"]["hasClass"] and r["off"]["stored"] is None
    # Appliqué à l'ouverture d'une analyse déjà en pleine largeur.
    assert r["afterLoad"]["hasClass"] and r["afterLoad"]["active"]
    assert not app.console_errors()
