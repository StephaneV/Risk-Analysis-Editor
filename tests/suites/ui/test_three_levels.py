"""Mode « 3 cotations » (Inhérente · Actuelle · Résiduelle).

Couvre le réglage, la modale, les registres, les matrices/trajectoire, les statistiques,
les radars et la colonne Transition des liens, plus la rétrocompatibilité (bascule 2↔3).
La fixture `trois-cotations.rae.json` porte `extensions.display.assessment_levels = 3`.
"""
import pytest

pytestmark = pytest.mark.ui

FX = "trois-cotations.rae.json"


def test_fixture_loads_in_mode3(app):
    app.load(FX)
    assert app.js("assessmentLevels()") == 3
    # current_assessment présent sur chaque risque
    assert app.js("analyse.risks.every(r=>!!r.current_assessment)")
    assert not app.console_errors()


def test_setting_toggle_and_persistence(app):
    app.load("ebios.rae.json")  # démarre en mode 2
    assert app.js("assessmentLevels()") == 2
    app.js("setAssessmentLevels(3)")
    assert app.js("assessmentLevels()") == 3
    # 2→3 pré-remplit current_assessment (copie de l'initiale)
    assert app.js("analyse.risks.every(r=>!!r.current_assessment)")
    # 3→2 conserve current_assessment (masqué, non perdu)
    app.js("setAssessmentLevels(2)")
    assert app.js("assessmentLevels()") == 2
    assert app.js("analyse.risks.every(r=>!!r.current_assessment)")
    assert not app.console_errors()


def test_risk_register_has_current_columns(app):
    app.load(FX)
    app.goto("risks")
    heads = app.js(
        "[...document.querySelectorAll('#view-risks thead th')].map(h=>h.textContent.replace('⠿','').replace('📌','').trim())"
    )
    assert "Inhérente" in heads and "Actuelle" in heads and "Résiduelle" in heads
    assert not app.console_errors()


def test_risk_register_mode2_has_no_current(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    heads = app.js(
        "[...document.querySelectorAll('#view-risks thead th')].map(h=>h.textContent.replace('⠿','').replace('📌','').trim())"
    )
    assert "Actuelle" not in heads
    assert "Initial" in heads and "Résiduel" in heads


def test_modal_has_third_block(app):
    app.load(FX)
    app.js("openRiskModal('R1')")
    assert app.js("!!document.getElementById('f_cp')")
    assert app.js("!!document.getElementById('f_cg')")
    blocks = app.js("[...document.querySelectorAll('#modalBody .sub-card b')].map(b=>b.textContent.trim())")
    assert blocks == ["Inhérente", "Actuelle", "Résiduelle"]
    app.close_modals()
    assert not app.console_errors()


def test_modal_writes_current_assessment(app):
    app.load(FX)
    app.js("openRiskModal('R1')")
    app.js("document.getElementById('f_cp').value='2';document.getElementById('f_cp').dispatchEvent(new Event('change',{bubbles:true}));")
    app.js("document.getElementById('f_cg').value='2';document.getElementById('f_cg').dispatchEvent(new Event('change',{bubbles:true}));")
    app.top_modal_confirm()
    ca = app.js("riskById('R1').current_assessment")
    assert ca["probability"] == 2 and ca["severity"] == 2
    assert not app.console_errors()


def test_distribution_has_three_series(app):
    app.load(FX)
    app.goto("stats")
    heads = app.js("[...document.querySelectorAll('#stats .st-tbl thead th')].map(h=>h.textContent.trim()).slice(0,4)")
    assert heads == ["Criticité", "Inhérente", "Actuelle", "Résiduelle"]
    # trois anneaux (Inhérente / Actuelle / Résiduelle)
    assert app.js("document.querySelectorAll('#stats .st-duo figure').length") == 3
    assert not app.console_errors()


def test_trajectory_three_dots_two_arrows(app):
    app.load(FX)
    app.goto("matrices")
    app.js("matrixMode='traj';renderMatrices();renderTrajectory(document.querySelector('#matrixArea .matrix-container'));")
    kinds = app.js(
        "[...document.querySelectorAll('#matrixArea .ov-chip')].reduce((a,c)=>{const k=c.className.replace('ov-chip','').trim();a[k]=(a[k]||0)+1;return a;},{})"
    )
    # R1 a 3 points distincts → au moins une pastille « mid » (Actuelle)
    assert kinds.get("mid", 0) >= 1
    assert kinds.get("start", 0) >= 1 and kinds.get("end", 0) >= 1
    lines = app.js(
        "[...document.querySelectorAll('#matrixArea svg line')].filter(l=>l.getAttribute('stroke')==='#fff')"
        ".reduce((a,l)=>{a[l.getAttribute('stroke-dasharray')?'dashed':'solid']=(a[l.getAttribute('stroke-dasharray')?'dashed':'solid']||0)+1;return a;},{})"
    )
    assert lines.get("solid", 0) >= 1  # Inhérente→Actuelle (pleine)
    assert lines.get("dashed", 0) >= 1  # Actuelle→Résiduelle (pointillée)
    assert not app.console_errors()


def test_side_view_three_matrices(app):
    app.load(FX)
    app.goto("matrices")
    app.js("matrixMode='side';renderMatrices();")
    assert app.js("document.querySelectorAll('#matrixArea .matrix-block').length") == 3
    subs = app.js("[...document.querySelectorAll('#matrixArea .matrix-block .matrix-sub, #matrixArea .matrix-block h4')].map(e=>e.textContent.trim())")
    assert "Inhérente" in subs and "Actuelle" in subs and "Résiduelle" in subs
    assert not app.console_errors()


def test_radar_current_option(app):
    app.load(FX)
    app.goto("radars")
    # bouton « Actuelle » visible en mode 3, « Accolés » masqué
    assert app.js("document.querySelector('#radarEvalSeg button[data-v=\"current\"]').style.display!=='none'")
    assert app.js("document.querySelector('#radarEvalSeg button[data-v=\"both-side\"]').style.display==='none'")
    # superposé = 3 séries
    app.js("radarState.eval='both-over';renderRadars();")
    names = app.js("radarComputeModel().series.map(s=>s.name)")
    assert names == ["Inhérente", "Actuelle", "Résiduelle"]
    assert not app.console_errors()


def test_radar_render_has_three_colours(app):
    app.load(FX)
    app.settings_subtab("radars")
    app.js("renderRadarSettings()")
    rds = app.js("[...document.querySelectorAll('#radarCfgPanel [data-rd^=\"color\"]')].map(i=>i.dataset.rd)")
    assert rds == ["colorInit", "colorCur", "colorRes"]
    # changer la couleur actuelle et vérifier la propagation à la série + la persistance
    app.js(
        "const el=document.querySelector('#radarCfgPanel [data-rd=\"colorCur\"]');el.value='#12a594';"
        "el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));"
    )
    assert app.js("radarCfg().render.colorCur") == "#12a594"
    cur = app.js("radarComputeModel({eval:'both-over',dim:radarBestDim(),metric:'avg'},visibleRisks()).series[1]")
    assert cur["name"] == "Actuelle" and cur["color"] == "#12a594"
    assert not app.console_errors()


def test_radar_render_two_colours_in_mode2(app):
    app.load("ebios.rae.json")
    app.settings_subtab("radars")
    app.js("renderRadarSettings()")
    rds = app.js("[...document.querySelectorAll('#radarCfgPanel [data-rd^=\"color\"]')].map(i=>i.dataset.rd)")
    assert rds == ["colorInit", "colorRes"]


def test_links_transition_column(app):
    app.load(FX)
    app.goto("links")
    heads = app.js("[...document.querySelectorAll('#view-links thead th')].map(h=>h.textContent.replace('⠿','').replace('📌','').trim())")
    assert "Transition" in heads
    counts = app.js(
        "[...document.querySelectorAll('#view-links .trans-tag')].reduce((a,c)=>{const k=c.textContent.trim();a[k]=(a[k]||0)+1;return a;},{})"
    )
    # M1 en place → Actuelle ; M2/M3/M4 → Résiduelle
    assert counts.get("Actuelle", 0) >= 1
    assert counts.get("Résiduelle", 0) >= 1
    assert not app.console_errors()
