# Catalogue des mots-clés — modèles Word RAE

Référence pour rédiger un **modèle de rapport Word** (`.docx`) à charger dans Risk Analysis Editor.
Les balises s'écrivent entre **doubles accolades** `{{ … }}`, vocabulaire **anglais**. Voir la
spécification complète : [`SPEC-rapport-modele-word.md`](../specs/SPEC-rapport-modele-word.md). Modèles
prêts à l'emploi : **ce dossier** [`word-templates/`](.).

> **v1** = valeurs, boucles, filtres, blocs `matrix` / `radar` / `table`.
> **v2** = statistiques (compteurs, couverture, graphiques donut/secteur — §4.5), conditions
> `{{#if}}` / `{{#unless}}` (§8) et **dimensions d'images** `width` / `height` (§4.8).
> **v3** = **objets & références** (§3.7) : collections `objects` / `object_types`, champs `object.*`,
> boucles sur les objets référencés (`{{#each risk.cf.<ref>}}`), blocs `stat` objets (§4.5).

---

## 1. Démarrage rapide

1. Dans Word, rédigez la mise en page souhaitée (page de garde, styles, tableaux…).
2. Aux endroits à remplir, insérez des balises : `{{ analysis.title }}`, `{{ matrix type="initial" }}`, etc.
3. Pour répéter du contenu (un paragraphe, une **ligne de tableau**), encadrez-le d'une boucle
   `{{#each risks}} … {{/each}}`.
4. Chargez le modèle via **Fichier › Exporter avec un modèle Word…** ; le rapport rempli est téléchargé.

---

## 2. Configuration — `{{ report … }}`

Directive globale (non affichée), de préférence en tête de document.

| Attribut | Rôle | Exemple |
|---|---|---|
| `filter` | filtre appliqué à **tout** le rapport (§7) | `{{ report filter="category='Accès illégitime'" }}` |
| `date_format` | format de date par défaut | `{{ report date_format="JJ/MM/AAAA" }}` |
| `badge` | style de badge par défaut : `cell` · `flat` · `chip` · `pill` (§5) | `{{ report badge="pill" }}` |

Le filtre global se **combine (ET)** aux filtres locaux. Un bloc/boucle l'ignore avec `report_filter="none"`.

---

## 3. Valeurs

Rendu **texte** par défaut. Voir les **formats** au §5.

### 3.1 Analyse — `analysis.*`
| Balise | Contenu |
|---|---|
| `{{ analysis.title }}` | titre |
| `{{ analysis.description }}` | description (texte enrichi Markdown) |
| `{{ analysis.author }}` | auteur |
| `{{ analysis.organization }}` | organisation |
| `{{ analysis.scope }}` | périmètre |
| `{{ analysis.reference }}` | référence méthodologique |
| `{{ analysis.revision }}` | révision |
| `{{ analysis.status }}` | statut (Brouillon / Validé / Archivé) |
| `{{ analysis.language }}` | langue |
| `{{ analysis.created }}` · `{{ analysis.updated }}` | dates de création / mise à jour |
| `{{ analysis.risks_count }}` · `{{ analysis.measures_count }}` · `{{ analysis.links_count }}` | nombres de risques · mesures · liens |
| `{{ analysis.reduced_count }}` | nombre de risques réduits (cotation modifiée entre initial et résiduel) |
| `{{ analysis.cf.<code> }}` | champ personnalisé d'analyse |

### 3.2 Grille — `grid.*`
`{{ grid.vertical_axis }}`, `{{ grid.horizontal_axis }}`, `{{ grid.method }}` (libellé localisé de la
méthode, ex. « Produit (P × G) »).
Collection `grid.levels` (niveaux de criticité, triée par ordre) : `code`, `label` (**étiquette colorée** —
`{{ level.label | badge }}`), `score_min`, `score_max`, `color`, `acceptance`, `description`, plus les
**comptes de risques** `count_initial` et `count_residual` (par ce niveau, en initial / résiduel).
**Échelles d'axes** — collections `grid.vertical_axis.levels` (vraisemblance) et
`grid.horizontal_axis.levels` (gravité), frame `step` : `{{ step.value }}`, `{{ step.label }}`,
`{{ step.description }}`.

### 3.3 Risque — `risk.*` (dans `{{#each risks}}`)
| Balise | Contenu |
|---|---|
| `{{ risk.id }}` · `{{ risk.label }}` | identifiant · libellé |
| `{{ risk.category }}` · `{{ risk.owner }}` | catégorie · propriétaire |
| `{{ risk.description }}` · `{{ risk.comment }}` | description · commentaire (enrichis) |
| `{{ risk.initial.probability }}` · `{{ risk.initial.severity }}` | vraisemblance · gravité (initial) |
| `{{ risk.initial.score }}` · `{{ risk.initial.criticality }}` | score · criticité (libellé) |
| `{{ risk.initial.criticality_code }}` · `{{ risk.initial.color }}` | code niveau · couleur hex |
| `{{ risk.residual.* }}` | idem pour le risque résiduel |
| `{{ risk.evolution }}` | Réduit / Inchangé / Aggravé |
| `{{ risk.cf.<code> }}` | champ personnalisé de risque / de cotation |
| `risk.measures` · `risk.links` | sous-collections (boucles imbriquées) |

> Synonymes : `risk.gross.*` = `risk.initial.*`, `risk.net.*` = `risk.residual.*`.

### 3.4 Mesure — `measure.*` (dans `{{#each measures}}`)
`{{ measure.id }}`, `{{ measure.label }}`, `{{ measure.type }}`, `{{ measure.status }}`,
`{{ measure.responsible }}`, `{{ measure.due_date }}` (date), `{{ measure.cost }}`,
`{{ measure.description }}`, `{{ measure.comment }}`, `{{ measure.overdue }}` (en retard, booléen),
`{{ measure.cf.<code> }}`. Sous-collections : `measure.risks` (risques couverts), `measure.links`.

### 3.5 Lien — `link.*` (dans `{{#each links}}`)
`{{ link.comment }}`, `{{ link.cf.<code> }}`, et les objets résolus `{{ link.risk.* }}` /
`{{ link.measure.* }}` (tous les champs du risque et de la mesure reliés) ; `link.risk_id`,
`link.measure_id` pour les seuls identifiants.

### 3.6 Champs personnalisés — référentiel (`custom_fields`)

Pour **décrire** les champs personnalisés (et non lire leurs valeurs) : collection `custom_fields`,
frame `field`. Attribut optionnel `target` (`analysis` · `risk` · `measure` · `link` · `cotation`)
pour se limiter à une cible ; `glossary="true"` pour ne garder que les champs à **valeurs décrites**
(comme le glossaire du rapport) ; `sort`, `limit` acceptés.

```
{{#each custom_fields target="risk"}}
  {{ field.label }} ({{ field.code }}) — {{ field.type }}
  {{#each field.items}}
    {{ option.code }} = {{ option.label }} [{{ option.color }}]
  {{/each}}
{{/each}}
```

| Balise | Contenu |
|---|---|
| `{{ field.code }}` · `{{ field.label }}` | code · libellé |
| `{{ field.target }}` · `{{ field.type }}` | cible · type (libellés localisés) |
| `{{ field.required }}` · `{{ field.filterable }}` | obligatoire · utilisable comme filtre (Oui/Non) |
| `{{ field.help }}` · `{{ field.description }}` | aide · description |
| `field.items` | sous-collection des valeurs possibles (types à valeurs fermées), frame `option` |
| `{{ option.code }}` · `{{ option.label }}` · `{{ option.color }}` · `{{ option.description }}` | code · libellé · couleur · description d'une valeur |

Tableau clé en main : `{{ table source="custom_fields" }}` (colonnes : code, libellé, cible, type,
obligatoire, filtrable), avec `target="…"` optionnel.

**Tableau des valeurs** (dans une boucle `custom_fields`) : `{{ field_values }}` — tableau
**Valeur / Description** du champ courant, **badge coloré pour les tags** (§4.4).

### 3.7 Objets & références — `object.*`, `type.*`

Les champs de type **référence** (champ personnalisé d'entité **ou** attribut d'objet) pointent vers
des **fiches d'objet** (valeurs métier, biens supports, sources de risque…). Trois usages.

**a) Rendu simple** — libellés des objets pointés (aucune boucle) :
`{{ risk.cf.<ref> }}` (libellés séparés par « , ») · `{{ risk.cf.<ref> | codes }}` (identifiants bruts) ·
`{{ risk.cf.<ref> | join:" ; " }}`. Vaut aussi pour `measure.cf.*`, `link.cf.*`, `analysis.cf.*`.

**b) Boucle sur les objets référencés** — `{{#each risk.cf.<ref>}} … {{/each}}` (idem `measure`, `link`,
`analysis`), variable de boucle **`object`**. Récursif objet→objet : `{{#each object.attr.<ref>}} …
{{/each}}` (l'`object` interne masque l'externe).

**c) Boucle sur le catalogue** — `{{#each objects type="<code>" sort="id|label" limit=N}}` : toutes les
instances (le référentiel **n'est pas** restreint par les filtres de risque/mesure). Sans `type=`,
itère tous les objets (`{{ object.type }}` les distingue).

Champs d'un objet (frame `object`) :

| Balise | Contenu |
|---|---|
| `{{ object.id }}` | identifiant (ex. `VM1`) |
| `{{ object.label }}` | libellé = valeur de l'attribut-nom (`name_attr`), repli id |
| `{{ object.type }}` · `{{ object.type_code }}` | libellé du type · code du type |
| `{{ object.attr.<code> }}` | valeur d'un **attribut** — déréférencée si référence, libellés pour select/tags, dates formatées |

**Types d'objets (schéma)** — collection `object_types`, frame `type` : `{{ type.code }}`,
`{{ type.label }}`, `{{ type.id_prefix }}`, `{{ type.name_attr }}`, `{{ type.count }}` (nombre
d'instances), et la sous-collection `{{#each type.attributes}}` (frame `attribute`, mêmes champs que
`field` du §3.6 : `{{ attribute.label }}`, `{{ attribute.code }}`, `{{ attribute.type }}`…).

> Chaque `{{#each}}` / `{{/each}}` va sur **sa propre ligne** (= son paragraphe Word) ; les boucles ne
> s'écrivent **pas** en ligne (contrairement aux conditions, §8).

```
{{#each objects type="bien_support" sort="id"}}
  {{ object.id }} — {{ object.label }} ({{ object.attr.type }})
  Valeurs métier soutenues :
  {{#each object.attr.valeurs_soutenues sort="id"}}
     · {{ object.label }}
  {{/each}}
{{/each}}

{{#each risks limit=5 sort="criticality_residual:desc"}}
  {{ risk.id }} — {{ risk.label }}
  Biens supports concernés :
  {{#each risk.cf.biens_concernes}}
     • {{ object.label }} ({{ object.attr.type }})
  {{/each}}
{{/each}}
```

### 3.8 Restitution générique — sans connaître le schéma (réflexif)

Pour écrire **un seul modèle** qui restitue *toutes* les informations de *n'importe quelle* analyse
(objets, attributs, champs perso, références) **sans coder aucun code** de type/attribut/champ.

**Blocs « notes » tout-faits** — « Libellé : valeur » de tous les champs renseignés, références
déréférencées :

| Bloc | Restitue |
|---|---|
| `{{ object_notes }}` | tous les **attributs** de l'objet courant (dans une boucle d'objets) |
| `{{ cf_notes }}` | champs perso du **risque / mesure / lien** courant |
| `{{ cf_notes target="analysis" }}` | champs perso de l'**analyse** |
| `{{ cf_notes target="cotation" phase="initial\|residual" }}` | champs de **cotation** (dans une boucle `risks`) |

**Boucles réflexives** — pour une mise en page libre (l'attribut/champ porte **sa valeur**) :

| Collection | Frame | Champs |
|---|---|---|
| `object.attributes` (dans une boucle d'objets) | `attribute` | `label`, `code`, `type`, **`value`** (rendue, déréférencée), **`is_reference`** |
| `risk.custom_fields` · `measure.custom_fields` · `link.custom_fields` · `analysis.custom_fields` | `field` | idem |

Traverser une référence **sans son code** : `{{#each attribute.objects}}` (ou `{{#each field.objects}}`)
itère les **instances pointées** lorsque `is_reference` est vrai.

```
{{! Inventaire complet et agnostique — un modèle, toute analyse }}
{{#each objects sort="id"}}
  {{ object.type }} — {{ object.id }} : {{ object.label }}
  {{ object_notes }}
{{/each}}

{{! Variante « boucles » (mise en page libre + traversée des références) }}
{{#each objects}}
  {{ object.label }}
  {{#each object.attributes}}
    {{ attribute.label }} : {{ attribute.value }}
    {{#if attribute.is_reference}}
      {{#each attribute.objects}}
         → {{ object.label }}
      {{/each}}
    {{/if}}
  {{/each}}
{{/each}}
```

---

## 4. Blocs — matrice, radar, tableau

Tous acceptent `filter="…"` (§7) et `report_filter="none"`.

### 4.1 `{{ matrix … }}`
| Attribut | Valeurs (défaut) |
|---|---|
| `type` | `initial` (syn. `gross`), `residual` (syn. `net`), `trajectory` — défaut `initial` |
| `title` | titre (aucun par défaut) |
| `width` · `height` | dimensions en cm (voir **§4.8**) |
| `filter` | filtre (§7) |

### 4.2 `{{ radar … }}`
`dimension` (`category` ou `cf.<code>`), `metric` (`average`, `max`, `cumulative`, `weighted`, `count`),
`evaluation` (`initial`, `residual`, `side`, `overlay`), `title`, `width` · `height` (§4.8), `filter`.
Le champ de `dimension` d'un `cf.<code>` doit être un **champ personnalisé de risque** de type
*sélection* / *cases* / *étiquettes* ; s'il est introuvable, un **avertissement** est émis (le radar n'est
pas produit).

### 4.3 `{{ table … }}`
| Attribut | Valeurs (défaut) |
|---|---|
| `source` | `risks`, `measures`, `links`, `levels`, `custom_fields` (**requis**) |
| `columns` | liste de champs (défaut : **colonnes par défaut de l'application**) |
| `sort` | `field[:asc\|desc]` (multi-clés : `field1,field2:desc`) |
| `style` | nom d'un **style de tableau du modèle** (`<w:tblStyle>`) |
| `filter` | filtre (§7) |
| `badge` | style des badges (criticité, statut **et colonnes `tags`** — une puce par valeur) de ce tableau : `cell` · `flat` · `chip` · `pill` (défaut : style du rapport, §5) |

Ex. : `{{ table source="risks" columns="id,label,category,criticality_initial,criticality_residual" }}` ·
`{{ table source="risks" badge="pill" }}` (criticités en pastilles arrondies)

### 4.4 `{{ field_values }}`
Dans une boucle `custom_fields` (§3.6) : tableau **Valeur / Description** des valeurs du champ courant,
avec un **badge coloré** pour les champs de type `tags` (texte simple pour `select` / `checklist`).
Reproduit la section « Référentiels et légendes des champs » du rapport intégré. Ne produit rien
(paragraphe retiré) pour les champs sans valeurs fermées, ou dont aucune valeur n'a de description.

### 4.5 `{{ stat type="…" }}`
Statistiques de l'analyse (tableaux et **graphiques**), calquées sur l'onglet Statistiques et le rapport
intégré.

**Types sans graphique** (tableaux/tuiles simples) :

| `type` | Rendu |
|---|---|
| `summary` (syn. `counts`) | **synthèse** : Risques / Mesures / Risques réduits |
| `counters` | **tuiles clés** : Risques · Mesures · Risques réduits · % traité |
| `coverage` | **couverture** : risques sans mesure · mesures orphelines (n / total) |

**Types à graphique** (répartition — tableau *Nombre / Part*, anneau/secteur, légende) :

| `type` | Dimension |
|---|---|
| `criticality` (syn. `distribution`) | **criticité** Initial vs Résiduel (deux graphiques) |
| `category` | catégorie des risques |
| `measure_type` · `measure_status` | type · statut des mesures |
| `risk_owner` · `measure_owner` | propriétaire des risques · responsable des mesures |
| `cf.<code>` | champ personnalisé (tags/select/checklist **ou référence** — libellés d'objets déréférencés) |
| `objects` | **objets par type** (répartition du référentiel) |
| `object_attr:<type>:<attr>` | un **type d'objet par attribut** (ex. `object_attr:valeur_metier:besoin_c`) |
| `object_usage:<type>` | **complétude** d'un type : instances **référencées** vs **orphelines** |

> Les blocs `objects`, `object_attr:…`, `object_usage:…` portent sur **tout le référentiel** (non
> filtré par les filtres de risque/mesure). `object_attr` accepte un attribut à valeurs fermées **ou**
> de référence.

Attributs des types à graphique :

| Attribut | Valeurs (défaut) | Rôle |
|---|---|---|
| `display` | `table` · `chart` · `both` — défaut **`table`** | tableau seul · graphique + légende · les deux |
| `shape` | `donut` · `pie` — défaut **`donut`** | forme du graphique |
| `width` · `height` | cm (§4.8) | dimensions du graphique |
| `filter` | filtre (§7) | restreint la population comptée |

Mise en page (`display="chart|both"`) : les éléments sont posés **sur une même ligne**, centrés —
`chart` → `graphique │ légende` ; `both` (dimension) → `tableau │ graphique │ légende` ;
`criticality` `chart` → les deux graphiques puis une **légende en ligne** ; `criticality` `both` → les deux
graphiques puis le tableau. Les tableaux de données sont ajustés au contenu et centrés.

Ex. : `{{ stat type="counters" }}` · `{{ stat type="category" display="both" shape="pie" }}` ·
`{{ stat type="measure_status" display="chart" filter="overdue='true'" }}`

### 4.6 `{{ cf_notes }}` · `{{ object_notes }}`
`{{ cf_notes }}` — dans une boucle `risks` / `measures` / `links` : **notes des champs personnalisés**
de l'entité courante (un « Libellé : valeur » par champ renseigné). Reproduit les notes des sections
« Détail » du rapport. Cibles supplémentaires : `{{ cf_notes target="analysis" }}` (champs de
l'analyse) et `{{ cf_notes target="cotation" phase="initial|residual" }}` (champs de cotation, dans une
boucle `risks`). `{{ object_notes }}` — dans une boucle d'objets : **tous les attributs** de l'objet
courant, mêmes règles (références déréférencées). Voir la **restitution générique**, §3.8.

### 4.7 `{{ logo }}`
Insère le **logo de couverture configuré** de l'analyse (`extensions…report.cover.logo`). Attributs
`width` · `height` optionnels (§4.8). Ne produit rien si aucun logo n'est configuré.

### 4.8 Dimensions des images (`width` / `height`)
Sur **tous les tags produisant une image** (`matrix`, `radar`, `logo`, `stat` en `display="chart|both"`) :

| Réglage | Effet |
|---|---|
| `width="8"` | 8 cm de large, **hauteur calculée** (proportions conservées) |
| `height="6"` | 6 cm de haut, **largeur calculée** |
| `width="10" height="5"` | **boîte maximale** : l'image est agrandie au maximum **sans dépasser** la largeur ni la hauteur, proportions conservées (**jamais déformée**) |
| *(aucun)* | taille par défaut (largeur intrinsèque plafonnée) |

Unité : **centimètres**. Les deux valeurs ensemble ne forcent donc **pas** une déformation : elles bornent
une boîte que l'image remplit en gardant son ratio.

---

## 5. Formats de valeur (`| …`)

| Format | Effet |
|---|---|
| `date="ISO\|JJ/MM/AAAA\|MM/JJ/AAAA\|long"` | mise en forme d'une date |
| `codes` / `labels` | champ perso : par ses **codes** / ses **libellés** (défaut) |
| `join="; "` | séparateur pour un champ multi-valeurs |
| `percent` | ajoute « % » |
| `upper` / `lower` | casse |
| `default="—"` | valeur de repli si vide |
| `swatch` | **couleur** (`*.color`) → **pastille carrée** ; **tags** / **étiquettes colorées** (statut, criticité) → pastille + libellé |
| `badge` | **tags** / **étiquettes colorées** (statut, criticité) → **puce colorée** (style au choix, ci-dessous) |

Ex. : `{{ risk.initial.color | swatch }}` · `{{ risk.cf.source | badge }}` · `{{ option.color | swatch }}` ·
`{{ measure.status | badge }}` · `{{ risk.initial.criticality | badge="pill" }}`

**Style de badge.** Un `{{ … | badge }}` **sans valeur** prend le **style par défaut du rapport**
(onglet Rapport › *Style des badges*, ou `{{ report badge="…" }}`). On peut forcer le style
sur une balise précise :

| Valeur | Rendu |
|---|---|
| `cell` *(défaut du rapport)* | dans un **tableau clé en main**, remplit toute la cellule ; en ligne, se rabat sur `flat` |
| `flat` | **surlignage** : fond coloré collé au texte, sans marge (rendu historique) |
| `chip` | vrai texte sur **fond coloré**, avec marge et fine bordure — soigné, **sélectionnable/recherchable**, coins carrés |
| `pill` | **pastille arrondie** en image (fidèle au rendu HTML) — la plus jolie, mais le texte devient une image (non sélectionnable) ; **corps du document uniquement** (repli `chip` en en-tête/pied) ; **idéale en cellule de tableau** — en flux de texte, une image inline « remonte » sur la ligne, préférer `chip` |

Portées : **globale** = *Style des badges* du rapport (défaut `cell`) ou `{{ report badge="pill" }}` ;
**par tableau clé en main** = `{{ table source="risks" badge="pill" }}` ; **par balise** = `{{ … | badge="chip" }}`.

> `swatch` / `badge` produisent des **runs colorés** dans le document. `badge` = libellé sur fond coloré
> (texte contrasté) ; `swatch` = pastille carrée colorée (seule pour une **valeur couleur**, suivie du
> libellé pour un **tags** ou une **étiquette colorée**). S'appliquent aux champs **tags**, au **statut**
> de mesure et à la **criticité** (initiale/résiduelle). Une valeur multi-étiquettes produit une pastille
> par valeur. Sur une valeur non pertinente, repli en texte simple.

---

## 6. Boucles — `{{#each … }} … {{/each}}`

```
{{#each risks sort="criticality_initial:desc" filter="…" limit=10}}
  {{ risk.id }} — {{ risk.label }} : {{ risk.initial.criticality }}
{{/each}}
```

- **Collections** : `risks`, `measures`, `links`, `grid.levels`, `custom_fields`,
  `grid.vertical_axis.levels`, `grid.horizontal_axis.levels`, **`objects`** (attr. `type="<code>"`),
  **`object_types`**, et les **sous-collections** (`risk.measures`, `measure.risks`, `field.items`,
  **`risk.cf.<ref>`** / `measure.cf.<ref>` / `link.cf.<ref>` / `analysis.cf.<ref>` = objets référencés,
  **`object.attr.<ref>`** = objet→objet, **`type.attributes`**, et les **réflexives** (§3.8) :
  **`object.attributes`**, **`<entité>.custom_fields`**, **`attribute.objects`** / `field.objects`).
  Imbrication libre. Détails objets : §3.7–3.8.
- **Attributs** : `filter`, `sort`, `limit`, `group_by`, `report_filter`, `autofit`, et **`type`**
  (filtre de type pour `objects`). Le tri des objets accepte `sort="id"` / `sort="label"`.
- **Tri multi-clés** : `sort="champ1[:asc|desc], champ2[:asc|desc], …"` — les clés sont appliquées
  successivement (départage). Ex. `sort="target,code"` (cible puis code), `sort="criticality_initial:desc,label"`.
- **Regroupement** `group_by="field"` → boucle de **groupes** : `{{ group.label }}`, `{{ group.count }}`,
  `{{ group.measures_count }}` (groupes de risques), et `{{#each group.items}} … {{/each}}`.
  Champs de regroupement des risques : `category`, `owner`, `criticality_initial/residual`, `cf.<code>`,
  et **`id`** (un chapitre par risque). Mesures : `type`, `status`, `responsible`, `cf.<code>`.
- **Portée implicite du groupe** : dans un `group_by`, les matrices/tableaux/boucles imbriqués sont
  **auto-filtrés** sur la valeur du groupe → base du **rapport éclaté** par catégorie.
- **Boucle de ligne de tableau** : placez `{{#each …}}` au début de la 1re cellule d'une ligne et
  `{{/each}}` à la fin de la dernière → **la ligne** est répétée par élément (reprend la mise en forme
  du modèle).
- **Colonnes ajustées au contenu** — drapeau `autofit` sur la boucle de ligne :
  `{{#each risks autofit }} … {{/each}}`. Le générateur **mesure le texte réellement produit** dans
  chaque colonne (« R1 », pas la longueur du tag `{{ risk.id }}`) et **répartit la largeur totale du
  tableau au prorata**. Résout la colonne ID (ou toute colonne à contenu court) trop large parce que
  calibrée dans le modèle sur la longueur des balises. La largeur totale du tableau est **conservée** ;
  les largeurs sont écrites en dur (rendu identique dans Word et LibreOffice). Sans le drapeau, les
  largeurs du modèle sont **respectées à l'identique**.
- **Repli si vide** : `{{#each … }} … {{else}} … {{/each}}` — le contenu placé après `{{else}}` s'affiche
  quand la collection (**après filtre**) est vide. Ex. lister les mesures en retard, sinon « Aucune mesure
  en retard ». (Portée paragraphe.)

---

## 7. Filtres — `filter="…"`

- **Comparaison** : `field operator "value"`. Opérateurs : `=`, `!=`, `>`, `>=`, `<`, `<=`, `contains`,
  `empty`, `not_empty`.
- **Combinaison** : `and`, `or`, parenthèses.
- **Champs** : `category`, `owner`, `type`, `status`, `responsible`, `overdue`, `criticality_initial`,
  `criticality_residual`, `cf.<code>`.
- **Code ou libellé** : la valeur est comparée au **code stocké** *ou* au **libellé affiché** (insensible
  à la casse). Ex. `status="in progress"` ≡ `status="in_progress"`.
- **Multi-valeurs** (tags) : `cf.source contains "internal"`.
- **Propagation** : un filtre de risque restreint aussi mesures/liens liés (et réciproquement).

Ex. : `filter="cf.source contains 'internal' and criticality_initial>='high'"`

---

## 8. Conditions — `{{#if …}}` · `{{#unless …}}`

Affiche une section **seulement si** une expression est vraie. Fonctionne à la **portée paragraphe** et à
la **portée ligne de tableau** (comme les boucles, §6).

```
{{#if measure.overdue}}⚠ En retard{{else}}À l'heure{{/if}}
{{#unless analysis.reduced_count}}Aucun risque réduit à ce stade.{{/unless}}
```

- **Expression** : `chemin operateur "valeur"`, où `chemin` est **n'importe quelle valeur** résoluble en
  `{{ … }}` (`analysis.*`, `risk.*`, `measure.*`, `link.*`, `level.*`, `grid.*`, compteurs, `cf.<code>`…).
- **Opérateurs** : `=`, `!=`, `>`, `>=`, `<`, `<=`, `contains`, `empty`, `not_empty` — combinables par
  `and`, `or` et parenthèses (mêmes règles qu'un filtre, §7 : comparaison numérique quand c'est possible,
  code **ou** libellé, insensible à la casse ; `contains` sur les multi-valeurs).
- **Forme courte** : `{{#if chemin}}` seul teste **« non vide »** (équivaut à `chemin not_empty`) ; utile
  pour un booléen (`overdue`) ou un champ renseigné.
- **`{{#unless expr}}`** = négation de `{{#if expr}}`. `{{else}}` est accepté dans les deux.
- **Bloc ou en ligne** : si les marqueurs sont **seuls** sur leur paragraphe (ou ligne de tableau), la
  condition encadre des **paragraphes entiers** (portée bloc). Si l'ouverture **et** la fermeture tiennent
  dans un **même paragraphe/cellule** (`… {{#if x}}texte{{/if}} …`), elle est évaluée **en ligne** — seul
  moyen d'agir dans une **cellule de boucle de ligne** (ex. « En retard » en rouge dans une colonne Statut).
- **Imbrication** libre avec les boucles et les autres conditions. Une expression invalide, une section non
  fermée ou un `{{else}}` orphelin déclenchent un **avertissement** (`tw_if_*`) et la section est laissée
  telle quelle.

Ex. : `{{#if risk.residual.criticality_code = "high" or risk.residual.criticality_code = "critical"}} … {{/if}}` ·
`{{#if measure.due_date empty}}Sans échéance{{/if}}` ·
`{{#if risk.cf.source contains "internal"}} … {{/if}}`

---

## 9. Échappement

- Guillemets **interchangeables** : attribut en `"…"` ou `'…'`, chaîne de filtre en `'…'` ou `"…"`.
  Choisir celui absent du contenu → aucun échappement.
  Ex. : `filter="label contains \"l'accès d'urgence\""`.
- Sinon **`\`** déspécialise : `\'`, `\"`, `\\`.
  Ex. : `filter="label contains 'l\'accès'"`.
- Accolades littérales dans le texte : `\{{` et `\}}`.

---

## 10. Modèles d'exemple

Chaque modèle existe en version **propre** (prête à l'emploi) et **annotée** (`…-annote.docx`, avec
notes explicatives — à ne pas utiliser telle quelle, les notes apparaîtraient dans le rapport).

- [`modele-rapport-classique.docx`](modele-rapport-classique.docx) —
  rapport complet (présentation, matrices, grille, registre des risques, tableau de mesures en **boucle
  de ligne**, détail par risque avec sous-boucle, radar).
- [`modele-rapport-eclate-par-categorie.docx`](modele-rapport-eclate-par-categorie.docx) —
  synthèse générale puis **un chapitre par catégorie** (portée implicite du groupe).
- [`modele-referentiels.docx`](modele-referentiels.docx) —
  **référentiels** : grille de cotation (méthode, échelles d'axes en boucle de ligne, niveaux de
  criticité) et **champs personnalisés** (tableau récapitulatif + détail des caractéristiques et des
  valeurs possibles).
- [`modele-tableau-de-bord.docx`](modele-tableau-de-bord.docx) —
  **tableau de bord** (v2) : tuiles clés et couverture, graphiques de répartition (criticité, catégorie,
  statut des mesures) et sections **conditionnelles** (`{{#if}}` / `{{#unless}}`) — alerte mesures en
  retard, risques non traités.
