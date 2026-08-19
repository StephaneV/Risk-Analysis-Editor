// Reproduction FIDÈLE du rapport « Exporter en Word » natif (mode classique, iteration.by = none).
// Produit word-templates/modele-rapport-complet-classique.docx (distinct de build-word-templates.js,
// qui génère les modèles de démonstration classique/éclaté/référentiels/tableau de bord).
//
// Utilisation (depuis ce dossier) :
//   npm install docx        # dépendance de génération (une fois ; non versionnée)
//   node build-rapport-complet-classique.js
const fs = require("fs"), path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, PageBreak,
  Header, Footer, PageNumber, Tab, TabStopType, TableOfContents,
} = require("docx");
const mkObjets = require("./sections-objets");

const OUT = process.env.OUT || __dirname;
const CW = 9638;                                  // largeur utile (twips), = DX_CW natif
const MUTED = "7A8699", LABEL = "3B4A63", ACCENT = "2F5BD0", BORDER = "D0D7E5";
const OBJ = mkObjets(require("docx"), { CW, MUTED, LABEL });   // sections objets agnostiques (variante -objets)
const bd = { style: BorderStyle.SINGLE, size: 4, color: BORDER };
const noBd = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const TB = { top: bd, bottom: bd, left: bd, right: bd, insideHorizontal: bd, insideVertical: bd };

const txt = (t, o = {}) => new TextRun({ text: t, ...o });
const P = (children, o = {}) => new Paragraph({ children: [].concat(children), ...o });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 240, after: 120 }, children: [txt(t)] });
const subTitle = (children) => new Paragraph({ spacing: { before: 160, after: 60 }, children: [].concat(children).map(c => typeof c === "string" ? txt(c, { bold: true, color: LABEL, size: 22 }) : c) });
const block = (tag) => P(txt(tag));             // balise de bloc, sur son paragraphe

// Cellule de tableau (largeur DXA + marges), texte simple.
const cell = (children, { w, head = false, muted = false } = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  shading: head ? { type: ShadingType.CLEAR, color: "auto", fill: "EEF2F8" } : undefined,
  margins: { top: 40, bottom: 40, left: 90, right: 90 },
  children: [P([].concat(children).map(c => typeof c === "string" ? txt(c, { color: muted ? MUTED : undefined, bold: head }) : c), { spacing: { before: 0, after: 0 } })],
});
const twoColTable = (rows, wl, wr) => new Table({
  columnWidths: [wl, wr], width: { size: wl + wr, type: WidthType.DXA }, borders: TB,
  rows: rows.map(r => new TableRow({ children: [cell(r[0], { w: wl, muted: true }), cell(r[1], { w: wr })] })),
});

// Table à ligne répétée pour une échelle d'axe (Valeur | Libellé | Description).
const axisTable = (collection) => {
  const W = [900, 2400, CW - 3300];
  const hc = (t) => cell(t, { w: W[["Valeur", "Libellé", "Description"].indexOf(t)], head: true });
  return new Table({
    columnWidths: W, width: { size: CW, type: WidthType.DXA }, borders: TB,
    rows: [
      new TableRow({ tableHeader: true, children: ["Valeur", "Libellé", "Description"].map(hc) }),
      new TableRow({ children: [
        cell([txt("{{#each " + collection + "}}"), txt("{{ step.value }}")], { w: W[0] }),
        cell(txt("{{ step.label }}"), { w: W[1] }),
        cell([txt("{{ step.description }}"), txt(" "), txt("{{/each}}")], { w: W[2] }),
      ] }),
    ],
  });
};

// En-tête / pied avec zones gauche/centre/droite (tabulations) — {page}/{pages} via champs Word.
const zonesPara = (leftRuns, centerRuns, rightRuns) => new Paragraph({
  tabStops: [{ type: TabStopType.CENTER, position: Math.round(CW / 2) }, { type: TabStopType.RIGHT, position: CW }],
  children: [].concat(leftRuns, [new TextRun({ children: [new Tab()] })], centerRuns, [new TextRun({ children: [new Tab()] })], rightRuns),
});
const header = new Header({ children: [ zonesPara(
  [txt("{{ analysis.organization }}", { color: MUTED, size: 16 })],
  [txt("{{ analysis.title }}", { color: MUTED, size: 16 })],
  [txt("{{ analysis.author }}", { color: MUTED, size: 16 })]
) ] });
const footer = new Footer({ children: [ zonesPara(
  [txt('{{ analysis.updated | date="ISO" }} {{ analysis.revision }}', { color: MUTED, size: 16 })],
  [new TextRun({ children: [PageNumber.CURRENT], color: MUTED, size: 16 }), txt(" / ", { color: MUTED, size: 16 }), new TextRun({ children: [PageNumber.TOTAL_PAGES], color: MUTED, size: 16 })],
  [txt("", { size: 16 })]
) ] });

// ---- Corps ----
const body = [];

// Page de garde
body.push(block("{{ logo }}"));
body.push(new Paragraph({ heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER, spacing: { before: 120, after: 80 }, children: [txt("{{ analysis.title }}")] }));
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [
  txt('{{ analysis.organization }} · {{ analysis.author }} · {{ analysis.updated | date="ISO" }} · Révision {{ analysis.revision }}', { color: MUTED }),
]}));
body.push(new Paragraph({ children: [new PageBreak()] }));

// Table des matières
body.push(H1("Table des matières"));
body.push(new TableOfContents("Table des matières", { hyperlink: true, headingStyleRange: "1-1" }));
body.push(new Paragraph({ children: [new PageBreak()] }));

// 1. Métadonnées
body.push(H1("Métadonnées"));
body.push(twoColTable([
  ["Auteur", "{{ analysis.author }}"],
  ["Organisation", "{{ analysis.organization }}"],
  ["Périmètre", "{{ analysis.scope }}"],
  ["Référence méthodologique", "{{ analysis.reference }}"],
  ["Date de création", '{{ analysis.created | date="ISO" }}'],
  ["Dernière modification", '{{ analysis.updated | date="ISO" }}'],
  ["Révision", "{{ analysis.revision }}"],
  ["Statut", "{{ analysis.status }}"],
], 2600, CW - 2600));

// 2. Présentation
body.push(H1("Présentation"));
body.push(P(txt("{{ analysis.description }}")));
body.push(P([txt("Référentiels : ", { bold: true, color: LABEL }), txt("{{ analysis.cf.referentiels }}")]));
body.push(P([txt("Périmètre : ", { bold: true, color: LABEL }), txt("{{ analysis.cf.perimetre }}")]));

// 3. Synthèse
body.push(H1("Synthèse"));
body.push(block('{{ stat type="summary" }}'));

// 4. Répartition par criticité
body.push(H1("Répartition par criticité (initial → résiduel)"));
body.push(block('{{ stat type="distribution" }}'));

// 5. Grille de cotation
body.push(H1("Grille de cotation"));
body.push(P(txt("Méthode : {{ grid.method }}", { color: MUTED })));
body.push(subTitle([txt("Axe vertical — ", { bold: true, color: LABEL, size: 22 }), txt("{{ grid.vertical_axis }}", { bold: true, color: LABEL, size: 22 })]));
body.push(axisTable("grid.vertical_axis.levels"));
body.push(subTitle([txt("Axe horizontal — ", { bold: true, color: LABEL, size: 22 }), txt("{{ grid.horizontal_axis }}", { bold: true, color: LABEL, size: 22 })]));
body.push(axisTable("grid.horizontal_axis.levels"));

// 6. Niveaux de criticité
body.push(H1("Niveaux de criticité (zones colorées)"));
body.push(block('{{ table source="levels" }}'));

// 7. Référentiels et légendes des champs
body.push(H1("Référentiels et légendes des champs"));
body.push(P(txt('{{#each custom_fields glossary="true" }}')));
body.push(subTitle([txt("{{ field.label }} — ", { bold: true, color: LABEL, size: 22 }), txt("{{ field.target }}", { bold: true, color: LABEL, size: 22 })]));
body.push(block("{{ field_values }}"));
body.push(P(txt("{{/each}}")));

const OBJ_IDX = body.length;                        // point d'insertion de la section « Objets » (variante -objets)

// 8-10. Matrices + trajectoire
body.push(H1("Matrice initiale seule"));
body.push(block('{{ matrix type="initial" }}'));
body.push(H1("Matrice résiduelle seule"));
body.push(block('{{ matrix type="residual" }}'));
body.push(H1("Trajectoire des risques"));
body.push(block('{{ matrix type="trajectory" }}'));

// 11. Radar
body.push(H1("Criticité moyenne — Catégorie · Superposés"));
body.push(block('{{ radar dimension="category" metric="average" evaluation="overlay" }}'));

// 12. Registre des risques
body.push(H1("Registre des risques"));
body.push(block('{{ table source="risks" columns="id,risk,cat,initial,residual,measures" }}'));

// 13. Détail des risques
body.push(H1("Détail des risques"));
body.push(P(txt("{{#each risks }}")));
body.push(new Paragraph({ spacing: { before: 160, after: 40 }, children: [txt("{{ risk.id }} — {{ risk.label }}", { bold: true }), txt("   {{ risk.category }}", { color: MUTED, size: 20 })] }));
body.push(P(txt("{{ risk.description }}")));
body.push(P(txt("{{ risk.comment }}")));
body.push(block("{{ cf_notes }}"));
body.push(P(txt("{{/each}}")));

// 14. Mesures de maîtrise
body.push(H1("Mesures de maîtrise"));
body.push(block('{{ table source="measures" columns="id,measure,type,status,resp,covered" }}'));

// 15. Détail des mesures
body.push(H1("Détail des mesures"));
body.push(P(txt("{{#each measures }}")));
body.push(new Paragraph({ spacing: { before: 160, after: 40 }, children: [txt("{{ measure.id }} — {{ measure.label }}", { bold: true }), txt("   {{ measure.type }} · {{ measure.status }} · {{ measure.responsible }}", { color: MUTED, size: 20 })] }));
body.push(P(txt("{{ measure.description }}")));
body.push(P(txt("{{ measure.comment }}")));
body.push(block("{{ cf_notes }}"));
body.push(P(txt("{{/each}}")));

// 16. Liens risques ↔ mesures
body.push(H1("Liens risques ↔ mesures"));
body.push(block('{{ table source="links" columns="rid,risk,mid,measure,notes" }}'));

// 17. Détail des liens
body.push(H1("Détail des liens"));
body.push(P(txt("{{#each links }}")));
body.push(new Paragraph({ spacing: { before: 160, after: 40 }, children: [txt("{{ link.risk_id }} → {{ link.measure_id }}", { bold: true }), txt("   {{ link.risk.label }} → {{ link.measure.label }}", { color: MUTED, size: 20 })] }));
body.push(P(txt("{{ link.comment }}")));
body.push(block("{{ cf_notes }}"));
body.push(P(txt("{{/each}}")));

// 18. Plan d'action
body.push(H1("Plan d'action"));
body.push(block('{{ table source="measures" columns="id,measure,status,resp,due" sort="due_date" }}'));

const makeDoc = (children) => new Document({
  styles: {
    default: {
      document: { run: { font: "Calibri", size: 21 }, paragraph: { spacing: { after: 140 }, widowControl: true } },
      title: { run: { font: "Calibri", size: 44, bold: true, color: "111827" }, paragraph: { spacing: { after: 120 }, keepNext: true, keepLines: true } },
      heading1: { run: { font: "Calibri", size: 28, bold: true, color: "1F2937" }, paragraph: { spacing: { before: 340, after: 160 }, keepNext: true, keepLines: true } },
    },
  },
  sections: [{
    properties: { page: { margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    headers: { default: header }, footers: { default: footer },
    children,
  }],
});

// Corps « objets » : le corps standard + une section « Objets » (inventaire agnostique) insérée après les référentiels.
const bodyObjets = body.slice();
bodyObjets.splice(OBJ_IDX, 0, ...OBJ.inventory());

(async () => {
  for (const [children, name] of [
    [body, "modele-rapport-complet-classique.docx"],
    [bodyObjets, "modele-rapport-complet-classique-objets.docx"],
  ]) {
    const p = path.join(OUT, name);
    fs.writeFileSync(p, await Packer.toBuffer(makeDoc(children)));
    console.log("écrit :", p);
  }
})();
