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


def test_change_dimension(app):
    # kitchen-sink : des champs perso servent de dimensions radar alternatives
    app.load("tous-types-champs.rae.json")
    app.goto("radars")
    opts = app.js("[...document.getElementById('radarDim').options].map(o=>o.value)")
    assert len(opts) >= 2, "aucune dimension alternative dans le sélecteur"
    for val in opts:
        app.set_input("#radarDim", val)     # passe par le gestionnaire de changement de l'appli
        assert not app.console_errors(), f"radar dim={val}"


def test_radar_export_svg(app):
    app.load("ebios.rae.json")
    app.goto("radars")
    out = app.js("buildRadarExportSVG(radarState)")   # renvoie {svg, W, H}
    assert isinstance(out, dict) and "<svg" in out.get("svg", ""), "export SVG du radar vide"


def test_radar_settings_weights_render_reset(app):
    """Paramètres › Radars (S07) : poids pondérés, curseur de rendu, réinitialisation."""
    app.load("ebios.rae.json")
    app.settings_subtab("radars")
    assert app.js("document.querySelectorAll('#radarCfgPanel [data-rw]').length") > 0
    code = app.js("critBands()[0].code")
    app.set_input(f'#radarCfgPanel [data-rw="{code}"]', "3.5")
    assert app.js(f"radarCfg().weights['{code}']") == 3.5
    app.set_input('#radarCfgPanel [data-rd="hslL"]', "0.8")
    assert abs(app.js("radarCfg().render.hslL") - 0.8) < 1e-9
    app.click("#radarCfgReset")
    assert app.js("!(analyse.extensions && analyse.extensions.display && analyse.extensions.display.radar)"), \
        "la réinitialisation n'a pas supprimé la config radar stockée"
    assert not app.console_errors()
