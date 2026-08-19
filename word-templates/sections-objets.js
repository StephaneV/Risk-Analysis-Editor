// Sections « objets » AGNOSTIQUES pour les modèles Word complets.
// Restituent les objets, leurs attributs et leurs références SANS coder aucun code de type/attribut
// (blocs {{ object_notes }} + boucles {{#each object_types}} / {{#each type.attributes}} /
// {{#each objects}}). Un seul modèle fonctionne donc sur n'importe quelle analyse.
// Rappel moteur : chaque {{#each}} / {{/each}} va sur SON paragraphe (pas de boucle en ligne).
module.exports = function (docx, opt) {
  opt = opt || {};
  const CW = opt.CW || 9638;
  const MUTED = opt.MUTED || "7A8699", LABEL = opt.LABEL || "3B4A63";
  const { Paragraph, TextRun, HeadingLevel } = docx;
  const txt = (t, o = {}) => new TextRun({ text: t, ...o });
  const P = (c, o = {}) => new Paragraph({ children: [].concat(c), ...o });
  const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 340, after: 160 }, children: [txt(t)] });
  const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 260, after: 100 }, children: [txt(t)] });
  const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 160, after: 40 }, children: [txt(t)] });
  const sub = (t) => new Paragraph({ spacing: { before: 160, after: 60 }, children: [txt(t, { bold: true, color: LABEL, size: 22 })] });
  const blk = (tag) => P(txt(tag));

  // Schéma des types d'objets (agnostique) : un bloc par type + la liste de ses attributs.
  const schema = (opts) => {
    opts = opts || {};
    const out = [];
    if (opts.heading !== false) { out.push(H1("Types d'objets")); out.push(P(txt("Structure des types d'objets définis dans l'analyse (attributs et leur type).", { color: MUTED }))); }
    out.push(P(txt("{{#each object_types}}")));
    out.push(new Paragraph({ spacing: { before: 120, after: 20 }, children: [txt("{{ type.label }}", { bold: true, color: LABEL, size: 22 }), txt("   {{ type.count }} instance(s) · préfixe {{ type.id_prefix }} · nom : {{ type.name_attr }}", { color: MUTED, size: 20 })] }));
    out.push(P(txt("{{#each type.attributes}}")));
    out.push(P([txt("   • "), txt("{{ attribute.label }}", { bold: true }), txt("  ({{ attribute.code }} · {{ attribute.type }})", { color: MUTED, size: 20 })]));
    out.push(P(txt("{{/each}}")));
    out.push(P(txt("{{/each}}")));
    return out;
  };

  // Inventaire des instances (agnostique), en titres hiérarchisés : type (N2) → instance (N3) → attributs.
  const inventory = (opts) => {
    opts = opts || {};
    const out = [];
    if (opts.heading !== false) { out.push(H1("Objets")); out.push(P(txt("Inventaire des objets de l'analyse, groupés par type ; toutes les valeurs d'attributs, références déréférencées.", { color: MUTED }))); }
    out.push(P(txt('{{#each objects group_by="type"}}')));
    out.push(H2("{{ group.label }}"));                              // niveau 2 : type d'objet
    out.push(P(txt('{{#each group.items sort="id"}}')));
    out.push(H3("{{ object.id }} — {{ object.label }}"));           // niveau 3 : instance
    out.push(blk("{{ object_notes }}"));                            // attributs de l'instance
    out.push(P(txt("{{/each}}")));
    out.push(P(txt("{{/each}}")));
    return out;
  };

  // Bloc statistique agnostique : répartition des objets par type (tableau + graphique).
  const dashboard = (opts) => {
    opts = opts || {};
    const out = [];
    if (opts.heading !== false) out.push(H1("Objets par type"));
    out.push(blk('{{ stat type="objects" display="both" }}'));
    return out;
  };

  return { schema, inventory, dashboard, sub, H1, P, txt, blk };
};
