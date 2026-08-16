# Spécification — Générateur de rapports à partir d'un modèle Word

> Brouillon de travail (branche `feat/rapport-modele-word`). But : charger un **modèle `.docx`**
> contenant des **balises** (mots-clés, en **anglais**), et produire un document Word où ces balises sont
> remplacées par les **valeurs**, **tableaux**, **matrices** et **radars** de l'analyse courante.
> Le modèle porte la mise en page et la charte ; l'application remplit le contenu.

**Décisions arrêtées** (cf. §12) : vocabulaire des balises **en anglais** ; **blocs nommés**
(`matrix`, `radar`, `table`) ; colonnes d'un tableau omises → **colonnes par défaut de l'application** ;
le **filtre actif de l'app n'est pas utilisé** — un rapport définit son propre filtre via la balise de
configuration **`{{ report filter="…" }}`**. La **v2** ajoute les **statistiques** (compteurs, couverture,
graphiques anneau/secteur — §4.5), les **conditions `{{#if}}` / `{{#unless}}`** (§6.1) et les **dimensions
d'images** `width` / `height` (§4.8).

---

## 1. Principe et flux

1. L'utilisateur **charge un modèle** `.docx` (Fichier › *Exporter avec un modèle Word…*).
2. L'application **dézippe** le `.docx` (fflate `unzipSync` — déjà embarqué) et lit `word/document.xml`
   (et, au besoin, en-têtes/pieds `header*.xml` / `footer*.xml`).
3. Elle **analyse les balises**, applique la **configuration** (`{{ report … }}`), les **boucles** et les
   **filtres**, remplace **valeurs** et **blocs**.
4. Elle **réinjecte** les fragments OOXML (réutilise `dxTbl` pour les tableaux, `addSvgImage` pour les
   images, `mdDocxBlocks` pour le texte enrichi), ajoute les images aux relations du modèle, puis
   **re-zippe** (fflate `zipSync`) et **télécharge** le document rempli.

Le modèle reste la **source unique de la mise en forme**. Ce mode **coexiste** avec l'export Word actuel
(généré de zéro), qui n'est pas modifié.

---

## 2. Syntaxe générale des balises

Délimiteurs : **`{{ … }}`**. Vocabulaire **anglais**. Familles :

| Famille | Forme | Rôle |
|---|---|---|
| **Configuration** | `{{ report attr="…" }}` | réglages du rapport (filtre global, format de date…) — non rendu |
| **Valeur** | `{{ path [\| format] }}` | insère une valeur (texte par défaut) |
| **Bloc** | `{{ block attr="…" … }}` | insère un tableau / une matrice / un radar |
| **Section / boucle** | `{{#each collection …}} … {{/each}}` | répète le contenu entre les balises |
| **Condition** | `{{#if expr}} … {{else}} … {{/if}}`, `{{#unless expr}}` | contenu conditionnel (§6.1) |
| **Commentaire** | `{{! … }}` | ignoré (non rendu) |

- **Attributs** : `key="value"`. Listes séparées par des virgules (`columns="id,label"`).
- **Balise inconnue** : laissée telle quelle + **signalée** (liste d'avertissements en fin de génération).
- Word découpe souvent une balise en plusieurs *runs* : l'implémentation **normalise les runs** d'un
  paragraphe avant de repérer `{{ … }}` (voir §10).

### 2.1 Balise de configuration — `{{ report … }}`

Définit des réglages **valables pour tout le document** (à placer de préférence en tête ; non rendu) :

| Attribut | Rôle |
|---|---|
| `filter` | **filtre global** appliqué à l'ensemble du rapport (valeurs comptées, boucles, matrices, radars, tableaux) — voir §8 |
| `date_format` | format de date par défaut (`ISO`, `JJ/MM/AAAA`, `MM/JJ/AAAA`, `long`) |

- Le filtre global **se combine (ET)** avec le `filter="…"` éventuel d'un bloc ou d'une boucle.
- Un bloc/boucle peut **ignorer** le filtre global avec `report_filter="none"`.
- Plusieurs `{{ report }}` : les filtres se cumulent (ET), les scalaires suivent le dernier.

### 2.2 Échappement (déspécialisation) des caractères

Dans une balise, certains caractères sont **spéciaux** : les délimiteurs `{{` et `}}`, et les guillemets
qui encadrent les valeurs d'attribut (`"…"`) ou les chaînes d'un filtre (`'…'`). Pour insérer un de ces
caractères **littéralement** :

- **Guillemets interchangeables** : une valeur d'attribut peut être encadrée par `"…"` **ou** `'…'`, et
  une chaîne de filtre par `'…'` **ou** `"…"`. On choisit de préférence le guillemet **absent** du
  contenu — aucune déspécialisation n'est alors nécessaire.
  Ex. : `filter="category=\"L'accès d'urgence\""` (les apostrophes ne sont pas échappées, la chaîne étant délimitée par `"`).
- **Échappement par `\`** : à l'intérieur d'une chaîne, `\` déspécialise le caractère suivant —
  `\'` = apostrophe littérale, `\"` = guillemet littéral, `\\` = antislash littéral.
  Ex. : `filter="label contains 'l\'accès'"`.
- **Accolades littérales** dans le texte du modèle : écrire `\{{` et `\}}` pour afficher `{{` et `}}`
  sans les interpréter comme une balise.
- Ces règles s'appliquent **après** la normalisation des runs (§10) : un `\` (ou une balise) scindé par
  Word est d'abord recollé, puis l'échappement est résolu.

---

## 3. Espace de noms des données

Chemins en notation pointée, **noms anglais**, correspondant aux clés du format `.rae.json`.

### 3.1 Contexte racine — `analysis`

| Balise | Clé `.rae.json` | Rendu |
|---|---|---|
| `analysis.title` | `metadata.title` | texte |
| `analysis.description` | `metadata.description` | texte enrichi (Markdown) |
| `analysis.author` | `metadata.author` | texte |
| `analysis.organization` | `metadata.organization` | texte |
| `analysis.scope` | `metadata.scope` | texte |
| `analysis.reference` | `metadata.methodology_reference` | texte |
| `analysis.revision` | `metadata.revision` | texte |
| `analysis.status` | `metadata.status` | libellé (Draft / Validated / Archived) |
| `analysis.language` | `metadata.language` | texte |
| `analysis.created` | `metadata.created_at` | date (format §5) |
| `analysis.updated` | `metadata.updated_at` | date |
| `analysis.cf.<code>` | `custom.<code>` (cible *analysis*) | libellé(s) du champ perso |
| `analysis.risks_count` · `analysis.measures_count` · `analysis.links_count` | *(dérivé)* | nombres |
| `analysis.reduced_count` | *(dérivé)* | nombre de risques dont la cotation a changé (initial → résiduel) |

> Compteurs et tableaux statistiques : voir aussi le bloc **`{{ stat … }}`** (§4.5) et les comptes par
> niveau `level.count_initial` / `level.count_residual` (§3.2).

### 3.2 Grille — `grid`

`grid.vertical_axis`, `grid.horizontal_axis`, `grid.method` (**libellé localisé** de la méthode).
Collection `grid.levels` (pour une boucle ou `table source="levels"`, triée par ordre), chaque niveau
exposant : `code`, `label` (**étiquette colorée**, cf. `| badge`), `score_min`, `score_max`, `color`,
`acceptance`, `description`, et les comptes de risques `count_initial` / `count_residual`.

**Échelles d'axes** — collections `grid.vertical_axis.levels` (vraisemblance) et
`grid.horizontal_axis.levels` (gravité), item `step` : `step.value` (nombre), `step.label`,
`step.description`.

### 3.3 Objet **risk** (boucle `risks`, item `risk`)

| Balise | Clé | Rendu |
|---|---|---|
| `risk.id` | `id` | texte |
| `risk.label` | `label` | texte |
| `risk.category` | `category` | texte |
| `risk.owner` | `owner` | texte |
| `risk.description` | `description` | texte enrichi |
| `risk.comment` | `comment` | texte enrichi |
| `risk.initial.probability` | `initial_assessment.probability` | nombre / libellé de niveau |
| `risk.initial.severity` | `initial_assessment.severity` | nombre / libellé |
| `risk.initial.score` | *(dérivé)* | nombre |
| `risk.initial.criticality` | *(dérivé)* | libellé du niveau |
| `risk.initial.criticality_code` | *(dérivé)* | code du niveau |
| `risk.initial.color` | *(dérivé)* | code couleur hex |
| `risk.residual.*` | idem sur `residual_assessment` | idem |
| `risk.evolution` | *(dérivé)* | Reduced / Unchanged / Worsened |
| `risk.cf.<code>` | `custom.<code>` (cible *risk* / *cotation*) | libellé(s) |
| `risk.measures` | *(dérivé via liens)* | sous-collection (boucle imbriquée) |
| `risk.links` | *(dérivé)* | sous-collection |

> Synonymes acceptés : `risk.gross.*` = `risk.initial.*`, `risk.net.*` = `risk.residual.*`.

### 3.4 Objet **measure** (boucle `measures`, item `measure`)

`measure.id`, `measure.label`, `measure.type`, `measure.status`, `measure.responsible`,
`measure.due_date` (date), `measure.cost`, `measure.description`, `measure.comment`,
`measure.overdue` *(dérivé, booléen)*, `measure.cf.<code>`, sous-collections `measure.risks`
(risques couverts) et `measure.links`.

### 3.5 Objet **link** (boucle `links`, item `link`)

`link.comment`, `link.cf.<code>`, plus les **objets résolus** `link.risk.*` et `link.measure.*` (accès à
tous les champs du risque et de la mesure reliés), et `link.risk_id` / `link.measure_id` pour les seuls
identifiants.

### 3.6 Champs personnalisés — référentiel (boucle `custom_fields`, item `field`)

Décrit la **définition** des champs personnalisés (par opposition à `*.cf.<code>` qui lit une *valeur*).
Attribut optionnel `target` (`analysis` / `risk` / `measure` / `link` / `cotation`) pour restreindre à
une cible ; `glossary="true"` pour ne conserver que les champs à **valeurs décrites** (usage glossaire) ;
`sort`, `limit` acceptés. Une `target` inconnue est signalée et n'itère sur rien.

| Balise | Clé | Rendu |
|---|---|---|
| `field.code` | `code` | texte |
| `field.label` | `label` | libellé localisé |
| `field.target` | `target` | libellé de cible localisé |
| `field.type` | `type` | libellé de type localisé |
| `field.required` | `required` | booléen (Oui/Non) |
| `field.filterable` | `filterable` | booléen (Oui/Non) |
| `field.help` | `help` | texte enrichi |
| `field.description` | `description` | texte enrichi |
| `field.items` | `items` | sous-collection des valeurs possibles (types à valeurs fermées), item `option` |

Item `option` : `option.code`, `option.label`, `option.color`, `option.description`.

Tableau clé en main : `{{ table source="custom_fields" }}` (colonnes code, libellé, cible, type,
obligatoire, filtrable), avec `target="…"` optionnel. Tableau des valeurs d'un champ (Valeur /
Description, badge coloré pour les tags) : `{{ field_values }}` (§4.4).

---

## 4. Blocs générateurs (tableaux, matrices, radars)

Balises qui produisent autre chose que du texte — c'est là que se choisit le **format** (image via
`matrix`/`radar`, ou `table`). Toutes acceptent **`filter="…"`** (§8) et **`report_filter="none"`**.

### 4.1 Matrice — `{{ matrix … }}`
| Attribut | Valeurs | Défaut |
|---|---|---|
| `type` | `initial` (syn. `gross`), `residual` (syn. `net`), `trajectory` | `initial` |
| `filter` | expression de filtre (§8) | — |
| `title` | texte (sinon aucun) | — |
| `width` · `height` | dimensions en cm (§4.8) | ajustée à la page |

Ex. : `{{ matrix type="initial" }}` · `{{ matrix type="initial" filter="category='Illegitimate data access'" }}`

### 4.2 Radar — `{{ radar … }}`
Attributs : `dimension` (`category` ou `cf.<code>`), `metric` (`average`, `max`, `cumulative`,
`weighted`, `count`), `evaluation` (`initial`, `residual`, `side`, `overlay`), `filter`, `title`,
`width` · `height` (§4.8).

### 4.3 Tableau — `{{ table … }}`
| Attribut | Valeurs | Défaut |
|---|---|---|
| `source` | `risks`, `measures`, `links`, `levels`, `custom_fields` | requis |
| `columns` | liste de champs (ex. `id,label,category,criticality_initial,cf.source`) | **colonnes par défaut de l'application** pour ce registre |
| `filter` | expression (§8) | — |
| `sort` | `field[:asc\|desc]`, multi-clés séparées par des virgules (`field1,field2:desc`) | ordre du fichier |

> Colonnes : mêmes noms que les champs des objets (§3), plus les colonnes dérivées
> (`score_initial`, `criticality_initial`, `criticality_residual`, `evolution`, `measures`…) et
> `cf.<code>`. Si `columns` est omis, on reprend la **liste de colonnes par défaut de l'application**
> pour ce registre.

### 4.4 Valeurs d'un champ — `{{ field_values }}`

Dans une boucle `custom_fields` (§3.6) : produit un tableau **Valeur / Description** des valeurs du champ
courant, avec **badge coloré** pour le type `tags` (texte simple pour `select` / `checklist`) — aligné sur
la section « Référentiels et légendes des champs » du rapport intégré (`dxBadgeCell`, `cfItemDesc`). Rend
`null` (paragraphe retiré) hors d'une boucle `custom_fields`, pour un type sans valeurs fermées, ou si
aucune valeur n'a de description. Réservé au corps (comme les autres blocs).

### 4.5 Statistiques — `{{ stat type="…" }}`

Statistiques de l'analyse (données de l'onglet Statistiques et du rapport intégré), en **tableaux**,
**tuiles** et **graphiques**.

**Types sans graphique :**

| `type` | Rendu |
|---|---|
| `summary` (syn. `counts`) | tableau **synthèse** : Risques / Mesures / Risques réduits |
| `counters` | **tuiles clés** : Risques · Mesures · Risques réduits · % traité (`statCounters`) |
| `coverage` | **couverture** : risques sans mesure · mesures orphelines (via les liens) |

**Types à graphique** (répartition — tableau *Nombre / Part* via `dxBadgeCell`, graphique via
`tmplStatChartSVG`, légende) :

| `type` | Dimension | Population |
|---|---|---|
| `criticality` (syn. `distribution`) | criticité Initial vs Résiduel (deux graphiques, `critOfEval`) | risques |
| `category` | catégorie | risques |
| `measure_type` · `measure_status` | type · statut (`STATUS_COLORS`) | mesures |
| `risk_owner` · `measure_owner` | propriétaire · responsable | risques · mesures |
| `cf.<code>` | champ perso (`statDist`, couleurs de valeurs) | cible du champ |

Attributs des types à graphique : `display` (`table` · `chart` · `both`, défaut **`table`**), `shape`
(`donut` · `pie`, défaut **`donut`**), `width` · `height` (§4.8), `filter` (§8).

**Mise en page** (`chart`/`both`) — tableaux de mise en page **sans bordure**, centrés (`tmplTblCenter` /
`tmplTblCenterFit`), tout sur une même ligne : `chart` → `graphique │ légende` ; `both` (dimension) →
`tableau │ graphique │ légende` ; `criticality` `chart` → paire de graphiques puis **légende en ligne**
(`tmplStatLegendInlineXml`) ; `criticality` `both` → paire de graphiques puis tableau. Les tableaux de
données sont ajustés au contenu (autofit) et centrés.

Le graphique SVG est **autonome** (couleurs en ligne) puis rasterisé en PNG et inséré comme les
matrices/radars (via `tmplImgReqs`, §4.1/§13). Un `type` inconnu, ou un `cf.<code>` introuvable
(`tw_stat_field`), est signalé.

### 4.6 Notes des champs perso — `{{ cf_notes }}`

Dans une boucle `risks` / `measures` / `links` : reproduit `dxCfNotes` pour l'entité courante — un
paragraphe « **Libellé** : valeur » par champ personnalisé renseigné (cible correspondante). Utilisé dans
les sections « Détail ». Rend `null` hors d'une entité, ou si aucun champ n'est renseigné.

### 4.7 Logo de couverture — `{{ logo }}`

Insère le **logo configuré** de l'analyse (`extensions.display.report.cover.logo`), préchargé en PNG
(`dxLogoPng`). Attributs `width` · `height` optionnels (§4.8 ; défaut : largeur intrinsèque, max 200 px).
Rend `null` si aucun logo n'est configuré ou si le chargement échoue. Réservé au corps.

### 4.8 Dimensions des images — `width` / `height`

Sur tous les blocs produisant une image (`matrix`, `radar`, `logo`, `stat` en `display="chart|both"`),
via le helper commun `tmplImgXml` / `tmplImgEmu` (unité **cm**, EMU internes) :

| Réglage | Effet |
|---|---|
| `width` seul | largeur fixée, **hauteur calculée** (ratio conservé) |
| `height` seul | hauteur fixée, **largeur calculée** |
| `width` **et** `height` | **boîte maximale** : image agrandie au maximum **sans dépasser** l'une ni l'autre, ratio conservé (jamais déformée) |
| aucun | taille par défaut (largeur intrinsèque plafonnée) |

Fournir les deux valeurs **ne force donc pas** une déformation : elles définissent une boîte que l'image
remplit en conservant ses proportions (`cx=w·EMU_CM ; cy=cx·H/W`, puis contrainte par la hauteur si
dépassement).

---

## 5. Formats de valeur (modificateurs `|`)

`{{ path | format }}` — le texte est le rendu par défaut.

| Format | Effet |
|---|---|
| `date="ISO\|JJ/MM/AAAA\|MM/JJ/AAAA\|long"` | mise en forme d'une date (défaut = `report.date_format`, sinon réglage de l'app) |
| `labels` *(défaut cf)* | champ perso rendu par ses **libellés** (langue de l'analyse) |
| `codes` | champ perso rendu par ses **codes** |
| `join="; "` | séparateur pour un champ multi-valeurs |
| `percent` | ajoute « % » (barres de progression) |
| `upper` / `lower` | casse |
| `default="—"` | valeur de repli si vide |
| `swatch` | **couleur** (`*.color`, hex) → **pastille carrée** (`■`) ; **tags** / **étiquette colorée** (statut, criticité) → pastille + libellé |
| `badge` | **tags** / **étiquette colorée** (statut de mesure, criticité initiale/résiduelle) → libellé sur **fond coloré** (`w:shd`, texte contrasté via `badgeFg`) |

`swatch` / `badge` sont des **rendus enrichis** : la substitution reconstruit le run en une séquence de
runs colorés (couleur de texte `w:color` pour la pastille, fond `w:shd` pour le badge), en héritant du
`rPr` de base. Ils s'appliquent aux champs **tags**, au **statut** de mesure (`STATUS_COLORS`) et à la
**criticité** (`kind:"clabel"` — étiquette colorée). Le format par défaut d'un `*.color` reste le **code
hex**, celui d'un `tags`/statut/criticité, le **texte**. Une valeur multi-étiquettes produit une pastille
par valeur. Sur une valeur non pertinente, repli en texte simple.

Le rendu **image** (matrice, radar) passe par les **blocs** du §4, pas par un format de valeur.

---

## 6. Boucles et sections

```
{{#each risks filter="…" sort="criticality_initial:desc" limit=10}}
  {{ risk.id }} — {{ risk.label }} : {{ risk.initial.criticality }}
{{/each}}
```

Attributs de `{{#each <collection> …}}` : `filter` (§8), `sort` (`field[:asc|desc]`, **multi-clés**
séparées par des virgules : `sort="target,code"` — départage successif), `limit` (N premiers),
`group_by` (regroupement, ci-dessous), `report_filter="none"`.

- **Collections** : `risks`, `measures`, `links`, `grid.levels`, `custom_fields`,
  `grid.vertical_axis.levels`, `grid.horizontal_axis.levels`, et les **sous-collections**
  (`risk.measures`, `measure.risks`, `field.items`, `link.*`…). Imbrication libre.
- **Regroupement** `group_by="field"` → itère des **groupes** ; chaque groupe expose `group.key`
  (valeur brute), `group.label`, `group.count`, `group.measures_count` (groupes de risques), et
  `group.items` (sous-collection à parcourir). Champs risque : `category`, `owner`,
  `criticality_initial/residual`, `cf.<code>`, **`id`** (un chapitre par risque). Champs mesure :
  `type`, `status`, `responsible`, `cf.<code>`.
- **Portée implicite d'un groupe** : à l'intérieur d'un groupe (`group_by`), les collections, blocs
  (`matrix`, `radar`, `table`) et compteurs **imbriqués** sont **automatiquement restreints** aux éléments
  du groupe (filtre implicite = valeur du groupe, propagé le long des liens). C'est ce qui permet un
  **rapport éclaté** : un chapitre par catégorie, chacun avec **sa** matrice et **ses** tableaux filtrés
  sans répéter le critère. La valeur du groupe reste accessible via `group.key` / `group.label`.
- **Boucle de ligne de tableau** *(essentiel)* : si `{{#each …}}` et `{{/each}}` sont dans une **ligne
  de tableau Word**, c'est **la ligne** qui est répétée par élément (façon naturelle de construire un
  tableau mis en forme dans le modèle). Sinon, ce sont les **paragraphes** encadrés qui sont répétés.
- **Repli si vide** (boucle de paragraphes) : `{{#each … }} … {{else}} … {{/each}}` — les paragraphes
  après `{{else}}` sont rendus **une fois** quand la collection (après filtre/limite) est **vide**
  (`elseAt` dans `tmplRenderContainer`). Sinon, seul le corps avant `{{else}}` est répété par élément.

### 6.1 Conditions — `{{#if expr}}` · `{{#unless expr}}` · `{{else}}`

Rend une section **seulement si** une expression est vraie. Mêmes deux portées que les boucles :
**paragraphe** (`tmplParagraphSection`) et **ligne de tableau** (`tmplRowSection`) ; imbrication libre avec
les boucles et entre conditions.

```
{{#if measure.overdue}}⚠ En retard{{else}}À l'heure{{/if}}
{{#unless analysis.reduced_count}}Aucun risque réduit à ce stade.{{/unless}}
```

- **Expression** (`tmplParseCond` / `tmplEvalCond`) : `chemin operateur "valeur"`, où `chemin` est
  **n'importe quelle valeur** résoluble en `{{ … }}` (`analysis.*`, `risk.*`, `measure.*`, `link.*`,
  `level.*`, `grid.*`, compteurs, `cf.<code>`) — évaluée par `tmplResolveValue`, **pas** contre une entité.
- **Opérateurs** : `=`, `!=`, `>`, `>=`, `<`, `<=`, `contains`, `empty`, `not_empty` ; combinateurs `and`,
  `or`, parenthèses. Réutilise le **tokeniseur de filtres** (§8) : comparaison numérique quand c'est
  possible, sinon `localeCompare` numérique ; code **ou** libellé pour les `tags`/`checklist` ; insensible
  à la casse (`tmplNorm`).
- **Forme courte** : `{{#if chemin}}` seul ⇒ test **« non vide »** (`not_empty`). `{{#unless expr}}` =
  négation. `{{else}}` accepté dans les deux.
- **Bloc ou en ligne** : marqueurs **seuls** sur leur paragraphe/ligne ⇒ portée **bloc** (encadre des
  paragraphes ou des lignes). Ouverture **et** fermeture dans un **même paragraphe/cellule** ⇒ condition
  **en ligne**, résolue **à l'échelle du paragraphe** (`tmplResolveInlineCondsInEl`) donc **à travers
  plusieurs runs** (mises en forme différentes, passage à la ligne), en conservant la mise en forme de
  chaque run et en laissant les balises de valeur intactes. C'est le seul moyen d'agir dans une **cellule
  de boucle de ligne** (substituée par `tmplSubstituteRuns`, sans traitement de bloc). Ex. mention « En
  retard » (rouge) conditionnelle dans une colonne Statut. Un `else`/`/if` en ligne sans `if` correspondant
  ⇒ avertissement `tw_if_orphan` (marqueur retiré) ; un `if` non fermé dans le texte est laissé visible.
- **Robustesse** : expression invalide (`tw_if_invalid`), section non fermée (`tw_if_unclosed`), `{{else}}`
  orphelin (`tw_if_orphan`) ou chemin inconnu (`tw_if_field`) ⇒ **avertissement** ; la section est laissée
  telle quelle (rendu non bloquant).

---

## 7. Exemples

### 7.1 Les 8 besoins de départ

| Besoin | Balise |
|---|---|
| Titre de l'analyse | `{{ analysis.title }}` |
| Description de l'analyse | `{{ analysis.description }}` |
| Matrice des risques bruts | `{{ matrix type="initial" }}` |
| Matrice brute filtrée sur une catégorie X | `{{ matrix type="initial" filter="category='X'" }}` |
| Tableau des risques avec colonnes choisies | `{{ table source="risks" columns="id,label,category,criticality_initial,criticality_residual" }}` |
| Boucle sur toutes les mesures | `{{#each measures}} … {{/each}}` |
| Boucle sur tous les propriétaires des mesures | `{{#each measures group_by="responsible"}} … {{/each}}` |
| Risques dont le champ perso X vaut Y | `{{#each risks filter="cf.X='Y'"}} … {{/each}}` |

### 7.2 Filtre global du rapport (en tête de modèle)

```
{{ report filter="category='Illegitimate data access'" date_format="JJ/MM/AAAA" }}
```
→ toutes les matrices, tableaux et boucles du document portent sur ce sous-ensemble, sauf mention
`report_filter="none"`.

### 7.3 Page de garde (valeurs)

```
{{ analysis.title }}
{{ analysis.organization }} — {{ analysis.author }}
Périmètre : {{ analysis.scope }}
Version {{ analysis.revision }} · {{ analysis.status }} · {{ analysis.updated | date="long" }}
```

### 7.4 Tableau de risques — colonnes par défaut vs colonnes choisies

```
{{ table source="risks" }}
{{ table source="risks" columns="id,label,category,owner,criticality_initial,criticality_residual,evolution" }}
```

### 7.5 Boucle simple sur les mesures (paragraphes)

```
{{#each measures sort="due_date:asc"}}
  • {{ measure.label }} — {{ measure.status }} — échéance {{ measure.due_date | date="JJ/MM/AAAA" }}
    Responsable : {{ measure.responsible | default="—" }}
{{/each}}
```

### 7.6 Regroupement par propriétaire des mesures (boucle de groupes + boucle imbriquée)

```
{{#each measures group_by="responsible"}}
  {{ group.label }} ({{ group.count }})
  {{#each group.items}}
    - {{ measure.label }} — {{ measure.type }}
  {{/each}}
{{/each}}
```

### 7.7 Boucle imbriquée : chaque risque et ses mesures

```
{{#each risks sort="criticality_initial:desc"}}
  {{ risk.id }} · {{ risk.label }} — brut {{ risk.initial.criticality }} → résiduel {{ risk.residual.criticality }}
  Mesures :
  {{#each risk.measures}}
    - {{ measure.label }} ({{ measure.status }})
  {{/each}}
{{/each}}
```

### 7.8 Boucle filtrée (champ perso + criticité)

```
{{#each risks filter="cf.source contains 'internal' and criticality_initial>='high'"}}
  {{ risk.id }} — {{ risk.label }} : {{ risk.initial.criticality }}
{{/each}}
```

### 7.9 Boucle de **ligne de tableau** (le modèle contient un tableau Word)

Un tableau Word à deux lignes — une ligne d'en-tête, **une ligne de corps** contenant les balises ;
la ligne de corps est répétée par risque :

| ID | Risque | Catégorie | Criticité initiale | Criticité résiduelle |
|---|---|---|---|---|
| `{{#each risks}}{{ risk.id }}` | `{{ risk.label }}` | `{{ risk.category }}` | `{{ risk.initial.criticality }}` | `{{ risk.residual.criticality }}{{/each}}` |

### 7.10 Boucle sur les liens (objets résolus)

```
{{#each links}}
  {{ link.risk.label }} ⟵ {{ link.measure.label }}
  Justification : {{ link.comment }}
{{/each}}
```

### 7.11 Rapport éclaté par catégorie (portée implicite du groupe)

Un chapitre par catégorie ; à l'intérieur, matrice et tableau **auto-filtrés** sur la catégorie courante :

```
{{#each risks group_by="category"}}
  ## {{ group.label }} ({{ group.count }} risques)
  {{ matrix type="trajectory" }}
  {{ table source="risks" columns="id,label,criticality_initial,criticality_residual,evolution" }}
  Mesures associées :
  {{#each measures}}
    - {{ measure.label }} ({{ measure.status }})
  {{/each}}
{{/each}}
```

---

## 8. Filtres

`filter="<expression>"`, utilisable dans `{{ report … }}` (global) et sur chaque **boucle**, **matrice**,
**radar** et **tableau**. Grammaire :

- **Comparaison** : `field operator "value"`.
  Opérateurs : `=`, `!=`, `>`, `>=`, `<`, `<=`, `contains`, `empty`, `not_empty`.
- **Combinaison** : `and`, `or`, parenthèses. Ex. `category="X" and criticality_initial>="high"`.
- **Champs filtrables** : `category`, `owner`, `type`, `status`, `responsible`, `overdue`,
  `criticality_initial`, `criticality_residual`, `cf.<code>`.
- **Codes ou libellés** : la valeur est comparée au **code stocké** *ou* au **libellé affiché**
  (insensible à la casse). Ex. `status="in progress"` ≡ `status="in_progress"`.
- **Multi-valeurs** (tags, listes à cocher) : `cf.source contains "internal"`.
- **Criticité** : comparée par **ordre de niveau** (`criticality_residual<="limited"`).

**Portée / propagation** : un filtre appliqué au rapport (ou à une boucle/bloc) restreint l'ensemble
concerné ; comme dans l'application, un critère de **risque** restreint aussi les **mesures** et **liens**
associés, et réciproquement (filtrage *propagé* le long des liens). Le **filtre actif de l'interface
n'est jamais utilisé** : seul compte le filtre déclaré dans le modèle.

---

## 9. Rendu et styles

- **Valeurs inline** : héritent de la **mise en forme du modèle** à l'emplacement de la balise.
- **Texte enrichi** (`description`, `comment`) : Markdown → paragraphes Word (via `mdDocxBlocks`).
- **Images** (matrice, radar) : insérées à l'emplacement, largeur ajustée à la page (ou `width=`),
  rasterisées depuis le SVG (réutilise `addSvgImage`).
- **Tableaux** injectés : mise en forme **neutre** par défaut (v1) ; option `style="TableStyleName"` pour
  réutiliser un **style de tableau du modèle** ; la **boucle de ligne** (§6, §7.9) reprend directement la
  mise en forme de la ligne du modèle.

---

## 10. Notes d'implémentation

- **Normalisation des runs** : avant substitution, fusionner les runs adjacents de mise en forme
  identique et recoller les balises `{{ … }}` scindées par Word.
- **Boucles** : repérer les paires ouvrante/fermante ; pour chaque item, **cloner** le fragment XML
  intermédiaire en substituant les valeurs. Détecter le cas « boucle dans une ligne de tableau »
  (répéter le `<w:tr>`) vs « boucle sur paragraphes ».
- **Insertion d'images dans le modèle** : ajouter les parties `media/*.png` au zip, une **relation** dans
  `word/_rels/document.xml.rels` avec un **`rId` non colisionnant** (scanner l'existant), garantir le
  `Default Extension="png"` dans `[Content_Types].xml`, et un **`docPr id`** unique par image.
- **Filtre global** : `{{ report filter }}` est résolu une fois, puis **combiné (ET)** au filtre de chaque
  boucle/bloc, sauf `report_filter="none"`.
- **Échappement XML** des valeurs texte substituées.
- **En-têtes/pieds** : balises de **valeur** traitées ; pas de boucles/blocs.
- **Erreurs** : balise inconnue / attribut invalide → laissée en place + **rapport d'avertissements**.

---

## 11. Interface

- **Fichier › Exporter avec un modèle Word…** → sélecteur `.docx`/`.dotx` → génération → téléchargement
  `<nom-analyse>-rapport.docx`.
- **Modèle d'exemple** téléchargeable + **catalogue des mots-clés** (aide in-app) pour démarrer.
- (Hors v1) mémoriser le dernier modèle utilisé.

---

## 12. Décisions

**Arrêtées :** (1) vocabulaire **anglais** ; (2) **blocs nommés** ; (3) `table` sans `columns` →
**colonnes par défaut de l'application** ; (4) **pas** de reprise du filtre actif de l'app — filtre défini
par `{{ report filter="…" }}`, combiné (ET) aux filtres locaux ; (5) **v1** = valeurs + boucles
(`filter`, `sort`, `group_by`, imbrication, **ligne de tableau**) + blocs **matrix**, **radar**, **table** ;
**v2** = **statistiques** (compteurs, couverture, graphiques donut/secteur — §4.5), **conditions**
`{{#if}}` / `{{#unless}}` (§6.1) et **dimensions d'images** `width` / `height` (§4.8) — **livrée**.

**Arrêtées (complément) :** **propagation des filtres le long des liens confirmée** (alignée sur l'app) ;
**échappement** des caractères spéciaux à l'intérieur des balises spécifié (§2.2).

**Arrêtée :** l'option `style="TableStyleName"` est **conservée** — un tableau auto-généré (`{{ table }}`)
peut reprendre un **style de tableau nommé du modèle** (`<w:tblStyle>`). Les tableaux entièrement à la
charte restent aussi réalisables via la **boucle de ligne de tableau** (§7.9).

---

## 13. Périmètre v2 (livré) et hors périmètre

**v2 — Statistiques** (§4.5) : compteurs (`analysis.risks_count` / `measures_count` / `links_count` /
`reduced_count`, plus le bloc `{{ stat type="counters" }}` : Risques · Mesures · Réduits · % traité) ;
couverture (`{{ stat type="coverage" }}`) ; **graphiques de répartition** `{{ stat type="criticality |
category | measure_type | measure_status | risk_owner | measure_owner | cf.<code>" display="table|chart|both"
shape="donut|pie" }}` (anneau/secteur autonome rasterisé en image, tableau *Nombre / Part*, légende).

**v2 — Conditions** (§6.1) : `{{#if expr}} … {{else}} … {{/if}}` et `{{#unless expr}}`, à la portée
paragraphe et ligne de tableau.

**v2 — Dimensions d'images** (§4.8) : `width` / `height` (cm) sur `matrix`, `radar`, `logo`, `stat` ; les
deux ensemble = boîte maximale sans déformation.

**Hors périmètre** : graphiques Word **natifs éditables** (on insère des **images**) ; styles/thème
imposés par l'application (c'est le **modèle** qui décide) ; édition du modèle dans l'app.
