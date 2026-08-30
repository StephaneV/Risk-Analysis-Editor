# SPEC — Vues des registres (tableaux larges)

> Statut : **validé (Proposition B)** — spécification d'implémentation.
> Concerne l'affichage et l'ergonomie des **registres tabulaires** : Risques, Mesures,
> Liens, et **Objets** (une table par type d'objet). Objectif : rester lisible et
> navigable quand il y a beaucoup de colonnes.

## 1. Objet & périmètre

Un registre peut être affiché selon **trois vues**, avec un **cadre figé**, une **densité**
réglable et une option **pleine largeur**. Le cœur du dispositif est le **placement des
colonnes** en trois états (*En ligne / En détail / Masqué*), qui pilote à la fois la vue
tableau et la vue maître·détail.

Tables concernées : `risks`, `measures`, `links`, et `objects.<type>` (chaque type d'objet
a sa propre configuration). Les mécanismes existants (ordre des colonnes par glisser‑déposer,
tri par clic sur l'en‑tête, glisser‑ligne, sélecteur ⚙, flag « Masquer en tableau ») sont
**conservés** et étendus, jamais remplacés.

## 2. Les trois vues

- **Tableau** — la vue tableur actuelle (toutes les colonnes non masquées, défilement).
- **Maître·détail** — quelques **colonnes clés** en ligne + un **panneau de détail** qui se
  déplie sous la ligne au clic (les champs relégués au détail).
- **Cartes** — chaque instance en fiche (titre + paires libellé/valeur + badges), lecture aérée.

Un **sélecteur de vue** (segmented control) dans la barre d'outils du registre bascule entre
les trois. Le choix est **mémorisé par table** (voir §9). Défaut : **Tableau** (comportement
actuel inchangé) ; le maître·détail est opt‑in par table.

## 3. Cadre figé & densité (piste 1)

Dans les vues **Tableau** et **Maître·détail** :

- **En‑tête figé** — la ligne d'en‑tête reste visible au défilement vertical (`position:sticky; top:0`).
- **Colonne ID figée** — la 1re colonne (ID, épinglée `pinned:"first"`) reste visible au
  défilement horizontal (`position:sticky; left:0`). **Seul l'ID** est figé à gauche.
- **Colonne Actions figée** — la dernière colonne (actions, `pinned:"last"`) reste à droite
  (`position:sticky; right:0`).
- **Ombres de bord** — un liseré/ombre discret sur le bord interne des colonnes figées
  signale qu'il y a du contenu masqué (uniquement quand un débordement existe).
- Les cellules figées ont un **fond opaque** (token de surface) pour couvrir le contenu qui défile.

**Densité** — un contrôle (Confortable / Compact / Dense) applique une classe sur la table
(`compact`, `dense`) qui réduit le `padding` et la taille de police. Défaut : **Confortable**.
Mémorisée par table.

Contraintes de largeur : les cellules gardent leur dimensionnement au contenu ; l'écrêtage
(`cell-clip`, ellipsis + loupe) déjà en place reste actif pour les textes longs en vue Tableau.

## 4. Placement des colonnes : trois états

Chaque colonne d'une table a un **placement** :

| Placement | Vue Maître·détail | Vue Tableau |
|---|---|---|
| **En ligne** | dans la ligne compacte | colonne visible |
| **En détail** | dans le panneau déplié | colonne visible (secondaire) |
| **Masqué** | nulle part | nulle part |

« En ligne » vs « En détail » est un **point de bascule de priorité** : le même réglage sert
aux deux vues (en Tableau, les colonnes « en détail » sont simplement des colonnes visibles
placées après les colonnes « en ligne » ; en Maître·détail, elles descendent au tiroir).
« Masqué » ré‑emploie le mécanisme existant `hide_table`.

### 4.1 Réglage — sélecteur ⚙ Colonnes enrichi

Le panneau ⚙ existant gagne, **par colonne**, un contrôle **3 états** (En ligne / En détail /
Masqué) à la place de la case visible/masqué, conservant le **glisser‑déposer d'ordre** (⠿) et
les **préréglages** (jeux de colonnes en un clic).

### 4.2 Colonnes verrouillées

Toujours **En ligne**, non déplaçables vers le détail ni masquables :
- la colonne **ID** (`pinned:"first"`),
- l'**attribut de libellé** (`name_attr` d'un type d'objet ; pour risks/measures : le libellé),
- la colonne **Actions** (`pinned:"last"`).

### 4.3 Défauts par type de champ (zéro configuration)

Au premier affichage, répartition automatique :
- **En ligne** : ID, libellé, `select`, `scale`, `boolean`, `reference` (mono‑valeur),
  et les valeurs à badge (statut, criticité, niveau…).
- **En détail** : `text`, `textarea`, `computed` à résultat `text` (verbeux).
- **Masqué** : rien par défaut (hors champs déjà marqués `hide_table`).

L'utilisateur peut tout redéfinir ; ses choix priment sur les défauts.

## 5. Le panneau de détail (ligne dépliée)

- Contenu : grille **libellé → valeur** des colonnes **En détail**, **dans l'ordre des colonnes**.
- **Texte complet** (pas d'écrêtage) et **Markdown rendu** (couleur/surlignage/gras…),
  cohérent avec l'affichage riche des champs texte/textarea/calculé‑texte.
- Un tiroir ouvert **reste rattaché à sa ligne** lors d'un tri.
- **Champs vides** : masqués du tiroir par défaut (option `show_empty_detail`, à confirmer),
  pour ne pas l'encombrer.
- Le dépliage est piloté par un **chevron** dans la 1re cellule ; l'état déplié n'est pas persisté
  (repart replié à l'ouverture de la vue).

## 6. Vue cartes

- Une **grille de fiches** ; chaque fiche : en‑tête (ID + libellé + actions) puis les champs
  **En ligne** en paires, plus un extrait de description si présent.
- Pas d'en‑têtes → tri via le **menu « Trier par »** (§8) ; l'ordre des champs suit le réglage
  des colonnes.

## 7. Pleine largeur (piste 5)

- **Option d'affichage** retirant la largeur maximale du contenu, pour exploiter les grands
  écrans. **Mémorisée** (globale ou par table — voir §9), **+ bouton bascule dans l'en‑tête**
  de l'application pour le confort.
- **Pas** de bascule automatique selon la fenêtre (imprévisible ; nuit à la longueur de ligne
  des vues de lecture). S'applique de préférence aux **vues registres**.

## 8. Tri & réordonnancement (préservés)

- **Glisser‑déposer des colonnes** — conservé partout où il y a des en‑têtes (Tableau ; colonnes
  **En ligne** du Maître·détail). ID/Actions restent épinglés (non déplaçables), comme aujourd'hui.
- **Tri par clic sur l'en‑tête** — conservé sur toute colonne à en‑tête (tri tri‑état existant).
  Trier réordonne les lignes parentes ; les tiroirs suivent.
- **Glisser‑ligne (⠿)** — conservé (actif sans tri) ; coexiste avec le chevron de dépliage.
- **Menu « Trier par ▾ »** (nouveau, complément) — dans la barre d'outils, liste **tous** les
  champs (En ligne + En détail) pour rester triable en **Maître·détail** (champs de détail) et
  en **Cartes** (aucun en‑tête). Réutilise l'état de tri (`listState[table]` / tri des objets).

## 9. Stockage

Sous `analyse.extensions.display`, en **cartes parallèles indexées par table** (`risks`,
`measures`, `links`) et **par type d'objet** (clé `objects.<code>`), dans le prolongement du
format existant `display.columns[table]` (ordre des colonnes). Chaque aspect a sa propre carte —
et non un objet unique par table — pour rester aligné sur `columns` déjà en place :

```json
"display": {
  "columns": {
    "objects.source_risque": ["id","nom","profil","np","retenue","desc","obj","motiv","just","res"]
  },
  "density": {                          // implémenté (piste 1)
    "measures": "compact",              // "compact" | "dense" ; "comfortable" (défaut) n'est pas écrit
    "objects.source_risque": "dense"
  },
  "view":   { "objects.source_risque": "master_detail" },   // à venir : "table" | "master_detail" | "cards"
  "detail": { "objects.source_risque": ["desc","obj","motiv","just","res"] }  // à venir : colonnes « en détail »
}
```

- `columns` (existant) = **ordre** des colonnes non masquées, par table.
- `density` (piste 1) = densité par table ; seule une valeur non‑défaut est écrite (retour à
  *Confort* ⇒ suppression de la clé).
- `detail` (à venir) = colonnes **En détail** ; tout ce qui est dans `columns` et hors `detail`
  est **En ligne**. `view` (à venir) = mémoire de la vue par table.
- La **pleine largeur** : `extensions.display.full_width` (booléen global) — à confirmer vs par table.
- Rétro‑compat : absence de ces clés ⇒ défauts (`view:"table"`, *Confort*, split par type §4.3).
  Aucune écriture de config vide dans le fichier (lecture paresseuse, comme l'existant).

## 10. Accessibilité & clavier

- Sélecteur de vue, densité, pleine largeur, menu de tri : boutons focusables, `aria-pressed`.
- Ligne dépliable : le chevron est un `button` (`aria-expanded`), activable au clavier ;
  la ligne de détail est un `row` révélé/masqué (pas d'`aria-hidden` incohérent).
- L'en‑tête figé et les colonnes figées ne changent pas l'ordre de tabulation.

## 11. Portée par table

- **Objets** — bénéficiaire principal (types à 12‑14 attributs). Maître·détail conseillé par défaut
  pour un type « large » (mais opt‑in explicite, pas d'auto‑bascule).
- **Risques / Mesures / Liens** — mêmes vues ; défauts « En ligne » : ID, libellé, catégorie,
  cotation, statut, évolution… ; « En détail » : descriptions, notes, champs perso verbeux.

## 12. Hors périmètre (plus tard)

- Tri multi‑critères depuis le menu (le tri tri‑état par en‑tête reste la base).
- Épinglage libre d'une colonne quelconque (au‑delà d'ID/Actions) — piste 4, complément ultérieur.
- Regroupement de lignes / sous‑totaux.

## 13. Plan d'implémentation (incrémental)

1. **Cadre figé + densité** (piste 1) — ✅ *fait* : colonnes ID/Actions et en‑tête figés ;
   conteneur qui remplit la fenêtre (défilement interne) ; ombres de bord latérales continues et
   conditionnelles ; contrôle de densité Confort/Compact/Dense mémorisé par table
   (`display.density`). S'applique à Risques, Mesures, Liens et chaque type d'objet.
2. **Modèle de placement** — état `view`/`detail` dans `extensions.display` ;
   helpers (colonnes en ligne / en détail) + défauts par type ; verrous ID/libellé/actions.
3. **Vue Maître·détail** (piste 2) — rendu colonnes clés + tiroir de détail (Markdown, texte complet) ;
   chevron ; préservation tri/drag/glisser‑ligne.
4. **⚙ Colonnes 3 états** — contrôle En ligne/En détail/Masqué + préréglages.
5. **Vue Cartes** (piste 3) — grille de fiches + bascule de vue.
6. **Menu « Trier par »** — tri des champs de détail / en cartes.
7. **Pleine largeur** (piste 5) — option + bouton d'en‑tête.

Chaque étape est committée séparément, avec tests (pytest + Playwright, suites `ui`/`export`).
