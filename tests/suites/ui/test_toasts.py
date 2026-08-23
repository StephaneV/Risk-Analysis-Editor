"""Notifications (toasts) : message simple, toast avec action (annulation), et toasts réels."""
import pytest

pytestmark = pytest.mark.ui


def test_toast_shows_message(app):
    app.load("ebios.rae.json")
    app.js("toast('Bonjour test')")
    shown = app.js("()=>{const el=document.getElementById('toast');"
                   " return el.classList.contains('show') && el.textContent.indexOf('Bonjour test')>=0;}")
    assert shown, "le toast ne s'affiche pas / message absent"


def test_toast_action_triggers_callback_and_hides(app):
    app.load("ebios.rae.json")
    r = app.js("""() => {
      window.__fired = false;
      toastAction('Supprimé', 'Annuler', () => { window.__fired = true; });
      const el = document.getElementById('toast');
      const shown = el.classList.contains('show');
      const btn = el.querySelector('.t-act');
      const label = btn ? btn.textContent : null;
      if (btn) btn.click();
      return { shown, label, fired: window.__fired, hiddenAfter: !el.classList.contains('show') };
    }""")
    assert r["shown"], "toast d'action non affiché"
    assert r["label"] == "Annuler", "bouton d'action absent/mal libellé"
    assert r["fired"] is True, "le callback d'action n'a pas été déclenché"
    assert r["hiddenAfter"] is True, "le toast ne se masque pas au clic sur l'action"


def test_real_toast_on_delete(app):
    """Une action réelle (suppression d'un risque) produit un toast d'annulation."""
    app.load("ebios.rae.json")
    app.goto("risks")
    app.click('#risksTable [data-del-r="R1"]')
    app.top_modal_confirm()
    shown = app.js("()=>{const el=document.getElementById('toast');"
                   " return el.classList.contains('show') && !!el.querySelector('.t-act');}")
    assert shown, "aucun toast d'annulation après suppression"
