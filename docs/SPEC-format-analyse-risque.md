# Spécification du format de fichier — Risk Analysis Editor (.rae.json)

**Nom du format :** Risk Analysis Editor (RAE)
**Identifiant format :** `risk-analysis-editor`
**Version de la spécification :** 1.0
**Date :** 2026-07-09
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
| `justification` | chaîne | F | Justification de la cotation. |
| `date` | date | F | Date de la cotation. |

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
| `target` | chaîne | O | Objet rattaché : `"analysis"`, `"risk"`, `"measure"` ou `"link"` (lien risque↔mesure, cf. `treatments`). |
| `label` | objet | O | Libellé affiché, par langue : `{ "fr": "…", "en": "…" }`. À l'affichage : langue courante, repli sur `fr` puis sur `code`. |
| `type` | chaîne | O | `"boolean"`, `"integer"`, `"float"`, `"date"`, `"text"` (une ligne), `"textarea"` (multi-lignes), `"select"` (liste, choix unique), `"checklist"` (liste, choix multiple). |
| `required` | booléen | F | Si `true`, une valeur est obligatoire (bloquant à la saisie). |
| `min`, `max` | nombre / chaîne | F | Bornes : valeurs pour `integer`/`float` ; dates `AAAA-MM-JJ` pour `date` ; **longueur en caractères** pour `text`/`textarea`. |
| `min_items`, `max_items` | entier | F | Nombre minimal / maximal d'items cochés pour `checklist`. |
| `items` | tableau | Cond. | **Obligatoire** pour `select` et `checklist`. Éléments de la liste (§4.6.2). |
| `help` | objet | F | Texte d'aide multilingue (infobulle), même forme que `label`. |
| `order` | entier | F | Ordre d'affichage parmi les champs d'une même cible. |

Objet `items[]` (§4.6.2) :

| Champ | Type | O/F | Description |
|---|---|---|---|
| `code` | chaîne | O | Identifiant de l'item, **unique** dans le champ. C'est cette valeur qui est stockée. |
| `label` | objet | O | Libellé multilingue de l'item, même forme que `label` du champ. |

#### 4.6.3 Valeurs (`custom`)

Chaque objet `custom` associe un `code` de champ à sa valeur, selon le type :

| Type | Valeur stockée |
|---|---|
| `boolean` | `true` / `false` |
| `integer`, `float` | nombre |
| `date` | chaîne `AAAA-MM-JJ` |
| `text`, `textarea` | chaîne |
| `select` | `code` de l'item choisi |
| `checklist` | tableau de `code` d'items |

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

---

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
| C8 | Une cotation résiduelle ne devrait pas être **plus grave** que l'initiale sans justification (avertissement). |

**Niveaux de sévérité :** C1–C7 sont **bloquants** (fichier invalide). C8 est un **avertissement** (fichier valide mais douteux).

---

## 6. Extensibilité

- **Champs additionnels :** un producteur peut ajouter des champs à n'importe quel objet ; un lecteur les ignore s'il ne les connaît pas (§2).
- **Espace réservé `extensions` :** objet libre, à la racine et/ou dans chaque entité, destiné aux données propriétaires (ex. cache de score, coordonnées d'affichage figées, champs métier). Il est recommandé d'y préfixer les clés par un identifiant d'éditeur, ex. `"omt:zone_geographique"`.
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

Le schéma couvre les contraintes structurelles (types, obligatoires, énumérations). Les règles sémantiques C3–C9 (§5), qui dépassent l'expressivité pratique de JSON Schema, sont à vérifier par l'outil.

---

## 9. Exemple complet

Un fichier d'exemple conforme, correspondant aux données des maquettes, est fourni :

- Fichier : [`analyse-de-risques-systeme-d-information.rae.json`](../examples/analyse-de-risques-systeme-d-information.rae.json)

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
