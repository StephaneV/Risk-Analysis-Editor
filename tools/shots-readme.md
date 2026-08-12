# Guide — `shots-readme.py`

Script de génération des **captures d'écran du README** (fichiers `docs/images/`).
Complément de [`shots-guide.py`](shots-guide.md), qui génère lui les captures du **guide utilisateur**.

## Ce que le script produit

Trois images, en **anglais** et **thème clair**, largeur 1180 px, densité ×2 :

| Fichier | Contenu | Démo utilisée |
|---|---|---|
| `docs/images/capture-trajectoire.png` | Matrices › Trajectoire, **curseur au milieu de la flèche du risque R1** (surlignée) + **infobulle du lien** visible | `demo-ebios-rm-information-system.rae.json` |
| `docs/images/capture-statistiques.png` | Onglet **Statistiques** (tableau de bord) | `demo-ebios-rm-information-system.rae.json` |
| `docs/images/capture-plan-echeancier.png` | **Plan d'action**, vue *échéancier* (Timeline) | `demo-ebios-rm-information-system.rae.json` |

> Le curseur de la souris n'est **pas** capturé par Playwright (rendu hors-écran). Le script injecte donc un **faux curseur** (une flèche SVG) au point survolé, et affiche l'infobulle du lien de façon **déterministe** (contenu reconstruit depuis `analyse`, libellés anglais en dur), plutôt que de dépendre d'un vrai survol souris.

## Prérequis

- **Python 3**
- **Playwright** + un navigateur Chromium (Microsoft **Edge** est utilisé par défaut, canal `msedge`) :
  ```bash
  pip install playwright
  ```
  L'app doit être **servie en HTTP(S)** : le script charge `app/risk-analysis-editor.html` et les fichiers de `examples/` via des requêtes réseau (le protocole `file://` ne convient pas).

## Utilisation

Depuis la **racine du dépôt** `Risk-Analysis-Editor` :

1. Servir le dépôt (dans un terminal) :
   ```bash
   python -m http.server 8799
   ```
2. Lancer le script en pointant vers ce serveur (dans un autre terminal) :
   ```bash
   # Linux / macOS / Git Bash
   SHOTS_ORIGIN="http://localhost:8799" python tools/shots-readme.py
   ```
   ```powershell
   # Windows PowerShell
   $env:SHOTS_ORIGIN="http://localhost:8799"; python tools/shots-readme.py
   ```

Sans `SHOTS_ORIGIN`, le script vise `http://localhost:8000`. Les images écrasent celles de `docs/images/`.

> Astuce (une commande, Git Bash) :
> ```bash
> python -m http.server 8799 & sleep 1 && SHOTS_ORIGIN="http://localhost:8799" python tools/shots-readme.py ; kill %1
> ```

## Personnalisation

Tout se règle en tête de `shots-readme.py` ou dans les trois fonctions `hero()`, `statistiques()`, `plan()` :

- **Risque survolé** sur la trajectoire : la constante `RID` dans `hero()` (par défaut `"R1"`). Le point survolé est le **milieu** de la flèche (moyenne des centres des deux pastilles du risque).
- **Fichiers de démo** : les URL passées à `page.goto(...)` dans chaque fonction (paramètre `?file=../examples/…`).
- **Langue / thème** : `locale="en-US"` et `color_scheme="light"` dans `ctx(...)`.
- **Cadrage** : largeur fixée à 1180 px ; la **hauteur du viewport** est le 2ᵉ argument de `ctx(browser, hauteur)` par capture (le rendu est pris en `full_page=False`, donc la hauteur découpe l'image).
- **Faux curseur** : la constante `CURSOR` (SVG). Le point de contact (« hotspot ») est le coin haut-gauche de la flèche ; l'offset de placement est réglé dans l'injection (`left: x-2, top: y-1`).
- **Position de l'infobulle** : `tip.style.left/top = (x + 16, y + 16)` dans le bloc d'affichage du tooltip.

## Après génération

- Vérifier visuellement les 3 images dans `docs/images/`.
- Les README (`README.md`, `README.fr.md`) référencent déjà ces trois fichiers ; aucun changement de texte n'est nécessaire si seuls les visuels sont mis à jour.
- Committer les images modifiées.

## Dépannage

- **`net::ERR_CONNECTION_REFUSED` / timeout** : le serveur HTTP n'est pas lancé, ou `SHOTS_ORIGIN` pointe vers le mauvais port. Vérifier `curl http://localhost:8799/app/risk-analysis-editor.html`.
- **`Executable doesn't exist` / navigateur introuvable** : installer Edge, ou remplacer `channel="msedge"` par `channel="chrome"`, ou installer les navigateurs Playwright (`python -m playwright install chromium`) et retirer l'argument `channel`.
- **Infobulle mal placée / hors cadre** : ajuster l'offset (`x + 16, y + 16`) ou augmenter la hauteur du viewport de `hero()`.
- **Curseur/infobulle sur la mauvaise flèche** : vérifier que le `RID` choisi est bien un risque **réduit** (il n'a une flèche que si sa cotation résiduelle diffère de l'initiale).
