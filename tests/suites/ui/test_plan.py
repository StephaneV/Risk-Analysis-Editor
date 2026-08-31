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


def test_plan_dblclick_edits_not_single(app):
    """Harmonisation clic sur le Plan d'action (échéancier / statut / responsable) : un simple-clic sur
    une carte/ligne n'ouvre plus la mesure ; il faut un double-clic (positionné sur le champ)."""
    app.load("ebios.rae.json")
    app.goto("plan")
    r = app.js(r"""(() => {
      const fire = (el,t) => el.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,view:window}));
      const open = () => !!document.querySelector('body > .modal-bg.open');
      const close = () => [...document.querySelectorAll('body > .modal-bg')].forEach(m=>{ if(m.id!=='modalBg') m.remove(); const b=[...m.querySelectorAll('footer button')].find(x=>/Annuler|Fermer/i.test(x.textContent||'')); if(b) b.click(); });
      const out = {};
      for (const mode of ['due_date','status','responsible']) {
        planMode = mode; renderPlan();
        const target = document.querySelector('#planArea [data-col="measure"]');
        fire(target,'click');    const single = open(); close();
        fire(target,'dblclick'); const dbl = open();
        const isMeasureModal = !!document.querySelector('body > .modal-bg.open #f_label, body > .modal-bg.open #f_resp'); close();
        out[mode] = { single, dbl, isMeasureModal };
      }
      // positionnement : double-clic sur la cellule 'resp' (mode échéancier) focalise le champ responsable
      planMode = 'due_date'; renderPlan();
      fire(document.querySelector('#planArea tr[data-mid] td[data-col="resp"]'),'dblclick');
      out.focusedRespField = document.activeElement && document.activeElement.id === 'f_resp';
      close();
      return out;
    })()""")
    for mode in ("due_date", "status", "responsible"):
        assert not r[mode]["single"], f"un simple-clic ne doit plus ouvrir la mesure ({mode})"
        assert r[mode]["dbl"] and r[mode]["isMeasureModal"], f"le double-clic n'ouvre pas la fiche mesure ({mode})"
    assert r["focusedRespField"], "le double-clic sur la cellule Responsable ne positionne pas la modale"
    assert not app.console_errors()


def test_plan_edit_button(app):
    """Chaque carte/ligne du Plan (échéancier / statut / responsable) porte un bouton ✎ qui ouvre la
    fiche mesure en un seul clic (accès direct, l'édition sur le corps se faisant au double-clic)."""
    app.load("ebios.rae.json")
    app.goto("plan")
    r = app.js(r"""(() => {
      const open = () => !!document.querySelector('body > .modal-bg.open');
      const close = () => [...document.querySelectorAll('body > .modal-bg')].forEach(m=>{ if(m.id!=='modalBg') m.remove(); const b=[...m.querySelectorAll('footer button')].find(x=>/Annuler|Fermer/i.test(x.textContent||'')); if(b) b.click(); });
      const out = {};
      for (const mode of ['due_date','status','responsible']) {
        planMode = mode; renderPlan();
        const btns = document.querySelectorAll('#planArea [data-plan-edit]');
        const nMeas = analyse.measures.length;
        btns[0].click();
        const opened = open() && !!document.querySelector('body > .modal-bg.open #f_label');
        close();
        out[mode] = { count: btns.length, nMeas, opened };
      }
      return out;
    })()""")
    for mode in ("due_date", "status", "responsible"):
        assert r[mode]["count"] == r[mode]["nMeas"], f"un bouton ✎ par mesure attendu ({mode})"
        assert r[mode]["opened"], f"le bouton ✎ n'ouvre pas la fiche mesure ({mode})"
    # Le rapport réutilise le tableau du plan mais NE doit PAS porter de bouton d'édition.
    app.goto("report")
    assert app.js("document.querySelectorAll('#view-report [data-plan-edit]').length") == 0, \
        "le bouton d'édition ✎ ne doit pas apparaître dans le rapport"
    assert not app.console_errors()
