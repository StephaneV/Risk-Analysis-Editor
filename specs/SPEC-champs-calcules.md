# Spécification (brouillon) — Champs « échelle » et « valeur calculée »

> **Statut : proposition de conception, non implémentée.** À valider avant développement.
> Cible : `app/risk-analysis-editor.html` (champs personnalisés, `custom_fields` / `custom`).
> Vocabulaire aligné sur l'existant (`SPEC-format-analyse-risque.md`, §4.6).

---

## 1. Objectifs

1. Des champs personnalisés porteurs d'une **valeur numérique de sens métier**, réutilisable dans des calculs :
   - **échelle** (`scale`) : une liste de niveaux, chacun avec une **valeur numérique** et un **libellé** ;
   - **échelle colorée** : idem avec une **couleur** par niveau.
2. Un champ **valeur calculée** (`computed`) : une **expression** portant sur d'autres champs (arithmétique,
   fonctions d'agrégation `min` / `max` / `moyenne` / `médiane`…), avec un **type de résultat** défini
   (nombre, date…), la **date courante** disponible et des **fonctions de manipulation de dates**.

Principe directeur : **aucun `eval` JavaScript**. L'évaluation passe par un **moteur d'expression maison**
(analyseur → arbre syntaxique → évaluateur), pour la sécurité, le déterminisme et la portabilité du format.

---

## 2. Type `scale` (échelle) — prérequis numérique

### 2.1 Définition (`custom_fields[]`)

Une échelle est une liste de niveaux ; **la `value` numérique tient lieu d'identité** (pas de `code`
séparé — décision, cf. plus bas) :

| Champ | Type | O/F | Description |
|---|---|---|---|
| `type` | `"scale"` | O | Nouveau type. |
| `items[]` | tableau | O | Niveaux de l'échelle (au moins un). |
| `items[].value` | nombre | O | **Valeur numérique** du niveau — **identité** (unique dans le champ), stockée, utilisée en calculs/stats/radar. |
| `items[].label` | i18n | O | Libellé affiché. |
| `items[].color` | `#RRGGBB` | F | Couleur du niveau → rendu en pastille (« échelle colorée »). |
| `items[].description` | i18n | F | Définition (infobulle, référentiels du rapport). |

> **Décidé** : un **seul** type `scale`. « Échelle colorée » = une échelle dont les items portent une
> `color`. Rendu en pastille colorée si des couleurs sont définies, sinon libellé texte.
>
> **Décidé — pas de `code` :** contrairement à `select`/`tags`, l'item n'a **pas** de `code` ; sa `value`
> numérique **est** son identité (donc **unique** dans le champ). La donnée devient **auto-descriptive**
> (un `3` stocké est interprétable seul) et directement exploitable en calcul, sans déréférencement.
> Contrepartie assumée : modifier la `value` d'un niveau est une **rebase délibérée** — les
> enregistrements existants conservent leur nombre (pas de réécriture silencieuse).

### 2.2 Saisie, stockage, affichage

- **Saisie** : liste déroulante (comme `select`) ; si les items ont des couleurs, pastilles colorées
  (comme `tags` en choix unique).
- **Stockage** : la **`value`** (nombre) du niveau choisi, directement dans `custom.<code>`.
- **Affichage** : `label` du niveau dont la `value` correspond (option : `label` + `(value)`). Une valeur
  **orpheline** (niveau retiré du barème) reste lisible : on affiche le **nombre** brut.

### 2.3 Intégration

- **Filtrable** (valeurs fermées) : la liste de choix propose les niveaux (libellé → `value`).
- **Statistiques** : dimension de répartition **et** — nouveauté — métrique **numérique**
  (moyenne / somme / min / max de la `value` sur une population).
- **Radar** : dimension (répartition) et/ou métrique numérique.
- **Calculs** : `cf.<code>` d'une échelle s'évalue **directement en nombre** (la `value` stockée) — c'est le
  pont vers les champs calculés (§3).

---

## 3. Type `computed` (valeur calculée)

### 3.1 Définition (`custom_fields[]`)

| Champ | Type | O/F | Description |
|---|---|---|---|
| `type` | `"computed"` | O | Champ dérivé, **non saisissable**. |
| `expression` | chaîne | O | Expression à évaluer (§3.4). |
| `result_type` | enum | O | `number` · `integer` · `date` · `text` · `boolean` (défaut `number`). |
| `decimals` | entier | F | `number` : nombre de décimales à l'affichage (défaut : brut). |
| `unit` | chaîne | F | Suffixe d'affichage (`€`, `j`, `%`…), purement cosmétique. |
| `filterable` | booléen | F | Autorise le filtrage par comparaison sur la valeur calculée (§3.9). |
| `alert` | objet | F | **Bornes d'alerte (v1)** — colore la valeur hors plage (§3.11). |

Pas de `required` ni de bornes de saisie (rien à saisir).

**Bornes d'alerte `alert`** (v1, §3.11) : `{ min?, max?, color? }` — la valeur affichée est **mise en
évidence** (couleur `color`, défaut *danger*) lorsqu'elle sort de `[min, max]` (l'une des deux bornes
suffit). Pour un `result_type` `date`, `min`/`max` sont des dates.

### 3.2 Modèle de valeurs — **dérivé, avec cache**

Comme le **score** et la **criticité** d'un risque, une valeur calculée n'est **pas saisie** ni faisant
foi : elle est **recalculée** à partir de l'expression (affichage, tri, filtre, stats, rapport, CSV, Word).
Avantages : cohérence garantie, jamais de valeur périmée vis-à-vis des champs sources.

**Cache (décidé, Q4)** : la dernière valeur calculée est **mémorisée dans `extensions`** (jamais dans
`custom`, qui reste réservé aux saisies), afin qu'un **consommateur tiers** (script, tableur, autre outil)
lise une valeur sans réimplémenter le moteur. Le cache est **informatif, jamais faisant foi** : l'app le
**recalcule et le réécrit** à l'ouverture et à chaque changement de source ; une entrée de cache dont
l'expression ou les sources ont changé est ignorée puis rafraîchie. Emplacement proposé :
`extensions.display.computed` = `{ "<entité>:<id>:<code>": <valeur>, "analysis:<code>": <valeur>, … }`
(clé stable par entité + code de champ). *(Détail d'emplacement à confirmer à l'implémentation.)*

### 3.3 Contexte et références

Une expression est évaluée **dans le contexte d'une entité** (celle de la `target` du champ) :

- **`cf.<code>`** — un autre champ personnalisé **de la même entité** (ou un autre **attribut** de la même
  instance, pour un attribut d'objet). Résolution par type :
  - `boolean` → `true`/`false` ; `integer`/`float`/`progress`/`scale` → nombre ; `date` → date ;
    `text`/`select`/`url`/… → texte ; `computed` → sa valeur (récursif, cf. §3.7).
  - Un champ **multivalué** (`tags`, `checklist`, `reference`) résout en **liste** de ses valeurs : `COUNT(cf.<code>)`
    en donne le **nombre** (0 si vide ou absent), et les autres agrégats parcourent chaque valeur. En contexte
    **texte** (`&`, `CONCAT`), la liste est rendue par ses valeurs jointes par `, `.
  - **Traversée de référence (un seul saut)** : `cf.<champ_référence>.cf.<attribut>` (ou `.id`) résout en
    **liste** de la valeur de cet attribut sur **tous les objets référencés** par le champ — donc agrégeable
    (`SUM` / `AVERAGE` / `COUNT` / `MIN` / `MAX`). L'attribut visé peut être une **échelle**, un **numérique**
    ou un attribut **calculé** de l'objet ; références cassées et attributs absents sont **ignorés** (nil).
    Limité à **un saut** (pas de `cf.a.cf.b.cf.c`). Exemple : `AVERAGE(cf.valeurs_metier.cf.niveau_risque)`.
- **Champs de base et dérivés de l'entité** — accessibles par leur nom (mêmes grandeurs que le rapport) :
  - **risque** : `id`, `label`, `category`, `owner`, `description`, `comment` ; `probability_initial`,
    `severity_initial`, `score_initial`, `criticality_initial` ; `probability_residual`, `severity_residual`,
    `score_residual`, `criticality_residual` ;
  - **mesure** : `id`, `label`, `type`, `status`, `responsible`, `due_date`, `cost`, `description`,
    `comment`, `overdue` ;
  - **cotation** : `probability`, `severity`, `score`, `criticality` ;
  - **lien** : `risk_id`, `measure_id`, `comment` ;
  - **objet** (attribut calculé) : `id`, et les autres attributs via `cf.<code>`.
- **`TODAY()`** — date du jour (§3.6).
- **Agrégats de collection** (surtout cible `analysis`) : une **collection** suivie d'un champ, réduite par
  une fonction d'agrégation :
  - `risks.cf.<code>`, `measures.cf.<code>`, `links.cf.<code>` — la valeur d'un champ sur **tous** les
    éléments ; `measures.cost`, `risks.score_initial`… pour les champs natifs/dérivés ;
  - `count(risks)`, `count(measures)` — effectifs.
  Exemple : `MEDIAN(risks.cf.gravite)`, `AVERAGE(measures.cost)`.

> **Portée par cible — décidé (Q2, séparation conservée) :**
> - `risk` / `measure` / `link` / `cotation` → expression **par entité** (ses propres champs + dérivés + `TODAY()`).
> - `analysis` → expression **globale** (agrégats de collections + `TODAY()`).
> Les agrégats de collection ne sont **pas** autorisés dans un champ par entité en v1 (évite l'ambiguïté
> « la moyenne de quoi, relativement à ce risque ? »). Les références **inter-entités** au sens
> *un risque lisant une valeur de ses mesures liées* restent **hors périmètre** (Q6). En revanche, la
> **traversée d'un champ de type référence vers les attributs des objets pointés** (un seul saut) est
> **prise en charge** — voir le §3.3 ci-dessus.
>
> **Affichage d'un champ calculé de cible `analysis` — décidé (Q3) : Statistiques et Rapport.** Il
> apparaît comme un **indicateur** (tuile / ligne) dans l'onglet **Statistiques** et dans la **synthèse du
> rapport** (écran/PDF/Word). Les champs calculés **par entité** s'affichent, eux, comme les autres champs
> de l'entité (fiche, colonne de registre `cf:<code>`, rapport, CSV, Word).

### 3.4 Grammaire — inspirée des formules Excel

Le langage s'inspire des **formules Excel** : mêmes fonctions et opérateurs usuels, syntaxe familière. La
**seule différence assumée** : les **références** ne sont pas des adresses de cellules (`A1`) mais des
**codes de champ** (`cf.<code>`, `risks.cf.<code>`, `score_initial`…), le tableur n'ayant pas de grille.

Conventions Excel reprises :
- Un **`=` initial est optionnel** (`=(cf.a+cf.b)/2` ≡ `(cf.a+cf.b)/2`).
- Opérateurs : `+ - * /`, **`^`** (puissance), **`&`** (concaténation de texte), comparaisons `=`, **`<>`**
  (aussi `!=`), `<`, `<=`, `>`, `>=`. Séparateur d'arguments : **`,`**. Décimale : **`.`**.
- Noms de fonctions **insensibles à la casse**, **canoniques en anglais** (stockés ainsi dans le fichier,
  comme le reste du format — cf. Q8 sur l'affichage localisé).

Notation EBNF simplifiée (chaînes entre `"…"` ou `'…'`) :

```
formula     := "="? expr
expr        := orExpr
orExpr      := andExpr ( "OR" andExpr )*
andExpr     := notExpr ( "AND" notExpr )*
notExpr     := "NOT" notExpr | comparison
comparison  := concat ( ( "=" | "<>" | "!=" | "<" | "<=" | ">" | ">=" ) concat )?
concat      := sum ( "&" sum )*                 // concaténation de texte (Excel)
sum         := product ( ( "+" | "-" ) product )*
product     := power  ( ( "*" | "/" ) power )*
power       := unary ( "^" power )?             // puissance, associative à droite
unary       := ( "-" | "+" ) unary | primary
primary     := number | string | boolean
             | funcName "(" argList? ")"
             | reference
             | "(" expr ")"
argList     := expr ( "," expr )*
reference   := ident ( "." ident )*             // cf.<code>, risks.cf.<code>, score_initial, …
```

Précédence (du plus fort au plus faible) : unaire → `^` → `* /` → `+ -` → `&` → comparaisons → `NOT` →
`AND` → `OR` (ordre Excel).

### 3.5 Catalogue de fonctions (noms Excel)

Chaque argument d'agrégation est **soit une liste** de valeurs (`AVERAGE(cf.a, cf.b, cf.c)`), **soit une
collection** (`AVERAGE(risks.cf.score)`) — l'équivalent d'une **plage** Excel.

**Numériques / agrégation :**

| Fonction | Rôle |
|---|---|
| `MIN(…)`, `MAX(…)` | minimum, maximum |
| `SUM(…)` | somme |
| `AVERAGE(…)` | moyenne arithmétique |
| `MEDIAN(…)` | médiane |
| `COUNT(…)` | nombre de valeurs **présentes** (non vides) |
| `ROUND(x, n)`, `ROUNDUP(x, n)`, `ROUNDDOWN(x, n)` | arrondis (comme Excel) |
| `INT(x)`, `ABS(x)` | partie entière (plancher), valeur absolue |
| `MOD(a, b)`, `POWER(a, b)` (≡ `a^b`), `SQRT(x)` | modulo, puissance, racine |

**Logique / conditionnel :** `IF(cond, siVrai, siFaux)`, `AND(…)`, `OR(…)`, `NOT(x)`, comparateurs
`=`, `<>`, `<`, `<=`, `>`, `>=`. *(Idiome de bornage à la Excel : `MEDIAN(lo, x, hi)`.)*

**Dates** (les dates sont des grandeurs comparables et soustractibles, façon Excel — §3.8) :

| Fonction | Rôle |
|---|---|
| `TODAY()` | date du jour (§3.6) |
| `DATE(a, m, j)` | construit une date |
| `YEAR(d)`, `MONTH(d)`, `DAY(d)` | composantes |
| `EDATE(d, n)` | d + n **mois** (calendaire, comme Excel) |
| `DATEDIF(début, fin, unité)` | écart ; `unité` ∈ `"D"` (jours) · `"M"` (mois) · `"Y"` (ans) — sémantique Excel |

**Texte :** opérateur `&` et `CONCAT(…)` ; `LEN(x)`. (Extensible : `UPPER`, `LOWER`, `LEFT`, `RIGHT`…)

### 3.6 Déterminisme et `today()`

`today()` est évaluée **au moment du rendu/export**, dans le **fuseau local**. Conséquence assumée : une
valeur calculée dépendant de `today()` **change au fil du temps** — c'est l'objectif (« jours avant
échéance »). Le fichier ne fige donc pas ces valeurs (cohérent avec §3.2). *(Note technique : l'app évite
`Date.now()` dans certains contextes — l'évaluation des champs calculés se fait à l'affichage, où l'accès à
la date locale est légitime.)*

### 3.7 Évaluation : dépendances, ordre, cycles, erreurs

- **Graphe de dépendances** entre champs calculés (un `computed` peut référencer un autre `computed`).
  Résolution en **ordre topologique** ; **cycle détecté → erreur** sur les champs impliqués (pas de boucle
  infinie).
- **Erreurs non bloquantes** : référence inconnue, type incompatible (ex. `date + texte`), division par
  zéro, cycle → la valeur affichée est un **marqueur d'erreur** (`—` ou `#ERR`) avec **infobulle**
  explicative ; le reste de l'analyse n'est pas affecté. Un avertissement peut être remonté dans l'éditeur
  du champ (validation de l'expression à l'enregistrement).
- **Valeurs manquantes** : un `cf.<code>` vide vaut « absent » ; les agrégats **ignorent** les absents
  (`avg` sur les présents) ; une opération arithmétique sur un absent donne « absent » (propagation), sauf
  via `if(... , ...)` explicite.

### 3.8 Système de types et coercition

- Types internes : `number`, `date`, `text`, `boolean`, `absent`.
- **Dates façon Excel** : une date se compare et se soustrait comme un nombre de jours —
  `TODAY() - due_date` → **nombre de jours** ; `due_date + 30` → **date** (30 jours après). Les mois/ans
  calendaires passent par `EDATE` / `DATEDIF` (Excel ne les fait pas au `+` brut).
- Comparaisons : numériques si possible, sinon `localeCompare` ; dates comparées chronologiquement.
- Le **`result_type`** déclaré **coerce** le résultat final (ex. `integer` arrondit ; `date` attend une
  date ; incompatibilité → erreur §3.7).

### 3.9 Intégration transverse

| Point | Comportement |
|---|---|
| **Saisie** | Aucune — non collecté, exclu de l'**import CSV**. |
| **Affichage en fiche** | **Aperçu lecture seule** dans la liste des champs personnalisés de la modale (risque, mesure, lien, cotation, instance d'objet), **recalculé en direct** au fil des saisies des autres champs. |
| **Affichage ailleurs** | Registre (colonne `cf:<code>`), rapport, exports — mis en forme selon `result_type`, `decimals` et `unit`. Un résultat **date** suit le **format de date global** de l'analyse (comme tout champ date), pas de format propre au champ. |
| **Tri** | Par valeur calculée (numérique/date/texte). |
| **Filtre** | Si `filterable` **et** résultat discret : **booléen** (Oui/Non) ou **alerte** définie (« En alerte » / « Hors alerte »), sous forme de liste de choix. Un résultat continu (numérique/date sans alerte) n'est pas proposé au filtre. (Lot F.) |
| **Statistiques** | Bloc **« agrégat numérique »** : tuiles effectif renseigné / moyenne / somme / min / max (lot F). Les calculés de cible *analyse* restent en **tuiles d'indicateurs** (lot E). |
| **Rapport / Word / CSV** | Valeur **matérialisée** au moment de l'export (colonne, cartouche, `field_values`…). |
| **Modèles Word** | `{{ risk.cf.<code> }}` rend la valeur calculée ; utilisable en `{{#if}}` et tri. |
| **Éditeur** | Zone *expression* (sans Markdown) avec **validation en direct**, choix *result_type*, et **pickers** d'insertion des jetons au curseur (champs perso, **champs de base/dérivés** de la cible, fonctions, opérateurs ; une fonction entoure la sélection). Les options **non pertinentes selon le `result_type` sont masquées** (décimales → `number` ; unité → `number`/`integer` ; alerte → `number`/`integer`/`date`) ; la case **« obligatoire » est masquée** (sans objet). |
| **Disponibilité** | Comme **champ personnalisé** (cibles `analysis`/`risk`/`cotation`/`measure`/`link`) **et** comme **attribut d'un type d'objet** (l'expression réfère alors aux autres attributs de l'instance). |
| **Schéma / i18n** | `computed` ajouté à `CF_TYPES` et à `objectAttribute`, au schéma JSON (contrainte `computed ⇒ expression`), au dictionnaire FR/EN/IT. |

### 3.10 Sécurité et robustesse

- **Aucun `eval`** ni accès au DOM/réseau : évaluateur pur sur l'AST.
- Bornes : longueur d'expression (ex. 2 000 car.), profondeur d'AST, nombre de nœuds — pour éviter les
  expressions pathologiques.
- Fonctions **en liste blanche** ; tout identifiant/fonction inconnu → erreur de compilation signalée.

### 3.11 Bornes d'alerte (v1)

Le champ `alert = { min?, max?, color? }` **met en évidence** la valeur affichée lorsqu'elle est **hors de
la plage attendue** : elle s'affiche alors en `color` (défaut *danger*, `#c0505a`). Purement **visuel** —
n'affecte ni le tri, ni les filtres, ni les calculs. L'alerte ne joue que si la valeur est **présente**
(une valeur absente / `#ERR` n'est jamais colorée). Les deux bornes sont **incluses** : la valeur est mise
en évidence **strictement** sous `min` ou **strictement** au-dessus de `max`.

**Format des bornes `min`/`max` :**

- Résultat **numérique** (`number` / `integer`) → `min`/`max` sont des **nombres** (décimale `.`), ex.
  `0`, `80`, `2.5`.
- Résultat **date** (`result_type = date`) → `min`/`max` sont des **dates au format ISO `AAAA-MM-JJ`**
  (ex. `2026-12-31`), la seule forme comparable de façon chronologique. Dans l'éditeur, ces deux champs
  deviennent des **sélecteurs de date** (qui produisent automatiquement une valeur ISO) ; dans le fichier,
  la borne est stockée telle quelle (`"2026-12-31"`).
- Les résultats `text` / `boolean` n'ont pas d'alerte de plage.

Les deux bornes sont **indépendantes et facultatives** ; on combine ainsi quatre comportements :

| `alert` | Colorée quand… | Lecture |
|---|---|---|
| *(absent)* | jamais | pas d'alerte. |
| `{ min: a }` | `valeur < a` | **plancher** : alerter en dessous de `a`. |
| `{ max: b }` | `valeur > b` | **plafond** : alerter au-dessus de `b`. |
| `{ min: a, max: b }` | `valeur < a` **ou** `valeur > b` | **plage tolérée** `[a, b]` : alerter en dehors. |

S'applique en fiche (aperçu lecture seule), en colonne de registre et dans le rapport.

**Exemples :**

- *Jours avant échéance* — `= due_date - TODAY()`, `alert = { min: 0 }` : coloré dès que la valeur est
  **négative** (mesure **en retard**). *(Plancher : rien à `0`, `3` ; alerté à `-1`.)*
- *Taux de couverture (%)* — `alert = { min: 80 }` : coloré si **< 80 %** (couverture insuffisante).
- *Budget consommé* — `alert = { max: 100 }` : coloré si **> 100** (dépassement).
- *Score maison attendu entre 2 et 4* — `alert = { min: 2, max: 4 }` : coloré si **< 2** ou **> 4**
  (hors de la plage cible). *(Ni `2`, ni `3`, ni `4` ne sont colorés ; `1` et `5` le sont.)*
- *Échéance limite* — `result_type = date`, `alert = { max: "2026-12-31" }` : coloré si la date calculée
  **dépasse** le 31/12/2026.

---

## 4. Ajouts au format `.rae.json` (schéma)

Dans `customField` :
- `type` : ajouter `"scale"` et `"computed"` à l'énumération.
- **`scale`** : `items[].value` (**nombre, requis, unique** — tient lieu d'identité, pas de `code`) ;
  `items[].label` (requis) ; `items[].color`, `items[].description` (optionnels).
- **`computed`** : `expression` (chaîne, requis), `result_type` (enum `number`/`integer`/`date`/`text`/
  `boolean`), `decimals` (entier), `unit` (chaîne), `filterable` (booléen),
  `alert` (objet `{ min?, max?, color? }`).
- Contraintes conditionnelles : `scale` ⇒ `items` (chaque item avec `value`) ; `computed` ⇒ `expression`.

**`custom`** : une échelle stocke la **`value`** (nombre) du niveau choisi ; un champ **calculé n'écrit
rien** dans `custom`. Le **cache** des valeurs calculées vit dans **`extensions`** (§3.2), séparé des
saisies et jamais faisant foi.

---

## 5. Exemples

```
# Échelle (cible risque) : niveau d'exposition, valeurs 1..4
scale « exposition » : { faible:1, moyen:2, eleve:3, critique:4 }

# Valeur calculée (cible risque) : criticité pondérée maison
computed « score_maison », result_type=number, decimals=1 :
    =(cf.exposition * 2 + cf.impact) / 3

# Valeur calculée (cible mesure) : jours restants avant échéance (dates façon Excel)
computed « jours_restants », result_type=integer :
    =due_date - TODAY()

# Valeur calculée (cible analyse) : médiane des scores maison du portefeuille
computed « mediane_score », result_type=number, decimals=1 :
    =MEDIAN(risks.cf.score_maison)

# Conditionnel (style Excel)
computed « alerte », result_type=text :
    =IF(due_date - TODAY() < 0, "En retard", IF(due_date - TODAY() <= 7, "Bientôt", "OK"))
```

---

## 6. Plan d'implémentation (par lots)

1. **Lot A — Échelle** ✅ : type `scale` (éditeur d'items `value`/`label`/`color`, saisie liste déroulante,
   lecture, affichage, filtre, stats numériques, schéma, i18n). La `value` stockée est directement le
   nombre exploité en calcul.
2. **Lot B — Moteur d'expression** ✅ : lexer + parseur + AST + évaluateur (arithmétique, `^`, `&`,
   comparaisons, `AND`/`OR`/`NOT`, `IF`), liste blanche de fonctions, gestion d'erreurs. Testable isolément.
3. **Lot C — Champ `computed` par entité** ✅ : `cf.<code>` même entité + **champs de base et dérivés**,
   `result_type`/formatage, **bornes d'alerte**, affichage lecture seule en fiche (live) + registre + tri,
   cache, éditeur (expression + validation + **pickers**), aussi disponible en **attribut d'objet**, schéma, i18n.
4. **Lot D — Dates** ✅ : `TODAY`, `DATE`, `YEAR`/`MONTH`/`DAY`, `EDATE`, `DATEDIF`, arithmétique de dates
   (livré avec le moteur au lot B et la liaison au lot C ; les dates calculées suivent le **format de date
   global** — pas de format propre au champ, cohérent avec tout champ date).
5. **Lot E — Agrégats de collection** ✅ (cible analyse) : références de collection `risks.cf.<code>` /
   `measures.cf.<code>` / `links.cf.<code>`, champs natifs/dérivés (`measures.cost`, `risks.score_initial`…),
   collections nues (`COUNT(risks)`) et effectifs directs (`risks_count`/`measures_count`/`links_count`) ;
   `AVERAGE`/`MEDIAN`/`SUM`/`MIN`/`MAX`/`COUNT` (absents ignorés). Affichage : **tuiles d'indicateurs** en
   tête de l'onglet **Statistiques** + section **présentation du rapport** (écran/PDF/Word), et aperçu
   lecture seule dans l'onglet **Présentation** (recalculé en direct). Détection de cycle par cible+code.
6. **Lot F — Filtre / stats / radar / rapport / Word / CSV** ✅ sur valeurs calculées et échelles numériques :
   - **Restitution** : valeurs calculées rendues partout (tableaux HTML du rapport, tables Word natives,
     moteur de gabarits Word, export CSV, notes d'objet) — pour les champs d'entité **et** les attributs
     d'objet calculés.
   - **Filtre** : les échelles filtrent déjà par item (type fermé) ; un champ **calculé** devient filtrable
     lorsqu'il produit des valeurs discrètes — résultat **booléen** (Oui/Non) ou **alerte** définie
     (« En alerte » / « Hors alerte »). Les résultats continus (numérique/date sans alerte) ne sont pas
     proposés comme filtre de sélection.
   - **Radar** : nouvelle **métrique « champ numérique »** — moyenne, max ou somme de la valeur d'un champ
     de risque *échelle* ou *calculé numérique* par axe (indépendante de l'évaluation initiale/résiduelle,
     comme le nombre de risques).
   - **Statistiques** : nouveau bloc **« agrégat numérique »** (tuiles : effectif renseigné, moyenne, somme,
     min, max) pour un champ *échelle* ou *calculé numérique* de risque/mesure/lien. Les échelles restent
     par ailleurs disponibles en répartition catégorielle ; les calculés d'analyse restent en tuiles
     d'indicateurs (lot E).
7. **Lot G — Consolidation** ✅ : i18n complète (FR/EN/IT), **guide utilisateur** — §14 sous-sections
   « Le type échelle » et « La valeur calculée » (formule & picker, fonctions, `COUNT` des multivalués,
   type du résultat, aperçu en direct, **alerte hors plage** avec les 4 cas et le format des bornes,
   surfaces d'exploitation), plus les mentions radar/statistiques/filtre —, alignement `SPEC-format`
   + schéma, banc de tests reproductible (lots B–F, 111/111).

---

## 7. Décisions (arrêtées avec l'utilisateur)

- **Q1** — Échelle : **un seul** type `scale`, couleur optionnelle par item (§2.1). *(La `value` numérique
  tient lieu d'identité — pas de `code`.)*
- **Q2** — **Séparation conservée** : agrégats de collection réservés à la cible **analyse** ; les champs
  calculés **par entité** ne voient que leurs propres champs + dérivés + `TODAY()` (§3.3).
- **Q3** — Champ calculé de cible `analysis` : affiché dans les **Statistiques** et le **Rapport** (§3.3).
- **Q4** — **Cache** des valeurs calculées dans `extensions` (informatif, recalculé à l'ouverture), pour les
  outils tiers (§3.2).
- **Q5** — **Fonctions dates comme proposées** : `TODAY`, `DATE`, `YEAR`/`MONTH`/`DAY`, `EDATE` (mois
  calendaires), `DATEDIF` (`D`/`M`/`Y`), et arithmétique de dates façon Excel (§3.5, §3.8).
- **Q6** — Références **inter-entités** : **hors v1** (§3.3).
- **Q7** — **Bornes d'alerte** : **en v1** (§3.11).
- **Q8** — Noms de fonctions : **anglais seuls** (§3.4).

*Reste à préciser à l'implémentation :* l'emplacement exact du cache dans `extensions` (§3.2), et le rendu
précis d'un indicateur calculé « analyse » dans les Statistiques et la synthèse du rapport (§3.3).
