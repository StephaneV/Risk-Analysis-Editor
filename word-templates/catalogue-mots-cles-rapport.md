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
| `{{ analysis.risks_count }}` · `{{ analysis.measures_count }}` · `{{ analysis.links_count }}` | nombres de risques · mesures · liens |
| `{{ analysis.reduced_count }}` | nombre de risques réduits (cotation modifiée entre initial et résiduel) |
| `{{ analysis.cf.<code> }}` | champ personnalisé d'analyse |

### 3.2 Grille — `grid.*`
`{{ grid.vertical_axis }}`, `{{ grid.horizontal_axis }}`, `{{ grid.method }}` (libellé localisé de la
méthode, ex. « Produit (P × G) »).
Collection `grid.levels` (niveaux de criticité, triée par ordre) : `code`, `label` (**étiquette colorée** —
`{{ level.label | badge }}`), `score_min`, `score_max`, `color`, `acceptance`, `description`, plus les
**comptes de risques** `count_initial` et `count_residual` (par ce niveau, en initial / résiduel).
**Échelles d'axes** — collections `grid.vertical_axis.levels` (vraisemblance) et
`grid.horizontal_axis.levels` (gravité), frame `step` : `{{ step.value }}`, `{{ step.label }}`,
`{{ step.description }}`.

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

### 3.6 Champs personnalisés — référentiel (`custom_fields`)

Pour **décrire** les champs personnalisés (et non lire leurs valeurs) : collection `custom_fields`,
frame `field`. Attribut optionnel `target` (`analysis` · `risk` · `measure` · `link` · `cotation`)
pour se limiter à une cible ; `glossary="true"` pour ne garder que les champs à **valeurs décrites**
(comme le glossaire du rapport) ; `sort`, `limit` acceptés.

```
{{#each custom_fields target="risk"}}
  {{ field.label }} ({{ field.code }}) — {{ field.type }}
  {{#each field.items}}
    {{ option.code }} = {{ option.label }} [{{ option.color }}]
  {{/each}}
{{/each}}
```

| Balise | Contenu |
|---|---|
| `{{ field.code }}` · `{{ field.label }}` | code · libellé |
| `{{ field.target }}` · `{{ field.type }}` | cible · type (libellés localisés) |
| `{{ field.required }}` · `{{ field.filterable }}` | obligatoire · utilisable comme filtre (Oui/Non) |
| `{{ field.help }}` · `{{ field.description }}` | aide · description |
| `field.items` | sous-collection des valeurs possibles (types à valeurs fermées), frame `option` |
| `{{ option.code }}` · `{{ option.label }}` · `{{ option.color }}` · `{{ option.description }}` | code · libellé · couleur · description d'une valeur |

Tableau clé en main : `{{ table source="custom_fields" }}` (colonnes : code, libellé, cible, type,
obligatoire, filtrable), avec `target="…"` optionnel.

**Tableau des valeurs** (dans une boucle `custom_fields`) : `{{ field_values }}` — tableau
**Valeur / Description** du champ courant, **badge coloré pour les tags** (§4.4).

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
| `source` | `risks`, `measures`, `links`, `levels`, `custom_fields` (**requis**) |
| `columns` | liste de champs (défaut : **colonnes par défaut de l'application**) |
| `sort` | `field[:asc\|desc]` (multi-clés : `field1,field2:desc`) |
| `style` | nom d'un **style de tableau du modèle** (`<w:tblStyle>`) |
| `filter` | filtre (§7) |

Ex. : `{{ table source="risks" columns="id,label,category,criticality_initial,criticality_residual" }}`

### 4.4 `{{ field_values }}`
Dans une boucle `custom_fields` (§3.6) : tableau **Valeur / Description** des valeurs du champ courant,
avec un **badge coloré** pour les champs de type `tags` (texte simple pour `select` / `checklist`).
Reproduit la section « Référentiels et légendes des champs » du rapport intégré. Ne produit rien
(paragraphe retiré) pour les champs sans valeurs fermées, ou dont aucune valeur n'a de description.

### 4.5 `{{ stat type="…" }}`
Tableaux statistiques du rapport intégré :
- `type="summary"` → **synthèse** (Risques / Mesures / Risques réduits) ;
- `type="distribution"` → **répartition par criticité** (Libellé en cellule colorée · Initial · Résiduel).

### 4.6 `{{ cf_notes }}`
Dans une boucle `risks` / `measures` / `links` : **notes des champs personnalisés** de l'entité courante
(un « Libellé : valeur » par champ renseigné). Reproduit les notes des sections « Détail » du rapport.

### 4.7 `{{ logo }}`
Insère le **logo de couverture configuré** de l'analyse (`extensions…report.cover.logo`). Attribut
`width="cm"` optionnel. Ne produit rien si aucun logo n'est configuré.

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
| `swatch` | **couleur** (`*.color`) → **pastille carrée** ; **tags** / **étiquettes colorées** (statut, criticité) → pastille + libellé |
| `badge` | **tags** / **étiquettes colorées** (statut, criticité) → libellé sur **fond coloré** |

Ex. : `{{ risk.initial.color | swatch }}` · `{{ risk.cf.source | badge }}` · `{{ option.color | swatch }}` ·
`{{ measure.status | badge }}` · `{{ risk.initial.criticality | badge }}`

> `swatch` / `badge` produisent des **runs colorés** dans le document. `badge` = libellé sur fond coloré
> (texte contrasté) ; `swatch` = pastille carrée colorée (seule pour une **valeur couleur**, suivie du
> libellé pour un **tags** ou une **étiquette colorée**). S'appliquent aux champs **tags**, au **statut**
> de mesure et à la **criticité** (initiale/résiduelle). Une valeur multi-étiquettes produit une pastille
> par valeur. Sur une valeur non pertinente, repli en texte simple.

---

## 6. Boucles — `{{#each … }} … {{/each}}`

```
{{#each risks sort="criticality_initial:desc" filter="…" limit=10}}
  {{ risk.id }} — {{ risk.label }} : {{ risk.initial.criticality }}
{{/each}}
```

- **Collections** : `risks`, `measures`, `links`, `grid.levels`, `custom_fields`,
  `grid.vertical_axis.levels`, `grid.horizontal_axis.levels`, et les **sous-collections**
  (`risk.measures`, `measure.risks`, `field.items`, …). Imbrication libre.
- **Attributs** : `filter`, `sort`, `limit`, `group_by`, `report_filter`.
- **Tri multi-clés** : `sort="champ1[:asc|desc], champ2[:asc|desc], …"` — les clés sont appliquées
  successivement (départage). Ex. `sort="target,code"` (cible puis code), `sort="criticality_initial:desc,label"`.
- **Regroupement** `group_by="field"` → boucle de **groupes** : `{{ group.label }}`, `{{ group.count }}`,
  `{{ group.measures_count }}` (groupes de risques), et `{{#each group.items}} … {{/each}}`.
  Champs de regroupement des risques : `category`, `owner`, `criticality_initial/residual`, `cf.<code>`,
  et **`id`** (un chapitre par risque). Mesures : `type`, `status`, `responsible`, `cf.<code>`.
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
- [`modele-referentiels.docx`](modele-referentiels.docx) —
  **référentiels** : grille de cotation (méthode, échelles d'axes en boucle de ligne, niveaux de
  criticité) et **champs personnalisés** (tableau récapitulatif + détail des caractéristiques et des
  valeurs possibles).
