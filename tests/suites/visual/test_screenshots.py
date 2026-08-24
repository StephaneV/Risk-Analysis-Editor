"""Régression visuelle (lane optionnelle @visual) — captures pleine page.

Couvre, en fr × clair/sombre, chaque « scène » de l'application :
- chrome : barre du haut, barre de navigation ;
- les 11 onglets, capturés **pleine page** (barre du haut + navigation + vue) ;
- variantes de la vue Matrices : trajectoire + les 8 dispositions ;
- variantes de la vue Radars : les 4 modes d'affichage (accolés/superposés/initial/résiduel).

Chaque scène est comparée à une baseline versionnée (tolérance).
- Baseline absente ou `--update-baselines` : (re)génère puis SKIP (pas de faux positif).
- Sinon : compare et échoue si l'écart dépasse le seuil.

Les surfaces hors onglets (menu Fichier, sous-onglets Paramètres, modales) sont
dans test_visual_ui.py.
"""
from pathlib import Path

import pytest

from harness import visual
from harness.app import VIEWS

pytestmark = pytest.mark.visual

BASELINES = Path(__file__).parent / "baselines"
COMBOS = [("fr", "light"), ("fr", "dark")]
THRESHOLD = 0.02
FIXTURE = "ebios.rae.json"

ARRANGEMENTS = ["grid", "row_col", "col_row", "cluster", "row", "column", "overflow", "manual"]
RADAR_EVALS = ["both-side", "both-over", "initial", "residual"]

# Une scène = (nom, vue à activer, setup JS optionnel, sélecteur de capture | None → pleine page)
SCENES = []
# chrome (barre du haut + navigation) — bornés à l'élément
SCENES.append(("chrome-topbar", "presentation", None, ".topbar"))
SCENES.append(("chrome-nav", "presentation", None, "#tabs"))
# les 11 onglets, pleine page
SCENES += [(f"view-{v}", v, None, None) for v in VIEWS]
# variantes Matrices
SCENES.append(("matrices-traj", "matrices", "matrixMode='traj';renderMatrices();", None))
SCENES += [(f"matrices-{c}", "matrices", f"setArrangement('{c}');renderMatrices();", None) for c in ARRANGEMENTS]
# variantes Radars (modes d'affichage)
SCENES += [(f"radars-{m}", "radars", f"radarState.eval='{m}';renderRadars();", None) for m in RADAR_EVALS]

PARAMS = [(name, view, js, sel, l, t) for (name, view, js, sel) in SCENES for (l, t) in COMBOS]


@pytest.mark.parametrize(
    "name,view,setup_js,selector,lang,theme", PARAMS,
    ids=[f"{name}-{l}-{t}" for (name, _v, _j, _s) in SCENES for (l, t) in COMBOS],
)
def test_scene_matches_baseline(app, update_baselines, name, view, setup_js, selector, lang, theme):
    app.load(FIXTURE)
    app.set_lang(lang)
    app.set_theme(theme)
    app.goto(view)
    if setup_js:
        app.js(f"()=>{{{setup_js}}}")
    assert not app.console_errors(), f"erreur console sur la scène {name}"
    png = app.element_screenshot(selector) if selector else app.full_screenshot()

    scene = f"{name}-{lang}-{theme}"
    visual.save_current(png, scene)              # capture conservée à chaque exécution

    baseline = BASELINES / f"{scene}.png"
    if update_baselines or not baseline.exists():
        baseline.parent.mkdir(parents=True, exist_ok=True)
        baseline.write_bytes(png)
        pytest.skip(f"baseline (re)générée : {baseline.name}")

    ratio = visual.diff_ratio(png, baseline)
    if ratio >= THRESHOLD:
        out = visual.save_failure(png, baseline, scene)
        pytest.fail(f"écart visuel {ratio:.4f} > {THRESHOLD} pour {baseline.name} — comparatif dans {out}")
