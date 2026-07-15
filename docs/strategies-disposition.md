# Stratégies de disposition des pastilles — matrices Initial / Résiduel

Ce document décrit le fonctionnement des **stratégies de disposition** utilisées pour placer les pastilles de risque dans les cases des matrices **Risque initial (brut)** et **Risque résiduel (net)**.

La stratégie se choisit soit dans **Matrices › barre d'outils › Disposition**, soit dans **Paramètres › Affichage des matrices › Stratégie de disposition « Initial / Résiduel »**. Elle est enregistrée dans le fichier `.rae.json` sous `extensions.display.arrangement`.

> La vue **Trajectoire** dispose de ses propres stratégies (voir [strategies-trajectoire.md](strategies-trajectoire.md)) ; l'option « Identique aux matrices Initial / Résiduel » y réutilise toutefois la stratégie décrite ici.

---

## Concepts communs

- **Pastille** : un pastille par risque, portant son identifiant (le préfixe `R` est retiré à l'affichage : `R1` → `1`). Une infobulle donne le libellé, la catégorie, la position et le score.
- **Tri** : dans toutes les stratégies automatiques, les pastilles d'une même case sont triées **par identifiant** — d'abord par la partie numérique, puis alphabétiquement (`R2` avant `R10`).
- **Déclenchement** : la disposition ne joue que lorsqu'une case contient **plusieurs** risques. Un risque seul est simplement centré.
- **Taille de référence** : une pastille mesure **22 px** de diamètre (`BASE_CHIP`), avec un espacement de **3 px** entre pastilles (soit un pas de **25 px**). Selon la stratégie, les pastilles **rétrécissent** pour tenir dans la case (jusqu'à 8 px minimum) — sauf la stratégie *Débordement*, qui les garde à taille pleine et masque le surplus.
- **`S`** désigne dans la suite la **largeur de la case** en pixels (les cases sont carrées). Elle dépend de la taille de la grille (nombre de niveaux), de l'espacement des cases et de la largeur d'affichage.

---

## Les stratégies

### 1. Grille carrée centrée (`grid`) — *par défaut*

Les pastilles sont réparties sur une grille aussi **carrée que possible**, centrée dans la case.

- Nombre de colonnes : `C = ⌈√N⌉` (N = nombre de pastilles) ; nombre de lignes : `R = ⌈N/C⌉`.
- Remplissage **ligne par ligne**, de gauche à droite.
- Les pastilles rétrécissent pour tenir : `taille = ⌊(S − 6 − (d−1)×3) / d⌋` où `d = max(C, R)`, bornée entre 8 px et 22 px.

C'est le meilleur compromis général : compact et lisible quel que soit le nombre de risques.

### 2. Gauche → droite, puis haut → bas (`row_col`)

Grille remplie **par lignes** : on remplit une ligne de gauche à droite, puis on passe à la ligne suivante.

- Nombre de colonnes : autant que la case peut en contenir à taille pleine — `C = max(1, min(N, ⌊(S − 3) / 25⌋))` ; lignes : `R = ⌈N/C⌉`.
- Sens de remplissage : horizontal d'abord (`grid-auto-flow: row`).
- Même règle de rétrécissement que la grille carrée.

À privilégier quand on veut un remplissage « lecture naturelle » (comme un texte).

### 3. Haut → bas, puis gauche → droite (`col_row`)

Identique à la précédente, mais remplie **par colonnes** : on remplit une colonne de haut en bas, puis on passe à la colonne suivante (`grid-auto-flow: column`).

- Le nombre de lignes `R` et de colonnes `C` est calculé comme pour `row_col`, mais le parcours est vertical d'abord.

### 4. Amas centré / spirale (`cluster`)

Placement **libre, organique** : les pastilles forment un amas compact au centre de la case.

- Positions initiales sur une **spirale à angle d'or** (137,5°).
- Puis **200 itérations** d'un petit moteur physique : chaque pastille est attirée vers le centre (facteur 0,04) et **repoussée** par ses voisines (distance minimale = taille + 3 px), le tout borné à l'intérieur de la case.
- Taille des pastilles ajustée à `≈ ⌈√N⌉` pastilles par côté, avec la même borne 8–22 px.

Rendu plus « naturel » qu'une grille, utile pour un effet visuel de regroupement.

### 5. Rangée unique horizontale (`row`)

Toutes les pastilles sur **une seule ligne**, centrée horizontalement.

- Taille : `⌊(S − 6 − (N−1)×2) / N⌋`, bornée entre 8 px et 22 px (espacement de 2 px).
- Au-delà de quelques risques, les pastilles deviennent très petites : à réserver aux cases peu peuplées.

### 6. Colonne unique verticale (`column`)

Identique à la rangée, mais sur **une seule colonne** verticale, centrée.

### 7. Débordement « +N » (`overflow`)

Affiche autant de pastilles **à taille pleine** que la case peut en contenir, puis condense le reste dans un badge **« +N »** (dont l'infobulle liste les risques masqués).

Contrairement aux autres stratégies, **les pastilles ne rétrécissent pas** : la lisibilité est préservée, au prix du masquage du surplus.

**Il n'y a pas de seuil fixe** : il est **calculé dynamiquement selon la taille de la case**.

```
per = 22 + 3 = 25 px          (pastille de 22 px + espacement de 3 px)
dim = max(1, ⌊(S − 3) / 25⌋)   (S = largeur de la case en px)
cap = dim × dim                ← le seuil
```

- Si le nombre de pastilles **≤ cap** → toutes affichées (sur `⌈√(min(N, cap))⌉` colonnes).
- Si **> cap** → on affiche **cap − 1** pastilles + un badge **« +N »** avec `N = total − (cap − 1)`.

Le seuil `cap` correspond au nombre de pastilles de 22 px qui tiennent dans une grille carrée `dim × dim` à l'intérieur de la case. Ordres de grandeur :

| Largeur de case `S` | `dim` | **`cap` (seuil)** |
|---|---|---|
| ~65 px | 2 | 4 |
| ~90 px | 3 | 9 |
| ~115 px | 4 | 16 |

> La même formule est utilisée pour le badge « +N » de la vue **Trajectoire**.

### 8. Manuel — glisser-déposer (`manual`)

L'utilisateur **place lui-même** chaque pastille par glisser-déposer.

- Les positions s'aimantent sur une **sous-grille N×N** propre à chaque case (pas de la grille paramétrable dans **Paramètres › Pas de la grille de placement**, **5×5 par défaut**).
- À l'initialisation, les pastilles sans position sont réparties **sans superposition**, au plus près du centre.
- Les positions sont **enregistrées dans le fichier** sous `extensions.placement[<idRisque>].initial` / `.residual` (`{col, row}`), séparément pour la matrice initiale et la matrice résiduelle.
- Option **Afficher la grille de placement** (Paramètres, ou case à cocher sous les matrices) pour visualiser les points d'accroche.
- La transposition des axes transpose aussi les placements manuels (`col ↔ row`).

---

## Tableau récapitulatif

| Stratégie | Code (`arrangement`) | Agencement | Pastilles réduites ? | Surplus masqué ? |
|---|---|---|---|---|
| Grille carrée centrée | `grid` | Grille ≈ carrée, par lignes | Oui | Non |
| Gauche → droite, puis haut → bas | `row_col` | Grille, remplissage horizontal | Oui | Non |
| Haut → bas, puis gauche → droite | `col_row` | Grille, remplissage vertical | Oui | Non |
| Amas centré / spirale | `cluster` | Amas libre (physique) | Oui | Non |
| Rangée unique | `row` | Une ligne | Oui | Non |
| Colonne unique | `column` | Une colonne | Oui | Non |
| Débordement « +N » | `overflow` | Grille à taille pleine + badge | **Non** | **Oui** (« +N ») |
| Manuel | `manual` | Positions libres (snap N×N) | Oui | Non |

> **Note sur les noms.** Les codes ci-dessus (`grid`, `row_col`, `cluster`, `overflow`, `manual`…) sont les valeurs stockées dans le fichier `.rae.json` (`extensions.display.arrangement`) **et** utilisées telles quelles en interne : le modèle interne emploie les mêmes clés anglaises que le fichier (aucune conversion).
