"""Régression visuelle — surfaces d'IHM hors onglets (lane @visual).

Complète test_screenshots.py (les 11 onglets) avec :
- le menu Fichier déroulé ;
- les 7 sous-onglets de Paramètres ;
- les fenêtres modales (risque, mesure, lien, champ perso, type d'objet, objet,
  import, confirmation).

Chaque surface est capturée en fr × clair/sombre et comparée à une baseline versionnée.
Baseline absente ou `--update-baselines` : (re)génération puis SKIP.
"""
from pathlib import Path

import pytest

from harness import visual
from harness.app import SETTINGS_SUBTABS

pytestmark = pytest.mark.visual

BASELINES = Path(__file__).parent / "baselines"
COMBOS = [("fr", "light"), ("fr", "dark")]
THRESHOLD = 0.02


def _check(png, name, update_baselines):
    baseline = BASELINES / name
    if update_baselines or not baseline.exists():
        baseline.parent.mkdir(parents=True, exist_ok=True)
        baseline.write_bytes(png)
        pytest.skip(f"baseline (re)générée : {baseline.name}")
    ratio = visual.diff_ratio(png, baseline)
    assert ratio < THRESHOLD, f"écart visuel {ratio:.4f} > {THRESHOLD} pour {baseline.name}"


# ------------------------------------------------------------------ menu Fichier
@pytest.mark.parametrize("lang,theme", COMBOS, ids=[f"{l}-{t}" for l, t in COMBOS])
def test_file_menu(app, update_baselines, lang, theme):
    app.load("ebios.rae.json")
    app.set_lang(lang)
    app.set_theme(theme)
    app.open_file_menu()
    png = app.element_screenshot("#fileMenu")
    _check(png, f"menu-file-{lang}-{theme}.png", update_baselines)


# --------------------------------------------------------- sous-onglets Paramètres
_SUB = [(s, l, t) for s in SETTINGS_SUBTABS for (l, t) in COMBOS]


@pytest.mark.parametrize("sub,lang,theme", _SUB, ids=[f"{s}-{l}-{t}" for s, l, t in _SUB])
def test_settings_subtab(app, update_baselines, sub, lang, theme):
    app.load("ebios-objets.rae.json")   # couvre aussi le sous-onglet « types d'objets »
    app.set_lang(lang)
    app.set_theme(theme)
    app.settings_subtab(sub)
    png = app.view_screenshot("settings")
    _check(png, f"settings-{sub}-{lang}-{theme}.png", update_baselines)


# ----------------------------------------------------------------------- modales
# (nom, fixture, ouverture JS, sélecteur de capture)
_MODALS = [
    ("risk",       "ebios.rae.json",        "openRiskModal(null)",                                "#modalBg .modal"),
    ("measure",    "ebios.rae.json",        "openMeasureModal(null)",                             "#modalBg .modal"),
    ("link",       "ebios.rae.json",        "openLinkModal(analyse.treatments[0].risk,analyse.treatments[0].measure)", "#modalBg .modal"),
    ("customfield","ebios.rae.json",        "openCustomFieldModal(null)",                         "#modalBg .modal"),
    ("objecttype", "ebios-objets.rae.json", "openObjectTypeModal(0)",                             "body > .modal-bg.open .modal"),
    ("object",     "ebios-objets.rae.json", "openObjectModal(analyse.object_types[0].code,null)", "body > .modal-bg.open .modal"),
    ("import",     "ebios.rae.json",        "openImportModal('risks')",                           "#modalBg .modal"),
    ("confirm",    "ebios.rae.json",        "confirmModal('Confirmer cette action ?', ()=>{})",   "body > .modal-bg.open .modal"),
]
_MODAL_PARAMS = [(m[0], m[1], m[2], m[3], l, t) for m in _MODALS for (l, t) in COMBOS]


@pytest.mark.parametrize(
    "name,fixture,open_js,selector,lang,theme", _MODAL_PARAMS,
    ids=[f"{m[0]}-{l}-{t}" for m in _MODALS for (l, t) in COMBOS],
)
def test_modal(app, update_baselines, name, fixture, open_js, selector, lang, theme):
    app.load(fixture)
    app.set_lang(lang)
    app.set_theme(theme)
    app.js(f"()=>{{{open_js};}}")
    assert not app.console_errors(), f"erreur à l'ouverture de la modale {name}"
    png = app.element_screenshot(selector)
    _check(png, f"modal-{name}-{lang}-{theme}.png", update_baselines)
