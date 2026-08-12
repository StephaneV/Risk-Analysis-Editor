# `embed-templates.py` — embarquer les modèles dans l'application

Embarque le contenu des **modèles méthodologiques** (`templates/*.template.<lang>.rae.json`)
directement dans le fichier `app/risk-analysis-editor.html`, afin que l'application soit
**autonome** : les modèles proposés sur l'écran d'accueil s'ouvrent alors **même en `file://`**
(double-clic), sans avoir à distribuer le dossier `templates/` à côté du HTML.

## Ce que fait le script

1. Lit tous les fichiers `templates/*.template.<lang>.rae.json` (langues `fr`, `en`, `it`).
2. Les regroupe par **base** (ex. `ebios-rm.template`) puis par **langue**.
3. Sérialise le tout en **JSON minifié** (clés triées, sans espaces).
4. Réécrit le bloc `const TEMPLATE_DATA={…};` dans l'application, **entre les marqueurs** :

   ```js
   /*__TEMPLATES_DATA_START__*/
   const TEMPLATE_DATA={…};
   /*__TEMPLATES_DATA_END__*/
   ```

Seul le contenu **entre les marqueurs** est remplacé ; le reste du fichier n'est pas touché.
Côté application, [`openTemplate()`](../app/risk-analysis-editor.html) lit d'abord
`TEMPLATE_DATA[base][lang]` (cloné avant chargement, car `applyLoadedData`/`normalize`
modifient la donnée) et **retombe** sur la lecture du fichier voisin `templates/…` en secours.

## Quand le relancer

**Après toute modification des modèles** dans `templates/`. Le flux complet est :

```bash
# 1) (re)générer les fichiers de modèles depuis leurs spécifications
node templates/build-templates.js

# 2) ré-embarquer le résultat dans l'application
python tools/embed-templates.py
```

> ⚠️ La donnée embarquée est une **copie**. Si l'on édite `templates/*.rae.json` sans relancer
> `embed-templates.py`, l'application continue de servir l'**ancienne** version embarquée
> (le fichier voisin n'est lu qu'en secours, quand la base est absente de `TEMPLATE_DATA`).

## Utilisation

Depuis la **racine du dépôt** (les chemins sont résolus par rapport à l'emplacement du script) :

```bash
python tools/embed-templates.py
```

Sortie typique :

```
Embarqué : 4 modèles (12 fichiers), 138027 octets de données.
```

Le script **avertit** si une base ne possède pas les trois langues attendues.

## Prérequis

- **Python 3** (bibliothèque standard uniquement : `json`, `os`, `re`, `sys` — aucune dépendance).

## Détails

| Élément | Valeur |
|---|---|
| Source | `templates/*.template.<lang>.rae.json` |
| Cible | `app/risk-analysis-editor.html` (entre les marqueurs `__TEMPLATES_DATA__`) |
| Langues | `fr`, `en`, `it` |
| Forme | `{ "<base>": { "fr": {…}, "en": {…}, "it": {…} }, … }`, JSON minifié |
| Poids | ~138 Ko de données ajoutées à l'application |

Chaque modèle porte `metadata.kind="template"` ; à l'ouverture, l'application retire ce marqueur,
ne relie pas de fichier et démarre une **nouvelle analyse** (voir `applyLoadedData`).
