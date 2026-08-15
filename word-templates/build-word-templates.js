// Génère les modèles Word d'exemple du générateur de rapports « modèle Word » de RAE.
// Modèles (classique, éclaté par catégorie, référentiels, tableau de bord), chacun en version
// PROPRE et ANNOTÉE. Sortie : word-templates/ (ou $OUT). Nécessite le module npm « docx » (npm i docx).
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
const H2 = (children) => new Paragraph({ heading: HeadingLevel.HEADING_2,
  children: [].concat(children).map((c) => typeof c === "string" ? txt(c) : c) });

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
        cell(val("{{ measure.label }}")), cell(val("{{ measure.type }}")), cell(val("{{ measure.status | badge }}")),
        cell(val("{{ measure.responsible }}")),
        cell([val('{{ measure.due_date | date="JJ/MM/AAAA" }}'), txt(" "), blk("{{/each}}")]),
      ] }),
    ],
  });
}

// Registre des risques en boucle de ligne : colonne « Sources » en badges colorés (| badge),
// criticité précédée d'une pastille de couleur (| swatch).
const RCW = [800, 2400, 1400, 2400, 1500, 1500];
function rowLoopRisksTable() {
  const border = { style: BorderStyle.SINGLE, size: 4, color: "C9D3E0" };
  return new Table({
    columnWidths: RCW, width: { size: 10000, type: WidthType.DXA },
    borders: { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border },
    rows: [
      new TableRow({ tableHeader: true, children: ["ID", "Libellé", "Catégorie", "Sources", "Criticité initiale", "Criticité résiduelle"].map(headCell) }),
      new TableRow({ children: [
        cell([blk('{{#each risks sort="criticality_initial:desc"}}'), val("{{ risk.id }}")]),
        cell(val("{{ risk.label }}")),
        cell(val('{{ risk.category | default="—" }}')),
        cell(val("{{ risk.cf.source | badge }}")),
        cell(val("{{ risk.initial.criticality | badge }}")),
        cell([val("{{ risk.residual.criticality | badge }}"), txt(" "), blk("{{/each}}")]),
      ] }),
    ],
  });
}

// Tableau à ligne de corps répétée pour une échelle d'axe (vraisemblance / gravité).
const AXCW = [1100, 3200, 5900];
function rowLoopAxisTable(collection) {
  const border = { style: BorderStyle.SINGLE, size: 4, color: "C9D3E0" };
  return new Table({
    columnWidths: AXCW, width: { size: 10200, type: WidthType.DXA },
    borders: { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border },
    rows: [
      new TableRow({ tableHeader: true, children: ["Valeur", "Niveau", "Description"].map(headCell) }),
      new TableRow({ children: [
        cell([blk("{{#each " + collection + "}}"), val("{{ step.value }}")]),
        cell(val("{{ step.label }}")),
        cell([val("{{ step.description }}"), txt(" "), blk("{{/each}}")]),
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
    note("Registre construit dans Word (boucle de ligne, triée par criticité initiale décroissante) : les "
       + "colonnes « Sources » et « Criticité » affichent les étiquettes en badges colorés (| badge). "
       + "Le tableau auto-généré { table source=risks } est illustré dans le modèle éclaté."),
    rowLoopRisksTable(),
    H1("5. Mesures de maîtrise"),
    note("Tableau construit dans Word : la ligne de corps est répétée pour chaque mesure — la balise "
       + "d'ouverture de boucle est placée au début de la première cellule, la balise de fermeture à la fin "
       + "de la dernière. La colonne « Statut » est affichée en badge coloré (| badge)."),
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

  const referentiels = () => new Document({ sections: [{ children: [
    ...header("Référentiels de l'analyse"),
    H1("1. Informations sur l'analyse"),
    note("Toutes les métadonnées de l'analyse, y compris la référence méthodologique."),
    P([txt("Titre : "), val("{{ analysis.title }}")]),
    P([txt("Organisation : "), val('{{ analysis.organization | default="—" }}'),
       txt(" · Auteur : "), val('{{ analysis.author | default="—" }}')]),
    P([txt("Périmètre : "), val('{{ analysis.scope | default="—" }}')]),
    P([txt("Référence méthodologique : "), val('{{ analysis.reference | default="—" }}')]),
    P([txt("Révision : "), val('{{ analysis.revision | default="—" }}'),
       txt(" · Statut : "), val("{{ analysis.status }}"),
       txt(" · Langue : "), val("{{ analysis.language }}")]),
    P([txt("Créée le : "), val('{{ analysis.created | date="long" }}'),
       txt(" · Mise à jour le : "), val('{{ analysis.updated | date="long" }}')]),
    P(txt("Description :")),
    P(val("{{ analysis.description }}")),
    H1("2. Grille de cotation"),
    P([txt("Méthode de calcul du score : "), val("{{ grid.method }}")]),
    H2([txt("Échelle de vraisemblance — "), val("{{ grid.vertical_axis }}")]),
    note("Table construite dans Word : la ligne de corps est répétée pour chaque niveau de l'échelle "
       + "(balise d'ouverture au début de la première cellule, fermeture à la fin de la dernière)."),
    rowLoopAxisTable("grid.vertical_axis.levels"),
    H2([txt("Échelle de gravité — "), val("{{ grid.horizontal_axis }}")]),
    rowLoopAxisTable("grid.horizontal_axis.levels"),
    H2("Niveaux de criticité"),
    P(blk('{{ table source="levels" }}')),
    H1("3. Champs personnalisés — tableaux récapitulatifs"),
    note("Bloc clé en main : colonnes code, libellé, cible, type, obligatoire, filtrable. Sans attribut, "
       + "tous les champs ; avec l'attribut target, une seule cible (analysis / risk / measure / link / cotation)."),
    H2("Tous les champs"),
    P(blk('{{ table source="custom_fields" }}')),
    H2("Champs de l'analyse"),
    P(blk('{{ table source="custom_fields" target="analysis" }}')),
    H2("Champs des risques"),
    P(blk('{{ table source="custom_fields" target="risk" }}')),
    H2("Champs des mesures"),
    P(blk('{{ table source="custom_fields" target="measure" }}')),
    H2("Champs des liens"),
    P(blk('{{ table source="custom_fields" target="link" }}')),
    note("La cible « cotation » (champs propres aux cotations de risque) s'utilise de la même façon."),
    H1("4. Détail des champs et de leurs valeurs"),
    note("Boucle sur les champs, triée par cible puis par code (tri multi-clés « target,code »). "
       + "Pour les champs à valeurs fermées (sélection, cases, étiquettes), sous-boucle sur les valeurs "
       + "possibles : code, libellé, couleur et description."),
    P(blk('{{#each custom_fields sort="target,code" }}')),
    H2([val("{{ field.label }}"), txt(" — "), val("{{ field.code }}")]),
    P([txt("Cible : "), val("{{ field.target }}"), txt(" · Type : "), val("{{ field.type }}"),
       txt(" · Obligatoire : "), val("{{ field.required }}"), txt(" · Filtre : "), val("{{ field.filterable }}")]),
    P([txt("Aide : "), val('{{ field.help | default="—" }}')]),
    P([txt("Description : "), val('{{ field.description | default="—" }}')]),
    P(txt("Valeurs possibles :")),
    P(blk("{{#each field.items }}")),
    P([val("{{ option.code }}"), txt(" — "), val("{{ option.label }}"), txt(" ("),
       val("{{ option.color | swatch }}"), txt(" "), val("{{ option.color }}"),
       txt(") : "), val('{{ option.description | default="—" }}')], { bullet: { level: 0 } }),
    P(blk("{{/each}}")),
    note("Même présentation qu'au rapport (« Référentiels et légendes des champs ») : tableau Valeur / "
       + "Description, badge coloré pour les tags. Le bloc n'apparaît que pour les champs à valeurs fermées "
       + "(sélection / cases / étiquettes) dont au moins une valeur porte une description."),
    P(blk("{{ field_values }}")),
    P(blk("{{/each}}")),
  ].filter(Boolean) }] });

  // Tableau de bord (v2) : statistiques (compteurs, couverture, graphiques donut/secteur) et sections
  // conditionnelles ({{#if}} / {{#unless}} de niveau bloc, dans et hors boucle).
  const tableauDeBord = () => new Document({ sections: [{ children: [
    new Paragraph({ heading: HeadingLevel.TITLE, children: [txt("Tableau de bord des risques")] }),
    P([val("{{ analysis.title }}"), txt(" · "), val("{{ analysis.organization }}"),
       txt(" · mise à jour "), val('{{ analysis.updated | date="long" }}')]),
    note("Modèle « tableau de bord » (v2) : blocs statistiques (compteurs, couverture, graphiques) et "
       + "sections conditionnelles. Aucune donnée saisie ici — tout est calculé à la génération."),

    H1("Chiffres clés"),
    note("Tuiles clés : Risques · Mesures · Risques réduits · % traité."),
    P(blk('{{ stat type="counters" }}')),
    note("Condition de niveau bloc : chaque balise {{#if}} / {{else}} / {{/if}} est SEULE sur son paragraphe."),
    P(blk('{{#if analysis.reduced_count > "0"}}')),
    P([val("{{ analysis.reduced_count }}"), txt(" risque(s) réduit(s) sur "), val("{{ analysis.risks_count }}"),
       txt(" — la maîtrise progresse.")]),
    P(blk("{{else}}")),
    P(txt("Aucun risque n'a encore été réduit entre l'initial et le résiduel.")),
    P(blk("{{/if}}")),

    H1("Couverture du traitement"),
    P(blk('{{ stat type="coverage" }}')),
    note("Condition {{#unless}} : le message ne s'affiche que si aucun lien n'est défini."),
    P(blk('{{#unless analysis.links_count > "0"}}')),
    P(txt("⚠ Aucun lien risque↔mesure n'est défini : la couverture ne peut pas être évaluée.")),
    P(blk("{{/unless}}")),

    H1("Criticité — initial vs résiduel"),
    note('display="both" : les deux graphiques (Initial / Résiduel) puis le tableau, centrés.'),
    P(blk('{{ stat type="criticality" display="both" shape="donut" }}')),

    H1("Répartition des risques par catégorie"),
    note('display="chart" : graphique + légende sur une même ligne, centrés.'),
    P(blk('{{ stat type="category" display="chart" shape="pie" }}')),

    H1("Avancement des mesures"),
    P(blk('{{ stat type="measure_status" display="both" shape="donut" }}')),

    P(new PageBreak()),

    H1("Suivi des échéances"),
    note("Boucle de LIGNE de tableau : la ligne de corps se répète pour chaque mesure ; statut en badge coloré."),
    rowLoopMeasuresTable(),

    H1("Mesures en retard"),
    note("Boucle + condition {{#if}} de niveau bloc à l'intérieur : n'affiche que les mesures en retard "
       + "(champ dérivé measure.overdue). Rien ne s'affiche si aucune n'est en retard."),
    P(blk('{{#each measures sort="due_date"}}')),
    P(blk("{{#if measure.overdue}}")),
    P([txt("⚠ ", { color: "C0392B", bold: true }), val("{{ measure.id }}"), txt(" — "), val("{{ measure.label }}"),
       txt(" · échéance "), val('{{ measure.due_date | date="JJ/MM/AAAA" }}'), txt(" · "), val("{{ measure.responsible }}")],
       { bullet: { level: 0 } }),
    P(blk("{{/if}}")),
    P(blk("{{/each}}")),

    H1("Points de vigilance"),
    note("Condition avec « or » et badge : ne liste que les risques dont la criticité résiduelle reste "
       + "importante ou maximale (comparaison sur criticality_code)."),
    P(blk('{{#each risks sort="criticality_residual:desc"}}')),
    P(blk('{{#if risk.residual.criticality_code = "important" or risk.residual.criticality_code = "maximal"}}')),
    P([val("{{ risk.id }}"), txt(" — "), val("{{ risk.label }}"), txt("  "),
       val("{{ risk.residual.criticality | badge }}")], { bullet: { level: 0 } }),
    P(blk("{{/if}}")),
    P(blk("{{/each}}")),
  ].filter(Boolean) }] });

  return { classique: classique(), eclate: eclate(), referentiels: referentiels(), tableauDeBord: tableauDeBord() };
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
  await write(clean.referentiels, "modele-referentiels.docx");
  await write(annot.referentiels, "modele-referentiels-annote.docx");
  await write(clean.tableauDeBord, "modele-tableau-de-bord.docx");
  await write(annot.tableauDeBord, "modele-tableau-de-bord-annote.docx");
})();
