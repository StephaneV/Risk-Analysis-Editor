# Guide — `shots-guide.py`

Script de génération des **captures d'écran du guide utilisateur** (fichiers `docs/images/guide-*.png`),
via Playwright. Il pilote l'application réelle (`app/risk-analysis-editor.html`) servie en local et
enregistre les PNG utilisés par `docs/guide-utilisateur.md`.

Complément de [`shots-readme.py`](shots-readme.md), qui génère lui les captures des README.

## Ce que le script produit

Les captures du guide, en **français**, **thème clair**, viewport **1280 px**, à partir de la démo
AIPD (`examples/demo-aipd-sst.rae.json`). La liste des captures (nom, onglet, préparation JS,
hauteur) est définie dans la constante `SHOTS` en tête de script.

Les captures dépassant `MAX_H` (1400 px) sont **recadrées** avec un léger **fondu** en bas (hauteur
`FADE`) pour signaler que le contenu se poursuit.

## Prérequis

- **Python 3** avec :
  - `playwright` + le canal **Edge** : `pip install playwright` puis `python -m playwright install msedge`
  - `Pillow` (traitement d'image) : `pip install pillow`
- Un **serveur statique local** servant la racine du dépôt (le script charge
  `http://localhost:4599/app/risk-analysis-editor.html`).

> **Mode fenêtré (headed).** `shots-guide.py` lance le navigateur avec `headless=False` : en mode *headless*,
> Chromium ne rend **aucune barre de défilement** (cf. [playwright#5778](https://github.com/microsoft/playwright/issues/5778)),
> et les modales scrollables apparaissaient sans barre. Un environnement graphique (session de bureau)
> est donc nécessaire.

## Utilisation

Toutes les commandes se lancent **depuis la racine du dépôt** (les chemins `docs/images/`,
`../examples/…` y sont relatifs).

```bash
# 1) démarrer un serveur statique (dans un terminal à part), à la racine du dépôt
python -m http.server 4599 --bind 127.0.0.1

# 2) générer les captures
python tools/shots-guide.py                                   # toutes les captures du guide
SHOTS_ONLY=guide-06-champ-editeur python tools/shots-guide.py # une seule (liste séparée par des virgules)
```

## Variables d'environnement

| Variable | Effet |
|---|---|
| `SHOTS_ORIGIN` | Origine du serveur statique (défaut `http://localhost:4599`). |
| `SHOTS_ONLY` | Ne régénérer que la/les capture(s) nommée(s), séparées par des virgules. |

## Personnalisation

- **Liste des captures** : la constante `SHOTS` (`nom`, suffixe d'URL, préparation JS après
  chargement, pleine page ?, hauteur du viewport).
- **Démo utilisée** : la constante `DEMO` (paramètre `?file=../examples/…&lang=fr`).
- **Recadrage / fondu** : les constantes `MAX_H` (1400 px) et `FADE` (120 px).
