"""Smoke sweep — chaque écran/sous-onglet s'ouvre et se rend SANS erreur console.

Pilote : couvre les 11 onglets et les 7 sous-onglets de Paramètres, en fr/clair et en/sombre.
La matrice complète (fr/en/it × clair/sombre) sera étendue en Phase 4.
"""
import pytest

from harness.app import VIEWS, SETTINGS_SUBTABS, LANGS, THEMES

pytestmark = pytest.mark.ui

# Matrice complète : fr/en/it × clair/sombre.
COMBOS = [(l, t) for l in LANGS for t in THEMES]


def _prepare(app, lang, theme, fixture="ebios.rae.json"):
    app.load(fixture)
    app.set_lang(lang)
    app.set_theme(theme)
    app.clear_errors()  # on ne juge que le rendu de l'écran cible


@pytest.mark.parametrize("lang,theme", COMBOS, ids=[f"{l}-{t}" for l, t in COMBOS])
@pytest.mark.parametrize("view", VIEWS)
def test_view_opens_without_console_error(app, view, lang, theme):
    _prepare(app, lang, theme)
    app.goto(view)
    errs = app.console_errors()
    assert not errs, f"vue {view} [{lang}/{theme}] — erreurs console : {errs}"


@pytest.mark.parametrize("lang,theme", COMBOS, ids=[f"{l}-{t}" for l, t in COMBOS])
@pytest.mark.parametrize("pmode", SETTINGS_SUBTABS)
def test_settings_subtab_opens_without_console_error(app, pmode, lang, theme):
    _prepare(app, lang, theme)
    app.settings_subtab(pmode)
    errs = app.console_errors()
    assert not errs, f"sous-onglet Paramètres {pmode} [{lang}/{theme}] — erreurs console : {errs}"
