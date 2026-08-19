# Modèles de rapport Word

Modèles `.docx` pour le **générateur de rapports à partir d'un modèle Word** de
[Risk Analysis Editor](https://github.com/StephaneV/Risk-Analysis-Editor) : un document Word porteur de
**balises** `{{ … }}` que l'application remplace par les valeurs, tableaux, matrices et radars de
l'analyse courante.

## Utilisation

Dans l'application : **Fichier › Exporter avec un modèle Word…**, choisissez l'un des `.docx` ci-dessous,
puis ouvrez le document généré dans Word.

**Pour rédiger votre propre modèle**, commencez par le
[**guide de rédaction**](guide-redaction-modeles.md) (tutoriel pas à pas), puis gardez le
[catalogue des mots-clés](catalogue-mots-cles-rapport.md) sous la main comme référence.

## Contenu

| Fichier | Rôle |
|---|---|
| `modele-rapport-classique.docx` | **Démonstration** : présentation, matrices initiale/résiduelle/trajectoire, grille, registre des risques, tableau des mesures (boucle de ligne), détail par risque avec sous-boucle, radar. |
| `modele-rapport-eclate-par-categorie.docx` | **Démonstration** : synthèse générale puis **un chapitre par catégorie de risque** (matrice et tableau filtrés automatiquement par catégorie). |
| `modele-referentiels.docx` | **Référentiels de l'analyse** : grille de cotation (méthode, échelles de vraisemblance/gravité, niveaux de criticité) et **champs personnalisés** (tableau récapitulatif + détail des caractéristiques et des valeurs possibles). |
| `modele-tableau-de-bord.docx` | **Tableau de bord** (v2) : tuiles clés et couverture, **graphiques** de répartition (criticité, catégorie, statut des mesures) et sections **conditionnelles** `{{#if}}` / `{{#unless}}` (alerte mesures en retard, points de vigilance). |
| `modele-rapport-complet-classique.docx` | **Reproduction fidèle** du rapport « Exporter en Word » (mode classique) : page de garde + logo, en-tête/pied, table des matières, métadonnées, présentation, statistiques (synthèse + répartition), grille, niveaux, référentiels/légendes, matrices, radar, registre, détails risques/mesures/liens, plan d'action. |
| `modele-rapport-complet-par-categorie.docx` | Idem en **rapport éclaté par catégorie** : zone d'introduction, un chapitre par catégorie (sections filtrées), puis annexe. |
| `modele-rapport-complet-par-risque.docx` | Idem en **rapport éclaté par risque** : un chapitre par risque (détail + trajectoire + mesures), puis annexe. |
| `modele-rapport-complet-classique-objets.docx` | **Complet classique + objets** : idem classique, avec une section **« Objets »** — inventaire **agnostique** (tous les objets, tous les attributs, références déréférencées), sans coder le schéma. |
| `modele-rapport-complet-par-categorie-objets.docx` | **Complet par catégorie + objets** : idem éclaté par catégorie, avec l'inventaire des objets en **annexe**. |
| `modele-rapport-complet-par-risque-objets.docx` | **Complet par risque + objets** : idem éclaté par risque, avec l'inventaire des objets en **annexe**. |
| `modele-referentiels-objets.docx` | **Référentiels + objets** : idem référentiels, avec le **schéma des types d'objets** (types, attributs) et l'**inventaire** des instances. |
| `modele-tableau-de-bord-objets.docx` | **Tableau de bord + objets** : idem tableau de bord, avec la **répartition des objets par type** (`{{ stat type="objets" }}`). |
| `…-annote.docx` | Variantes **annotées** (notes explicatives grises) des modèles de démonstration. ⚠️ Ne pas utiliser telles quelles : les notes apparaîtraient dans le rapport. |
| [`guide-redaction-modeles.md`](guide-redaction-modeles.md) | **Guide de rédaction** (tutoriel pas à pas) pour créer votre propre modèle. |
| [`catalogue-mots-cles-rapport.md`](catalogue-mots-cles-rapport.md) | **Référence des mots-clés** (valeurs, blocs, boucles, filtres, échappement). |
| `build-word-templates.js` | Générateur des modèles de **démonstration** (classique, éclaté, référentiels, tableau de bord) — propres + annotés — **et** des variantes `…-objets` de référentiels et tableau de bord. |
| `build-rapport-complet-classique.js` | Générateur de `modele-rapport-complet-classique.docx` **et** `…-classique-objets.docx`. |
| `build-rapport-complet-eclate.js` | Générateur de `modele-rapport-complet-par-{categorie,risque}.docx` **et** de leurs variantes `…-objets.docx`. |
| `sections-objets.js` | Module partagé : sections **objets agnostiques** (schéma des types, inventaire, répartition) insérées dans les variantes `-objets`. |

Spécification complète du langage de gabarit :
[`specs/SPEC-rapport-modele-word.md`](../specs/SPEC-rapport-modele-word.md).

## Langue

Le texte fixe des modèles (titres de sections, notes) est en **français** ; les **valeurs** des balises
se rendent dans la **langue de l'analyse**. Des variantes anglaise/italienne pourront être ajoutées.

## Régénérer les modèles

```bash
npm install docx        # dépendance de génération (non versionnée), une fois
node build-word-templates.js              # démonstration + référentiels + tableau de bord (propres + annotés)
node build-rapport-complet-classique.js   # modele-rapport-complet-classique.docx
node build-rapport-complet-eclate.js      # modele-rapport-complet-par-{categorie,risque}.docx
```
Chaque script écrit dans ce dossier (ou dans `$OUT` si défini : `OUT=<dossier> node …`). Les trois
`.docx` **complets** sont des reproductions fidèles du rapport « Exporter en Word » ; les autres sont des
modèles de **démonstration** du langage de gabarit.
