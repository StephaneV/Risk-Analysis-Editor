# Guide — rédiger son propre modèle de rapport Word

Ce guide explique **pas à pas** comment créer un modèle Word (`.docx`) pour le générateur de rapports de
Risk Analysis Editor. Il est **complémentaire** du [catalogue des mots-clés](catalogue-mots-cles-rapport.md),
qui reste la **référence exhaustive** des balises (à garder ouvert à côté).

> En bref : vous rédigez un document Word normal (mise en page, charte, styles), vous y insérez des
> **balises** `{{ … }}` aux endroits à remplir, puis l'application produit le rapport en remplaçant chaque
> balise par les données de l'analyse.

---

## 1. Le principe en une minute

1. Vous créez un `.docx` dans Word avec votre mise en page habituelle.
2. Aux emplacements à remplir, vous écrivez des balises entre **doubles accolades** — vocabulaire **anglais** :
   `{{ analysis.title }}`, `{{#each risks}} … {{/each}}`, `{{ matrix type="initial" }}`…
3. Dans l'application : **Fichier › Exporter avec un modèle Word…**, vous choisissez votre `.docx`.
4. Le rapport rempli est téléchargé. **Le modèle reste la seule source de la mise en forme** ; l'application
   n'apporte que le contenu.

À la fin de la génération, un **rapport d'avertissements** signale les balises non reconnues ou les
problèmes (voir §7) — pensez à le lire.

---

## 2. Démarrer : partir d'un exemple

Le plus simple est de **copier un modèle existant** de ce dossier et de l'adapter :

| Pour… | Partez de |
|---|---|
| un rapport classique complet | `modele-rapport-classique.docx` |
| un rapport « un chapitre par catégorie » | `modele-rapport-eclate-par-categorie.docx` |
| décrire la grille et les champs perso | `modele-referentiels.docx` |
| un tableau de bord (stats + conditions) | `modele-tableau-de-bord.docx` |
| reproduire fidèlement l'export Word natif | `modele-rapport-complet-*.docx` |

**Astuce — les variantes annotées.** Chaque modèle existe aussi en version `…-annote.docx` avec des
**notes grises** expliquant chaque balise. Ouvrez-les pour **apprendre**, mais **ne les exportez pas telles
quelles** : les notes apparaîtraient dans le rapport. Utilisez la version propre pour produire.

---

## 3. Les quatre familles de balises

| Famille | Forme | Rôle |
|---|---|---|
| **Valeur** | `{{ chemin [\| format] }}` | insère une donnée (texte par défaut) |
| **Bloc** | `{{ bloc attr="…" }}` | insère un tableau, une matrice, un radar, un graphique… |
| **Boucle** | `{{#each collection …}} … {{/each}}` | répète le contenu pour chaque élément |
| **Condition** | `{{#if expr}} … {{else}} … {{/if}}` | affiche selon une condition |

Il existe aussi la directive de configuration `{{ report … }}` (filtre global, format de date) et les
commentaires `{{! … }}` (ignorés). Voir le catalogue §2.

---

## 4. Recettes pas à pas

### 4.1 Page de garde (valeurs + logo)
```
{{ logo }}
{{ analysis.title }}
{{ analysis.organization }} · {{ analysis.author }} · {{ analysis.updated | date="long" }}
```
`{{ logo }}` insère le logo configuré de l'analyse. Les valeurs héritent de la **mise en forme du modèle**
à l'endroit de la balise (police, taille, couleur).

### 4.2 Un tableau mis en forme (boucle de ligne)
La façon la plus naturelle de construire un tableau à votre charte : créez le tableau dans Word (une ligne
d'**en-tête** + **une** ligne de corps), puis placez `{{#each …}}` au **début de la première cellule** de la
ligne de corps et `{{/each}}` à la **fin de la dernière**. La ligne est répétée pour chaque élément.

Dans la **ligne de corps** (3 cellules), écrivez :

- cellule 1 : `{{#each measures}}{{ measure.id }}`
- cellule 2 : `{{ measure.label }}`
- cellule 3 : `{{ measure.status | badge }} {{/each}}`

La balise d'ouverture ouvre la boucle, la balise de fermeture (dans la dernière cellule) la referme.

> **Astuce — colonnes trop larges.** Dans le modèle, une colonne se dimensionne mal parce qu'elle
> contient un tag long (`{{ risk.id }}` ≈ 13 caractères) alors que la valeur produite est courte
> (« R1 ») : la colonne ID ressort trop large. Ajoutez le drapeau **`autofit`** à la boucle de ligne —
> `{{#each risks autofit }}` — et le générateur ajuste chaque colonne à son **contenu réel** (largeur
> totale du tableau conservée). Sans le drapeau, vos largeurs sont respectées telles quelles.

### 4.3 Un tableau « clé en main »
Sans construire le tableau vous-même : `{{ table source="risks" }}` (colonnes par défaut de l'application) ou
`{{ table source="risks" columns="id,label,category,criticality_initial,criticality_residual" }}`.
Sources possibles : `risks`, `measures`, `links`, `levels`, `custom_fields`.

### 4.4 Répéter un chapitre (par risque, par catégorie…)
```
{{#each risks group_by="category"}}
  {{ group.label }} ({{ group.count }} risques)
  {{ matrix type="trajectory" }}
  {{ table source="risks" columns="id,label,criticality_initial,criticality_residual" }}
{{/each}}
```
**Portée implicite du groupe** : à l'intérieur d'un `group_by`, les matrices/tableaux/boucles imbriqués sont
**automatiquement filtrés** sur la valeur du groupe — c'est ce qui produit un rapport « éclaté ».

### 4.5 Insérer matrices, radars, graphiques de statistiques
```
{{ matrix type="initial" title="Risque initial" }}
{{ radar dimension="category" metric="average" evaluation="overlay" }}
{{ stat type="counters" }}
{{ stat type="criticality" display="both" shape="donut" }}
```
Ces blocs produisent des **images** ou des **tableaux**. Dimensions optionnelles `width`/`height` en cm
(catalogue §4.8). Le radar par `dimension="cf.<code>"` exige un champ perso de risque existant (sinon
avertissement).

### 4.6 Afficher conditionnellement
De **niveau bloc** — chaque marqueur **seul** sur son paragraphe :
```
{{#if measure.overdue}}
  ⚠ Mesure en retard
{{else}}
  À l'heure
{{/if}}
```
**Repli de boucle** — le `{{else}}` s'affiche si la collection (après filtre) est **vide** :
```
{{#each measures filter="overdue='true'"}}
  ⚠ {{ measure.id }} — {{ measure.label }}
{{else}}
  Aucune mesure en retard.
{{/each}}
```
**En ligne** — quand l'ouverture *et* la fermeture tiennent dans **le même paragraphe** (ou la même cellule ;
seul moyen d'agir dans une cellule de boucle de ligne) :
```
{{ measure.status | badge }}{{#if measure.overdue}} En retard{{/if}}
```
Vous pouvez **styliser le contenu** (ex. « En retard » en **rouge**) : le style est conservé même si les
marqueurs et le texte ont des mises en forme différentes.

### 4.7 Filtrer
Presque tous les blocs et boucles acceptent `filter="…"` :
```
{{ table source="risks" filter="criticality_initial>='important' and cf.source contains 'internal'" }}
```
Opérateurs : `= != > >= < <= contains empty not_empty`, combinés par `and`/`or` et parenthèses. La valeur se
compare au **code** ou au **libellé** (insensible à la casse). Un filtre de risque restreint aussi les
mesures/liens liés (**propagation**). Voir catalogue §7.

---

## 5. Mettre en forme les valeurs (formats `| …`)

`{{ chemin | format }}`. Les plus utiles :

- `date="JJ/MM/AAAA"` · `default="—"` (valeur de repli) · `percent` · `upper` / `lower` · `join="; "` ;
- `badge` : libellé sur **fond coloré** (statut, criticité, étiquettes). Le style d'un `| badge` **sans
  valeur** vient du réglage **Style des badges** de l'onglet Rapport (`cell` par défaut). Styles forçables :
  `badge="flat"` (surlignage), `badge="chip"` (**puce nette** bordée), `badge="pill"` (**pastille
  arrondie**, comme le rendu HTML). On peut aussi le fixer par tableau clé en main
  (`{{ table source="risks" badge="pill" }}`) ou globalement (`{{ report badge="pill" }}`) ;
- `swatch` : **pastille** carrée colorée (couleur) ou pastille + libellé (tags/criticité) ;
- `codes` / `labels` : champ perso par ses codes ou ses libellés.

Ex. : `{{ measure.status | badge="pill" }}` · `{{ risk.initial.criticality | badge }}` ·
`{{ measure.due_date | date="JJ/MM/AAAA" }}` · `{{ risk.owner | default="—" }}`. (Catalogue §5.)

---

## 6. Pièges et bonnes pratiques

- **Homogénéité de mise en forme d'une balise.** Word découpe parfois un `{{ … }}` en morceaux ; l'appli
  les recolle automatiquement **si la mise en forme est homogène**. Écrivez donc chaque balise d'un seul
  tenant, dans une même police/couleur (n'appliquez pas de gras à la moitié d'une balise).
- **Conditions en ligne et mise en forme.** Le **contenu** entre `{{#if …}}` et `{{/if}}` peut être stylé
  librement (ex. « En retard » en rouge) : la condition est évaluée même si ses marqueurs et son contenu ont
  des mises en forme différentes. Seule règle : toute la condition tient dans **un même paragraphe** (ou une
  même cellule). Si elle s'étend sur **plusieurs paragraphes**, ses marqueurs doivent être **seuls** chacun
  sur leur paragraphe (condition **de bloc**).
- **Modèle portable = champs de base.** `category`, `owner`, `status`, `criticality_*` existent dans toute
  analyse. Un champ **perso** `cf.<code>` n'existe que si l'analyse le définit : sinon la balise n'est pas
  résolue (accolades visibles) et un avertissement est émis. Prévoyez un `| default="—"` ou réservez les
  `cf.<code>` aux modèles dédiés à une analyse précise.
- **Guillemets interchangeables.** Un attribut en `"…"` peut contenir des `'…'` (et inversement) :
  `filter="cf.source contains 'internal'"`. Pour une accolade **littérale** dans le texte, échappez : `\{{`
  et `\}}`.
- **Ne pas exporter les modèles annotés** (`…-annote.docx`) : leurs notes apparaîtraient dans le rapport.
- **En-têtes / pieds** : seules les balises de **valeur** y sont traitées (pas de boucles ni de blocs).

---

## 7. Tester son modèle

1. **Fichier › Exporter avec un modèle Word…**, choisissez votre `.docx`, ouvrez le résultat dans Word.
2. Vérifiez qu'aucune **accolade `{{ … }}` ne subsiste** (balise mal orthographiée ou champ absent).
3. Lisez le **rapport d'avertissements** affiché en fin de génération : il liste les balises inconnues,
   champs introuvables, sections mal fermées, etc.
4. Essayez le modèle sur **plusieurs analyses** si vous voulez qu'il soit réutilisable (les schémas de
   champs perso diffèrent d'une analyse à l'autre).

---

## 8. Aller plus loin

- **Référence complète des balises** : [catalogue-mots-cles-rapport.md](catalogue-mots-cles-rapport.md)
  (valeurs disponibles, tous les blocs et attributs, boucles, filtres, échappement).
- **Spécification technique** : [`specs/SPEC-rapport-modele-word.md`](../specs/SPEC-rapport-modele-word.md).
- **Modèles d'exemple** : ce dossier ([`word-templates/`](.)), versions propres et annotées.
