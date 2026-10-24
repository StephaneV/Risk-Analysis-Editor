"""Vue Matrices : rendu des grilles, trajectoire, titre long."""
import pytest

pytestmark = pytest.mark.ui


def _cells(app):
    return app.js("document.querySelectorAll('#view-matrices .cell').length")


def test_matrices_render(app):
    app.load("ebios.rae.json")
    app.goto("matrices")
    assert _cells(app) > 0


def test_trajectory_mode(app):
    app.load("ebios.rae.json")
    app.goto("matrices")
    app.js("matrixMode='traj'; renderMatrices();")
    assert _cells(app) > 0
    assert not app.console_errors()


def test_long_title_renders(app):
    app.load("titre-long.rae.json")
    app.goto("matrices")
    assert _cells(app) > 0
    assert not app.console_errors()


def test_grid_3x3_and_5x5(app):
    for fx in ("grille-3x3.rae.json", "grille-5x5.rae.json"):
        app.load(fx)
        app.goto("matrices")
        assert _cells(app) > 0, f"{fx} : aucune cellule"
        assert not app.console_errors()


def test_all_arrangements_render(app):
    app.load("ebios.rae.json")
    app.goto("matrices")
    codes = app.js("ARRANGEMENT_CODES")
    for code in codes:
        app.js("c=>{setArrangement(c); renderMatrices();}", code)
        assert _cells(app) > 0, f"disposition {code} : aucune cellule"
        assert not app.console_errors(), f"disposition {code} : erreur console"


def test_export_svg_side_and_trajectory(app):
    app.load("ebios.rae.json")
    app.goto("matrices")
    side = app.js("reportMatrixSVG('side').indexOf('<svg')")
    traj = app.js("reportMatrixSVG('traj').indexOf('<svg')")
    assert side >= 0 and traj >= 0, "export SVG des matrices vide"
    assert not app.console_errors()


def test_hover_highlights_same_risk_peers(app):
    """Survol d'une pastille : toutes les pastilles du même risque (copies accolées) se mettent
    en évidence, et l'effet est retiré quand on quitte vers le vide."""
    app.load("ebios.rae.json")
    app.goto("matrices")
    app.js("matrixMode='side';renderMatrices();layoutStacks(document.getElementById('matrixArea'));")
    res = app.js(
        "(()=>{const area=document.getElementById('matrixArea');"
        "const chips=[...area.querySelectorAll('.chip,.ov-chip')];"
        "const rid=chips[0].dataset.rid;"
        "const peers=chips.filter(c=>c.dataset.rid===rid);"
        "chips.find(c=>c.dataset.rid===rid).dispatchEvent(new MouseEvent('mouseover',{bubbles:true}));"
        "const hl=[...area.querySelectorAll('.peer-hl')];"
        "const r={total:peers.length,hl:hl.length,allSame:hl.every(c=>c.dataset.rid===rid)};"
        "hl[0].dispatchEvent(new MouseEvent('mouseout',{bubbles:true,relatedTarget:area}));"
        "r.cleared=area.querySelectorAll('.peer-hl').length;return r;})()"
    )
    assert res["total"] >= 2, "2 matrices accolées → au moins 2 copies du risque"
    assert res["hl"] == res["total"] and res["allSame"]
    assert res["cleared"] == 0
    assert not app.console_errors()
