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
