"""Vue Plan d'action : trois présentations (échéancier / statut / responsable)."""
import pytest

pytestmark = pytest.mark.ui


def test_plan_three_modes(app):
    app.load("ebios.rae.json")
    app.goto("plan")
    for mode in ("due_date", "status", "responsible"):
        app.js("m=>{planMode=m; renderPlan();}", mode)
        assert not app.console_errors(), f"plan mode {mode}"
    assert app.js("document.getElementById('view-plan').querySelectorAll('*').length") > 10


def test_overdue_measure_flagged(app):
    """Une mesure échue et non terminée est « en retard » (isOverdue) et signalée dans le plan (T09)."""
    app.load("ebios.rae.json")
    # rend une mesure échue : date passée + statut non terminé/abandonné
    r = app.js("""()=>{
      const m = analyse.measures[0];
      m.due_date = '2000-01-01'; m.status = 'planned';
      return { late: isOverdue(m), id: m.id };
    }""")
    assert r["late"] is True, "isOverdue devrait être vrai pour une échéance passée non terminée"
    app.goto("plan")
    app.js("()=>{planMode='due_date'; renderPlan();}")
    # au moins un marqueur de retard dans la vue
    marked = app.js("!!document.querySelector('#view-plan .overdue-row, #view-plan .plan-card.overdue')")
    assert marked, "aucun élément marqué « en retard » dans le plan"
    assert not app.console_errors()
