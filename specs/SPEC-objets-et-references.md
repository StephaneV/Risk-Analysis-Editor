# SPEC — Objets et références (champs complexes)

> **Statut : proposition v1 — points ouverts tranchés (§11), prête à figer.** Branche `feat/objets-et-references`.
> Objectif : permettre de modéliser des **entités complexes réutilisables** (biens supports,
> valeurs métier, sources de risque…) et de les **référencer** depuis les risques, les mesures,
> l'analyse et entre objets — de quoi mener une analyse façon **EBIOS RM**.

## 1. Objectif et cas d'usage

Aujourd'hui, un champ personnalisé porte une valeur **scalaire** (texte, date, tags…) attachée à
une entité. On veut des valeurs **structurées et partagées** :

- **Bien support** = { nom, catégorie, niveau de sécurité… } — un même bien référencé par plusieurs risques.
- **Valeur métier** = { nom, responsable, **biens supports** (référence multiple) } — relation objet→objet.
- Un **risque** référence une ou plusieurs valeurs métier, une source de risque, etc.

## 2. Vocabulaire (trois concepts distincts)

| Terme | Définition | Où c'est stocké |
|---|---|---|
| **Type d'objet** | *schéma* réutilisable : nom + liste d'**attributs** typés. N'est attaché à aucune entité. | `analyse.object_types[]` |
| **Instance d'objet** | une valeur concrète du type (ex. « Serveur HDS-01 »), avec un **id** et les valeurs de ses attributs. | `analyse.objects[]` |
| **Attribut** | un champ *à l'intérieur* d'un type ; réutilise les 14 types de champ perso **+ `reference`**. | `object_types[].attributes[]` |
| **Champ référence** | champ perso de type **`reference`** pointant vers des instances d'un type d'objet ; posé sur une entité (risque/mesure/analyse) **ou** comme attribut d'un type (objet→objet). | `custom_fields[]` ou `attributes[]` |

> Décision actée : « objet » **n'est pas** un type de champ. Le seul nouveau type de champ est
> **`reference`**. Les types d'objets sont des **schémas séparés** (évite le « problème de cible »
> — `CF_TARGETS` reste un enum fixe, filtres/rapport/i18n intacts).

## 3. Modèle de données (`.rae.json`)

Deux nouvelles collections de premier niveau (absentes = vides ; rétrocompatible) :

### 3.1 Types d'objets — `analyse.object_types[]`

```json
{
  "code": "bien_support",              // slug unique du type
  "label": {"fr": "Bien support"},     // nom affiché (localisé)
  "name_attr": "nom",                  // attribut servant de libellé d'instance (libre ; absent → id)
  "id_prefix": "BS",                   // préfixe des id d'instances (OBLIGATOIRE, saisi à la création)
  "order": 1,
  "attributes": [                      // définitions de champ, SANS `target`
    {"code": "nom", "type": "text", "label": {"fr": "Nom"}, "required": true},
    {"code": "categorie", "type": "select", "label": {"fr": "Catégorie"},
     "items": [{"code": "serveur", "label": {"fr": "Serveur"}}, {"code": "poste", "label": {"fr": "Poste"}}]},
    {"code": "heberge", "type": "reference", "label": {"fr": "Héberge"},
     "object_type": "valeur_metier", "multiple": true}
  ]
}
```

Un **attribut** est un champ perso au sens actuel (mêmes propriétés : `code`, `label`, `type`,
`required`, `items`, `min/max`, `pattern`, `multiple`, `palette`…) **moins `target`** (implicite =
le type). Le type d'un attribut peut être `reference` (→ objet↔objet).

### 3.2 Instances — `analyse.objects[]`

```json
{ "id": "BS1", "type": "bien_support",
  "values": { "nom": "Serveur HDS-01", "categorie": "serveur", "heberge": ["VM2"] } }
```

- `id` : **unique dans toute l'analyse**, forme `<id_prefix><n>` avec **numérotation par type**
  (ex. `BS1`, `BS2`). Le préfixe est **obligatoire** (saisi à la création du type). Immuable.
- `values[code]` : même **forme de valeur** que `custom[code]` aujourd'hui (scalaire, ou tableau de
  codes pour tags/checklist, ou id/tableau d'ids pour `reference`).

### 3.3 Champ référence (dans `custom_fields[]` ou `attributes[]`)

```json
{ "code": "biens", "target": "risk", "type": "reference",
  "object_type": "bien_support", "multiple": true, "required": false, "label": {"fr": "Biens supports"} }
```

- `object_type` : **un** type d'objet ciblé (mono-type au départ, cf. §11). **Évolution post-v1** : la cible peut aussi être une **entité de l'analyse** via une sentinelle `"@risks"` ou `"@measures"` — la référence pointe alors vers un risque ou une mesure (par leur `id`), et non vers une instance d'objet.
- `multiple` : mono- ou multi-valeur. `required` : obligatoire ou non.
- **Valeur** stockée dans l'entité : `risk.custom.biens = "BS1"` (mono) ou `["BS1","BS3"]` (multi) —
  on réutilise le stockage `custom{}` existant (pas de nouvelle structure côté entités).

## 4. Le type de champ `reference`

Étend le système des champs perso (points d'extension identifiés dans la cartographie) :

- `CF_TYPES` += `"reference"`. Nouvelle propriété de définition : `object_type` (+ `multiple`,
  `required` déjà gérés).
- **Saisie** (`cfControlHTML`) : sélecteur d'instances du `object_type` (liste déroulante mono, ou
  multi-sélection façon tags), avec bouton **« ＋ créer »** ouvrant l'édition d'une nouvelle instance
  à la volée.
- **Lecture/validation** (`cfReadValue`, `cfValidate`, `cfPresent`) : id(s) ; requis = au moins une.
- **Affichage** (`cfDisplay`/`cfDisplayHTML`) : le **`name_attr`** de chaque instance, rendu en
  **pastille** (réutilise le style des pastilles de mesure `measurePill`). Pour une cible
  `"@risks"`/`"@measures"`, la pastille porte le **code R*n*/M*n*** (libellé en infobulle) et
  ouvre la fiche visée — dans l'application comme dans le rapport Word.
- **Cibles autorisées** (entité) : les **5 cibles** actuelles — `analysis`, `risk`, `cotation`,
  `measure`, `link`. Objet→objet : via un attribut de type `reference` (auto-référence autorisée
  avec avertissement, cf. §11).

## 5. Interface utilisateur

### 5.1 Définition (Paramètres, approche hybride)

Zone Paramètres, **deux sous-sections côte à côte** :
- **Champs** (existant) — inchangé.
- **Types d'objets** (nouveau) — liste des types ; créer/éditer un type = nom + `name_attr` +
  **liste d'attributs**. L'édition d'un attribut ouvre **la même modale que celle d'un champ perso**
  (`openCustomFieldModal` réutilisé, **sans** le sélecteur de cible), pour tous les types y compris
  `reference`.

### 5.2 Instances (onglet dédié « Objets »)

- Nouvel onglet de premier niveau (comme Risques/Mesures), **groupé par type d'objet**.
- Table par type (colonnes = attributs, libellé d'instance = `name_attr`), ajout/édition/suppression.
- Le formulaire d'instance est **généré depuis les attributs du type** (réutilise `cfControlHTML` /
  `cfCollect`).
- **Création à la volée** : depuis un champ référence, « ＋ créer » ouvre le même formulaire.

### 5.3 Rendu d'un champ référence sur une entité

Pastilles cliquables (nom de l'instance) ; multi = plusieurs pastilles.

## 6. Intégrité référentielle

- **Supprimer une instance** : compter les usages (champs d'entités + attributs d'autres objets qui
  la référencent), **avertir** puis **retirer l'id** partout, sur confirmation. (`cfUsageCount`-like
  étendu au balayage des références.)
- **Supprimer un type d'objet** : **cascade avec confirmation** — supprime ses instances **et**
  nettoie les références vers ces instances, après avertissement (compte d'instances + d'usages).
- **Références orphelines** (id introuvable) : ignorées silencieusement à l'affichage (lecture défensive).

## 7. Filtres

- Un champ `reference` est **filtrable dès le départ** par instance (filtrer les risques portant tel
  bien support) — cf. `cfFilterableFields` / `cfEntityMatches`.

## 8. Rapport Word (moteur de modèle)

Extension du moteur (`tmplCollection`, `tmplResolveValue`, `tmplRenderCf`) :
- Nouvelle collection **`objects`** (et sous-collections par type / par référence) pour `{{#each …}}`.
- Un champ référence `risk.cf.biens` **déréférence** vers l'instance : accès au `name_attr` et,
  dans une boucle, aux attributs de l'instance (`{{#each risk.cf.biens}}{{ object.nom }}{{/each}}`).
- Rendu par défaut (hors boucle) : le `name_attr`, en badge (styles cell/flat/chip/pill déjà en place).
- **Navigation dans les attributs** dès la phase 1 : `{{#each risk.cf.biens}} … {{ object.<attr> }} … {{/each}}`
  — l'instance devient le **contexte courant**, ses attributs sont adressables (y compris ses propres
  références, déréférencées récursivement, profondeur bornée).
- *Syntaxe exacte des mots-clés figée au moment de l'implémentation du lot « rapport ».*

## 9. i18n

Trois langues (FR/EN/IT) : `cft.reference` ; libellés de la sous-section « Types d'objets », de
l'onglet « Objets », de la modale de type (`name_attr`, `id_prefix`), du sélecteur de référence
(« créer »), et messages d'intégrité. Les noms de types/attributs/instances restent dans les données
(`label{…}` / `values`), repli sur le `code`/`id`.

## 10. Format et migration

- `emptyAnalysis()` : ajouter `object_types: []` et `objects: []`.
- `normalize()` : garantir la présence des deux tableaux (défaut `[]`) ; aucune migration destructive.
- Fichiers existants (sans ces clés) : traités comme « pas d'objets » → **100 % rétrocompatible**.
- `validateStructure()` : tolérant (tableaux optionnels).

## 11. Décisions (points tranchés)

1. **Id d'instance** : `<id_prefix><n>`, **préfixe obligatoire** saisi à la création du type,
   **numérotation par type** (ex. `BS1`, `BS2`).
2. **Libellé d'instance** (`name_attr`) : l'attribut servant de libellé est **choisi librement** ; à
   défaut (non défini ou vide), on affiche l'**id** de l'instance.
3. **Suppression d'un type d'objet** : **cascade avec demande de confirmation** (supprime instances +
   nettoie les références).
4. **Référence** : cible **un seul** type d'objet.
5. **Filtres** : les références sont **filtrables dès le départ**.
6. **Rapport Word** : **navigation dans les attributs** de l'instance dès la phase 1 (pas seulement
   le nom).
7. **Cibles d'un champ référence** : les **5 cibles** (`analysis`, `risk`, `cotation`, `measure`, `link`).
8. **Auto-référence** (type se référençant lui-même) : **autorisée**, avec **avertissement** à la
   définition (risque de boucles) ; profondeur de déréférencement/affichage bornée.
