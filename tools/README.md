# Outils — captures d'écran

Scripts de génération des **captures d'écran** de la documentation (dossier `docs/images/`), via
Playwright. Ils pilotent l'application réelle (`app/risk-analysis-editor.html`) servie en local et
enregistrent les PNG utilisés par le guide et les README.

| Fichier | Rôle | Sorties |
|---|---|---|
| `shots.py` | Captures du **guide utilisateur** (démo AIPD, FR, thème clair, 1280 px). | `docs/images/guide-*.png` |
| `shots-readme.py` | Captures des **README** (démo EBIOS RM, EN, thème clair, 1180 px, ×2). | `docs/images/capture-*.png` |
| `guide-shots-readme.md` | Documentation détaillée de `shots-readme.py`. | — |

## Prérequis (une fois)

- **Python 3** avec :
  - `playwright` + le canal **Edge** : `pip install playwright` puis `python -m playwright install msedge`
  - `Pillow` (traitement d'image) : `pip install pillow`
- Un **serveur statique local** servant la racine du dépôt (les scripts chargent
  `http://localhost:4599/app/risk-analysis-editor.html`).

> **Mode fenêtré (headed).** `shots.py` lance le navigateur avec `headless=False` : en mode *headless*,
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
python tools/shots.py                                   # toutes les captures du guide
SHOTS_ONLY=guide-06-champ-editeur python tools/shots.py # une seule (liste séparée par des virgules)
python tools/shots-readme.py                            # captures des README
```

## Variables d'environnement

| Variable | Effet |
|---|---|
| `SHOTS_ORIGIN` | Origine du serveur statique (défaut `http://localhost:4599`). |
| `SHOTS_ONLY` | (`shots.py`) Ne régénérer que la/les capture(s) nommée(s), séparées par des virgules. |

Les captures dépassant `MAX_H` (1400 px) sont **recadrées** avec un léger fondu en bas pour signaler
que le contenu se poursuit.
