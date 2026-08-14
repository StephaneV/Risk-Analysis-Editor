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
| `modele-rapport-classique.docx` | **Démonstration** : présentation, matrices initiale/résiduelle/trajectoire, grille, registre des risques, tableau des mesures (boucle de ligne), détail par risque avec sous-boucle, radar. |
| `modele-rapport-eclate-par-categorie.docx` | **Démonstration** : synthèse générale puis **un chapitre par catégorie de risque** (matrice et tableau filtrés automatiquement par catégorie). |
| `modele-referentiels.docx` | **Référentiels de l'analyse** : grille de cotation (méthode, échelles de vraisemblance/gravité, niveaux de criticité) et **champs personnalisés** (tableau récapitulatif + détail des caractéristiques et des valeurs possibles). |
| `modele-rapport-complet-classique.docx` | **Reproduction fidèle** du rapport « Exporter en Word » (mode classique) : page de garde + logo, en-tête/pied, table des matières, métadonnées, présentation, statistiques (synthèse + répartition), grille, niveaux, référentiels/légendes, matrices, radar, registre, détails risques/mesures/liens, plan d'action. |
| `modele-rapport-complet-par-categorie.docx` | Idem en **rapport éclaté par catégorie** : zone d'introduction, un chapitre par catégorie (sections filtrées), puis annexe. |
| `modele-rapport-complet-par-risque.docx` | Idem en **rapport éclaté par risque** : un chapitre par risque (détail + trajectoire + mesures), puis annexe. |
| `…-annote.docx` | Variantes **annotées** (notes explicatives grises) des modèles de démonstration. ⚠️ Ne pas utiliser telles quelles : les notes apparaîtraient dans le rapport. |
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
Produit les six `.docx` de **démonstration** et de **référentiels** (propres + annotés). Pour écrire
ailleurs : `OUT=<dossier> node …`.

Les modèles `modele-rapport-complet-*.docx` (reproductions fidèles du rapport « Exporter en Word ») sont
issus de générateurs dédiés, distincts de `build-word-templates.js`.
