# Validateur `.rae.json`

Outil **HTML autonome, 100 % hors‑ligne** qui vérifie le **format** et la **cohérence** d'un fichier
d'analyse de risque `.rae.json`. Aucune dépendance, aucune installation, aucune donnée envoyée : ouvrez
`index.html` dans un navigateur (double‑clic) ou servez‑le en HTTP.

## Utilisation

- **Glissez‑déposez** un ou plusieurs `.rae.json` sur la page, ou **Charger un fichier…**, ou
  **Coller le JSON…**.
- La colonne de gauche liste les fichiers chargés avec un badge de synthèse (*valide* /
  *n erreurs* / *n avertissements*).
- Le panneau de droite affiche :
  - un **verdict** — *Fichier valide* / *Conforme, avec réserves* / *Fichier non conforme* ;
  - des **filtres** (Erreurs, Avertissements, recherche texte) ;
  - les résultats **groupés par catégorie**, chacun avec le **numéro de ligne** et un **extrait**
    de la ligne source (élidé `…` avant/après si elle est trop longue), son **chemin** dans le fichier
    (ex. `risks[3].initial_assessment.probability`) et le **numéro de règle** (voir plus bas).
- Paramètre d'URL `?file=<url>` : charge automatiquement le fichier pointé (si l'outil est servi en
  HTTP) — pratique pour un usage scripté.

## Deux niveaux de sévérité

- **Erreur** — le fichier est *non conforme* : structure invalide, incohérence, ou donnée qui empêche
  une lecture fiable (règles bloquantes **C1–C8** de la spec).
- **Avertissement** — à vérifier, sans bloquer : donnée douteuse, incomplète, ou orpheline tolérée
  (règles **C9/C10**, validations de valeur, conflits de nommage).

> Les numéros de règle **C1–C10** renvoient à `specs/SPEC-format-analyse-risque.md` §5. L'application
> elle‑même est **permissive au chargement** (elle ne vérifie pas ces règles) : ce validateur les
> applique d'après la spécification.

---

## Liste complète des contrôles

### 1. Format & structure (racine)
- **Erreur** — la racine n'est pas un objet JSON ; JSON illisible (syntaxe).
- **Erreur** — clé `format` absente ou ≠ `"risk-analysis-editor"`.
- **Erreur** — clé obligatoire `risks` absente ; `grid` absente/invalide.
- **Erreur** — `risks`, `measures`, `treatments`, `custom_fields`, `object_types`, `objects` présents
  mais **pas un tableau** ; `metadata` présent mais pas un objet.
- **Avertissement** — `version` absente ou hors format `MAJEUR.MINEUR`.
- **Avertissement** — `metadata.language` hors `fr`/`en`/`it` ; `metadata.status` hors
  `draft`/`approved`/`archived`.

### 2. Grille de cotation
- **Erreur** — axe (vraisemblance / gravité) absent, ou moins de 2 niveaux, ou niveau sans `value`
  numérique.
- **Erreur (C3)** — valeurs d'axe **dupliquées** ou **non strictement croissantes**.
- **Erreur (C7)** — méthode de score `matrix` sans matrice, ou dimensions ≠ (niveaux V × niveaux G).
- **Erreur (C5)** — niveau de criticité avec `score_min > score_max` ; **plages qui se chevauchent**.
- **Avertissement** — méthode de score inconnue ; `grid.score` absente ; aucun niveau de criticité ;
  `acceptance` inconnue ; `color` de criticité non `#RRGGBB`.

### 3. Champs personnalisés (définitions)
- **Erreur** — champ sans `code` ; `target` invalide (≠ analysis/risk/cotation/measure/link) ;
  `type` inconnu (parmi les 19 types).
- **Erreur** — type `select`/`checklist`/`tags`/`scale` sans `items` ; `reference` sans `object_type` ;
  `computed` sans `expression`.
- **Erreur (C2)** — deux champs de même **cible** partagent le même `code` ; **code d'item** dupliqué ;
  **valeur d'échelle** dupliquée.
- **Avertissement** — champ sans `label` ; `result_type` inconnu.
- **Avertissement (nommage)** — deux champs de même cible portent le **même libellé**.

### 4. Types d'objets & attributs
- **Erreur** — type d'objet sans `code` ; **type dupliqué** (C2) ; attribut sans `code`, **attribut
  dupliqué** dans un type (C2) ; type d'attribut inconnu ; attribut `select/…` sans `items`,
  `reference` sans `object_type`, `computed` sans `expression`.
- **Avertissement** — type sans `label` / sans `id_prefix` ; `id_prefix` partagé par plusieurs types ;
  `name_attr` pointant vers un attribut inexistant (C8) ; libellés de types / d'attributs en double.

### 5. Risques
- **Erreur** — risque non‑objet ; risque sans `id` ; **id de risque en double** (C2).
- **Erreur (C4)** — vraisemblance/gravité manquante ou non numérique ; **hors des niveaux de l'axe**.
- **Avertissement** — risque sans `label` ; libellés de risques en double ; **résiduel > initial** (C9).

### 6. Mesures
- **Erreur** — mesure non‑objet ; mesure sans `id` ; **id de mesure en double** (C2).
- **Avertissement** — mesure sans `label` ; libellés en double ; `status` inconnu ; `due_date` hors
  format `AAAA-MM-JJ`.

### 7. Liens (`treatments`)
- **Erreur (C6)** — lien sans `risk`/`measure` ; lien vers un **risque** ou une **mesure inexistants**.
- **Avertissement** — **lien en double** (même risque + même mesure).

### 8. Objets (instances)
- **Erreur** — objet non‑objet ; objet sans `id` ; objet sans `type` ; **type inconnu** (C8) ;
  **objet en double** dans son type (C8) ; `values` pas un objet.
- **Avertissement** — même id d'objet réutilisé dans deux types ; **valeur d'attribut orpheline**
  (clé sans attribut correspondant).

### 9. Valeurs de champs (custom & attributs)
Pour les champs de cible `analysis` (`custom` racine), `risk` (`risk.custom`), `cotation`
(`initial/residual_assessment.custom`), `measure`, `link` (`treatment.custom`), et les attributs d'objet :
- **Avertissement (C10)** — **valeur orpheline** : clé présente dans `custom`/`values` sans définition
  de champ/attribut correspondant.
- **Avertissement** — **champ obligatoire** (`required`) manquant ou vide.
- **Avertissement (validation de valeur)** — selon le type :
  - `integer`/`float` : non numérique, hors `min`/`max`, non entier ;
  - `progress` : hors 0–100 ; `boolean` : non booléen ;
  - `date` : hors `AAAA-MM-JJ`, hors `min`/`max` ; `color` : hors `#RRGGBB` ;
  - `url` / `email` / `tel` : format invalide ; `regexp` : ne respecte pas `pattern` ;
  - `text`/`textarea` : longueur hors `min`/`max` ;
  - `select` : valeur absente des items ; `checklist`/`tags` : item absent, `min_items`/`max_items` ;
  - `scale` : niveau absent de l'échelle.

### 10. Références (`reference`)
- **Erreur (C8)** — `object_type` d'une référence inconnu (ni type d'objet défini, ni `@risks`,
  ni `@measures`).
- **Avertissement (C10)** — **référence orpheline** : id pointant vers un objet / risque / mesure
  **inexistant**.

### 11. Formules des champs calculés (`computed`)
- **Erreur** — **erreur de syntaxe** (grammaire du moteur : opérateurs, parenthèses, chaînes…), avec
  position ; **fonction inconnue** (hors catalogue Excel : `IF, SUM, AVERAGE, MEDIAN, MIN, MAX, COUNT,
  ROUND, ABS, MOD, POWER, SQRT, CONCAT, LEN, TODAY, DATE, YEAR, MONTH, DAY, EDATE, DATEDIF`, …).
- **Erreur** — **référence inexistante** : `cf.<code>` absent de la même cible ; grandeur native
  inconnue ; collection `risks.cf.<code>` / `measures.…` / `links.…` invalide.
- **Erreur** — **cycle** de dépendances entre champs calculés (`A → B → A`).
- **Avertissement** — traversée de référence `cf.<ref>.cf.<attr>` via un champ non‑référence, ou vers
  un attribut absent du type cible ; grandeur de collection inconnue.

### 12. Nommage (avertissements)
- Libellés en double parmi les champs (même cible), les types d'objet, les attributs (même type),
  les risques, les mesures.

---

## Notes de conception

- Le validateur **reproduit** fidèlement le vocabulaire de l'application : les 19 types de champ, les
  énumérations (statuts, cibles, méthodes de score…), les expressions rationnelles de validation
  (URL/e‑mail/téléphone/motif) et la **grammaire des formules** (analyseur descendant récursif, sans
  `eval`).
- Il applique **en plus** les règles de cohérence **C1–C10** que l'application tolère silencieusement au
  chargement (références et champs orphelins acceptés, id non revérifiés, etc.).
- Un seul fichier `index.html` autosuffisant : rien à générer, rien à installer.
