// Reproduction FIDÈLE des rapports « Exporter en Word » natifs éclatés (iteration.by = risk_category
// / per_risk). Produit word-templates/modele-rapport-complet-par-categorie.docx et
// modele-rapport-complet-par-risque.docx (distinct de build-word-templates.js).
//
// Utilisation (depuis ce dossier) :
//   npm install docx        # dépendance de génération (une fois ; non versionnée)
//   node build-rapport-complet-eclate.js
const fs = require("fs"), path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, PageBreak,
  Header, Footer, PageNumber, Tab, TabStopType, TableOfContents,
} = require("docx");

const OUT = process.env.OUT || __dirname;
const CW = 9638;
const MUTED = "7A8699", LABEL = "1F2937", ACCENT = "2F5BD0", BORDER = "D0D7E5";
const bd = { style: BorderStyle.SINGLE, size: 4, color: BORDER };
const TB = { top: bd, bottom: bd, left: bd, right: bd, insideHorizontal: bd, insideVertical: bd };

const txt = (t, o = {}) => new TextRun({ text: t, ...o });
const P = (children, o = {}) => new Paragraph({ children: [].concat(children), ...o });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [txt(t)] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [txt(t)] });
const h3 = (children) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [].concat(children).map(c => typeof c === "string" ? txt(c) : c) });
const tag = (t) => P(txt(t));                     // balise (bloc ou section) sur son paragraphe
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

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
const axisTable = (collection) => {
  const W = [900, 2400, CW - 3300];
  return new Table({
    columnWidths: W, width: { size: CW, type: WidthType.DXA }, borders: TB,
    rows: [
      new TableRow({ tableHeader: true, children: ["Valeur", "Libellé", "Description"].map((t, i) => cell(t, { w: W[i], head: true })) }),
      new TableRow({ children: [
        cell([txt("{{#each " + collection + "}}"), txt("{{ step.value }}")], { w: W[0] }),
        cell(txt("{{ step.label }}"), { w: W[1] }),
        cell([txt("{{ step.description }}"), txt(" "), txt("{{/each}}")], { w: W[2] }),
      ] }),
    ],
  });
};

// En-tête / pied avec zones (tabulations) ; {page}/{pages} via champs Word.
const zonesPara = (L, C, R) => new Paragraph({
  tabStops: [{ type: TabStopType.CENTER, position: Math.round(CW / 2) }, { type: TabStopType.RIGHT, position: CW }],
  children: [].concat(L, [new TextRun({ children: [new Tab()] })], C, [new TextRun({ children: [new Tab()] })], R),
});
const header = () => new Header({ children: [ zonesPara(
  [txt("{{ analysis.organization }}", { color: MUTED, size: 16 })],
  [txt("{{ analysis.title }}", { color: MUTED, size: 16 })],
  [txt("{{ analysis.author }}", { color: MUTED, size: 16 })]) ] });
const footer = () => new Footer({ children: [ zonesPara(
  [txt('{{ analysis.updated | date="ISO" }} {{ analysis.revision }}', { color: MUTED, size: 16 })],
  [new TextRun({ children: [PageNumber.CURRENT], color: MUTED, size: 16 }), txt(" / ", { color: MUTED, size: 16 }), new TextRun({ children: [PageNumber.TOTAL_PAGES], color: MUTED, size: 16 })],
  [txt("", { size: 16 })]) ] });

// Entrée de détail (heading + description + commentaire + notes cf) dans une boucle `coll`.
const detailLoop = (coll, headRuns, metaTag) => [
  P(txt("{{#each " + coll + " }}")),
  new Paragraph({ spacing: { before: 160, after: 40 }, children: [].concat(headRuns, metaTag ? [txt("   " + metaTag, { color: MUTED, size: 20 })] : []) }),
  P(txt("{{ " + coll.replace(/s$/, "") + ".description }}")),
  P(txt("{{ " + coll.replace(/s$/, "") + ".comment }}")),
  tag("{{ cf_notes }}"),
  P(txt("{{/each}}")),
];
const risksDetail = () => detailLoop("risks", [txt("{{ risk.id }} — {{ risk.label }}", { bold: true })], "{{ risk.category }}");
const measuresDetail = () => detailLoop("measures", [txt("{{ measure.id }} — {{ measure.label }}", { bold: true })], "{{ measure.type }} · {{ measure.status }} · {{ measure.responsible }}");
const linksDetail = () => [
  P(txt("{{#each links }}")),
  new Paragraph({ spacing: { before: 160, after: 40 }, children: [txt("{{ link.risk_id }} → {{ link.measure_id }}", { bold: true }), txt("   {{ link.risk.label }} → {{ link.measure.label }}", { color: MUTED, size: 20 })] }),
  P(txt("{{ link.comment }}")),
  tag("{{ cf_notes }}"),
  P(txt("{{/each}}")),
];

// Zone d'en-tête (une fois) : identique au classique.
const headerZone = () => [
  H1("Métadonnées"),
  twoColTable([
    ["Auteur", "{{ analysis.author }}"], ["Organisation", "{{ analysis.organization }}"],
    ["Périmètre", "{{ analysis.scope }}"], ["Référence méthodologique", "{{ analysis.reference }}"],
    ["Date de création", '{{ analysis.created | date="ISO" }}'], ["Dernière modification", '{{ analysis.updated | date="ISO" }}'],
    ["Révision", "{{ analysis.revision }}"], ["Statut", "{{ analysis.status }}"],
  ], 2600, CW - 2600),
  H1("Présentation"),
  P(txt("{{ analysis.description }}")),
  P([txt("Référentiels : ", { bold: true, color: LABEL }), txt("{{ analysis.cf.referentiels }}")]),
  P([txt("Périmètre : ", { bold: true, color: LABEL }), txt("{{ analysis.cf.perimetre }}")]),
  H1("Synthèse"), tag('{{ stat type="summary" }}'),
  H1("Répartition par criticité (initial → résiduel)"), tag('{{ stat type="distribution" }}'),
];

// Annexe (une fois) : plan d'action (par responsable), grille, niveaux, glossaire.
const appendix = () => [
  pageBreak(), H1("Annexe"),
  H2("Plan d'action"),
  P(txt('{{#each measures group_by="responsible" }}')),
  h3("{{ group.label }}"),
  tag('{{ table source="measures" columns="id,measure,status,resp,due" }}'),
  P(txt("{{/each}}")),
  H2("Grille de cotation"),
  P(txt("Méthode : {{ grid.method }}", { color: MUTED })),
  h3([txt("Axe vertical — "), txt("{{ grid.vertical_axis }}")]), axisTable("grid.vertical_axis.levels"),
  h3([txt("Axe horizontal — "), txt("{{ grid.horizontal_axis }}")]), axisTable("grid.horizontal_axis.levels"),
  H2("Niveaux de criticité (zones colorées)"), tag('{{ table source="levels" }}'),
  H2("Référentiels et légendes des champs"),
  P(txt('{{#each custom_fields glossary="true" }}')),
  h3([txt("{{ field.label }} — "), txt("{{ field.target }}")]),
  tag("{{ field_values }}"),
  P(txt("{{/each}}")),
];

// Sections répétées d'un chapitre (mode catégorie : jeu complet ; mode risque : détail + trajectoire + mesures).
const chapterBody = (mode) => {
  if (mode === "risque") {
    return [
      H2("Détail des risques"),
      P(txt("{{#each group.items }}")),
      new Paragraph({ spacing: { before: 160, after: 40 }, children: [txt("{{ risk.id }} — {{ risk.label }}", { bold: true }), txt("   {{ risk.category }}", { color: MUTED, size: 20 })] }),
      P(txt("{{ risk.description }}")), P(txt("{{ risk.comment }}")), tag("{{ cf_notes }}"),
      P(txt("{{/each}}")),
      H2("Trajectoire des risques"), tag('{{ matrix type="trajectory" }}'),
      H2("Mesures de maîtrise"), tag('{{ table source="measures" columns="id,measure,type,status,resp,covered" }}'),
    ];
  }
  return [].concat(
    [H2("Matrice initiale seule"), tag('{{ matrix type="initial" }}'),
     H2("Matrice résiduelle seule"), tag('{{ matrix type="residual" }}'),
     H2("Trajectoire des risques"), tag('{{ matrix type="trajectory" }}'),
     H2("Criticité moyenne — Catégorie · Superposés"), tag('{{ radar dimension="category" metric="average" evaluation="overlay" }}'),
     H2("Registre des risques"), tag('{{ table source="risks" columns="id,risk,cat,initial,residual,measures" }}'),
     H2("Détail des risques")], risksDetail(),
    [H2("Mesures de maîtrise"), tag('{{ table source="measures" columns="id,measure,type,status,resp,covered" }}'),
     H2("Détail des mesures")], measuresDetail(),
    [H2("Liens risques ↔ mesures"), tag('{{ table source="links" columns="rid,risk,mid,measure,notes" }}'),
     H2("Détail des liens")], linksDetail()
  );
};

function buildEclate(mode) {
  const groupBy = mode === "risque" ? "id" : "category";
  const body = [];
  // Page de garde
  body.push(tag("{{ logo }}"));
  body.push(new Paragraph({ heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER, spacing: { before: 120, after: 80 }, children: [txt("{{ analysis.title }}")] }));
  body.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [txt('{{ analysis.organization }} · {{ analysis.author }} · {{ analysis.updated | date="ISO" }} · Révision {{ analysis.revision }}', { color: MUTED })] }));
  body.push(pageBreak());
  // TOC
  body.push(H1("Table des matières"));
  body.push(new TableOfContents("Table des matières", { hyperlink: true, headingStyleRange: "1-2" }));
  // Zone d'en-tête
  headerZone().forEach(x => body.push(x));
  // Chapitres
  body.push(P(txt('{{#each risks group_by="' + groupBy + '" }}')));
  body.push(pageBreak());
  body.push(H1("{{ group.label }}"));
  body.push(new Paragraph({ spacing: { after: 120 }, children: [txt("Risques : {{ group.count }} · Mesures : {{ group.measures_count }}", { color: MUTED, size: 20 })] }));
  chapterBody(mode).forEach(x => body.push(x));
  body.push(P(txt("{{/each}}")));
  // Annexe
  appendix().forEach(x => body.push(x));

  return new Document({
    styles: {
      default: {
        document: { run: { font: "Calibri", size: 21 }, paragraph: { spacing: { after: 120, line: 264 }, widowControl: true } },
        title: { run: { font: "Calibri", size: 44, bold: true, color: "111827" }, paragraph: { spacing: { after: 80 }, keepNext: true, keepLines: true } },
        heading1: { run: { font: "Calibri", size: 30, bold: true, color: "1F2937" }, paragraph: { spacing: { before: 360, after: 120 }, keepNext: true, keepLines: true, outlineLevel: 0 } },
        heading2: { run: { font: "Calibri", size: 26, bold: true, color: "1F2937" }, paragraph: { spacing: { before: 280, after: 100 }, keepNext: true, keepLines: true, outlineLevel: 1 } },
        heading3: { run: { font: "Calibri", size: 22, bold: true, color: "3B4A63" }, paragraph: { spacing: { before: 160, after: 60 }, keepNext: true, keepLines: true, outlineLevel: 2 } },
      },
    },
    sections: [{
      properties: { page: { margin: { top: 1418, bottom: 1418, left: 1134, right: 1134, header: 708, footer: 708 } } },
      headers: { default: header() }, footers: { default: footer() },
      children: body,
    }],
  });
}

(async () => {
  for (const [mode, name] of [["categorie", "modele-rapport-complet-par-categorie.docx"], ["risque", "modele-rapport-complet-par-risque.docx"]]) {
    const p = path.join(OUT, name);
    fs.writeFileSync(p, await Packer.toBuffer(buildEclate(mode)));
    console.log("écrit :", p);
  }
})();
