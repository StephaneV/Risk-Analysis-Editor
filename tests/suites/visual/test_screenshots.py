"""Régression visuelle (lane optionnelle @visual).

Capture chaque vue en fr × clair/sombre et compare à une baseline versionnée (tolérance).
- Baseline absente ou `--update-baselines` : (re)génère la baseline puis SKIP (pas de faux positif).
- Sinon : compare et échoue si l'écart dépasse le seuil.
"""
from pathlib import Path

import pytest

from harness import visual
from harness.app import VIEWS

pytestmark = pytest.mark.visual

BASELINES = Path(__file__).parent / "baselines"
COMBOS = [("fr", "light"), ("fr", "dark")]
THRESHOLD = 0.02   # 2 % d'écart absolu moyen toléré

PARAMS = [(v, l, t) for v in VIEWS for (l, t) in COMBOS]


@pytest.mark.parametrize("view,lang,theme", PARAMS, ids=[f"{v}-{l}-{t}" for v, l, t in PARAMS])
def test_view_matches_baseline(app, update_baselines, view, lang, theme):
    app.load("ebios.rae.json")
    app.set_lang(lang)
    app.set_theme(theme)
    app.goto(view)
    png = app.view_screenshot(view)

    baseline = BASELINES / f"{view}-{lang}-{theme}.png"
    if update_baselines or not baseline.exists():
        baseline.parent.mkdir(parents=True, exist_ok=True)
        baseline.write_bytes(png)
        pytest.skip(f"baseline (re)générée : {baseline.name}")

    ratio = visual.diff_ratio(png, baseline)
    assert ratio < THRESHOLD, f"écart visuel {ratio:.4f} > {THRESHOLD} pour {baseline.name}"
