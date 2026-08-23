# Fixtures de test

Jeux de données **versionnés** utilisés par les suites. Les analyses `.rae.json` valides sont
chargées via `applyLoadedData` ; les malformées servent à tester le chemin d'erreur.

## `analyses/` — analyses fictives

| Fichier | Origine | Ce qu'elle couvre |
|---|---|---|
| `vide.rae.json` | généré | analyse vierge (grille par défaut 5×5, 0 risque) |
| `minimale.rae.json` | généré | 1 risque + 1 mesure + 1 lien — cas le plus simple |
| `ebios.rae.json` | examples (fr) | EBIOS RM, grille **4×4**, 12 risques, champs perso de cotation |
| `ebios-objets.rae.json` | examples (fr) | idem + **objets & références** |
| `ebios-en.rae.json` | examples (en) | i18n **anglais** (`language:"en"`) |
| `dpia-en.rae.json` | examples (en) | volet AIPD/PIA, anglais |
| `aipd.rae.json` | examples (fr) | AIPD/PIA santé au travail |
| `aipd-objets.rae.json` | examples (fr) | AIPD + objets |
| `si.rae.json` | travaux | jeu « Système d'information » (accompagne les CSV d'import) |
| `tous-types-champs.rae.json` | généré | **kitchen-sink** : un champ perso de **chaque** type (18) sur les risques, un champ de cotation, un champ d'analyse, un type d'objet avec attributs (texte/échelle/calculé/couleur) + 2 instances, valeurs renseignées (dont image data-URI, tags, référence, calculé, traversée de référence) |
| `titre-long.rae.json` | généré | titre d'analyse volontairement très long (retour à la ligne dans les matrices) |
| `volumineuse.rae.json` | généré | 60 risques / 20 mesures (performance, débordement de listes) |
| `grille-3x3.rae.json` | généré | grille **3×3** (criticité sur 1..9) |
| `grille-5x5.rae.json` | généré | grille **5×5** (par défaut) |
| `grille-transposee.rae.json` | généré | ebios avec **axes échangés** (`transposeAxes`) |

### `analyses/malformes/` — chemin d'erreur
| Fichier | Défaut testé |
|---|---|
| `champs-manquants.rae.json` | structure incomplète (grille + risques absents) → `validateStructure` renvoie une erreur |
| `format-invalide.rae.json` | objet sans le bon `format` → rejet |
| `json-casse.txt` | JSON syntaxiquement invalide → erreur du lecteur de fichier |

## `csv/` — imports
`analyse-si-risks.csv`, `analyse-si-measures.csv`, `analyse-si-links.csv` — accompagnent `si.rae.json`.

## `word-templates/` — gabarits `.docx`
Gabarits repris de `travaux/` : boucles (paragraphes/tableau), bloc `{{ table }}`, conditions,
statistiques, dimensions d'image, objets génériques. Sous-dossier `erreurs/` : **31 gabarits** de cas
d'erreur (`e01`…`e30` + `e27b`) pour vérifier les messages non bloquants du moteur de gabarit.

## `generators/` — (re)génération
`make_fixtures.py` régénère les analyses **synthétiques** (auto-validées : chaque fixture est rechargée
et contrôlée sans erreur console). Les fixtures reprises d'`examples/`/`travaux/` sont, elles, copiées
telles quelles.

```bash
python tests/fixtures/generators/make_fixtures.py
```
