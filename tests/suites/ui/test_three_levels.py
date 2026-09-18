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
    apps = app.js(
        "[...document.querySelectorAll('#matrixArea .ov-chip')].reduce((a,c)=>{const k=c.className.replace('ov-chip','').trim();a[k]=(a[k]||0)+1;return a;},{})"
    )
    # R1 : 3 points distincts → inherent + current + residual
    assert apps.get("inherent", 0) >= 1 and apps.get("current", 0) >= 1 and apps.get("residual", 0) >= 1
    # Toutes les flèches sont blanches pleines (aucune pointillée).
    dashed = app.js("[...document.querySelectorAll('#matrixArea svg line')].filter(l=>l.getAttribute('stroke')==='#fff'&&l.getAttribute('stroke-dasharray')).length")
    solid = app.js("[...document.querySelectorAll('#matrixArea svg line')].filter(l=>l.getAttribute('stroke')==='#fff'&&!l.getAttribute('stroke-dasharray')).length")
    assert dashed == 0 and solid >= 1
    assert not app.console_errors()


def test_trajectory_six_appearances(app):
    """Les 6 apparences de pastille du mode 3 (cas d'égalité entre stades) et la légende."""
    app.load(FX)
    # R1 distinct, R2 I=A, R3 A=R, R4 tout égal → couvre inherent/current/residual/unch_ia/unch_ar/unch_all
    app.js(
        "const R=analyse.risks;const set=(x,I,A,Rr)=>{x.initial_assessment={probability:I[0],severity:I[1]};"
        "x.current_assessment={probability:A[0],severity:A[1]};x.residual_assessment={probability:Rr[0],severity:Rr[1]};};"
        "set(R[0],[4,4],[3,3],[1,1]);set(R[1],[4,4],[4,4],[1,2]);set(R[2],[4,3],[2,2],[2,2]);set(R[3],[1,1],[1,1],[1,1]);markDirty();"
    )
    app.goto("matrices")
    app.js("matrixMode='traj';renderMatrices();renderTrajectory(document.querySelector('#matrixArea .matrix-container'));")
    apps = app.js(
        "[...document.querySelectorAll('#matrixArea .ov-chip')].reduce((a,c)=>{const k=c.className.replace('ov-chip','').trim();a[k]=(a[k]||0)+1;return a;},{})"
    )
    for cls in ("inherent", "current", "residual", "unch_ia", "unch_ar", "unch_all"):
        assert apps.get(cls, 0) >= 1, f"apparence manquante : {cls}"
    # la légende expose les 6 swatches
    sw = app.js("[...document.querySelectorAll('#matrixLegend .swatch')].map(s=>s.className.replace('swatch','').trim())")
    for cls in ("inherent", "current", "residual", "unch_ia", "unch_ar", "unch_all"):
        assert cls in sw, f"légende sans swatch : {cls}"
    assert not app.console_errors()


def test_side_view_three_matrices(app):
    app.load(FX)
    app.goto("matrices")
    app.js("matrixMode='side';renderMatrices();")
    assert app.js("document.querySelectorAll('#matrixArea .matrix-block').length") == 3
    subs = app.js("[...document.querySelectorAll('#matrixArea .matrix-block .matrix-sub, #matrixArea .matrix-block h4')].map(e=>e.textContent.trim())")
    assert "Inhérente" in subs and "Actuelle" in subs and "Résiduelle" in subs
    assert not app.console_errors()


def test_radar_eval_dropdown_mode3(app):
    app.load(FX)
    app.goto("radars")
    # mode 3 : menu déroulant (seg masqué), 6 options
    assert app.js("document.getElementById('radarEvalSel').style.display!=='none'")
    assert app.js("document.getElementById('radarEvalSeg').style.display==='none'")
    opts = app.js("[...document.getElementById('radarEvalSel').options].map(o=>o.value)")
    assert opts == ["initial", "current", "residual", "over_iar", "over_ar", "over_ir"]
    # séries selon l'option
    app.js("radarState.eval='over_iar';renderRadars();")
    assert app.js("radarComputeModel().series.map(s=>s.name)") == ["Inhérente", "Actuelle", "Résiduelle"]
    app.js("radarState.eval='over_ar';renderRadars();")
    assert app.js("radarComputeModel().series.map(s=>s.name)") == ["Actuelle", "Résiduelle"]
    app.js("radarState.eval='over_ir';renderRadars();")
    assert app.js("radarComputeModel().series.map(s=>s.name)") == ["Inhérente", "Résiduelle"]
    app.js("radarState.eval='current';renderRadars();")
    assert app.js("radarComputeModel().series.map(s=>s.name)") == ["Actuelle"]
    assert not app.console_errors()


def test_radar_seg_mode2(app):
    app.load("ebios.rae.json")
    app.goto("radars")
    # mode 2 : boutons segmentés (menu masqué), sans « Actuelle »
    assert app.js("document.getElementById('radarEvalSeg').style.display!=='none'")
    assert app.js("document.getElementById('radarEvalSel').style.display==='none'")
    vs = app.js("[...document.querySelectorAll('#radarEvalSeg button')].map(b=>b.dataset.v)")
    assert "current" not in vs and "both-side" in vs


def test_matrix_side_subsets_mode3(app):
    app.load(FX)
    app.goto("matrices")
    app.js("matrixMode='side';renderMatrices();")
    assert app.js("!!document.getElementById('levelSubsetSel')")
    app.js("setLevelSubset('side','ar');renderMatrices();")
    assert app.js("document.querySelectorAll('#matrixArea .matrix-block').length") == 2
    app.js("setLevelSubset('side','ir');renderMatrices();")
    assert app.js("document.querySelectorAll('#matrixArea .matrix-block').length") == 2
    app.js("setLevelSubset('side','iar');renderMatrices();")
    assert app.js("document.querySelectorAll('#matrixArea .matrix-block').length") == 3
    assert not app.console_errors()


def test_trajectory_subsets_mode3(app):
    app.load(FX)
    app.goto("matrices")
    app.js("matrixMode='traj';renderMatrices();")

    def apps():
        app.js("renderTrajectory(document.querySelector('#matrixArea .matrix-container'));")
        return app.js(
            "[...document.querySelectorAll('#matrixArea .ov-chip')].reduce((a,c)=>{const k=c.className.replace('ov-chip','').trim();a[k]=(a[k]||0)+1;return a;},{})"
        )

    def arrows():
        return app.js(
            "[...document.querySelectorAll('#matrixArea svg line')].filter(l=>l.getAttribute('stroke')==='#fff')"
            ".reduce((a,l)=>{const k=l.getAttribute('stroke-dasharray')?'dashed':'solid';a[k]=(a[k]||0)+1;return a;},{})"
        )

    # A·R : que current/residual/unch_ar ; toutes les flèches pleines
    app.js("setLevelSubset('traj','ar');renderMatrices();")
    ar = apps()
    assert set(ar) <= {"current", "residual", "unch_ar"}
    assert arrows().get("dashed", 0) == 0 and arrows().get("solid", 0) >= 1
    # I·R : que inherent/residual/unch_all ; toutes les flèches pleines
    app.js("setLevelSubset('traj','ir');renderMatrices();")
    ir = apps()
    assert set(ir) <= {"inherent", "residual", "unch_all"}
    assert arrows().get("dashed", 0) == 0 and arrows().get("solid", 0) >= 1
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


def test_links_no_transition_measure_pills_coloured(app):
    app.load(FX)
    app.goto("links")
    heads = app.js("[...document.querySelectorAll('#view-links thead th')].map(h=>h.textContent.replace('⠿','').replace('📌','').trim())")
    assert "Transition" not in heads
    # Les codes de mesure sont des pastilles colorées selon le statut (comme le registre des risques).
    pills = app.js("document.querySelectorAll('#view-links tbody .pill[data-open-m]').length")
    assert pills >= 1
    coloured = app.js("[...document.querySelectorAll('#view-links tbody .pill[data-open-m]')].some(p=>p.style.background)")
    assert coloured
    assert not app.console_errors()
