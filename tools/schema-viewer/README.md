# Visualiseur de schéma `.rae.json` (diagramme entité-relation)

Outil HTML autonome (hors-ligne) qui dessine le **schéma** d'une analyse Risk Analysis Editor
sous forme de diagramme entité-relation, avec [Mermaid](https://mermaid.js.org) (`erDiagram`).

## Usage

Ouvrir **`index.html`** dans un navigateur, puis **glisser-déposer** un fichier `.rae.json`
(ou bouton « Charger »). Aucun serveur, aucune connexion requise.

## Ce qui est représenté

- **Boîtes** : les *types d'objets* (valeur métier, bien support…) et les *entités cœur* qui
  portent des champs personnalisés (risque, mesure, lien, analyse, cotation). Chaque boîte liste
  ses **champs / attributs** avec leur **type**.
  - `PK` = attribut servant de libellé (`name_attr`) · `FK` = champ de type référence.
- **Flèches** : les **relations de référence**.
  - champ de référence d'une entité → type d'objet visé (ex. Risque → Valeur métier) ;
  - attribut de référence d'un objet → autre objet (ex. Bien support → Valeur métier).
  - **cardinalité** pattes-d'oie : `||` un · `o|` zéro/un · `o{` zéro/plusieurs (mono/multi,
    obligatoire/optionnel).

## Interaction

- **Zoom** molette · **Déplacer la vue** cliquer-glisser · boutons `＋ － Ajuster 1:1`.
- **Orientation** : bouton pour basculer la mise en page haut-bas ⇄ gauche-droite.
- **Attributs** : bouton pour n'afficher que les **clés** (PK) et **références** (FK) — vue épurée
  centrée sur les relations — ou tous les attributs.
- **Export** SVG et PNG.
- **Source** : affiche le code Mermaid généré (copiable).

> Mermaid ne permet pas de déplacer les nœuds individuellement (mise en page automatique) ;
> l'outil offre le zoom / déplacement de la vue et l'export.

## Fichiers

- `index.html` — l'outil (logique + interface).
- `mermaid.min.js` — bibliothèque Mermaid vendorisée en local (UMD, pour le hors-ligne).
