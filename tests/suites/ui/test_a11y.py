"""Accessibilité (D12) : motif ARIA tablist/tab, synchronisation aria-selected."""
import pytest

from harness.app import VIEWS

pytestmark = pytest.mark.ui


def test_tablist_roles(app):
    app.load("ebios.rae.json")
    assert app.js("document.getElementById('tabs').getAttribute('role')") == "tablist"
    n_tabs = app.js("document.querySelectorAll('#tabs [role=\"tab\"]').length")
    assert n_tabs == len(VIEWS), f"{n_tabs} onglets ARIA pour {len(VIEWS)} vues"
    # chaque onglet contrôle une vue existante
    missing = app.js("""()=>[...document.querySelectorAll('#tabs [role=tab]')]
        .map(t=>t.getAttribute('aria-controls'))
        .filter(id=>!document.getElementById(id))""")
    assert not missing, f"aria-controls sans cible : {missing}"


def test_aria_selected_follows_active(app):
    app.load("ebios.rae.json")
    for v in ("risks", "radars", "settings"):
        app.goto(v)
        r = app.js("""v=>{
          const tabs=[...document.querySelectorAll('#tabs [role=tab]')];
          const sel=tabs.filter(t=>t.getAttribute('aria-selected')==='true');
          const active=document.querySelector('#tabs [data-view=\"'+v+'\"]');
          return { nSel: sel.length, activeSelected: active.getAttribute('aria-selected')==='true' };
        }""", v)
        assert r["activeSelected"], f"onglet {v} non aria-selected après activation"
        assert r["nSel"] == 1, f"{r['nSel']} onglets sélectionnés (attendu 1) sur {v}"
