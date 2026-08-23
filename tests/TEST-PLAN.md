# TEST-PLAN — matrice de couverture

Contrat d'**exhaustivité** de la suite : chaque écran, onglet, sous-onglet, menu et modale de
l'application y est listé et rattaché à des tests. Sert à mesurer la couverture et à repérer les trous.

**Légende de statut** : ✅ couvert · 🟡 partiel (pilote / à compléter) · ⬜ à couvrir · ⏭️ lane optionnelle.

**Cible de suite** : `U`=`suites/unit` · `I`=`suites/ui` · `X`=`suites/export` · `V`=`suites/visual`.

> État au démarrage de la construction : seul le **socle + pilote** est en place (Phase 1). Les lignes
> 🟡/⬜ sont la feuille de route des phases 2→7. Ce fichier est mis à jour au fil des phases.

---

## 1. Onglets principaux (11)

| # | Onglet (`data-view`) | Éléments / interactions à couvrir | Suite | Statut |
|---|---|---|---|---|
| T01 | **presentation** | métadonnées (titre/auteur/orga/périmètre/réf/révision/statut/description Markdown), champs perso d'analyse, aperçu Markdown (double-clic), Enregistrer/Annuler de l'onglet | I `test_presentation` | ⬜ |
| T02 | **risks** | registre, ouverture fiche, création/duplication/suppression+undo, tri colonnes, recherche, colonnes perso, réordonnancement lignes, pastilles mesures | I `test_risks` | ⬜ |
| T03 | **measures** | idem risques (type/statut/responsable/échéance/coût), pastilles risques couverts | I `test_measures` | ⬜ |
| T04 | **links** | sous-onglets **Associations** (tableau croisé, clavier) / **Détails** (registre + champs perso de lien), confirmation d'association débrayable | I `test_links` | ⬜ |
| T05 | **objects** | navigation par type (segments/déroulant selon nb), tri 3 états, création/édition/suppression d'instance, références, import/export CSV par type | I `test_objects` | ⬜ |
| T06 | **matrices** | initial/résiduel/accolés/trajectoire, dispositions (grid/cluster/manual…), glisser pastille, export PNG/SVG/copie, titre long (retour ligne) | I `test_matrices` | ⬜ |
| T07 | **radars** | dimension, métrique (moyenne/max/somme/pondérée/nombre), évaluation (accolés/superposés), axes vides, infobulle criticité, export | I `test_radars` | ⬜ |
| T08 | **stats** | blocs (compteurs/répartition/coverage/custom/num_agg/object_*), graphiques (donut/pie), glisser-réordonner, redimensionner, ajout/suppression bloc | I `test_stats` | ⬜ |
| T09 | **plan** | échéancier / statut (kanban) / responsable, retards, cartes éditables, alternatives clavier | I `test_plan` | ⬜ |
| T10 | **report** | aperçu, sections, structure (complet/filtré/éclaté), impression (mécanisme) | I `test_report` | ⬜ |
| T11 | **settings** | 7 sous-onglets (voir §2) | I `test_settings` | 🟡 (ouverture) |
| — | **smoke sweep** | **chaque** onglet s'ouvre et se rend sans erreur console | I `test_smoke_sweep` | 🟡 fr/clair + en/sombre (→ +it, +light/dark) |

## 2. Sous-onglets Paramètres (7, `data-pmode`)

| # | Sous-onglet | À couvrir | Statut |
|---|---|---|---|
| S01 | **display** (Affichage) | thème, langue, contraste WCAG, options d'affichage | ⬜ |
| S02 | **grid** (Grille de cotation) | axes (niveaux, libellés, valeurs, descriptions), niveaux de criticité, méthode de score, transposition, tailles 3×3/5×5 | ⬜ |
| S03 | **fields** (Champs personnalisés) | CRUD d'un champ perso, tous les types, bornes, filtrable, réordonnancement | ⬜ |
| S04 | **objtypes** (Types d'objets) | CRUD d'un type, attributs, préfixe d'id | ⬜ |
| S05 | **report** (Rapport) | sections & ordre, page de garde, en-tête/pied, colonnes, matrices, orientation, éclaté | ⬜ |
| S06 | **stats** (Statistiques) | blocs par défaut, cibles | ⬜ |
| S07 | **radars** (Radars) | poids pondérés, rendu (luminosité/saturation/contour/pas/couleurs) | ⬜ |
| — | smoke | chaque sous-onglet s'ouvre sans erreur console | 🟡 fr/clair + en/sombre |

## 3. Menus & barre supérieure

| # | Élément | À couvrir | Suite | Statut |
|---|---|---|---|---|
| M01 | Menu **Fichier** : Nouvelle analyse | confirmation, remise à zéro | I `test_menus` | ⬜ |
| M02 | Fichier : Charger `.rae.json` | sélection + `applyLoadedData` | I `test_menus` | ⬜ |
| M03 | Fichier : Enregistrer / Enregistrer sous | mécanisme (sans clic natif) | I `test_menus` | ⬜ |
| M04 | Fichier : Enregistrer comme modèle | squelette | I `test_menus` | ⬜ |
| M05 | Fichier : Exporter Word (natif) | → §5 | X | ⬜ |
| M06 | Fichier : Exporter avec un modèle Word | → §5 | X | ⬜ |
| M07 | Fichier : Exporter Excel / CSV | → §5 | X | ⬜ |
| M08 | Sélecteur **langue** (fr/en/it) | bascule + `toEN`/`fromEN` | I/U | 🟡 |
| M09 | Sélecteur **thème** (clair/sombre) | bascule `data-theme` | I | 🟡 |
| M10 | Écran d'**accueil** | démo, charger, nouvelle, récents | I `test_menus` | ⬜ |
| M11 | **Fichiers récents** | IndexedDB, ouverture, vidage | I `test_persistence` | ⬜ |

## 4. Modales & transverses

| # | Élément | À couvrir | Suite | Statut |
|---|---|---|---|---|
| D01 | Modale **risque / mesure / lien / objet** | ouverture au clic cellule + focus colonne, validation, enregistrement | I | ⬜ |
| D02 | Modale **type d'objet / attribut / champ perso** | CRUD, types, validation | I | ⬜ |
| D03 | **Champ fautif** (focus + contour rouge) | libellé manquant, id dupliqué, perso obligatoire/hors bornes | I `test_modals_focus` | ⬜ |
| D04 | **Empilement / focus / inert** | confirmation par-dessus modale, restitution focus, Échap | I `test_modals_focus` | ⬜ |
| D05 | **Lightbox** image | ouverture/fermeture (fond/Échap/croix), depuis modale | I | ⬜ |
| D06 | **Import CSV** (risques/mesures/liens/objets) | mappage colonnes, erreurs par ligne, commit | I/X | ⬜ |
| D07 | **Filtres** (natifs + champs perso) | puces, application, propagation le long des liens, reset | I `test_filters_sort_columns` | ⬜ |
| D08 | **Tri** (3 états) & **colonnes perso** (menu, ordre, épingle) | | I `test_filters_sort_columns` | ⬜ |
| D09 | **Glisser-déposer** (kanban, lignes, pastilles matrices) + alternatives clavier | | I | ⬜ |
| D10 | **Persistance** save→reload, **autosave**, restauration | | I `test_persistence` | ⬜ |
| D11 | **i18n** parité + rendu fr/en/it | | U `test_i18n` + I | 🟡 |
| D12 | **Accessibilité** (ARIA tablist, roving tabindex, focus visible) | | I | ⬜ |

## 5. Exports bureautiques

| # | Export | À couvrir | Suite | Statut |
|---|---|---|---|---|
| X01 | **Rapport HTML** | sections, éclaté, périmètre filtré, détail risques (2 panneaux) | X `test_report_html` | ⬜ |
| X02 | **Word natif** (`buildDocx`) | registres, détail, matrices (image), radars, stats, objets, champs perso (couleur/image/calculé) | X `test_word_native` | ⬜ |
| X03 | **Word via gabarit** (`tmpl*`) | boucles, conditions, blocs (matrix/radar/table/stat), images, objets | X `test_word_template` | ⬜ |
| X04 | Word gabarit — **30 cas d'erreur** | messages clairs, non bloquants (repris de `travaux/test-modeles-erreurs`) | X `test_word_template` | ⬜ |
| X05 | **Excel** (`buildXlsx`) | feuilles, styles, distribution | X `test_excel` | ⬜ |
| X06 | **CSV** export (risques/mesures/liens/objets) | colonnes, valeurs, encodage | X `test_csv_export` | ⬜ |

## 6. Moteurs internes (unit)

| # | Domaine | À couvrir | Suite | Statut |
|---|---|---|---|---|
| U01 | **Moteur d'expression** | lexer, précédence, fonctions, IF, dates, texte, erreurs, agrégats, traversée réf., multivalué | U `test_expression` | 🟡 (échantillon) |
| U02 | **Modèle & grille** | `scoreOf`, `critFor`, `residual`, `normalize`, `validateStructure`, transposition | U `test_model` | ⬜ |
| U03 | **Champs perso** (18 types) | `cfControlHTML` / `cfDisplay*` / `cfValidate` par type | U `test_custom_fields` | ⬜ |
| U04 | **i18n** | parité des clés fr/en/it, `toEN`/`fromEN` (aller-retour) | U `test_i18n` | ⬜ |
| U05 | **CSV** | parse / format | U `test_csv` | ⬜ |
| U06 | **OOXML** | primitives `dx*` | U `test_ooxml` | ⬜ |
| U07 | **Markdown** | sous-ensemble GFM, sécurité (échappement, filtrage URL) | U `test_markdown` | ⬜ |

## 7. Lanes optionnelles

| # | Lane | À couvrir | Suite | Statut |
|---|---|---|---|---|
| P01 | **PDF** (LibreOffice) | exports Word/rapport convertis en PDF, contrôle de non-plantage | X `@pdf` | ⏭️ |
| Vz1 | **Visuel** (captures) | baseline par écran, fr/en/it × clair/sombre, tolérance | V `@visual` | ⏭️ |

---

## Correspondance avec l'existant de `travaux/` (à migrer/généraliser)

| Existant (`travaux/`) | Cible dans `tests/` | Ligne |
|---|---|---|
| `test-champs-calcules/` (127 tests) | `suites/unit/test_expression.py` (+ cf/model) | U01 |
| `test-objets/` (UI, non-régression) | `suites/ui/test_objects.py` (+ smoke) | T05 |
| `test-rapport-word/`, `test-rapport-images/` | `suites/export/test_word_native.py` | X02 |
| `test-stats/`, `test-conditions/`, `test-image-dims/`, `test-modele-word-objets/` | `suites/export/test_word_template.py` | X03 |
| `test-modeles-erreurs/` (30 cas) | `suites/export/test_word_template.py` | X04 |
| `test-badges/`, `test-prooferr/` | `suites/export/test_word_*` | X02/X03 |
| jeux `tests/`, `acme-test/`, `aipd*/`, `.tuto-serve/` | `tests/fixtures/analyses/`, `fixtures/csv/`, `fixtures/word-templates/` | §fixtures |

> Après migration **et vérification** d'un pan, proposer à l'utilisateur la suppression des dossiers
> `travaux/` devenus redondants (consigne utilisateur — ne jamais supprimer sans accord).
