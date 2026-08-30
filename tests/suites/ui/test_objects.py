"""Vue Objets & références (généralise travaux/test-objets, auto-contenu)."""
import pytest

pytestmark = pytest.mark.ui


def test_object_types_and_instances(app):
    app.load("ebios-objets.rae.json")
    app.goto("objects")
    assert app.js("(analyse.object_types||[]).length") > 0
    assert app.js("(analyse.objects||[]).length") > 0
    assert not app.console_errors()


OBJ_ROUNDTRIP = r"""
code => {
  const q = s => { s = String(s==null?'':s); return /[",;\n]/.test(s) ? '"'+s.replace(/"/g,'""')+'"' : s; };
  const ids0 = objectsOfType(code).map(o=>o.id).sort();
  let cap=null; const dl=window.downloadCSV; window.downloadCSV=(rows)=>{cap={rows};};
  exportObjectTypeCSV(code); window.downloadCSV=dl;
  const text = cap.rows.map(r=>r.map(q).join(',')).join('\n');
  analyse.objects = objectsAll().filter(o=>o.type!==code);   // vide les instances de ce type
  const an = analyzeObjectsCSV(code, text);
  const res = commitObjectImport(code, an.items);
  return { ids0, ids1: objectsOfType(code).map(o=>o.id).sort(), errors: an.errors, added: res.added };
}
"""


def test_object_type_csv_roundtrip(app):
    """Export CSV d'un type d'objet → réimport : les instances (ids) sont préservées (T05)."""
    app.load("ebios-objets.rae.json")
    code = app.js("analyse.object_types[0].code")
    r = app.js(OBJ_ROUNDTRIP, code)
    assert r["ids0"], "le type choisi n'a aucune instance"
    assert not r["errors"], f"erreurs d'import objets : {r['errors']}"
    assert r["ids1"] == r["ids0"], "aller-retour CSV objets : instances altérées"
    assert not app.console_errors()


def test_open_instance_modal(app):
    app.load("ebios-objets.rae.json")
    code = app.js("analyse.object_types[0].code")
    app.js("c=>openObjectModal(c, null)", code)
    # une modale empilée avec des contrôles d'attribut
    assert app.js("!!document.querySelector('body > .modal-bg.open')")
    assert app.js("document.querySelectorAll('body > .modal-bg.open [data-cf]').length") >= 1
    app.close_modals()


# Ouvre la fiche d'une instance d'un type possédant un attribut « textarea ».
OPEN_TEXTAREA_INSTANCE = r"""
() => {
  for (const ot of (analyse.object_types || [])) {
    if ((ot.attributes || []).some(a => a.type === 'textarea')) {
      const inst = objectsOfType(ot.code)[0];
      if (inst) { openObjectModal(ot.code, inst.id); return ot.code; }
    }
  }
  return null;
}
"""

# Règle une valeur Markdown dans la première textarea d'attribut de la fiche, bascule en
# aperçu, et renvoie si la couleur et le surlignage sont bien rendus.
PREVIEW_RENDERS_MD = r"""
() => {
  const ta = document.querySelector('body > .modal-bg.open .md-wrap textarea[data-cfv]');
  if (!ta || !ta._mdSetMode) return false;
  ta.value = 'Texte [rouge]{.red} et ==surligné==.';
  ta._mdSetMode(true);
  const html = ta.closest('.md-wrap').querySelector('.md-preview').innerHTML;
  return /color:#d64545/.test(html) && /<mark>/.test(html);
}
"""


def test_instance_textarea_supports_markdown(app):
    """Les attributs « texte multi-lignes » de la fiche d'instance ont l'aperçu/édition
    Markdown (enveloppe .md-wrap + bascule) — comme les descriptions de risque/mesure."""
    app.load("ebios-objets.rae.json")
    code = app.js(OPEN_TEXTAREA_INSTANCE)
    assert code, "aucun type d'objet avec attribut textarea + instance dans la fixture"
    enhanced = app.js(
        "document.querySelectorAll('body > .modal-bg.open .md-wrap textarea[data-cfv]').length"
    )
    assert enhanced >= 1, "attribut textarea non équipé du Markdown dans la fiche d'instance"
    assert app.js(PREVIEW_RENDERS_MD), "l'aperçu Markdown ne rend pas couleur/surlignage"
    assert not app.console_errors()
    app.close_modals()


# Modale « loupe » d'une cellule écrêtée : elle doit AFFICHER le HTML rendu de la cellule
# (Markdown mis en forme), et non un textContent qui effacerait la mise en forme.
CLIP_MAGNIFIER_MD = r"""
() => {
  const d = document.createElement('div');
  d.className = 'cell-clip'; d.setAttribute('data-label', 'Desc');
  d.innerHTML = mdToHTML('Texte [rouge]{.red}, ==surligné== et **gras**.');
  document.body.appendChild(d);
  showClipText(d);
  const m = [...document.querySelectorAll('.modal')].pop();
  const html = m.querySelector('.clip-view').innerHTML;
  d.remove();
  return { color: /color:#d64545/.test(html), mark: /<mark>/.test(html), bold: /<strong>/.test(html) };
}
"""


def test_clip_magnifier_preserves_markdown(app):
    """La modale loupe (cellule tronquée) conserve la mise en forme Markdown de la cellule."""
    app.load("ebios-objets.rae.json")
    r = app.js(CLIP_MAGNIFIER_MD)
    assert r["color"] and r["mark"] and r["bold"], f"mise en forme perdue dans la loupe : {r}"
    app.close_modals()


def test_open_object_type_editor(app):
    app.load("ebios-objets.rae.json")
    app.js("openObjectTypeModal(0)")   # index dans object_types, pas le code
    assert app.js("!!document.querySelector('body > .modal-bg.open')")
    assert app.js("!!document.getElementById('otLabel')")
    app.close_modals()


def test_reference_field_present(app):
    # kitchen-sink : un champ 'reference' sur les risques pointant vers des objets
    app.load("tous-types-champs.rae.json")
    refs = app.js("analyse.risks[0].custom.f_ref")
    assert isinstance(refs, list) and len(refs) == 2


def test_create_instance_via_modal(app):
    app.load("tous-types-champs.rae.json")
    before = app.js("(analyse.objects||[]).length")
    app.js("openObjectModal('srv', null)")
    # remplir l'attribut texte « nom » puis créer
    app.js("()=>{const i=document.querySelector('body > .modal-bg.open [data-cf=\"nom\"] [data-cfv]');"
           " if(!i)throw new Error('champ nom absent'); i.value='Serveur créé par test';"
           " i.dispatchEvent(new Event('input',{bubbles:true}));}")
    app.top_modal_confirm()   # « Créer »
    assert app.js("(analyse.objects||[]).length") == before + 1
    assert not app.console_errors()


def test_type_cascade_delete_referential_integrity(app):
    """Suppression d'un type d'objet : cascade sur ses instances ET purge des champs de référence
    qui le ciblent (intégrité référentielle)."""
    app.load("tous-types-champs.rae.json")   # type 'srv' + objets SRV1/SRV2 + champ ref 'f_ref' -> srv
    assert app.js("analyse.objects.filter(o=>o.type==='srv').length") == 2
    assert app.js("!!analyse.custom_fields.find(f=>f.code==='f_ref')")
    app.js("()=>{const i=analyse.object_types.findIndex(t=>t.code==='srv'); deleteObjectType(i);}")
    app.top_modal_confirm()   # confirmer la cascade
    assert app.js("!analyse.object_types.find(t=>t.code==='srv')"), "type non supprimé"
    assert app.js("analyse.objects.filter(o=>o.type==='srv').length") == 0, "instances non supprimées"
    assert app.js("!analyse.custom_fields.find(f=>f.code==='f_ref')"), "champ de référence non purgé"
    assert not app.console_errors()


def test_modal_cleanup_no_phantom(app):
    """Contexte fantôme : l'éditeur de type (id #otLabel/#cfCode) ne doit pas laisser de résidu DOM
    qui entrerait en collision avec la modale d'instance ouverte ensuite."""
    app.load("ebios-objets.rae.json")
    app.js("openObjectTypeModal(0)")
    assert app.js("!!document.getElementById('otLabel')")
    app.close_modals()
    assert app.js("!document.getElementById('otLabel')"), "résidu DOM de la modale de type"
    code = app.js("analyse.object_types[0].code")
    app.js("c=>openObjectModal(c, null)", code)
    assert app.js("!!document.querySelector('body > .modal-bg.open')")
    # aucun champ fantôme de l'éditeur de type dans la modale d'instance
    assert app.js("!document.getElementById('otLabel')")
    app.close_modals()


# Registre pleine hauteur (piste 1) : conteneur borné remplissant la fenêtre. Deux régressions
# vérifiées ici : (1) aucune scrollbar fantôme quand le contenu tient (le conteneur se réduit à
# sa taille naturelle) ; (2) le trait bas de l en-tête est présent aussi sous les colonnes figées
# ID (gauche) et Actions (droite) — leur ombre de bord ne doit pas écraser le box-shadow du trait.
OBJ_FILL = r"""
() => {
  sizeRegScrollers();
  const sc = document.querySelector('#view-objects .table-scroll');
  if(!sc) return null;
  const ths = sc.querySelectorAll('thead th');
  const first = ths[0], last = ths[ths.length-1];
  const bodyFirst = sc.querySelector('tbody td:first-child');
  const bodyLast = sc.querySelector('tbody td:last-child');
  const grad = (el,pseudo) => getComputedStyle(el, pseudo).backgroundImage;   // dégradé d'ombre de bord
  return {
    fill: sc.classList.contains('reg-fill'),
    vscroll: sc.scrollHeight > sc.clientHeight + 1,
    pageScrolls: document.documentElement.scrollHeight > window.innerHeight + 2,
    headerBorder: getComputedStyle(first).borderBottomWidth,      // trait bas = bordure (pas d'ombre)
    headerShadow: getComputedStyle(first).boxShadow,              // doit être 'none' (aucune ombre sur l'en-tête)
    theadPos: getComputedStyle(ths[0]).position,
    borderCollapse: getComputedStyle(sc.querySelector('table')).borderCollapse,
    headerBg: getComputedStyle(first).backgroundColor,
    bodyStickyBg: bodyFirst ? getComputedStyle(bodyFirst).backgroundColor : null,
    edgeLeft: /gradient/.test(grad(bodyFirst, '::after')),        // ombre de bord droite de la colonne ID
    edgeRight: /gradient/.test(grad(bodyLast, '::before'))        // ombre de bord gauche de la colonne Actions
  };
}
"""


def test_registre_fill_no_phantom_scrollbar_and_header_borders(app):
    app.page.set_viewport_size({"width": 1280, "height": 1100})
    app.load("ebios-objets.rae.json")
    app.goto("objects")
    r = app.js(OBJ_FILL)
    assert r, "conteneur du registre objets introuvable"
    assert r["fill"], "conteneur non borné (reg-fill absent)"
    assert r["theadPos"] == "sticky", "en-tête non figé"
    assert not r["vscroll"], "scrollbar fantôme : le conteneur ne se réduit pas au contenu court"
    assert not r["pageScrolls"], "la page défile alors que le contenu tient dans la fenêtre"
    assert r["headerBorder"] != "0px", "trait bas d'en-tête manquant"
    # Profondeur du cadre figé (comme la maquette) : bande d'en-tête distincte du corps.
    assert r["headerBg"] != r["bodyStickyBg"], "en-tête sans bande de surface distincte (pas d'effet de profondeur)"
    # Ombres UNIQUEMENT latérales : dégradé pleine hauteur (pseudo-élément) sur ID/Actions, aucune sur l'en-tête.
    assert r["edgeLeft"], "ombre de bord absente à droite de la colonne ID"
    assert r["edgeRight"], "ombre de bord absente à gauche de la colonne Actions"
    assert r["headerShadow"] == "none", "l'en-tête ne doit plus porter d'ombre (seules les latérales sont conservées)"
    # border-collapse:collapse recouvrirait les ombres latérales : les tables .reg doivent être en separate.
    assert r["borderCollapse"] == "separate", "table de registre en border-collapse:collapse (ombres masquées)"
    assert not app.console_errors()


# Ombres de bord conditionnelles : elles n'apparaissent que si du contenu passe sous la colonne
# figée. Début de défilement → rien de caché à gauche (ombre ID masquée) ; fin → rien à droite
# (ombre Actions masquée). Sans débordement horizontal, les deux sont masquées.
EDGE = r"""
() => {
  sizeRegScrollers();
  const sc = document.querySelector('#view-objects .table-scroll');
  if(!sc) return null;
  const maxX = sc.scrollWidth - sc.clientWidth;
  const res = { overflowsX: maxX > 1 };
  // sh-left = ombre de l'ID (contenu caché à gauche) ; sh-right = ombre des Actions (contenu à droite).
  sc.scrollLeft = 0; updateRegEdgeShadows(sc);
  res.startLeft = sc.classList.contains('sh-left');
  res.startRight = sc.classList.contains('sh-right');
  if (maxX > 1) {
    sc.scrollLeft = maxX; updateRegEdgeShadows(sc);
    res.endLeft = sc.classList.contains('sh-left');
    res.endRight = sc.classList.contains('sh-right');
  }
  return res;
}
"""


def test_registre_edge_shadows_conditional(app):
    app.page.set_viewport_size({"width": 760, "height": 820})
    app.load("ebios-objets.rae.json")
    app.goto("objects")
    r = app.js(EDGE)
    assert r, "conteneur du registre objets introuvable"
    assert r["overflowsX"], "le scénario de test ne déborde pas horizontalement"
    # début : ombre ID masquée (rien à gauche), ombre Actions visible (contenu caché à droite)
    assert not r["startLeft"] and r["startRight"], "état de début incorrect"
    # fin : ombre ID visible (contenu caché à gauche), ombre Actions masquée (rien à droite)
    assert r["endLeft"] and not r["endRight"], "état de fin incorrect"
    assert not app.console_errors()


# Densité par TYPE d'objet : mémorisée sous extensions.display.density["objects.<code>"], indépendante
# d'un type à l'autre.
OBJ_DENSITY = r"""
() => {
  const types = analyse.object_types.map(t => t.code);
  const seg = () => document.querySelector('#view-objects .density-seg');
  const tbl = () => document.querySelector('#view-objects table.reg');
  setObjMode(types[0]);
  seg().querySelector('[data-density="dense"]').click();
  const firstCls = tbl().className;
  setObjMode(types[1]);           // autre type : doit rester Confort (indépendant)
  const secondCls = tbl().className;
  const secondActive = seg().querySelector('button.active').getAttribute('data-density');
  setObjMode(types[0]);           // retour : densité conservée
  const backCls = tbl().className;
  const dens = ((analyse.extensions||{}).display||{}).density||{};
  return {
    firstCls, secondCls, backCls, secondActive,
    storedFirst: dens['objects.'+types[0]], storedSecond: dens['objects.'+types[1]]
  };
}
"""


def test_object_density_per_type(app):
    app.load("ebios-objets.rae.json")
    app.goto("objects")
    r = app.js(OBJ_DENSITY)
    assert "dense" in r["firstCls"], "densité non appliquée au 1er type"
    assert r["secondCls"] == "reg", "densité du 1er type déteint sur le 2e (pas indépendante)"
    assert r["secondActive"] == "comfortable", "2e type : contrôle non revenu à Confort"
    assert "dense" in r["backCls"], "densité du 1er type non conservée au retour"
    assert r["storedFirst"] == "dense", "densité du 1er type non mémorisée sous objects.<code>"
    assert r["storedSecond"] is None, "densité écrite pour le 2e type alors qu'il est en Confort"
    assert not app.console_errors()


# Modèle de placement des colonnes (piste 2, fondation Maître·détail) : défauts par type, verrous
# (ID/libellé/Actions), stockage view/detail. Helpers non encore consommés par le rendu.
PLACEMENT = r"""
() => {
  const code = 'source_risque', tk = 'objects.' + code;
  const ot = objectTypeByCode(code), na = ot.name_attr;
  const snap = () => JSON.parse(JSON.stringify((analyse.extensions.display||{}).detail||{}));
  const out = {};
  // Défauts par type : verbeux (text/textarea/computed-text) → détail ; sauf le libellé (verrouillé).
  out.defaultDetail = detailColKeys(tk).sort();
  out.defaultInline = inlineColKeys(tk);
  out.labelKey = labelColKey(tk);
  out.labelLockedInline = colPlacement(tk, 'cf:' + na);         // libellé texte mais verrouillé → inline
  out.labelIsVerbose = regColumns(tk).find(c => c.key === 'cf:' + na).verbose;
  // Déplacer un champ détail → en ligne, puis retour.
  const d0 = detailColKeys(tk)[0];
  setColPlacement(tk, d0, 'inline');
  out.afterInline = { placement: colPlacement(tk, d0), stored: snap()[tk] || null };
  setColPlacement(tk, d0, 'detail');
  out.afterDetail = { placement: colPlacement(tk, d0), storedHasKey: (snap()[tk] || []).indexOf(d0) >= 0 };
  // Verrou : tenter de reléguer le libellé au détail est ignoré.
  setColPlacement(tk, 'cf:' + na, 'detail');
  out.labelStillInline = colPlacement(tk, 'cf:' + na);
  // Vue mémorisée par table.
  out.viewDefault = tableView(tk);
  setTableView(tk, 'master_detail'); out.viewSet = tableView(tk);
  out.viewStored = ((analyse.extensions.display||{}).view||{})[tk];
  setTableView(tk, 'table'); out.viewReset = tableView(tk);
  out.viewKeyCleared = ((analyse.extensions.display||{}).view||{})[tk] === undefined;
  // Risques : le libellé (risk) est verrouillé en ligne.
  out.risksLabelKey = labelColKey('risks');
  out.risksLabelPlacement = colPlacement('risks', 'risk');
  return out;
}
"""


def test_column_placement_model(app):
    app.load("ebios-objets.rae.json")
    r = app.js(PLACEMENT)
    # Défauts par type : les deux attributs verbeux (motivation, objectif_vise) partent au détail ;
    # le libellé (nom), pourtant texte, reste en ligne car verrouillé.
    assert r["labelKey"] == "cf:nom"
    assert r["labelIsVerbose"] is True and r["labelLockedInline"] == "inline"
    assert "cf:nom" not in r["defaultDetail"], "le libellé ne doit jamais partir au détail"
    assert "cf:motivation" in r["defaultDetail"] and "cf:objectif_vise" in r["defaultDetail"]
    assert "cf:nom" in r["defaultInline"] and "cf:categorie" in r["defaultInline"]
    # Bascule détail ↔ en ligne + stockage.
    assert r["afterInline"]["placement"] == "inline"
    assert r["afterDetail"]["placement"] == "detail" and r["afterDetail"]["storedHasKey"]
    # Verrou du libellé.
    assert r["labelStillInline"] == "inline", "le libellé ne doit pas pouvoir passer au détail"
    # Vue mémorisée par table.
    assert r["viewDefault"] == "table" and r["viewSet"] == "master_detail"
    assert r["viewStored"] == "master_detail"
    assert r["viewReset"] == "table" and r["viewKeyCleared"], "retour à 'table' doit purger la clé"
    # Risques : libellé verrouillé en ligne.
    assert r["risksLabelKey"] == "risk" and r["risksLabelPlacement"] == "inline"
    assert not app.console_errors()


# Vue Maître·détail (piste 2 UI, objets) : sélecteur de vue, colonnes en ligne réduites + chevron,
# tiroir de détail (paires libellé→valeur, Markdown rendu, champs vides masqués), clic-ligne ≠ chevron.
MASTER_DETAIL = r"""
() => {
  const code = 'source_risque', tk = 'objects.' + code, ot = objectTypeByCode(code);
  setObjMode(code);
  // instance connue : un champ détail avec Markdown, un autre vidé (doit être masqué du tiroir)
  const inst = objectsOfType(code)[0];
  inst.values.motivation = 'Mot [rouge]{.red} ==surli== **gras**';
  inst.values.objectif_vise = '';
  // bascule en Maître·détail
  const vseg = document.querySelector('#view-objects .view-seg');
  vseg.querySelector('[data-view-mode="master_detail"]').click();
  const tbl = document.querySelector('#view-objects table.reg');
  const out = {
    stored: ((analyse.extensions.display||{}).view||{})[tk],
    isMd: tbl.classList.contains('md'),
    headerCols: [...tbl.querySelectorAll('thead th')].map(th => th.textContent.replace(/[▲▼]/g,'').trim()),
    inlineKeys: inlineColKeys(tk), detailKeys: detailColKeys(tk),
    nChev: tbl.querySelectorAll('.md-chev').length,
    nInst: objectsOfType(code).length,
    nDetailRows: tbl.querySelectorAll('tr.md-detail-row').length
  };
  // déplier la ligne de l'instance éditée
  const row = tbl.querySelector('tr[data-obj-row="' + inst.id + '"]');
  row.querySelector('.md-chev').click();
  const detail = row.nextElementSibling;
  out.detailOpen = row.classList.contains('md-open') && !detail.hidden;
  const grid = detail.querySelector('.md-detail'), gh = grid.innerHTML;
  out.mdColor = /color:#d64545/.test(gh); out.mdMark = /<mark>/.test(gh); out.mdBold = /<strong>/.test(gh);
  out.labels = [...grid.querySelectorAll('.md-lbl')].map(x => x.textContent);
  // Chevron dans sa propre colonne dédiée (comme la maquette) ; l'ID est une cellule distincte, et la
  // colonne chevron comme l'ID restent figées à gauche.
  const chevCell = row.querySelector('td.md-chev-col');
  const idCell = row.querySelector('td[data-col="id"]');
  out.chevOwnColumn = !!(chevCell && chevCell.querySelector('.md-chev'));
  out.idHasNoChevron = idCell && !idCell.querySelector('.md-chev');
  out.chevBtnBig = (() => { const b = tbl.querySelector('.md-chev').getBoundingClientRect(); return b.width >= 20 && b.height >= 20; })();
  out.chevFrozen = getComputedStyle(chevCell).position === 'sticky';
  out.idFrozen = getComputedStyle(idCell).position === 'sticky';
  out.tableMdChev = tbl.classList.contains('md-haschev');
  // clic sur la cellule ID de la ligne maître (hors chevron, non écrêtée) ouvre la fiche.
  row.querySelector('td[data-col="id"]').click();
  out.rowClickOpensModal = !!document.querySelector('body > .modal-bg.open');
  return out;
}
"""


def test_object_master_detail_view(app):
    app.load("ebios-objets.rae.json")
    app.goto("objects")
    r = app.js(MASTER_DETAIL)
    assert r["stored"] == "master_detail" and r["isMd"], "vue Maître·détail non activée"
    # Colonnes en ligne = tout sauf les colonnes « en détail ».
    assert "cf:motivation" not in r["inlineKeys"] and "cf:objectif_vise" not in r["inlineKeys"]
    assert "cf:motivation" in r["detailKeys"] and "cf:objectif_vise" in r["detailKeys"]
    # En-tête : ID + colonnes en ligne + Actions (les colonnes détail ne sont pas en en-tête).
    assert "Motivation" not in r["headerCols"] and "Objectif visé" not in r["headerCols"]
    assert r["nChev"] == r["nInst"] and r["nDetailRows"] == r["nInst"], "chevron/tiroir par instance"
    # Tiroir : ouvert, Markdown rendu, champ vidé masqué (seul Motivation apparaît).
    assert r["detailOpen"], "le tiroir ne s'ouvre pas"
    assert r["mdColor"] and r["mdMark"] and r["mdBold"], "Markdown non rendu dans le tiroir"
    assert r["labels"] == ["Motivation"], f"champ vide non masqué / libellés inattendus : {r['labels']}"
    # Chevron : colonne dédiée, plus gros, ID distinct, chevron+ID figés.
    assert r["chevOwnColumn"] and r["idHasNoChevron"], "le chevron doit être dans sa propre colonne"
    assert r["chevBtnBig"], "chevron trop petit (< 20px)"
    assert r["tableMdChev"] and r["chevFrozen"] and r["idFrozen"], "colonne chevron / ID non figées"
    # Clic-ligne (hors chevron) ouvre la fiche.
    assert r["rowClickOpensModal"], "le clic sur la ligne maître n'ouvre pas la fiche"
    app.close_modals()
    assert not app.console_errors()


# ⚙ Colonnes des objets — contrôle 3 états (En ligne / En détail / Masqué). « Masqué » = hide_table ;
# « En ligne » / « En détail » = placement. ID et attribut de libellé verrouillés. Popover : reste
# ouvert après un clic, se ferme au clic dehors.
OBJ_COLMENU = r"""
() => {
  const code = 'source_risque', ot = objectTypeByCode(code), tk = 'objects.' + code;
  setObjMode(code);
  const gear = document.querySelector('#view-objects .objcolgear');
  const out = { gearPresent: !!gear };
  gear.click();
  const menu = () => [...document.querySelectorAll('.col-menu')].find(m => m.style.display === 'block' && m.querySelector('.cm-pl'));
  out.opened = !!menu();
  out.lockedNames = [...menu().querySelectorAll('.cm-row.locked .cm-name')].map(x => x.textContent);
  // clic « Masqué » sur Catégorie (via l'UI) : reste ouvert + hide_table + hors table
  const seg = c => [...menu().querySelectorAll('.cm-pl')].find(s => s.dataset.code === c);
  seg('categorie').querySelector('[data-pl="hidden"]').click();
  out.stillOpen = !!menu();
  out.categorieHidden = !!ot.attributes.find(a => a.code === 'categorie').hide_table;
  out.categorieActive = menu() && !!seg('categorie') ? '' : 'row-gone';  // la ligne existe toujours (attribut masqué reste listé)
  out.categorieActiveState = seg('categorie').querySelector('.cm-pl-b.active').dataset.pl;
  // « En détail » sur Ressources → au tiroir en Maître·détail
  seg('ressources').querySelector('[data-pl="detail"]').click();
  out.ressourcesPlacement = colPlacement(tk, 'cf:ressources');
  // verrou : le libellé (name_attr) n'a pas de contrôle 3 états (ligne verrouillée)
  out.labelHasSeg = !!seg(ot.name_attr);
  // clic dehors ferme
  document.body.click();
  out.closedOnOutside = !menu();
  return out;
}
"""


def test_object_column_manager_3states(app):
    app.load("ebios-objets.rae.json")
    app.goto("objects")
    r = app.js(OBJ_COLMENU)
    assert r["gearPresent"] and r["opened"], "⚙ Colonnes objets absent / ne s'ouvre pas"
    # ID et libellé verrouillés (listés sans contrôle 3 états).
    assert "Id" in r["lockedNames"] and "Nom" in r["lockedNames"]
    assert not r["labelHasSeg"], "l'attribut de libellé ne doit pas avoir de contrôle 3 états"
    # Masqué = hide_table, popover reste ouvert, état actif reflété.
    assert r["stillOpen"], "le popover se ferme après un clic (devrait rester ouvert)"
    assert r["categorieHidden"] and r["categorieActiveState"] == "hidden"
    # En détail = placement detail.
    assert r["ressourcesPlacement"] == "detail"
    # Clic dehors ferme.
    assert r["closedOnOutside"], "le popover ne se ferme pas au clic dehors"
    assert not app.console_errors()


# Vue Cartes (§6, piste 3) : grille de fiches. En-tête (ID + libellé + actions), colonnes « en ligne »
# en paires, colonnes « en détail » en blocs (texte complet). Densité masquée ; clic-fiche ouvre la
# fiche. Champs vides masqués.
CARDS = r"""
() => {
  const code = 'source_risque', tk = 'objects.' + code, ot = objectTypeByCode(code);
  setObjMode(code);
  const inst = objectsOfType(code)[0];
  inst.values.activite = '';   // champ « en ligne » vidé → doit être absent des paires de sa fiche
  const vseg = document.querySelector('#view-objects .view-seg');
  vseg.querySelector('[data-view-mode="cards"]').click();
  const out = {
    stored: ((analyse.extensions.display||{}).view||{})[tk],
    hasCardsBtn: [...vseg.querySelectorAll('button')].some(b => b.dataset.viewMode === 'cards'),
    densityHidden: !document.querySelector('#view-objects .density-seg'),
    gearPresent: !!document.querySelector('#view-objects .objcolgear'),
    cardCount: document.querySelectorAll('#view-objects .obj-card').length,
    nInst: objectsOfType(code).length
  };
  const card = document.querySelector('#view-objects .obj-card[data-obj-row="' + inst.id + '"]');
  out.cardId = card.querySelector('.id-badge').textContent;
  out.cardTitle = card.querySelector('.oc-title') ? card.querySelector('.oc-title').textContent : null;
  out.pairs = [...card.querySelectorAll('.oc-pairs .oc-k')].map(k => k.textContent);
  out.blocks = [...card.querySelectorAll('.oc-blocks .oc-k')].map(k => k.textContent);
  // Non-régression overflow : aucune valeur / pastille ne doit déborder de sa fiche (réf. multi-valeurs).
  let overflow = 0;
  document.querySelectorAll('#view-objects .obj-card').forEach(c => {
    const cr = c.getBoundingClientRect();
    c.querySelectorAll('.oc-v, .oc-v .pill').forEach(el => { if (el.getBoundingClientRect().right > cr.right + 1) overflow++; });
  });
  out.overflow = overflow;
  // clic sur la fiche (hors actions) ouvre la fiche d'édition
  card.querySelector('.oc-head .oc-title, .oc-head .id-badge').click();
  out.cardClickOpens = !!document.querySelector('body > .modal-bg.open');
  return out;
}
"""


def test_object_cards_view(app):
    app.load("ebios-objets.rae.json")
    app.goto("objects")
    r = app.js(CARDS)
    assert r["stored"] == "cards" and r["hasCardsBtn"], "vue Cartes non activée / bouton absent"
    assert r["densityHidden"], "la densité devrait être masquée en vue Cartes"
    assert r["gearPresent"], "le ⚙ Colonnes devrait rester en vue Cartes"
    assert r["cardCount"] == r["nInst"], "une fiche par instance"
    assert r["cardTitle"] == "Groupe cybercriminel (rançongiciel)", "titre = attribut de libellé"
    # Paires = colonnes « en ligne » (hors libellé, hors champ vidé) ; blocs = colonnes « en détail ».
    assert "Catégorie" in r["pairs"] and "Activité" not in r["pairs"], "champ vidé non masqué des paires"
    assert "Motivation" in r["blocks"] and "Objectif visé" in r["blocks"]
    assert r["overflow"] == 0, "des valeurs/pastilles débordent de leur fiche"
    assert r["cardClickOpens"], "le clic sur une fiche n'ouvre pas l'éditeur"
    app.close_modals()
    assert not app.console_errors()


# Menu « Trier par ▾ » (§8) : tri par n'importe quel champ (ID + attributs, en ligne ET en détail),
# indispensable en Cartes (aucun en-tête). Réutilise objSort ; asc↔desc ; réinitialisation.
SORT_MENU = r"""
() => {
  const code = 'source_risque';
  setObjMode(code);
  document.querySelector('#view-objects .view-seg [data-view-mode="cards"]').click();
  const btn = () => document.querySelector('#view-objects .objsortbtn');
  const menu = () => [...document.querySelectorAll('.col-menu')].find(m => m.style.display === 'block' && m.querySelector('.srow'));
  const pick = col => { btn().click(); menu().querySelector('.srow[data-col="' + col + '"]').click(); };
  const out = { btnPresent: !!btn(), defaultLabel: btn().textContent.trim() };
  btn().click();
  out.rows = [...menu().querySelectorAll('.srow')].map(r => r.dataset.col);
  menu().querySelector('.srow[data-col="cf:objectif_vise"]').click();   // tri par un champ DÉTAIL
  out.menuClosedAfterPick = !menu();
  out.afterDetailSort = { col: objSort[code].col, dir: objSort[code].dir, label: btn().textContent.trim() };
  pick('cf:objectif_vise');   // re-clic → sens inversé
  out.afterToggle = objSort[code].dir;
  pick('__none');   // Ordre d'origine
  out.afterReset = { sort: objSort[code] || null, label: btn().textContent.trim() };
  return out;
}
"""


def test_object_sort_menu(app):
    app.load("ebios-objets.rae.json")
    app.goto("objects")
    r = app.js(SORT_MENU)
    assert r["btnPresent"], "bouton « Trier par » absent"
    assert r["defaultLabel"].startswith("Trier par"), "libellé par défaut inattendu"
    # Le menu liste ID + tous les attributs (dont les champs « en détail »).
    assert "id" in r["rows"] and "cf:categorie" in r["rows"] and "cf:objectif_vise" in r["rows"]
    assert "__none" in r["rows"], "option « Ordre d'origine » manquante"
    # Tri par un champ en détail (impossible via en-tête en cartes) + fermeture après choix.
    assert r["menuClosedAfterPick"], "le menu ne se ferme pas après un choix"
    assert r["afterDetailSort"]["col"] == "cf:objectif_vise" and r["afterDetailSort"]["dir"] == 1
    assert "Objectif visé" in r["afterDetailSort"]["label"], "libellé du bouton non mis à jour"
    # Re-clic → sens inversé, puis réinitialisation.
    assert r["afterToggle"] == -1, "le second clic ne bascule pas en décroissant"
    assert r["afterReset"]["sort"] is None, "« Ordre d'origine » ne réinitialise pas le tri"
    assert not app.console_errors()
