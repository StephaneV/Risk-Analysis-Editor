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


# Densité du registre (Confort / Compact / Dense) : classe sur la table, mémorisée par table,
# préservée au re-rendu ; le padding des cellules diminue. Défaut = Confort (aucune classe).
DENSITY = r"""
(mode) => {
  const seg = document.querySelector('#view-risks .density-seg');
  if (!seg) return { error: 'contrôle de densité absent' };
  const tbl = () => document.getElementById('risksTableEl');
  const pad = () => getComputedStyle(tbl().querySelector('tbody td')).paddingTop;
  const before = { cls: tbl().className, pad: pad(), active: seg.querySelector('button.active').textContent };
  seg.querySelector('[data-density="'+mode+'"]').click();
  renderRisks();   // re-rendu : la densité doit persister
  const t = tbl();
  const btn = v => document.querySelector('#view-risks .density-seg [data-density="'+v+'"]');
  return {
    before,
    hasClass: t.classList.contains(mode),
    padShrunk: parseFloat(pad()) < parseFloat(before.pad),
    stored: (((analyse.extensions||{}).display||{}).density||{}).risks,
    active: document.querySelector('#view-risks .density-seg button.active').getAttribute('data-density'),
    // icônes famille B (2·3·4 traits) + infobulle « Affichage… »
    lines: {comfortable: btn('comfortable').querySelectorAll('svg line').length,
            compact: btn('compact').querySelectorAll('svg line').length,
            dense: btn('dense').querySelectorAll('svg line').length},
    tip: btn('dense').title, aria: btn('dense').getAttribute('aria-label')
  };
}
"""


def test_registre_density(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    r = app.js(DENSITY, "dense")
    assert not r.get("error"), r.get("error")
    assert "compact" not in r["before"]["cls"] and "dense" not in r["before"]["cls"], "densité par défaut ≠ Confort (classe parasite)"
    assert r["hasClass"], "la classe de densité n'est pas appliquée à la table après re-rendu"
    assert r["padShrunk"], "le padding des cellules n'a pas diminué en mode Dense"
    assert r["stored"] == "dense", "densité non mémorisée dans extensions.display.density"
    assert r["active"] == "dense", "bouton actif non synchronisé après re-rendu"
    # Icônes famille B : nombre de traits croissant (2 · 3 · 4) + infobulle « Affichage… ».
    assert r["lines"] == {"comfortable": 2, "compact": 3, "dense": 4}, f"icônes de densité inattendues : {r['lines']}"
    assert r["tip"] == "Affichage dense" and r["aria"] == "Affichage dense", "infobulle/aria-label de densité incorrect"
    assert not app.console_errors()


def test_risks_view_selector_and_cards(app):
    """Registre Risques : sélecteur de vue (Tableau/Maître·détail/Cartes) + vue Cartes."""
    app.load("ebios.rae.json")
    app.goto("risks")
    modes = app.js("[...document.querySelectorAll('#view-risks .view-seg button')].map(b=>b.dataset.viewMode).join(',')")
    assert modes == "table,master_detail,cards", f"sélecteur de vue inattendu : {modes}"
    app.js("document.querySelector('#view-risks .view-seg [data-view-mode=\"cards\"]').click()")
    n = app.js("document.querySelectorAll('#view-risks .reg-cards-host .obj-card').length")
    assert n == app.js("analyse.risks.length"), "une fiche par risque"
    assert app.js("document.querySelector('#view-risks .table-scroll').hidden"), "le tableau devrait être masqué en Cartes"
    app.js("document.querySelector('#view-risks .obj-card .oc-title').click()")
    assert app.modal_open(), "le clic sur une fiche n'ouvre pas l'éditeur"
    app.close_modals()
    assert not app.console_errors()


# ⚙ Colonnes 3 états (colMap) : En ligne / En détail / Masqué + réordonnancement conservé. Le
# placement pilote la vue Maître·détail. « Masqué » = colonne retirée du tableau.
COLMENU_3S = r"""
() => {
  const gear = document.querySelector('#risksTableEl .colgear');
  gear.click();
  const menu = () => [...document.querySelectorAll('.col-menu')].find(m => m.style.display === 'block' && m.querySelector('.cm-row-3s'));
  const out = { locked: [...menu().querySelectorAll('.cm-row.locked .cm-name')].map(x => x.textContent) };
  const row = name => [...menu().querySelectorAll('.cm-row-3s')].find(r => r.querySelector('.cm-name').textContent.trim() === name);
  // Catégorie → En détail
  row('Catégorie').querySelector('[data-cstate="detail"]').click();
  out.stillOpen = !!menu();
  out.catPlacement = colPlacement('risks', 'cat');
  out.hasReorderArrows = !!row('Initial').querySelector('.cm-arrow');
  // Initial → Masqué
  row('Initial').querySelector('[data-cstate="hidden"]').click();
  out.initialHidden = colOrder('risks').indexOf('initial') < 0;
  return out;
}
"""


def test_risks_column_manager_3states(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    r = app.js(COLMENU_3S)
    assert "ID" in r["locked"] and "Actions" in r["locked"], "ID/Actions non verrouillés"
    assert r["stillOpen"], "le ⚙ se ferme après un choix"
    assert r["catPlacement"] == "detail", "En détail non appliqué"
    assert r["hasReorderArrows"], "réordonnancement (flèches) non conservé"
    assert r["initialHidden"], "Masqué ne retire pas la colonne du tableau"
    # Le placement « en détail » descend au tiroir en Maître·détail.
    app.js("document.querySelector('#view-risks .view-seg [data-view-mode=\"master_detail\"]').click()")
    cols = app.js("[...document.querySelectorAll('#risksTableEl thead th')].map(th=>th.textContent.replace(/[▲▼📌⚙⠿]/g,'').trim()).filter(Boolean)")
    assert "Catégorie" not in cols, "la colonne en détail reste en en-tête en Maître·détail"
    assert not app.console_errors()


def test_risks_sort_menu(app):
    """Menu « Trier par » du registre Risques : tri par n'importe quel champ visible (listState)."""
    app.load("ebios.rae.json")
    app.goto("risks")
    app.js("document.querySelector('#view-risks .colsortbtn').click()")
    rows = app.js("[...document.querySelector('.col-menu[style*=\"block\"] .cm-list').querySelectorAll('.srow')].map(r=>r.dataset.sort)")
    assert "__none" in rows and "residual" in rows, f"champs de tri inattendus : {rows}"
    app.js("[...document.querySelectorAll('.col-menu')].find(m=>m.style.display==='block'&&m.querySelector('.srow')).querySelector('.srow[data-sort=\"residual\"]').click()")
    assert app.js("listState.risks.sort") == "residual" and app.js("listState.risks.dir") == 1
    assert "Résiduel" in app.js("document.querySelector('#view-risks .colsortbtn').textContent")
    assert not app.console_errors()


# Poignée de glissement dans sa propre colonne figée (pas de passage à la ligne avec l'ID) :
# présente quand la liste n'est pas triée, absente une fois triée.
GRIP_COL = r"""
() => {
  const tbl = () => document.getElementById('risksTableEl');
  sizeRegScrollers();
  const gripCol = tbl().querySelector('tbody td.reg-grip-col');
  const idCol = tbl().querySelector('tbody td[data-col="id"]');
  const gripTh = tbl().querySelector('thead th.reg-grip-col');
  const out = {
    hasLead: tbl().classList.contains('has-lead'),
    gripFirst: tbl().querySelector('tbody tr').children[0].classList.contains('reg-grip-col'),
    gripHasHandle: !!(gripCol && gripCol.querySelector('.row-grip')),
    gripSticky: gripCol ? getComputedStyle(gripCol).position : null,
    // l'en-tête de la poignée doit aussi être figé à gauche (sinon du blanc apparaît au défilement)
    gripThSticky: gripTh && getComputedStyle(gripTh).position === 'sticky' && getComputedStyle(gripTh).left === '0px',
    idSticky: getComputedStyle(idCol).position,
    idLeft: parseInt(getComputedStyle(idCol).left) || 0
  };
  // Maître·détail (Catégorie en détail) : l'en-tête du chevron doit être figé à gauche (décalé de la poignée).
  setColPlacement('risks', 'cat', 'detail');
  document.querySelector('#view-risks .view-seg [data-view-mode="master_detail"]').click();
  sizeRegScrollers();
  const chevTh = tbl().querySelector('thead th.md-chev-col');
  out.chevThStickyLeft = chevTh && getComputedStyle(chevTh).position === 'sticky' && parseInt(getComputedStyle(chevTh).left) > 0;
  document.querySelector('#view-risks .view-seg [data-view-mode="table"]').click();
  // trié → la poignée disparaît, l'ID redevient 1re colonne
  listState.risks.sort = 'id'; listState.risks.dir = 1; renderRisks(); sizeRegScrollers();
  out.sortedGrip = !!tbl().querySelector('.reg-grip-col');
  out.sortedIdLeft = parseInt(getComputedStyle(tbl().querySelector('tbody td[data-col="id"]')).left) || 0;
  return out;
}
"""


def test_risks_grip_own_sticky_column(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    r = app.js(GRIP_COL)
    assert r["gripFirst"] and r["gripHasHandle"], "la poignée n'est pas dans sa propre 1re colonne"
    assert r["gripSticky"] == "sticky" and r["idSticky"] == "sticky", "poignée / ID non figées"
    assert r["gripThSticky"], "en-tête de la poignée non figé à gauche (blanc au défilement)"
    assert r["chevThStickyLeft"], "en-tête du chevron non figé à gauche en Maître·détail (blanc au défilement)"
    assert r["idLeft"] > 0, "l'ID n'est pas décalé à droite de la poignée (chevauchement)"
    # Trié : plus de poignée, ID de nouveau figé à gauche (left 0).
    assert not r["sortedGrip"], "la poignée subsiste alors que la liste est triée"
    assert r["sortedIdLeft"] == 0, "ID non recollé à gauche une fois trié"
    assert not app.console_errors()


def test_md_hover_highlights_chevron_cell(app):
    """En Maître·détail, la surbrillance de survol de la ligne couvre aussi la cellule figée du
    chevron (fond opaque) — elle ne doit pas rester claire quand le reste de la ligne s'assombrit."""
    app.load("ebios.rae.json")
    app.goto("risks")
    app.js("setColPlacement('risks','cat','detail');"
           "document.querySelector('#view-risks .view-seg [data-view-mode=\"master_detail\"]').click();")
    app.page.hover("#risksTableEl tbody tr[data-rid]")
    bgs = app.js("""() => {
      const row = document.querySelector('#risksTableEl tbody tr[data-rid]');
      return {
        chev: getComputedStyle(row.querySelector('td.md-chev-col')).backgroundColor,
        id: getComputedStyle(row.querySelector('td[data-col="id"]')).backgroundColor
      };
    }""")
    assert bgs["chev"] == bgs["id"], f"cellule chevron sans surbrillance de survol : chev={bgs['chev']} id={bgs['id']}"
    assert not app.console_errors()
