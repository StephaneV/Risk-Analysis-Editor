# Stratégies de disposition — vue « Trajectoire »

Ce document décrit les **stratégies de disposition** de la vue **Trajectoire**, qui superpose sur une seule matrice la position **initiale** et la position **résiduelle** de chaque risque, reliées par une flèche.

La stratégie se choisit soit dans **Matrices › barre d'outils › Disposition** (quand la vue *Trajectoire* est active), soit dans **Paramètres › Affichage des matrices › Stratégie de disposition « Trajectoire »**. Elle est enregistrée dans le fichier `.rae.json` sous `extensions.display.trajectory_arrangement`.

> Pour la disposition des pastilles dans les matrices **Risque initial** / **Risque résiduel**, voir [strategies-disposition.md](strategies-disposition.md).

---

## Concepts communs

- **Jetons.** Chaque risque produit :
  - s'il a **bougé** entre l'initial et le résiduel : deux jetons — une **position initiale** (contour en **pointillé**) et une **position résiduelle** (contour **plein**) — reliés par une flèche ;
  - s'il **n'a pas bougé** : un seul jeton **« risque non réduit »** (couleur dédiée), sans flèche.
- **Flèche.** Une flèche blanche à tête va de la position initiale vers la position résiduelle. Au survol, elle s'épaissit et une infobulle affiche les **mesures de maîtrise liées** au risque (avec le tag coloré de leur statut).
- **Classement des flèches** (utilisé par la stratégie optimisée) :
  - **H** (horizontale) : même **probabilité**, la gravité change ;
  - **V** (verticale) : même **gravité**, la probabilité change ;
  - **D** (diagonale) : la probabilité **et** la gravité changent.
- **Pastille de référence.** 22 px de diamètre (`BASE_CHIP`) ; les pastilles rétrécissent (jusqu'à ~8 px) quand une case est chargée. `S` désigne la largeur d'une case en pixels.
- **Tri.** Les jetons d'une même case sont ordonnés par identifiant.
- **Légende.** Sous la matrice : niveaux de criticité **+** repères *Position initiale* / *Position résiduelle* / *Risque non réduit*.

---

## Les stratégies

### 1. Flèches droites optimisées (`grille_opt`) — *par défaut*

Objectif : des trajectoires **lisibles**, avec des flèches droites, sans croisement ni pastille posée sur une flèche.

Les jetons sont placés sur une **grille K×K** à l'intérieur de chaque case, puis un **optimiseur par recherche locale** (descente de coordonnées + redémarrages déterministes) cherche l'affectation des emplacements qui minimise une fonction de coût combinant plusieurs objectifs :

| Objectif | Traitement |
|---|---|
| **Flèches droites** | une flèche **H** est droite si ses deux extrémités partagent la même sous-ligne ; une flèche **V**, la même sous-colonne. Un écart est pénalisé. |
| **Pas de croisement** | chaque paire de flèches qui se croisent (ou se longent de trop près) est pénalisée. |
| **Pas de pastille sur une flèche** | une pastille trop proche d'une flèche qui n'est pas la sienne est pénalisée. |
| **Pas de superposition** | contrainte stricte : au plus un jeton par emplacement dans une case. |
| **Pastilles centrées** | le décentrage d'un jeton (distance au centre de sa case) est pénalisé. |
| **Flèches courtes** | la longueur de chaque flèche est pénalisée. |

Points clés de l'algorithme :

- La grille reçoit une **marge d'un emplacement** (K = besoin + 1, borné pour garder des pastilles ≥ ~9 px) : des emplacements peuvent ainsi **rester vides pour laisser passer une flèche**.
- La recherche part d'un placement central, puis chaque jeton **migre vers le meilleur emplacement libre** de sa case. S'y ajoute un mouvement de **couloir** : les deux extrémités d'une flèche droite se déplacent **ensemble** vers une sous-ligne/colonne libre, ce qui permet de **recentrer** un couloir sans casser l'alignement (impossible en déplaçant les extrémités une à une).
- Quelques **redémarrages déterministes** (mélange reproductible) évitent les minima locaux ; la meilleure configuration est retenue. Le résultat est **stable** d'un rendu à l'autre (pas d'aléa non reproductible).

C'est la stratégie recommandée, active par défaut.

### 2. Identique aux matrices Initial / Résiduel (`comme_matrices`)

Les jetons sont disposés dans chaque case **avec la même stratégie que les matrices Initial / Résiduel** (celle sélectionnée dans *Paramètres › Affichage › « Initial / Résiduel »*, voir [strategies-disposition.md](strategies-disposition.md)). Les flèches sont ensuite tracées entre les positions réelles des pastilles.

- Positions initiales, résiduelles et « non réduit » sont regroupées **par case**, puis placées selon la stratégie choisie (grille, rangée, amas, débordement « +N »…). Le badge **« +N »** de débordement est pris en charge.
- Aucune optimisation des flèches : elles peuvent se croiser ou passer sur des pastilles.

À utiliser pour une **cohérence visuelle** parfaite avec les deux matrices (mêmes positions de pastilles d'un affichage à l'autre).

### 3. Manuel — glisser-déposer (`manual`)

L'utilisateur **place lui-même** chaque jeton par glisser-déposer.

- Les positions s'aimantent sur une **sous-grille N×N** propre à chaque case (pas paramétrable dans *Paramètres › Pas de la grille de placement*, **5×5 par défaut**).
- Les positions **initiale** et **résiduelle** d'un risque sont **stockées séparément** dans le fichier, sous `extensions.placement[<idRisque>].initial` et `.residual` (`{col, row}`).
- Les jetons initiale et résiduelle se **déplacent indépendamment** ; un risque non réduit se déplace d'un seul bloc. Les flèches suivent les positions manuelles.
- Option **Afficher la grille de placement** pour visualiser les points d'accroche.

---

## Tableau récapitulatif

| Stratégie | Code (`trajectory_arrangement`) | Placement | Flèches droites | Évite croisements / pastilles sur flèche |
|---|---|---|---|---|
| Flèches droites optimisées | `optimized_grid` | Grille K×K + optimiseur | Oui (H/V) | **Oui** |
| Identique aux matrices | `like_matrices` | Stratégie des matrices Initial / Résiduel | Selon la stratégie | Non |
| Manuel | `manual` | Libre (snap N×N), positions enregistrées | À la main | À la main |

> **Note sur les noms.** Les codes ci-dessus (`optimized_grid`, `like_matrices`, `manual`) sont les valeurs stockées dans le fichier `.rae.json` **et** utilisées telles quelles en interne (mêmes clés anglaises que le fichier, aucune conversion). Les anciennes valeurs (`grid`, `optimized`…) sont acceptées et retombent sur la stratégie optimisée.
