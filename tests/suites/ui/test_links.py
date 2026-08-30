"""Vue Liens : sous-onglets Associations (tableau croisé) / Détails."""
import pytest

pytestmark = pytest.mark.ui


def test_cross_grid_renders(app):
    app.load("ebios.rae.json")
    app.goto("links")
    app.js("()=>{linkMode='grid'; renderLinks();}")
    assert app.js("document.querySelectorAll('#crossArea tbody tr').length") > 0
    assert not app.console_errors()


def test_details_subtab(app):
    app.load("ebios.rae.json")
    app.goto("links")
    app.js("()=>{linkMode='details'; renderLinks();}")
    assert not app.console_errors()
    assert app.js("document.getElementById('view-links').querySelectorAll('*').length") > 10


# Non-régression : la scrollbar verticale du sous-onglet Détails doit survivre à un aller-retour
# Détails → Associations → Détails. Bug : sizeRegScrollers() effaçait le max-height du panneau
# Détails masqué (grid) ; en revenant, setLinkMode doit re-borner le registre.
LINKS_DETAILS_ROUNDTRIP = r"""
() => {
  const seg = document.getElementById('linksSeg');
  const det = seg.querySelector('[data-mode="details"]');
  const grid = seg.querySelector('[data-mode="grid"]');
  const sc = () => document.querySelector('#view-links .lpanel[data-lmode="details"] .table-scroll');
  det.click();
  const first = { fill: sc().classList.contains('reg-fill'), maxH: sc().style.maxHeight };
  grid.click();
  sizeRegScrollers();   // simule un resize/rendu pendant que Détails est masqué (efface son max-height)
  det.click();
  const second = { fill: sc().classList.contains('reg-fill'), maxH: sc().style.maxHeight };
  return { first, second };
}
"""


def test_links_details_scrollbar_survives_subtab_switch(app):
    app.page.set_viewport_size({"width": 1000, "height": 680})
    app.load("ebios-objets.rae.json")   # 21 liens → déborde verticalement
    app.goto("links")
    r = app.js(LINKS_DETAILS_ROUNDTRIP)
    assert r["first"]["fill"] and r["first"]["maxH"], "Détails non borné au premier affichage"
    assert r["second"]["fill"] and r["second"]["maxH"], "Détails a perdu son cadre borné après l'aller-retour"
    assert not app.console_errors()


def test_links_master_detail_view(app):
    """Registre Liens : vue Maître·détail (chevron + tiroir « Notes » relégué au détail)."""
    app.load("ebios.rae.json")
    app.goto("links")
    app.js("document.querySelector('#linksSeg [data-mode=\"details\"]').click()")
    app.js("document.querySelector('#view-links .view-seg [data-view-mode=\"master_detail\"]').click()")
    tbl = "#view-links table.reg"
    assert app.js(f"document.querySelector('{tbl}').classList.contains('md-haschev')"), "Maître·détail non actif (pas de colonne détail ?)"
    nlinks = app.js("visibleTreatments().length")
    assert app.js(f"document.querySelectorAll('{tbl} .md-chev').length") == nlinks
    # déplier un tiroir → libellé « Notes »
    app.js(f"document.querySelector('{tbl} .md-chev').click()")
    labels = app.js(f"[...document.querySelector('{tbl} tr.md-detail-row .md-detail').querySelectorAll('.md-lbl')].map(x=>x.textContent)")
    assert any("ote" in l for l in labels), f"tiroir sans la colonne Notes : {labels}"
    assert not app.console_errors()
