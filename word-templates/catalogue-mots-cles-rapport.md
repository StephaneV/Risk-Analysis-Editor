# Catalogue des mots-clés — modèles Word RAE

Référence pour rédiger un **modèle de rapport Word** (`.docx`) à charger dans Risk Analysis Editor.
Les balises s'écrivent entre **doubles accolades** `{{ … }}`, vocabulaire **anglais**. Voir la
spécification complète : [`SPEC-rapport-modele-word.md`](../specs/SPEC-rapport-modele-word.md). Modèles
prêts à l'emploi : **ce dossier** [`word-templates/`](.).

> **v1** = valeurs, boucles, filtres, blocs `matrix` / `radar` / `table`.
> **v2** (à venir) = statistiques (compteurs + graphiques) et conditions `{{#if}}`.

---

## 1. Démarrage rapide

1. Dans Word, rédigez la mise en page souhaitée (page de garde, styles, tableaux…).
2. Aux endroits à remplir, insérez des balises : `{{ analysis.title }}`, `{{ matrix type="initial" }}`, etc.
3. Pour répéter du contenu (un paragraphe, une **ligne de tableau**), encadrez-le d'une boucle
   `{{#each risks}} … {{/each}}`.
4. Chargez le modèle via **Fichier › Exporter avec un modèle Word…** ; le rapport rempli est téléchargé.

---

## 2. Configuration — `{{ report … }}`

Directive globale (non affichée), de préférence en tête de document.

| Attribut | Rôle | Exemple |
|---|---|---|
| `filter` | filtre appliqué à **tout** le rapport (§7) | `{{ report filter="category='Accès illégitime'" }}` |
| `date_format` | format de date par défaut | `{{ report date_format="JJ/MM/AAAA" }}` |

Le filtre global se **combine (ET)** aux filtres locaux. Un bloc/boucle l'ignore avec `report_filter="none"`.

---

## 3. Valeurs

Rendu **texte** par défaut. Voir les **formats** au §5.

### 3.1 Analyse — `analysis.*`
| Balise | Contenu |
|---|---|
| `{{ analysis.title }}` | titre |
| `{{ analysis.description }}` | description (texte enrichi Markdown) |
| `{{ analysis.author }}` | auteur |
| `{{ analysis.organization }}` | organisation |
| `{{ analysis.scope }}` | périmètre |
| `{{ analysis.reference }}` | référence méthodologique |
| `{{ analysis.revision }}` | révision |
| `{{ analysis.status }}` | statut (Brouillon / Validé / Archivé) |
| `{{ analysis.language }}` | langue |
| `{{ analysis.created }}` · `{{ analysis.updated }}` | dates de création / mise à jour |
| `{{ analysis.cf.<code> }}` | champ personnalisé d'analyse |

### 3.2 Grille — `grid.*`
`{{ grid.vertical_axis }}`, `{{ grid.horizontal_axis }}`, `{{ grid.method }}` (product/sum/matrix).
Collection `grid.levels` (niveaux de criticité) : `code`, `label`, `score_min`, `score_max`, `color`,
`acceptance`, `description`.

### 3.3 Risque — `risk.*` (dans `{{#each risks}}`)
| Balise | Contenu |
|---|---|
| `{{ risk.id }}` · `{{ risk.label }}` | identifiant · libellé |
| `{{ risk.category }}` · `{{ risk.owner }}` | catégorie · propriétaire |
| `{{ risk.description }}` · `{{ risk.comment }}` | description · commentaire (enrichis) |
| `{{ risk.initial.probability }}` · `{{ risk.initial.severity }}` | vraisemblance · gravité (initial) |
| `{{ risk.initial.score }}` · `{{ risk.initial.criticality }}` | score · criticité (libellé) |
| `{{ risk.initial.criticality_code }}` · `{{ risk.initial.color }}` | code niveau · couleur hex |
| `{{ risk.residual.* }}` | idem pour le risque résiduel |
| `{{ risk.evolution }}` | Réduit / Inchangé / Aggravé |
| `{{ risk.cf.<code> }}` | champ personnalisé de risque / de cotation |
| `risk.measures` · `risk.links` | sous-collections (boucles imbriquées) |

> Synonymes : `risk.gross.*` = `risk.initial.*`, `risk.net.*` = `risk.residual.*`.

### 3.4 Mesure — `measure.*` (dans `{{#each measures}}`)
`{{ measure.id }}`, `{{ measure.label }}`, `{{ measure.type }}`, `{{ measure.status }}`,
`{{ measure.responsible }}`, `{{ measure.due_date }}` (date), `{{ measure.cost }}`,
`{{ measure.description }}`, `{{ measure.comment }}`, `{{ measure.overdue }}` (en retard, booléen),
`{{ measure.cf.<code> }}`. Sous-collections : `measure.risks` (risques couverts), `measure.links`.

### 3.5 Lien — `link.*` (dans `{{#each links}}`)
`{{ link.comment }}`, `{{ link.cf.<code> }}`, et les objets résolus `{{ link.risk.* }}` /
`{{ link.measure.* }}` (tous les champs du risque et de la mesure reliés) ; `link.risk_id`,
`link.measure_id` pour les seuls identifiants.

---

## 4. Blocs — matrice, radar, tableau

Tous acceptent `filter="…"` (§7) et `report_filter="none"`.

### 4.1 `{{ matrix … }}`
| Attribut | Valeurs (défaut) |
|---|---|
| `type` | `initial` (syn. `gross`), `residual` (syn. `net`), `trajectory` — défaut `initial` |
| `title` | titre (aucun par défaut) |
| `width` | largeur en cm (ajustée à la page par défaut) |
| `filter` | filtre (§7) |

### 4.2 `{{ radar … }}`
`dimension` (`category` ou `cf.<code>`), `metric` (`average`, `max`, `cumulative`, `weighted`, `count`),
`evaluation` (`initial`, `residual`, `side`, `overlay`), `title`, `width`, `filter`.

### 4.3 `{{ table … }}`
| Attribut | Valeurs (défaut) |
|---|---|
| `source` | `risks`, `measures`, `links`, `levels` (**requis**) |
| `columns` | liste de champs (défaut : **colonnes par défaut de l'application**) |
| `sort` | `field[:asc\|desc]` |
| `style` | nom d'un **style de tableau du modèle** (`<w:tblStyle>`) |
| `filter` | filtre (§7) |

Ex. : `{{ table source="risks" columns="id,label,category,criticality_initial,criticality_residual" }}`

---

## 5. Formats de valeur (`| …`)

| Format | Effet |
|---|---|
| `date="ISO\|JJ/MM/AAAA\|MM/JJ/AAAA\|long"` | mise en forme d'une date |
| `codes` / `labels` | champ perso : par ses **codes** / ses **libellés** (défaut) |
| `join="; "` | séparateur pour un champ multi-valeurs |
| `percent` | ajoute « % » |
| `upper` / `lower` | casse |
| `default="—"` | valeur de repli si vide |

Ex. : `{{ measure.due_date | date="JJ/MM/AAAA" }}` · `{{ risk.owner | default="—" }}`

---

## 6. Boucles — `{{#each … }} … {{/each}}`

```
{{#each risks sort="criticality_initial:desc" filter="…" limit=10}}
  {{ risk.id }} — {{ risk.label }} : {{ risk.initial.criticality }}
{{/each}}
```

- **Collections** : `risks`, `measures`, `links`, `grid.levels`, et les **sous-collections**
  (`risk.measures`, `measure.risks`, …). Imbrication libre.
- **Attributs** : `filter`, `sort` (`field[:asc|desc]`), `limit`, `group_by`, `report_filter`.
- **Regroupement** `group_by="field"` → boucle de **groupes** : `{{ group.label }}`, `{{ group.count }}`,
  et `{{#each group.items}} … {{/each}}`.
- **Portée implicite du groupe** : dans un `group_by`, les matrices/tableaux/boucles imbriqués sont
  **auto-filtrés** sur la valeur du groupe → base du **rapport éclaté** par catégorie.
- **Boucle de ligne de tableau** : placez `{{#each …}}` au début de la 1re cellule d'une ligne et
  `{{/each}}` à la fin de la dernière → **la ligne** est répétée par élément (reprend la mise en forme
  du modèle).

---

## 7. Filtres — `filter="…"`

- **Comparaison** : `field operator "value"`. Opérateurs : `=`, `!=`, `>`, `>=`, `<`, `<=`, `contains`,
  `empty`, `not_empty`.
- **Combinaison** : `and`, `or`, parenthèses.
- **Champs** : `category`, `owner`, `type`, `status`, `responsible`, `overdue`, `criticality_initial`,
  `criticality_residual`, `cf.<code>`.
- **Code ou libellé** : la valeur est comparée au **code stocké** *ou* au **libellé affiché** (insensible
  à la casse). Ex. `status="in progress"` ≡ `status="in_progress"`.
- **Multi-valeurs** (tags) : `cf.source contains "internal"`.
- **Propagation** : un filtre de risque restreint aussi mesures/liens liés (et réciproquement).

Ex. : `filter="cf.source contains 'internal' and criticality_initial>='high'"`

---

## 8. Échappement

- Guillemets **interchangeables** : attribut en `"…"` ou `'…'`, chaîne de filtre en `'…'` ou `"…"`.
  Choisir celui absent du contenu → aucun échappement.
  Ex. : `filter="label contains \"l'accès d'urgence\""`.
- Sinon **`\`** déspécialise : `\'`, `\"`, `\\`.
  Ex. : `filter="label contains 'l\'accès'"`.
- Accolades littérales dans le texte : `\{{` et `\}}`.

---

## 9. Modèles d'exemple

Chaque modèle existe en version **propre** (prête à l'emploi) et **annotée** (`…-annote.docx`, avec
notes explicatives — à ne pas utiliser telle quelle, les notes apparaîtraient dans le rapport).

- [`modele-rapport-classique.docx`](modele-rapport-classique.docx) —
  rapport complet (présentation, matrices, grille, registre des risques, tableau de mesures en **boucle
  de ligne**, détail par risque avec sous-boucle, radar).
- [`modele-rapport-eclate-par-categorie.docx`](modele-rapport-eclate-par-categorie.docx) —
  synthèse générale puis **un chapitre par catégorie** (portée implicite du groupe).
