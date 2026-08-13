// Génère les modèles Word d'exemple du générateur de rapports « modèle Word » de RAE.
// Deux modèles (classique, éclaté par catégorie), chacun en version PROPRE et ANNOTÉE.
// Sortie : word-templates/ (ou $OUT). Nécessite le module npm « docx » (npm i docx).
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, PageBreak,
} = require("docx");

const OUT = process.env.OUT || __dirname;
fs.mkdirSync(OUT, { recursive: true });

const ACCENT = "2F5BD0", MUTED = "8A94A6";
const val = (t) => new TextRun({ text: t, font: "Consolas" });
const blk = (t) => new TextRun({ text: t, font: "Consolas", color: ACCENT, bold: true });
const txt = (t, o = {}) => new TextRun({ text: t, ...o });
const P = (children, o = {}) => new Paragraph({ children: [].concat(children), ...o });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [txt(t)] });
const H2 = (children) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [].concat(children) });

// Tableau à ligne de corps répétée (boucle de ligne) — mesures.
const CW = [900, 3000, 1500, 1500, 1900, 1400];
const cell = (children, { head = false } = {}) => new TableCell({
  width: { size: 0, type: WidthType.AUTO },
  shading: head ? { type: ShadingType.CLEAR, color: "auto", fill: "EEF2F8" } : undefined,
  margins: { top: 40, bottom: 40, left: 80, right: 80 },
  children: [new Paragraph({ children: [].concat(children) })],
});
const headCell = (t) => cell(new TextRun({ text: t, bold: true, size: 18 }), { head: true });
function rowLoopMeasuresTable() {
  const border = { style: BorderStyle.SINGLE, size: 4, color: "C9D3E0" };
  return new Table({
    columnWidths: CW, width: { size: 10200, type: WidthType.DXA },
    borders: { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border },
    rows: [
      new TableRow({ tableHeader: true, children: ["ID", "Mesure", "Type", "Statut", "Responsable", "Échéance"].map(headCell) }),
      new TableRow({ children: [
        cell([blk("{{#each measures}}"), val("{{ measure.id }}")]),
        cell(val("{{ measure.label }}")), cell(val("{{ measure.type }}")), cell(val("{{ measure.status }}")),
        cell(val("{{ measure.responsible }}")),
        cell([val('{{ measure.due_date | date="JJ/MM/AAAA" }}'), txt(" "), blk("{{/each}}")]),
      ] }),
    ],
  });
}

// `ann` = document annoté (notes explicatives grises) ou non.
function build(ann) {
  const note = (t) => ann ? new Paragraph({ spacing: { before: 60, after: 60 },
    children: [new TextRun({ text: t, italics: true, color: MUTED, size: 18 })] }) : null;
  const header = (subtitle) => {
    const k = [new Paragraph({ heading: HeadingLevel.TITLE, children: [val("{{ analysis.title }}")] })];
    if (subtitle) k.push(P(txt(subtitle, { color: MUTED, size: 24 })));
    k.push(
      P([val("{{ analysis.organization }}"), txt(" — "), val("{{ analysis.author }}")]),
      P([txt("Périmètre : "), val("{{ analysis.scope }}")]),
      P([txt("Version "), val("{{ analysis.revision }}"), txt(" · "), val("{{ analysis.status }}"),
         txt(" · "), val('{{ analysis.updated | date="long" }}')]),
      note("Les champs à remplacer sont écrits entre doubles accolades et sont remplacés à la génération "
         + "(voir le catalogue des mots-clés). Les balises de boucle et de bloc apparaissent en bleu ; "
         + "les valeurs texte, en police à chasse fixe."),
      note("Directive de configuration (non affichée dans le rapport) :"),
      P(blk('{{ report date_format="JJ/MM/AAAA" }}')),
      P(new PageBreak()),
    );
    return k;
  };

  const classique = () => new Document({ sections: [{ children: [
    ...header(null),
    H1("1. Présentation"), P(val("{{ analysis.description }}")),
    H1("2. Matrices de risque"),
    P(blk('{{ matrix type="initial" title="Risque initial" }}')),
    P(blk('{{ matrix type="residual" title="Risque résiduel" }}')),
    P(blk('{{ matrix type="trajectory" title="Trajectoire" }}')),
    H1("3. Grille de cotation"), P(blk('{{ table source="levels" }}')),
    H1("4. Registre des risques"),
    note("Tableau auto-généré : colonnes par défaut de l'application, avec un style de tableau du modèle "
       + "(remplacer « Grid Table 4 Accent 1 » par le nom d'un style présent dans votre modèle)."),
    P(blk('{{ table source="risks" style="Grid Table 4 Accent 1" }}')),
    H1("5. Mesures de maîtrise"),
    note("Tableau construit dans Word : la ligne de corps est répétée pour chaque mesure — la balise "
       + "d'ouverture de boucle est placée au début de la première cellule, la balise de fermeture à la fin de la dernière."),
    rowLoopMeasuresTable(),
    H1("6. Détail par risque"),
    note("Boucle sur les risques (triés par criticité initiale décroissante), avec sous-boucle sur leurs mesures."),
    P(blk('{{#each risks sort="criticality_initial:desc" }}')),
    H2([val("{{ risk.id }}"), txt(" — "), val("{{ risk.label }}")]),
    P([txt("Catégorie : "), val("{{ risk.category }}"), txt(" · Propriétaire : "), val('{{ risk.owner | default="—" }}')]),
    P([txt("Criticité : "), val("{{ risk.initial.criticality }}"), txt(" → "), val("{{ risk.residual.criticality }}"),
       txt(" ("), val("{{ risk.evolution }}"), txt(")")]),
    P(val("{{ risk.description }}")), P(txt("Mesures de maîtrise :")),
    P(blk("{{#each risk.measures }}")),
    P([val("{{ measure.label }}"), txt(" ("), val("{{ measure.status }}"), txt(")")], { bullet: { level: 0 } }),
    P(blk("{{/each}}")), P(blk("{{/each}}")),
    H1("7. Profil par source de risque"),
    P(blk('{{ radar dimension="cf.source" metric="average" evaluation="overlay" title="Criticité moyenne par source" }}')),
  ].filter(Boolean) }] });

  const eclate = () => new Document({ sections: [{ children: [
    ...header("Rapport par catégorie de risque"),
    H1("Synthèse générale"),
    P(blk('{{ matrix type="trajectory" title="Vue d\'ensemble" }}')),
    P(blk('{{ table source="risks" columns="id,label,category,criticality_initial,criticality_residual" }}')),
    H1("Analyse par catégorie"),
    note("Un chapitre par catégorie : à l'intérieur du group_by, matrice et tableau sont "
       + "automatiquement filtrés sur la catégorie courante (portée implicite du groupe)."),
    P(blk('{{#each risks group_by="category" }}')),
    H2([val("{{ group.label }}"), txt(" ("), val("{{ group.count }}"), txt(" risques)")]),
    P(blk('{{ matrix type="trajectory" }}')),
    P(blk('{{ table source="risks" columns="id,label,criticality_initial,criticality_residual,evolution" }}')),
    P(txt("Mesures associées :")),
    P(blk("{{#each measures }}")),
    P([val("{{ measure.label }}"), txt(" ("), val("{{ measure.status }}"), txt(")")], { bullet: { level: 0 } }),
    P(blk("{{/each}}")), P(blk("{{/each}}")),
  ].filter(Boolean) }] });

  return { classique: classique(), eclate: eclate() };
}

async function write(doc, name) {
  const p = path.join(OUT, name);
  fs.writeFileSync(p, await Packer.toBuffer(doc));
  console.log("écrit :", name);
}
(async () => {
  const clean = build(false), annot = build(true);
  await write(clean.classique, "modele-rapport-classique.docx");
  await write(annot.classique, "modele-rapport-classique-annote.docx");
  await write(clean.eclate, "modele-rapport-eclate-par-categorie.docx");
  await write(annot.eclate, "modele-rapport-eclate-par-categorie-annote.docx");
})();
