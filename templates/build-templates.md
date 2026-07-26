# `build-templates.js` — générateur des modèles de démarrage

Ce script génère les **modèles méthodologiques** (squelettes vierges) livrés dans `templates/`, à partir d'une définition unique par méthode. Les fichiers `*.template.<lang>.rae.json` de ce dossier sont **produits** par ce script : ne les modifiez pas à la main, éditez la source puis régénérez.

## À quoi ça sert

Chaque modèle est une analyse **vide** (aucun risque, mesure ni lien) mais avec une **grille de cotation**, des **niveaux de criticité** et des **champs personnalisés** préconfigurés, prête à être complétée. Les métadonnées portent `kind:"template"`, ce qui indique à l'application d'ouvrir une **nouvelle analyse non reliée** (le modèle n'est jamais écrasé).

## Lancer la génération

Depuis le dossier `templates/` :

```bash
node build-templates.js
```

Le script écrit **12 fichiers** (4 méthodes × 3 langues) dans le dossier courant et affiche un récapitulatif. Aucune dépendance externe (uniquement `fs` et `path` de Node).

## Ce qui est produit

- **Nommage** : `<slug>.template.<lang>.rae.json` — par ex. `ebios-rm.template.fr.rae.json`.
- **Un fichier par langue** (`fr`, `en`, `it`). En effet, le format `.rae.json` n'est multilingue que pour les **libellés de champs personnalisés** (objets `{fr,en,it}`). Les axes de la grille, les niveaux de criticité et les métadonnées sont des **chaînes uniques** : on produit donc un fichier par langue, chacun avec ces chaînes dans sa langue.
- Les **champs personnalisés** restent, eux, pleinement `{fr,en,it}` dans **tous** les fichiers, afin que le changement de langue après ouverture les traduise aussi.

## Modèles définis

Quatre appels `emit(slug, spec)` en bas du fichier :

| slug | Méthode | Grille |
|---|---|---|
| `ebios-rm` | EBIOS Risk Manager (ANSSI) | vraisemblance × gravité 4×4 (produit) |
| `cnil-pia` | AIPD — méthode CNIL PIA | 4×4, niveau de risque **par cellule** (matrice) |
| `iso-27005` | ISO/IEC 27005 | vraisemblance × impact 5×5 (produit) |
| `generique` | Générique (aucune méthode) | probabilité × impact 5×5 (produit) |

> Le `slug` doit correspondre au `base` déclaré côté application dans la constante `TEMPLATES` de `app/risk-analysis-editor.html` (qui charge `../templates/<base>.<lang>.rae.json`).

## Structure d'un `spec`

`emit("slug", spec)` où `spec` a la forme :

```js
{
  meta:{
    title:                 T("fr","en","it"),
    description:           T("fr","en","it"),   // Markdown autorisé (**gras**, \n\n)
    methodology_reference: T("fr","en","it"),
  },
  grid:{
    vertical_axis:   { label:T(…), description:T(…), levels:LEVELS },  // = vraisemblance / probability
    horizontal_axis: { label:T(…), description:T(…), levels:LEVELS },  // = gravité / severity
    score: { method:"product" | "sum" | "matrix", matrix?:[[…]] },
    criticality_levels: CRIT_LEVELS,
  },
  fields:[ …champs personnalisés… ]   // optionnel
}
```

- `LEVELS` : tableau `{value, label:T(…), description:T(…)}`. Des barèmes réutilisables sont définis en constantes au début du fichier (ex. `VRAIS4`, `GRAV4_EBIOS`).
- `CRIT_LEVELS` : tableau `{code, label:T(…), score_min, score_max, color, acceptance, order, description:T(…)}`.
- `score.method` : `product` (P × G), `sum` (P + G) ou `matrix` (niveau défini case par case — fournir `matrix`).

### Champs personnalisés (`fields`)

Chaque champ :

```js
{
  code, target,               // target : "analysis" | "risk" | "measure" | "link"
  type,                       // "text" | "textarea" | "select" | "tags" | "progress" | "boolean" | "date" | …
  order, filterable?, multiple?,
  label: T("fr","en","it"),
  description?: T(…),          // aide en infobulle
  items?: [ … ],              // pour select / tags / checklist
  palette?, step?,            // pour progress
}
```

- Listes déroulantes (`select`) : `items:[ opt(code, T(…)), … ]`.
- Tags colorés (`tags`) : `items:[ tag(code, T(…), "#couleur"), … ]`.

## Helpers

| Helper | Rôle |
|---|---|
| `T(fr,en,it)` | fabrique un objet `{fr,en,it}`. |
| `pick(o, lang)` | extrait la langue voulue d'un objet `{fr,en,it}`, **repli sur `fr`** si absente. |
| `tag(code, label, color)` | item de champ `tags` (label = objet `T(…)`). |
| `opt(code, label)` | item de champ `select` (label = objet `T(…)`). |
| `resolve(spec, lang)` | transforme un `spec` en une analyse `.rae.json` pour une langue (grille + métadonnées en chaînes ; champs personnalisés conservés en `{fr,en,it}`). |
| `emit(slug, spec)` | appelle `resolve` pour chaque langue de `LANGS` et écrit les fichiers. |

## Modifier ou ajouter un modèle

- **Modifier** un texte, un barème, un champ : éditer le `spec` concerné (ou les constantes de barème partagées), puis relancer `node build-templates.js`.
- **Ajouter un modèle** : ajouter un appel `emit("nouveau-slug", { … })`, puis déclarer le `base` correspondant dans la constante `TEMPLATES` de l'application pour qu'il apparaisse sur l'écran d'accueil.
- **Ajouter une langue** : étendre `LANGS`, **et** ajouter la 4ᵉ valeur à chaque `T(fr,en,it)` (sinon `pick` retombe sur le français).

## Convention éditoriale

Les descriptions présentent les modèles comme des squelettes **inspirés de** ces méthodes, **à compléter** — jamais comme une implémentation complète ou conforme. Conserver ce ton (« inspiré de… », liste « À compléter… ») lors des ajouts.
