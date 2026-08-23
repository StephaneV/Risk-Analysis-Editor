"""Vue Radars : rendu, changement de dimension/métrique."""
import pytest

pytestmark = pytest.mark.ui


def test_radar_area_rendered(app):
    app.load("ebios.rae.json")
    app.goto("radars")
    assert app.js("document.getElementById('radarArea').innerHTML.length") > 0
    assert not app.console_errors()


def test_change_metric(app):
    app.load("ebios.rae.json")
    app.goto("radars")
    app.js("()=>{radarState.metric='max'; renderRadars();}")
    assert not app.console_errors()
    app.js("()=>{radarState.metric='count'; renderRadars();}")
    assert not app.console_errors()


def test_change_eval_mode(app):
    app.load("ebios.rae.json")
    app.goto("radars")
    for mode in ("both-side", "both-over", "initial", "residual"):
        app.js("m=>{radarState.eval=m; renderRadars();}", mode)
        assert not app.console_errors(), f"radar eval={mode}"
