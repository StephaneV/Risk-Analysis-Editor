# Modèles de rapport Word

Modèles `.docx` pour le **générateur de rapports à partir d'un modèle Word** de
[Risk Analysis Editor](https://github.com/StephaneV/Risk-Analysis-Editor) : un document Word porteur de
**balises** `{{ … }}` que l'application remplace par les valeurs, tableaux, matrices et radars de
l'analyse courante.

## Utilisation

Dans l'application : **Fichier › Exporter avec un modèle Word…**, choisissez l'un des `.docx` ci-dessous,
puis ouvrez le document généré dans Word.

## Contenu

| Fichier | Rôle |
|---|---|
| `modele-rapport-classique.docx` | Rapport complet : présentation, matrices initiale/résiduelle/trajectoire, grille de cotation, registre des risques, tableau des mesures (boucle de ligne), détail par risque avec sous-boucle, radar. |
| `modele-rapport-eclate-par-categorie.docx` | Synthèse générale puis **un chapitre par catégorie de risque** (matrice et tableau filtrés automatiquement par catégorie). |
| `…-annote.docx` | Mêmes modèles **annotés** (notes explicatives grises) pour comprendre la syntaxe. ⚠️ Ne pas utiliser tels quels : les notes apparaîtraient dans le rapport. |
| [`catalogue-mots-cles-rapport.md`](catalogue-mots-cles-rapport.md) | **Référence des mots-clés** (valeurs, blocs, boucles, filtres, échappement) pour rédiger vos propres modèles. |
| `build-word-templates.js` | Script de **génération** de ces `.docx` (reproductible). |

Spécification complète du langage de gabarit :
[`specs/SPEC-rapport-modele-word.md`](../specs/SPEC-rapport-modele-word.md).

## Langue

Le texte fixe des modèles (titres de sections, notes) est en **français** ; les **valeurs** des balises
se rendent dans la **langue de l'analyse**. Des variantes anglaise/italienne pourront être ajoutées.

## Régénérer les modèles

```bash
npm install docx        # dépendance de génération (non versionnée)
node word-templates/build-word-templates.js
```
Produit les quatre `.docx` (propres + annotés). Pour écrire ailleurs : `OUT=<dossier> node …`.
