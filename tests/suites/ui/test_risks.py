"""Vue Risques : registre, ouverture de fiche, création via modale."""
import pytest

pytestmark = pytest.mark.ui


def test_registry_row_count_matches_model(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    n = app.js("(analyse.risks||[]).length")
    rows = app.js("document.querySelectorAll('#risksTable tr').length")
    assert n > 0 and rows == n


def test_open_risk_modal_prefilled(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    app.js("openRiskModal('R1', null, null)")
    assert app.modal_open()
    assert app.js("document.getElementById('f_label').value")  # libellé pré-rempli


def test_create_risk_via_modal(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    before = app.js("analyse.risks.length")
    app.js("openRiskModal(null)")
    app.set_input("#f_label", "Nouveau risque de test")
    app.click("#modalOk")   # « Créer »
    assert app.js("analyse.risks.length") == before + 1
    assert not app.console_errors()


# Cadre figé (piste 1) : la 1re colonne (ID) et la dernière (Actions) sont sticky, à fond
# opaque, pour rester visibles au défilement horizontal des registres larges.
FROZEN = r"""
() => {
  const t = document.getElementById('risksTableEl');
  const row = t.querySelector('tbody tr'); if(!row) return null;
  const first = row.children[0], last = row.children[row.children.length-1];
  return {
    reg: t.classList.contains('reg'),
    first: getComputedStyle(first).position,
    last: getComputedStyle(last).position,
    opaque: getComputedStyle(first).backgroundColor !== 'rgba(0, 0, 0, 0)'
  };
}
"""


def test_registre_frozen_id_and_actions(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    r = app.js(FROZEN)
    assert r, "aucune ligne de risque"
    assert r["reg"], "table du registre sans classe .reg"
    assert r["first"] == "sticky" and r["last"] == "sticky", "colonnes ID/Actions non figées"
    assert r["opaque"], "colonne figée sans fond opaque"


# Registre pleine hauteur : le conteneur remplit la fenêtre et défile en interne (barre d'outils
# + en-tête toujours visibles). L'en-tête est figé en haut (top:0) ; la page ne double-défile pas.
FILL = r"""
() => {
  sizeRegScrollers();
  const sc = document.querySelector('#view-risks .table-scroll');
  if(!sc) return null;
  const th = sc.querySelector('thead th'), csTh = getComputedStyle(th);
  sc.scrollTop = 140;
  const scr = sc.getBoundingClientRect(), thr = th.getBoundingClientRect();
  return {
    fill: sc.classList.contains('reg-fill'),
    maxH: parseInt(sc.style.maxHeight) || 0,
    canScroll: sc.scrollHeight > sc.clientHeight + 1,
    theadPos: csTh.position,
    theadTop: csTh.top,
    headerStays: Math.abs(thr.top - scr.top) < 2,
    pageScrolls: document.documentElement.scrollHeight > window.innerHeight + 2
  };
}
"""


def test_registre_fills_window_and_header_sticky(app):
    app.page.set_viewport_size({"width": 1280, "height": 680})
    app.load("ebios.rae.json")
    app.goto("risks")
    r = app.js(FILL)
    assert r, "conteneur de registre introuvable"
    assert r["fill"], "le registre ne remplit pas la fenêtre (classe reg-fill absente)"
    assert r["maxH"] >= 220, "hauteur du conteneur non bornée"
    assert r["theadPos"] == "sticky" and r["theadTop"] == "0px", "en-tête non figé en haut"
    assert not r["pageScrolls"], "la page défile au lieu du conteneur (double défilement)"
    if r["canScroll"]:
        assert r["headerStays"], "l'en-tête ne reste pas en haut au défilement interne"
    assert not app.console_errors()
