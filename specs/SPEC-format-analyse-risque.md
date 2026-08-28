# Spécification du format de fichier — Risk Analysis Editor (.rae.json)

**Nom du format :** Risk Analysis Editor (RAE)
**Identifiant format :** `risk-analysis-editor`
**Version de la spécification :** 1.0
**Date :** 2026-08-19
**Extension recommandée :** `.rae.json` (ou `.json`)
**Type MIME :** `application/vnd.rae+json`
**Encodage :** UTF-8, sans BOM

---

## 1. Objet et périmètre

Ce document spécifie un format de fichier destiné à contenir une **analyse de risque complète** et autoportante, exploitable par un outil de visualisation de matrices de risque (matrice de risque initial et matrice de risque résiduel).

Un fichier conforme contient :

- les **paramètres de la grille** (axes, niveaux, méthode de calcul du score, zones de criticité) ;
- la **liste des risques** avec leur évaluation initiale (brute) et résiduelle (nette) ;
- la **liste des mesures** de maîtrise ;
- les **liens** entre risques et mesures (traitements) ;
- des **champs personnalisés** et des **objets** définis par l'utilisateur (référentiels réutilisables et références entre entités) ;
- des **métadonnées** de gestion documentaire.

Le format est indépendant de toute méthodologie particulière (ISO 27005, EBIOS RM, COSO, référentiel interne…) : la grille est entièrement paramétrable.

### 1.1 Objectifs de conception

| Objectif | Traduction dans le format |
|---|---|
| Autoportant | Un seul fichier suffit à reconstituer les deux matrices, sans ressource externe. |
| Lisible et éditable | JSON, clés en anglais (snake_case), valeurs libres dans la langue de l'analyse, structure plate. |
| Paramétrable | La grille (taille, libellés, seuils, couleurs) est décrite dans le fichier, pas codée en dur dans l'outil. |
| Traçable | Séparation claire entre évaluation initiale et résiduelle, liens risque↔mesure explicites. |
| Extensible | Champs optionnels et espace d'extension réservé, sans casser la compatibilité. |

---

## 2. Conventions

- Le fichier est un **document JSON** unique (RFC 8259).
- Toutes les chaînes sont en **UTF-8**.
- Les **dates** sont au format `AAAA-MM-JJ` (ISO 8601, date seule).
- Les **couleurs** sont des chaînes hexadécimales `#RRGGBB`.
- Les **identifiants** (`id`) sont des chaînes non vides, uniques dans leur collection, stables dans le temps (voir §7).
- Dans les tableaux de champs ci-dessous : **O** = obligatoire, **F** = facultatif.
- Les clés inconnues d'un lecteur doivent être **ignorées silencieusement** (tolérance ascendante), jamais rejetées.
- Les **champs de texte libre multi-lignes** (`description` et `comment` des risques, mesures et liens, `metadata.description`, valeurs des champs personnalisés de type `textarea`) peuvent contenir du **Markdown** (sous-ensemble étendu : titres, gras/italique/barré, code, liens, listes, cases à cocher, citations, tableaux). Le stockage reste du **texte brut** : la mise en forme est appliquée à l'affichage. Un lecteur qui ne gère pas le Markdown peut afficher le texte tel quel sans perte de sens. Le **HTML brut n'est pas interprété** (il doit être échappé à l'affichage).

---

## 3. Vue d'ensemble de la structure

```
{
  "format": "risk-analysis-editor",
  "version": "1.0",
  "metadata":  { … },        // §4.1  informations documentaires
  "grid":    { … },        // §4.2  paramètres de la matrice
  "risks":   [ … ],        // §4.3  risques + évaluations initiale/résiduelle
  "measures":   [ … ],        // §4.4  mesures de maîtrise
  "treatments": [ … ],      // §4.5  liens risque ↔ mesure
  "custom_fields": [ … ],    // §4.6  définitions de champs personnalisés
  "custom":  { … },        // §4.6  valeurs des champs personnalisés de l'analyse
  "object_types": [ … ],    // §4.7  définitions des types d'objets
  "objects":  [ … ],        // §4.7  instances d'objet
  "extensions": { … }        // §6    données propriétaires (facultatif)
}
```

### 3.1 Champs racine

| Champ | Type | O/F | Description |
|---|---|---|---|
| `format` | chaîne | O | Constante `"risk-analysis-editor"`. Sert à identifier le type de fichier. |
| `version` | chaîne | O | Version de la spécification suivie, ex. `"1.0"` (voir §7). |
| `metadata` | objet | F | Métadonnées documentaires (§4.1). |
| `grid` | objet | O | Définition de la grille de cotation (§4.2). |
| `risks` | tableau | O | Liste des risques (§4.3). Peut être vide. |
| `measures` | tableau | F | Liste des mesures (§4.4). Absent ou vide = aucune mesure. |
| `treatments` | tableau | F | Liens risque↔mesure (§4.5). Absent ou vide = aucun lien. |
| `custom_fields` | tableau | F | Définitions de champs personnalisés (§4.6). |
| `custom` | objet | F | Valeurs des champs personnalisés **de l'analyse** (§4.6). |
| `object_types` | tableau | F | Définitions des **types d'objets** (§4.7). Absent ou vide = aucun objet. |
| `objects` | tableau | F | **Instances d'objet** (§4.7). Absent ou vide = aucune instance. |
| `extensions` | objet | F | Espace d'extension libre (§6). |

---

## 4. Description détaillée des objets

### 4.1 `metadata` — métadonnées documentaires

| Champ | Type | O/F | Description |
|---|---|---|---|
| `title` | chaîne | F | Titre de l'analyse. |
| `description` | chaîne | F | Description libre du périmètre analysé. |
| `author` | chaîne | F | Auteur / responsable de l'analyse. |
| `organization` | chaîne | F | Entité concernée. |
| `scope` | chaîne | F | Périmètre (projet, système, processus…). |
| `methodology_reference` | chaîne | F | Référentiel employé, ex. `"ISO 27005:2022"`, `"EBIOS RM"`, `"interne"`. |
| `created_at` | date | F | Date de création du document. |
| `updated_at` | date | F | Date de dernière modification. |
| `revision` | chaîne | F | Numéro/étiquette de révision du document (distinct de `version` du format). |
| `status` | chaîne | F | Ex. `"draft"`, `"approved"`, `"archived"`. |
| `language` | chaîne | F | Langue de l'interface associée à l'analyse, code ISO 639-1 (`"fr"`, `"en"`, `"it"`). À l'ouverture, l'application adopte cette langue (sauf paramètre d'URL `?lang`) ; en son absence, la langue du navigateur est utilisée, avec repli sur l'anglais. |
| `kind` | chaîne | F | Vaut `"template"` pour un **modèle méthodologique** — un squelette vierge (grille, niveaux de criticité et champs personnalisés préconfigurés, sans risque ni mesure). L'application ouvre alors le fichier comme une **nouvelle analyse non reliée** et retire ce marqueur avant tout enregistrement, de sorte que l'analyse de l'utilisateur n'est pas elle-même un modèle. Comme les libellés de grille, de criticité et les métadonnées sont des chaînes uniques (non commutables par langue), les modèles sont fournis **un fichier par langue** : convention `xxx.template.<lang>.rae.json` (`fr`, `en`, `it`) ; les définitions de champs personnalisés restent, elles, pleinement multilingues. |

### 4.2 `grid` — paramètres de la matrice

La grille décrit **les deux axes**, la **méthode de calcul du score** et les **niveaux de criticité** (zones colorées).

| Champ | Type | O/F | Description |
|---|---|---|---|
| `vertical_axis` | objet `Axe` | O | Axe affiché **verticalement** (par convention : vraisemblance / probabilité), §4.2.1. |
| `horizontal_axis` | objet `Axe` | O | Axe affiché **horizontalement** (par convention : gravité / impact), §4.2.1. |
| `score` | objet `Score` | O | Méthode de combinaison des deux axes (§4.2.2). |
| `criticality_levels` | tableau `NiveauCriticite` | O | Zones de criticité et leur couleur (§4.2.3). |

> **Taille de la matrice.** Elle n'est pas donnée par un champ dédié : elle est déduite du **nombre de niveaux** de chaque axe. Une grille 5×5 a 5 niveaux sur chaque axe ; une grille 4×3 a 4 niveaux sur l'axe vertical et 3 sur l'axe horizontal. Les axes peuvent avoir des tailles différentes.

#### 4.2.1 Objet `Axe`

| Champ | Type | O/F | Description |
|---|---|---|---|
| `label` | chaîne | O | Nom affiché de l'axe, ex. `"Probabilité"`, `"Gravité"`. |
| `levels` | tableau `NiveauAxe` | O | Échelons de l'axe, **ordonnés du plus faible au plus fort**. Au moins 2. |

Objet `NiveauAxe` :

| Champ | Type | O/F | Description |
|---|---|---|---|
| `value` | entier | O | Valeur numérique de l'échelon (typiquement 1..N, croissante et sans trou). Sert au calcul du score et au positionnement. |
| `label` | chaîne | O | Libellé affiché, ex. `"Très faible"`, `"Critique"`. |
| `description` | chaîne | F | Définition détaillée du critère (aide à la cotation). |

**Règles :** les `value` d'un axe sont **uniques**, **strictement croissantes** dans l'ordre du tableau, et de préférence contiguës à partir de 1.

#### 4.2.2 Objet `Score`

Définit comment on combine (probabilité, gravité) en un **score de criticité**.

| Champ | Type | O/F | Description |
|---|---|---|---|
| `method` | chaîne | O | `"product"` (P×G), `"sum"` (P+G) ou `"matrix"` (valeur définie case par case). |
| `matrix` | tableau 2D d'entiers | Cond. | **Obligatoire si** `method = "matrix"`. Score de chaque cellule (voir ci-dessous). Ignoré sinon. |

Convention pour `matrix` : `matrix[i][j]` est le score de la cellule où la **probabilité** vaut le `i`-ème niveau (index 0 = niveau le plus faible) et la **gravité** vaut le `j`-ème niveau. Les dimensions doivent correspondre au nombre de niveaux des deux axes.

> Avec `"product"` ou `"sum"`, le score est calculé à partir des `value` des niveaux — aucune matrice n'est nécessaire. Le mode `"matrix"` permet de coller à un référentiel où l'acceptabilité n'est pas une simple fonction de P×G.

#### 4.2.3 Objet `NiveauCriticite`

Chaque niveau de criticité définit une **plage de score** et son rendu visuel. Les plages doivent **couvrir sans se chevaucher** l'ensemble des scores possibles.

| Champ | Type | O/F | Description |
|---|---|---|---|
| `code` | chaîne | O | Identifiant court, ex. `"faible"`, `"critique"`. Unique. |
| `label` | chaîne | O | Libellé affiché, ex. `"Élevé (à traiter)"`. |
| `score_min` | entier | O | Borne **inférieure incluse** de la plage de score. |
| `score_max` | entier | O | Borne **supérieure incluse** de la plage de score. |
| `color` | chaîne | O | Couleur de la zone, `#RRGGBB`. |
| `acceptance` | chaîne | F | Décision associée : `"acceptable"`, `"tolerable"`, `"to_treat"`, `"unacceptable"`. |
| `order` | entier | F | Ordre d'affichage / gravité relative (1 = le moins grave). |

### 4.3 `risks` — liste des risques

| Champ | Type | O/F | Description |
|---|---|---|---|
| `id` | chaîne | O | Identifiant unique du risque, ex. `"R1"`. Stable. |
| `label` | chaîne | O | Intitulé court du risque. |
| `description` | chaîne | F | Description détaillée (scénario, cause, conséquence). |
| `category` | chaîne | F | Famille, ex. `"Cybersécurité"`, `"RH"`. |
| `owner` | chaîne | F | Responsable du risque (risk owner). |
| `initial_assessment` | objet `Cotation` | O | Cotation **brute**, avant mesures (§4.3.1). |
| `residual_assessment` | objet `Cotation` | F | Cotation **nette**, après application des mesures (§4.3.1). **Si absente**, le risque est considéré non traité et le résiduel est égal à l'initial. |
| `comment` | chaîne | F | Note libre. |

#### 4.3.1 Objet `Cotation`

| Champ | Type | O/F | Description |
|---|---|---|---|
| `probability` | entier | O | Valeur sur l'axe vertical ; doit correspondre à une `value` de `vertical_axis.levels`. |
| `severity` | entier | O | Valeur sur l'axe horizontal ; doit correspondre à une `value` de `horizontal_axis.levels`. |
| `custom` | objet | F | Valeurs des champs personnalisés de cible `"cotation"` (§4.6) — propres à cette cotation (initiale ou résiduelle). |

> **Le score et le niveau de criticité ne sont pas stockés dans la cotation** : ce sont des **valeurs dérivées**, recalculées par l'outil à partir de (`probability`, `severity`) et de `grid`. Cela évite toute incohérence entre valeurs saisies et valeurs affichées. (Un outil peut néanmoins les mettre en cache dans `extensions`.)

### 4.4 `measures` — liste des mesures de maîtrise

| Champ | Type | O/F | Description |
|---|---|---|---|
| `id` | chaîne | O | Identifiant unique de la mesure, ex. `"M1"`. Stable. |
| `label` | chaîne | O | Intitulé de la mesure. |
| `description` | chaîne | F | Description détaillée. |
| `type` | chaîne | F | Nature : `"preventive"`, `"detective"`, `"corrective"`, `"dissuasive"`, `"organizational"`, `"technical"`… (libre). |
| `status` | chaîne | F | `"proposed"`, `"planned"`, `"in_progress"`, `"implemented"`, `"abandoned"`. |
| `responsible` | chaîne | F | Pilote de la mesure. |
| `due_date` | date | F | Date cible de mise en œuvre. |
| `cost` | chaîne \| nombre | F | Coût estimé (libre ou montant). |
| `comment` | chaîne | F | Note libre. |

### 4.5 `treatments` — liens risque ↔ mesure

Un `traitement` associe **une mesure à un risque**. La relation est **plusieurs-à-plusieurs** : une mesure peut couvrir plusieurs risques, un risque peut être couvert par plusieurs mesures. Cette collection est **la source de vérité** des liens.

| Champ | Type | O/F | Description |
|---|---|---|---|
| `risk` | chaîne | O | `id` d'un risque existant. |
| `measure` | chaîne | O | `id` d'une mesure existante. |
| `comment` | chaîne | F | Note libre. |
| `custom` | objet | F | Valeurs des champs personnalisés de cible `"link"` (§4.6). |

> **Autorité de la valeur résiduelle.** La position résiduelle affichée est **`risk.residual_assessment`**, saisie globalement par l'analyste. Les `treatments` ne portent que le **lien** risque↔mesure : ils indiquent *quelles* mesures couvrent un risque, pas de combien chacune le réduit. La quantification de la réduction relève entièrement de la cotation résiduelle du risque.

### 4.6 `custom_fields` et `custom` — champs personnalisés

Le format permet de **définir des champs supplémentaires** rattachés à l'analyse, aux risques, aux mesures ou aux liens, sans modifier le schéma de base. Les **définitions** sont regroupées à la racine dans `custom_fields` ; les **valeurs** sont portées par un objet `custom` sur l'objet concerné (racine pour l'analyse, chaque `risk`, chaque `measure`, chaque `treatment`).

> **Codes libres, libellés multilingues.** Comme le reste du format, les clés structurelles de `custom_fields` et `custom` sont en anglais. Les `code` (de champ et d'item) sont des chaînes **libres** définies par l'utilisateur (identifiants stables, communs à toutes les langues) ; les libellés destinés à l'affichage sont **multilingues** (voir `label`).

#### 4.6.1 Définition d'un champ (`custom_fields[]`)

| Champ | Type | O/F | Description |
|---|---|---|---|
| `code` | chaîne | O | Identifiant du champ, **unique**, stable. Sert de clé dans les objets `custom` et d'en-tête de colonne à l'export CSV. |
| `target` | chaîne | O | Objet rattaché : `"analysis"`, `"risk"`, `"cotation"` (évaluation initiale/résiduelle d'un risque), `"measure"` ou `"link"` (lien risque↔mesure, cf. `treatments`). |
| `label` | objet | O | Libellé affiché, par langue : `{ "fr": "…", "en": "…" }`. À l'affichage : langue courante, repli sur `fr` puis sur `code`. |
| `type` | chaîne | O | `"boolean"`, `"integer"`, `"float"`, `"date"`, `"text"` (une ligne), `"textarea"` (multi-lignes), `"url"` (lien web `http(s)://`), `"email"` (adresse électronique), `"tel"` (numéro de téléphone, format international permissif), `"regexp"` (texte contrôlé par le motif `pattern`), `"color"` (couleur, stockée en hex `#RRGGBB` ; affichage réglé par `color_mode` : `both` pastille + hex (défaut), `swatch` pastille seule, `hex` valeur), `"image"` (image embarquée en *data-URI*, affichée en vignette ; les matricielles trop grandes sont réduites), `"select"` (liste, choix unique), `"checklist"` (liste, choix multiple), `"tags"` (étiquettes colorées, choix unique ou multiple), `"scale"` (échelle : niveaux à valeur numérique, §4.6.5), `"progress"` (barre de progression 0–100 %), `"reference"` (référence vers une ou plusieurs instances d'objet, §4.7), `"computed"` (valeur calculée par une expression, §4.6.6). |
| `object_type` | chaîne | Cond. | **Obligatoire** pour le type `reference` : cible de la référence. Soit le `code` d'un **type d'objet** (`object_types[].code`, §4.7) — la valeur stockée est alors l'`id` d'une instance ; soit une **entité de l'analyse** via une valeur sentinelle : `"@risks"` (les risques) ou `"@measures"` (les mesures) — la valeur stockée est alors l'`id` d'un risque (`risks[].id`) ou d'une mesure (`measures[].id`). Tableau d'`id` si `multiple`. |
| `required` | booléen | F | Si `true`, une valeur est obligatoire (bloquant à la saisie). |
| `filterable` | booléen | F | Si `true`, le champ alimente une liste de filtrage dans les vues qui affichent l'objet ciblé. **Réservé aux types à valeurs fermées** (`select`, `checklist`, `tags`, `boolean`, `reference`) **et aux cibles `risk`, `measure`, `link`** ; ignoré ailleurs. Cf. § *Filtrage par champ personnalisé*. |
| `pattern` | chaîne | F | Type `regexp` uniquement : expression régulière (syntaxe JavaScript) que la valeur doit respecter **en totalité** (ancrage implicite). Motif absent ou non compilable : aucun contrôle de format. |
| `color_mode` | chaîne | F | Type `color` uniquement : mode d'affichage. `"both"` (pastille carrée + valeur hexa, **défaut**), `"swatch"` (pastille seule) ou `"hex"` (valeur hexadécimale). |
| `multiple` | booléen | F | Type `tags` ou `reference` : autorise la sélection de plusieurs valeurs (sinon une seule). |
| `palette` | chaîne | F | Type `progress` uniquement : palette de la barre. Couleur **interpolée en TSL** entre des jalons équirépartis de 0 à 100 %. Valeurs : `"accent"` (couleur unique du thème, défaut), `"red-green"`, `"red-orange-green"`, `"red-orange-yellow-green"`, `"white-black"`, `"custom"` (couleurs dans `colors`). |
| `colors` | tableau | Cond. | Type `progress`, palette `"custom"` : jalons de couleur hex `#RRGGBB`, du premier (0 %) au dernier (100 %). Au moins un élément. |
| `step` | entier | F | Type `progress` uniquement : pas du curseur (1–100). Défaut `10`. |
| `min`, `max` | nombre / chaîne | F | Bornes : valeurs pour `integer`/`float` ; dates `AAAA-MM-JJ` pour `date` ; **longueur en caractères** pour `text`/`textarea`. |
| `min_items`, `max_items` | entier | F | Nombre minimal / maximal d'items cochés pour `checklist`. |
| `items` | tableau | Cond. | **Obligatoire** pour `select`, `checklist` et `tags`. Éléments de la liste (§4.6.2). |
| `help` | objet | F | Texte d'aide **court** multilingue, affiché en **infobulle** sur le libellé. Même forme que `label`. |
| `description` | objet | F | Texte **long** multilingue décrivant le champ, affiché **sous le contrôle de saisie**. Même forme que `label`. Distinct de `help`. |
| `order` | entier | F | Ordre d'affichage parmi les champs d'une même cible. |

Objet `items[]` (§4.6.2) :

| Champ | Type | O/F | Description |
|---|---|---|---|
| `code` | chaîne | Cond. | Identifiant de l'item, **unique** dans le champ (types `select` / `checklist` / `tags`). C'est cette valeur qui est stockée. **Absent pour le type `scale`** (l'identité est alors `value`). |
| `value` | nombre | Cond. | **Type `scale` uniquement** : valeur numérique du niveau — **identité** (unique dans le champ), stockée dans `custom`, exploitable en calculs/statistiques/radar. Voir §4.6.5. |
| `label` | objet | O | Libellé multilingue de l'item, même forme que `label` du champ. |
| `description` | objet | F | Définition multilingue de la valeur (même forme que `label`). Reprise dans la section **« Référentiels et légendes des champs »** du rapport (un tableau valeur → description par champ à valeurs fermées portant au moins une description). |
| `color` | chaîne | F | Types `tags` et `scale` : couleur de l'étiquette, hexadécimal `#RRGGBB`. |

#### 4.6.3 Valeurs (`custom`)

Chaque objet `custom` associe un `code` de champ à sa valeur, selon le type :

| Type | Valeur stockée |
|---|---|
| `boolean` | `true` / `false` |
| `integer`, `float` | nombre |
| `date` | chaîne `AAAA-MM-JJ` |
| `text`, `textarea` | chaîne |
| `url`, `email`, `tel`, `regexp` | chaîne |
| `color` | chaîne hexadécimale `#RRGGBB` |
| `image` | chaîne *data-URI* (`data:image/…;base64,…`) — image embarquée dans l'analyse |
| `select` | `code` de l'item choisi |
| `checklist` | tableau de `code` d'items |
| `tags` | tableau de `code` d'items (même en sélection unique : un seul élément) |
| `scale` | **nombre** — la `value` du niveau choisi (§4.6.5) |
| `progress` | nombre entier `0`–`100` (pourcentage) |
| `reference` | `id` d'une instance d'objet (`multiple` faux) ou tableau d'`id` d'instances (`multiple` vrai) |
| `computed` | **rien** — champ dérivé, non stocké dans `custom` (§4.6.6) |

Exemple :

```json
{
  "custom_fields": [
    { "code": "threat_source", "target": "risk", "type": "select", "required": true,
      "label": { "fr": "Source de menace", "en": "Threat source" },
      "items": [
        { "code": "internal", "label": { "fr": "Interne", "en": "Internal" } },
        { "code": "external", "label": { "fr": "Externe", "en": "External" } }
      ] }
  ],
  "risks": [
    { "id": "R1", "label": "…", "initial_assessment": { "probability": 5, "severity": 5 },
      "custom": { "threat_source": "external" } }
  ]
}
```

Un champ dont la définition a été supprimée peut laisser des valeurs orphelines dans `custom` : un lecteur les ignore.

#### 4.6.5 Type `scale` (échelle)

Une **échelle** est une liste de niveaux, chacun décrit par une **valeur numérique** (`items[].value`), un
`label` et une `color` optionnelle. Contrairement à `select`/`tags`, l'item n'a **pas** de `code` : sa
**`value` tient lieu d'identité** (donc **unique** dans le champ). C'est cette **valeur numérique** qui est
**stockée** dans `custom` (un nombre), ce qui la rend **auto-descriptive** (interprétable sans la
définition) et directement exploitable dans des **calculs**, **statistiques** et **radars**. Une valeur
orpheline (niveau retiré du barème) reste affichée comme le **nombre brut**. Le rendu est une **pastille
colorée** (couleur du niveau). Voir la spécification dédiée [`SPEC-champs-calcules.md`](SPEC-champs-calcules.md).

```json
{ "code": "gravite", "target": "risk", "type": "scale",
  "label": { "fr": "Gravité" },
  "items": [
    { "value": 1, "label": { "fr": "Faible" }, "color": "#2e9e5b" },
    { "value": 2, "label": { "fr": "Moyen" }, "color": "#e0b93a" },
    { "value": 3, "label": { "fr": "Élevé" }, "color": "#c0505a" }
  ] }
// custom : { "gravite": 2 }   ← le nombre, pas un code
```

---

#### 4.6.6 Type `computed` (valeur calculée)

Un champ **calculé** porte une **`expression`** (chaîne, obligatoire) — un langage **inspiré d'Excel** — et
un **`result_type`** (`number` / `integer` / `date` / `text` / `boolean`, défaut `number`). Il est
**dérivé** : sa valeur n'est **pas** écrite dans `custom` (ni dans `values` pour un attribut d'objet), elle
est **recalculée** partout — affichage, tri, filtre, statistiques et **exports** (registre, rapport, CSV,
**modèle Word**) — jamais lue depuis une valeur stockée. Options : `decimals` (résultat numérique), `unit`
(suffixe), `alert` (`{ min?, max?, color? }` — met la valeur en évidence hors plage ; en modèle Word,
pastille de la couleur d'alerte avec `| badge`). Non saisissable (exclu des formulaires et de l'import CSV).

L'expression réfère aux champs de la **même entité** (`cf.<code>`) et à des grandeurs **dérivées**
(`score_initial`, `score_residual`, `criticality_initial`/`residual` pour un risque ; `due_date`, `cost`,
`status`, `overdue` pour une mesure), et à `TODAY()`. Aucun `eval` : moteur d'expression maison. La
spécification complète (grammaire, fonctions, portée) est dans
[`SPEC-champs-calcules.md`](SPEC-champs-calcules.md). Un **cache** informatif des valeurs peut être écrit dans
`extensions.display.computed` (jamais faisant foi, recalculé à l'ouverture).

#### 4.6.4 Filtrage par champ personnalisé

Un champ portant `"filterable": true` alimente une **liste de filtrage** dans les vues qui affichent l'objet ciblé :

| `target` | Vues concernées |
|---|---|
| `risk` | Risques, Matrices, Liens |
| `measure` | Mesures, Plan d'action, Liens |
| `link` | Liens |

L'option n'a de sens que si deux conditions sont réunies, et elle est ignorée sinon :

- le **type** est à valeurs énumérables — `select`, `checklist`, `tags`, `boolean`, `reference` (choix = instances du type ciblé) — seul cas où une liste de choix peut être construite ;
- la **cible** est `risk`, `measure` ou `link`. Un champ rattaché à l'**analyse** (`"target": "analysis"`) ou à une **cotation** (`"target": "cotation"`) ne peut pas être filtrable.

Un fichier portant `"filterable": true` hors de ces conditions reste valide : la propriété est simplement sans effet.

**Un état commun à toutes les vues.** Une valeur retenue s'applique partout où l'objet apparaît : filtrer les risques sur un champ restreint simultanément le registre, les matrices, les statistiques et les liens. Comme les critères se propagent (voir ci-dessous), **chaque barre de filtres propose l'ensemble des champs filtrables** — risque, mesure et lien confondus —, quel que soit l'onglet : un filtre de mesure a un effet sur l'onglet Risques, il doit donc pouvoir y être posé.

**Conjonction et propagation le long des liens.** Tous les critères actifs valent **simultanément** (ET), et chacun se **propage** aux entités liées :

- un filtre de **risque** retient les risques correspondants, les liens qui en partent, et les seules mesures qui traitent ces risques ;
- un filtre de **mesure** retient les mesures correspondantes, les liens qui y aboutissent, et les seuls risques traités par ces mesures ;
- un filtre de **lien** retient les liens correspondants, et les seules extrémités (risques et mesures) de ces liens.

La propagation n'a lieu que dans le sens où elle en a un : sans filtre de mesure ni de lien, un risque dépourvu de lien reste affiché — aucun critère ne l'écarte. Dès qu'un filtre de mesure ou de lien est actif, ce même risque disparaît, faute de lien retenu pour le rattacher.

Le bouton **Réinitialiser** efface **tous les filtres propagés** (catégorie, type, statut et champs personnalisés), quelle que soit la barre d'où il est actionné : un filtre d'une autre famille continuerait sinon, par propagation, de masquer des fiches dans la vue courante.

**Règles de correspondance.** Pour `select`, la valeur de la fiche doit être égale au code retenu ; pour `checklist` et `tags`, elle doit figurer parmi les valeurs de la fiche ; pour `boolean`, « Non » retient également les fiches où la case n'a jamais été cochée.

**Filtre enregistré dans le fichier.** Le filtrage propagé (catégorie, type, statut **et** champs personnalisés) est enregistré avec l'analyse, sous `extensions.display.filters` (§6), et **réappliqué à la réouverture**. Modifier un filtre marque le fichier comme *à enregistrer*. Les valeurs périmées (catégorie/type/statut disparu, champ dévalidé ou renommé) sont **ignorées en silence**.

**Paramètre d'adresse `?filter=`.** Au démarrage, le paramètre d'URL `?filter=code:valeur;code:valeur` (champs personnalisés uniquement) applique un filtrage — par exemple `?filter=evenement_redoute:acces;supports:messagerie`. Un couple par champ, séparés par des points-virgules ; codes et valeurs peuvent être encodés (`encodeURIComponent`) ; codes inconnus et valeurs hors liste **ignorés en silence**. S'il est présent, il **écrase la partie « champs personnalisés »** du filtre enregistré, puis il est retiré de la barre d'adresse. L'application ne propage **plus** le filtrage dans l'URL : les fichiers `.rae.json` étant locaux, une URL ne suffit pas à rouvrir la vue.

Le placement manuel des pastilles et l'évitement des collisions dans les matrices continuent de raisonner sur **tous** les risques : masquer une pastille ne déplace pas les autres.

---

### 4.7 `object_types` et `objects` — objets et références

Là où un champ personnalisé ajoute une **valeur** à une entité, un **objet** décrit une **entité à part entière**, réutilisable et partagée par toute l'analyse (valeur métier, bien support, partie prenante, source de risque, finalité de traitement, donnée personnelle…). Le mécanisme est **agnostique** : c'est l'utilisateur qui définit les types, leurs attributs et les liens entre eux.

- Les **types** sont définis à la racine dans `object_types` (schéma d'attributs).
- Les **instances** sont regroupées à la racine dans `objects` ; chacune référence son type et porte ses valeurs.
- Une **référence** est un champ (personnalisé ou attribut d'objet) de type `reference` qui pointe vers une ou plusieurs instances par leur `id`.

> **Codes libres, libellés multilingues** — comme pour les champs personnalisés (§4.6) : les `code` (de type, d'attribut, d'item) sont des chaînes libres et stables ; les `label` sont multilingues.

#### 4.7.1 Définition d'un type (`object_types[]`)

| Champ | Type | O/F | Description |
|---|---|---|---|
| `code` | chaîne | O | Identifiant du type, **unique**, stable. Référencé par `objects[].type` et par l'attribut `object_type` des champs/attributs `reference`. |
| `label` | objet | O | Libellé multilingue du type (même forme que `label` d'un champ, §4.6). |
| `id_prefix` | chaîne | O | Préfixe des identifiants d'instance, ex. `"BS"` → `BS1`, `BS2`… La **numérotation est propre à chaque type**. |
| `name_attr` | chaîne | F | `code` de l'attribut servant de **libellé** à une instance (dans les listes, les pastilles de référence). Vide ou absent : l'`id` est utilisé. |
| `attributes` | tableau | O | Schéma des **attributs** du type, dans l'ordre (§4.7.2). Peut être vide (instances réduites à un `id`). |

#### 4.7.2 Attribut d'un type (`attributes[]`)

Un attribut se décrit **exactement comme un champ personnalisé** (§4.6.1) — mêmes `type`, `label`, `help`, `description`, `required`, `pattern`, bornes, `items`, `palette`, `colors`, `step`, `order` — **sans** `target` ni `filterable`, et **avec** le type supplémentaire `reference` :

| Champ | Type | O/F | Description |
|---|---|---|---|
| `code` | chaîne | O | Identifiant de l'attribut, **unique** dans le type. Sert de clé dans `objects[].values`. |
| `label` | objet | O | Libellé multilingue. |
| `type` | chaîne | O | Mêmes types qu'un champ personnalisé (§4.6.1) **plus** `"reference"` (objet → objet, ou objet → risque/mesure). |
| `object_type` | chaîne | Cond. | **Obligatoire** pour le type `reference` : `code` du type ciblé (peut être **le type courant** — auto-référence, attention aux boucles), ou une sentinelle d'entité de l'analyse `"@risks"` / `"@measures"` (cf. §4.6.1). |
| `multiple` | booléen | F | Type `tags` ou `reference` : plusieurs valeurs autorisées. |
| *(autres)* | — | F | `required`, `pattern`, `min`/`max`, `min_items`/`max_items`, `items` (pour `select`/`checklist`/`tags`), `help`, `description`, `palette`, `colors`, `step`, `order` — voir §4.6.1. |

#### 4.7.3 Instance (`objects[]`)

| Champ | Type | O/F | Description |
|---|---|---|---|
| `id` | chaîne | O | Identifiant de l'instance, ex. `"BS1"`. **Unique au sein de son type.** Stable. |
| `type` | chaîne | O | `code` du type de l'instance (`object_types[].code`). |
| `values` | objet | O | Valeurs des attributs, par `code` d'attribut. Mêmes conventions de stockage que `custom` (§4.6.3) selon le type de l'attribut ; pour un attribut `reference`, la valeur est l'`id` d'une instance (ou un tableau d'`id` si `multiple`). |

#### 4.7.4 Références et intégrité

Une valeur de type `reference` (champ personnalisé d'entité **ou** attribut d'objet) contient l'`id` — ou un tableau d'`id` — d'instances du type `object_type`. L'application maintient la cohérence :

- **Suppression d'une instance référencée** : l'`id` est **retiré partout** où il apparaît (tableaux multivalués et références simples, tous champs et attributs confondus).
- **Suppression d'un type** : **en cascade** — instances supprimées, champs personnalisés et attributs qui le ciblaient retirés, valeurs correspondantes purgées.
- **Référence orpheline** (id inexistant) : **ignorée en silence** à l'affichage et à la réouverture, sans erreur (tolérance ascendante, §2).

#### 4.7.5 Exemple

```json
{
  "object_types": [
    { "code": "valeur_metier", "id_prefix": "VM", "name_attr": "nom",
      "label": { "fr": "Valeur métier" },
      "attributes": [ { "code": "nom", "type": "text", "label": { "fr": "Nom" } } ] },
    { "code": "bien_support", "id_prefix": "BS", "name_attr": "nom",
      "label": { "fr": "Bien support" },
      "attributes": [
        { "code": "nom", "type": "text", "label": { "fr": "Nom" } },
        { "code": "valeurs_soutenues", "type": "reference", "object_type": "valeur_metier",
          "multiple": true, "label": { "fr": "Valeurs métier soutenues" } }
      ] }
  ],
  "objects": [
    { "id": "VM1", "type": "valeur_metier", "values": { "nom": "Gestion de la relation client" } },
    { "id": "BS1", "type": "bien_support",
      "values": { "nom": "CRM", "valeurs_soutenues": ["VM1"] } }
  ],
  "custom_fields": [
    { "code": "vm_impactees", "target": "risk", "type": "reference",
      "object_type": "valeur_metier", "multiple": true, "filterable": true,
      "label": { "fr": "Valeurs métier impactées" } }
  ],
  "risks": [
    { "id": "R1", "label": "…", "initial_assessment": { "probability": 3, "severity": 4 },
      "custom": { "vm_impactees": ["VM1"] } }
  ]
}
```

## 5. Règles de cohérence et validation

Un fichier est **valide** s'il respecte le schéma JSON (§8) **et** les règles sémantiques suivantes :

| # | Règle |
|---|---|
| C1 | `format` vaut exactement `"risk-analysis-editor"`. |
| C2 | Chaque `id` est unique au sein de sa collection (`risks`, `measures`). |
| C3 | Pour chaque axe, les `value` des niveaux sont uniques et strictement croissantes dans l'ordre du tableau. |
| C4 | Toute `probability` d'une cotation correspond à une `value` existante de `vertical_axis` ; toute `severity` à une `value` de `horizontal_axis`. |
| C5 | Les plages `[score_min, score_max]` des `criticality_levels` couvrent tous les scores atteignables et ne se chevauchent pas. |
| C6 | Dans chaque `traitement`, `risk` et `measure` référencent des `id` existants (intégrité référentielle). |
| C7 | Si `method = "matrix"`, les dimensions de `matrix` égalent (nb niveaux probabilité) × (nb niveaux gravité). |
| C8 | Les `code` de `object_types` sont uniques ; chaque `objects[].type` référence un `object_types[].code` existant ; chaque `objects[].id` est unique **au sein de son type**. Tout attribut/champ `reference` porte un `object_type` existant. |
| C9 | Une cotation résiduelle ne devrait pas être **plus grave** que l'initiale (avertissement). |
| C10 | Une valeur de `reference` devrait pointer vers une instance **existante** du type ciblé ; une référence orpheline est tolérée et ignorée (avertissement, §4.7.4). |

**Niveaux de sévérité :** C1–C8 sont **bloquants** (fichier invalide). C9 et C10 sont des **avertissements** (fichier valide mais douteux).

---

## 6. Extensibilité

- **Champs additionnels :** un producteur peut ajouter des champs à n'importe quel objet ; un lecteur les ignore s'il ne les connaît pas (§2).
- **Espace réservé `extensions` :** objet libre, à la racine et/ou dans chaque entité, destiné aux données propriétaires (ex. cache de score, coordonnées d'affichage figées, champs métier). Il est recommandé d'y préfixer les clés par un identifiant d'éditeur, ex. `"omt:zone_geographique"`.
- **Préférences d'affichage `extensions.display` (non normatif) :** l'application y stocke des choix de présentation propres à l'analyse.
  - `arrangement` : disposition des pastilles dans les matrices.
  - `date_format` : format d'affichage des dates (échéances, dates du rapport, champs personnalisés de type date) dans l'application et les rapports — `iso` (AAAA-MM-JJ, défaut), `eu` (JJ/MM/AAAA), `us` (MM/JJ/AAAA) ou `long` (localisé selon la langue). Les dates restent **stockées en ISO** ; seul l'affichage change (la saisie, le tri et les exports CSV conservent l'ISO).
  - `columns` : personnalisation des colonnes des registres. Objet dont les clés sont `risks`, `measures` et `links` ; chaque valeur est la **liste ordonnée des colonnes visibles** du registre correspondant (la colonne « Actions » est implicite et toujours affichée). Une colonne de champ personnalisé est désignée par `cf:<code>` ; une colonne inconnue (champ supprimé) est ignorée. Absent : ordre par défaut. Exemple : `{ "risks": ["id","risk","initial","residual","cf:source_risque"] }`.
  - `filters` : **filtrage propagé** enregistré avec l'analyse et réappliqué à la réouverture. `{ risk_category, measure_type, measure_status, custom }`, où `custom` est un objet `code → valeur` pour les champs personnalisés filtrables (ce que reflète le paramètre d'adresse `?filter=`). Ne couvre pas la recherche texte ni les filtres locaux du plan d'action (responsable, « en retard »). Les valeurs périmées sont ignorées ; absent : aucun filtre.
  - `stats` : personnalisation de l'**onglet Statistiques**. `{ blocks: [ … ] }` — liste **ordonnée** de blocs `{ id, type, on, size, display, shape, target?, field? }`. Types : `counters`, `criticality`, `risk_category`, `measure_type`, `measure_status`, `risk_owner`, `measure_owner`, `coverage`, `custom` (répartition par champ personnalisé à valeurs fermées, id `custom:<cible>:<code>`) et `num_agg` (**agrégat numérique** — tuiles effectif renseigné / moyenne / somme / min / max — d'un champ *échelle* ou *calculé numérique*, id `num_agg:<cible>:<code>`). `size` : `full`/`half` ; `display` : `table`/`chart`/`both` (les compteurs et `num_agg` sont en tuiles) ; `shape` : `donut`/`pie`. Absent : blocs par défaut. Bloc de type inconnu **ignoré** ; bloc `custom`/`num_agg` dont le champ a disparu **retiré**.
  - `radar` : personnalisation de l'**onglet Radars**. `{ view, render, weights }`. **`view`** est la vue courante, **enregistrée avec l'analyse et restaurée à la réouverture** (comme les filtres) : `{ dim, metric, eval, empty_axes }` — `dim` = `"cat"` (catégorie) ou le **code** d'un champ personnalisé de risque à valeurs fermées (select / checklist / tags / **scale** / **reference**) ; `metric` ∈ `avg` / `max` / `sum` / `weighted` / `count`, **ou** une métrique « champ numérique » `cf:<code>:avg` / `cf:<code>:max` / `cf:<code>:sum` (moyenne, max ou somme d'un champ de risque *échelle* ou *calculé numérique* par axe, indépendante de l'évaluation) ; `eval` ∈ `initial` / `residual` / `both-side` / `both-over` ; `empty_axes` (booléen, **défaut `true`**) affiche **tous les axes possibles**, y compris ceux sans risque dans la vue (item/instance non utilisé, ou valeur écartée par un filtre) — `false` ne garde que les axes présents. Une valeur périmée est ramenée à son défaut. `render` (teinte des bandes, contour, pas des anneaux, couleurs des séries, réticule) et `weights` (poids par code de criticité pour la métrique *pondérée*) portent le **rendu**. Absent : réglages par défaut.
  - `report` : personnalisation du rapport (rendu écran/PDF **et** export Word, pilotés par la même configuration). Sous-clés :
    - `scope` : `"all"` (analyse complète) ou `"filtered"` (sous-ensemble selon les filtres et la recherche actifs).
    - `orientation` : `"portrait"` (défaut) ou `"landscape"` — orientation de la page à l'impression PDF et à l'export Word.
    - `cover` : page de garde `{ on, logo, title, subtitle, show_organization, show_author, show_date, version, confidentiality, free_text }`. `logo` est un *data URI* incorporé ; `title`/`version` vides reprennent le titre/la révision de l'analyse ; `free_text` accepte du Markdown.
    - `toc` : `{ on }` — table des matières (champ **TOC natif** à l'export Word).
    - `header` / `footer` : en-tête / pied à trois zones `{ left, center, right }` (`header` accepte aussi `logo`), **réservés à l'export Word** — ils ne sont **pas** rendus à l'écran ni à l'impression PDF. Variables : `{title}`, `{organization}`, `{author}`, `{date}`, `{version}`, `{confidentiality}`, `{page}`, `{pages}` (l'en-tête/pied est répété par page).
    - `sections` : **liste ordonnée** des sections publiées, chacune `{ id, on, … }`. Identifiants : `metadata`, `presentation`, `summary_counts`, `summary_distribution`, `grid_axes`, `grid_criticality`, `matrix_ir` (matrices initiale et résiduelle **accolées**), `matrix_initial` (matrice initiale **seule**), `matrix_residual` (matrice résiduelle **seule**), `matrix_traj`, `risks_table`, `risks_detail`, `measures_table`, `measures_detail`, `links_table`, `links_detail`, `action_plan`. Options par section : `zone` (`"header"` / `"repeated"` / `"appendix"` — utilisé par le **rapport éclaté**, voir `iteration`) ; `action_plan.view` (`"due_date"` / `"status"` / `"responsible"`) ; `metadata.rows[{id,on}]` (ordre du cartouche) ; `presentation.items[{id,on}]` (`description` et `cf:<code>`) ; `*_table.columns` (mêmes clés que `display.columns`).
    - `iteration` : **rapport éclaté** — le rapport se répète pour chaque valeur d'un critère (chaque chapitre étant automatiquement filtré). `{ by, sort }`. `by` : `"none"` (défaut, rapport unique), `"risk_category"`, `"measure_type"`, `"risk_owner"`, `"measure_responsible"`, `"per_risk"` (un chapitre par risque : fiche détaillée + trajectoire + mesures), ou `"cf:<code>"` (champ personnalisé à valeurs fermées, cible risque ou mesure ; un item à valeurs multiples apparaît dans plusieurs chapitres). `sort` : `"criticality"` (défaut, criticité du risque le plus critique du groupe), `"alpha"`, ou `"count"` (nombre de risques) ; le groupe « valeur vide » (non catégorisé / sans propriétaire…) est toujours placé **en dernier**. En mode éclaté, les sections se répartissent selon leur `zone` (**en tête** une fois, **répétées** filtrées par chapitre, **annexe** une fois non filtrée) ; l'éclaté part de l'**analyse complète** (les trois modes *complète* / *filtré* / *éclaté* sont exclusifs). S'applique au rendu écran, à l'impression PDF **et** à l'export Word.
    - Lorsque `scope` vaut `"filtered"`, un **résumé du périmètre filtré** (nombre de risques/mesures retenus et valeurs des filtres actifs) est ajouté automatiquement en tête du rapport ; il ne figure pas dans `sections`.
    - **Absent : modèle par défaut** — page de garde, table des matières et toutes les sections activées, dans l'ordre par défaut, plan d'action inclus, **sauf** `matrix_initial` et `matrix_residual` (désactivées par défaut ; seule `matrix_ir` accolée est cochée). **Robustesse :** une section, une ligne ou une colonne connue absente d'une configuration existante est ajoutée **désactivée** ; un identifiant inconnu est ignoré.
- **Compatibilité :** les lecteurs doivent traiter un fichier de version mineure supérieure connue en mode « meilleure lecture possible ».

---

## 7. Versionnement du format et identifiants

- **`version`** suit un schéma `MAJEUR.MINEUR`.
  - Incrément **mineur** : ajout de champs facultatifs, rétrocompatible.
  - Incrément **majeur** : changement cassant (renommage/suppression de champ obligatoire, changement de sémantique).
- **Identifiants (`id`) :** chaînes stables et immuables une fois attribuées (ne pas réutiliser un `id` supprimé). Format libre ; recommandation : préfixe + numéro (`R1`, `M1`) ou UUID pour l'interopérabilité outillée.

---

## 8. Schéma JSON

Un schéma JSON (Draft 2020-12) accompagne cette spécification et permet la validation automatique de la structure :

- Fichier : [`schema-analyse-risque.json`](schema-analyse-risque.json)

Le schéma couvre les contraintes structurelles (types, obligatoires, énumérations, dont `object_types` / `objects` et le type de champ `reference`). Les règles sémantiques C2–C10 (§5) — unicité et intégrité référentielle des risques, mesures, liens **et objets/références** —, qui dépassent l'expressivité pratique de JSON Schema, sont à vérifier par l'outil.

---

## 9. Exemple complet

Un fichier d'exemple conforme, correspondant aux données des maquettes, est fourni :

- Fichier : [`demo-ebios-rm-systeme-d-information.rae.json`](../examples/demo-ebios-rm-systeme-d-information.rae.json)

Extrait :

```json
{
  "format": "risk-analysis-editor",
  "version": "1.0",
  "grid": {
    "vertical_axis": {
      "label": "Probabilité",
      "levels": [
        { "value": 1, "label": "Très faible" },
        { "value": 5, "label": "Très forte" }
      ]
    },
    "horizontal_axis": {
      "label": "Gravité",
      "levels": [
        { "value": 1, "label": "Très faible" },
        { "value": 5, "label": "Très forte" }
      ]
    },
    "score": { "method": "product" },
    "criticality_levels": [
      { "code": "faible", "label": "Faible", "score_min": 1, "score_max": 4,
        "color": "#2e9e5b", "acceptance": "acceptable" }
    ]
  },
  "risks": [
    {
      "id": "R1", "label": "Fuite de données clients", "category": "Cybersécurité",
      "initial_assessment":   { "probability": 5, "severity": 5 },
      "residual_assessment": { "probability": 2, "severity": 5 }
    }
  ],
  "measures": [
    { "id": "M1", "label": "Chiffrement + contrôle d'accès + DLP", "type": "technical", "status": "implemented" }
  ],
  "treatments": [
    { "risk": "R1", "measure": "M1" }
  ]
}
```

---

## Annexe A — Glossaire

| Terme | Définition |
|---|---|
| **Risque initial (brut)** | Niveau de risque avant toute mesure de maîtrise. |
| **Risque résiduel (net)** | Niveau de risque subsistant après application des mesures. |
| **Mesure de maîtrise** | Action réduisant la probabilité et/ou la gravité d'un ou plusieurs risques. |
| **Traitement** | Lien entre un risque et une mesure qui le couvre. |
| **Cotation** | Couple (probabilité, gravité) attribué à un risque à un instant donné. |
| **Score de criticité** | Valeur dérivée combinant probabilité et gravité selon `grid.score`. |
| **Niveau de criticité** | Zone colorée (faible → critique) déterminée par la plage de score. |
