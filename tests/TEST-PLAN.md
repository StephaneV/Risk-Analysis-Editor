# TEST-PLAN — matrice de couverture

Contrat d'**exhaustivité** de la suite : chaque écran, onglet, sous-onglet, menu et modale de
l'application y est listé et rattaché à des tests. Sert à mesurer la couverture et à repérer les trous.

**Légende de statut** : ✅ couvert · 🟡 partiel (pilote / à compléter) · ⬜ à couvrir · ⏭️ lane optionnelle.

**Cible de suite** : `U`=`suites/unit` · `I`=`suites/ui` · `X`=`suites/export` · `V`=`suites/visual`.

## Bilan de couverture

Suite **construite et verte** (`run-all.py --with-pdf --with-visual` → **391 tests**).

| Couche | Tests | Contenu |
|---|---:|---|
| `unit` | 53 | moteurs : expression (68 cas) + avancés (J/E/LF/MV/RH/IMP/CI), modèle/grille, i18n, champs perso (18 types), markdown, ooxml, csv |
| `ui` | 224 | chargement fixtures + **CRUD** (risques/mesures/champs perso/objets/stats) + **tris 3 états** + **colonnes** (visibilité/ordre) + **clavier** (onglets/kanban/lignes) + **grille** (axes/score/criticité) + **import CSV** + **contraste** + **Markdown** + **autosave** + **réglages stats/radars** + **toasts** + fonctionnel (17 écrans) + smoke **fr/en/it × clair/sombre** |
| `export` | 28 | Word natif + rapport éclaté, gabarit (31 cas d'erreur + conditions/prooferr/badges/lot9), **images/couleur/EMU**, Excel, CSV (+ **round-trip**) — inspection OOXML |
| `@pdf` (lane) | 2 | conversion PDF (LibreOffice) |
| `@visual` (lane) | 84 | baselines **pleine page** : chrome (barre haut/nav) + 11 onglets + matrices (trajectoire + 8 dispositions) + radars (4 modes) + menu Fichier + 7 sous-onglets Paramètres + 8 modales (fr clair/sombre) |

Migration depuis `travaux/` (tous les dossiers `test-*` supersédés) : voir **[MIGRATION-travaux.md](MIGRATION-travaux.md)**.

---

## 1. Onglets principaux (11)

| # | Onglet (`data-view`) | Éléments / interactions à couvrir | Suite | Statut |
|---|---|---|---|---|
| T01 | **presentation** | métadonnées, champs perso d'analyse, Enregistrer | I `test_presentation` | ✅ (méta, édition titre, champs perso, **aperçu Markdown**) |
| T02 | **risks** | registre, fiche, CRUD | I `test_risks` + `test_crud` + `test_keyboard` | ✅ (compte, modale, création, **duplication, édition, suppression+undo, réordonnancement clavier**) · ⬜ réordonnancement glisser |
| T03 | **measures** | idem risques | I `test_measures` + `test_crud` | ✅ (compte, modale, création, **duplication, suppression+undo**) |
| T04 | **links** | Associations (tableau croisé) / Détails | I `test_links` | ✅ (grille croisée, sous-onglet Détails) · ⬜ clavier, confirmation débrayable |
| T05 | **objects** | types, instances, références, CSV par type | I `test_objects` + `test_crud` + `test_filters_sort_columns` | ✅ (types/instances, **création/édition/suppression d'instance**, cascade, **tri 3 états**, filtre référence) · ⬜ import/export CSV par type (UI) |
| T06 | **matrices** | initial/résiduel/accolés/trajectoire, titre long | I `test_matrices` | ✅ (rendu, trajectoire, titre long, grilles 3×3/5×5, **8 dispositions**, **export SVG**) · ⬜ glisser (placement manuel) |
| T07 | **radars** | dimension, métrique, évaluation | I `test_radars` | ✅ (métriques, modes d'éval, **dimension** dont champ `scale`, **export SVG**) · ⬜ infobulle |
| T08 | **stats** | blocs, graphiques | I `test_stats` + `test_crud` | ✅ (rendu, statCounters, **ajout/suppression de bloc**) · ⬜ déplacement (glisser) |
| T09 | **plan** | échéancier / statut / responsable | I `test_plan` | ✅ (3 présentations) · ⬜ retards, clavier |
| T10 | **report** | sections, détail (panneaux), éclaté | I `test_report` | ✅ (sections, panneaux Initial/Résiduel, volumineuse) · ⬜ éclaté, impression |
| T11 | **settings** | 7 sous-onglets (voir §2) | I `test_settings` | ✅ (rendu des 7 sous-onglets + création champ perso) |
| — | **smoke sweep** | **chaque** onglet s'ouvre sans erreur console | I `test_smoke_sweep` | ✅ **fr/en/it × clair/sombre** |

## 2. Sous-onglets Paramètres (7, `data-pmode`)

| # | Sous-onglet | À couvrir | Statut |
|---|---|---|---|
| S01 | **display** (Affichage) | thème, langue, contraste WCAG, options d'affichage | ✅ (thème/langue via smoke, **contraste WCAG** `test_settings`) · ⬜ options d'affichage fines |
| S02 | **grid** (Grille de cotation) | axes, criticité, méthode de score, transposition, tailles 3×3/5×5 | ✅ (**édition UI** : ajout/suppr. niveau d'axe, libellé, méthode de score, ajout/suppr. criticité — `test_grid` ; transposition + grilles 3×3/5×5 via fixtures/unit) |
| S03 | **fields** (Champs personnalisés) | CRUD d'un champ perso, types, bornes, filtrable, réordonnancement | ✅ (**création, édition, réordonnancement, suppression** + validation 18 types en unit) |
| S04 | **objtypes** (Types d'objets) | CRUD d'un type, attributs, préfixe d'id | ✅ (**réordonnancement, suppression en cascade**, ouverture éditeur) · ⬜ création UI d'un type |
| S05 | **report** (Rapport) | sections & ordre, page de garde, en-tête/pied, colonnes, matrices, orientation, éclaté | 🟡 (**activation/désactivation de section** + reflet dans `reportCfg`, présence des contrôles de structure — `test_report_settings`) · ⬜ ordre (glisser), page de garde, en-tête/pied, orientation |
| S06 | **stats** (Statistiques) | blocs par défaut, cibles | 🟡 (bascule on/off d'un bloc + réinitialisation → `test_stats`) · ⬜ cibles numériques, formes/affichage, réordonnancement |
| S07 | **radars** (Radars) | poids pondérés, rendu (luminosité/saturation/contour/pas/couleurs) | ✅ (poids pondéré, curseur de rendu → `radarCfg`, réinitialisation — `test_radars`) |
| — | smoke | chaque sous-onglet s'ouvre sans erreur console | ✅ **fr/en/it × clair/sombre** |

## 3. Menus & barre supérieure

| # | Élément | À couvrir | Suite | Statut |
|---|---|---|---|---|
| M01 | Menu **Fichier** : ouverture + Nouvelle analyse | confirmation, remise à zéro | I `test_menus` | ✅ (ouverture menu, reset) |
| M02 | Fichier : Charger `.rae.json` | sélection + `applyLoadedData` | I `test_menus` | ⬜ |
| M03 | Fichier : Enregistrer / Enregistrer sous | mécanisme (sans clic natif) | I `test_menus` | ⬜ |
| M04 | Fichier : Enregistrer comme modèle | squelette | I `test_menus` | ⬜ |
| M05 | Fichier : Exporter Word (natif) | → §5 | X | ⬜ |
| M06 | Fichier : Exporter avec un modèle Word | → §5 | X | ⬜ |
| M07 | Fichier : Exporter Excel / CSV | → §5 | X | ⬜ |
| M08 | Sélecteur **langue** (fr/en/it) | bascule d'interface | I/U | ✅ (smoke fr/en/it) |
| M09 | Sélecteur **thème** (clair/sombre) | bascule `data-theme` | I | ✅ (smoke clair/sombre) |
| M10 | Écran d'**accueil** | démo, charger, nouvelle, récents | I `test_menus` | ⬜ |
| M11 | **Fichiers récents** | IndexedDB, ouverture, vidage | I `test_persistence` | ⬜ |

## 4. Modales & transverses

| # | Élément | À couvrir | Suite | Statut |
|---|---|---|---|---|
| D01 | Modale **risque / mesure / lien / objet** | ouverture au clic cellule + focus colonne, validation, enregistrement | I | ⬜ |
| D02 | Modale **type d'objet / attribut / champ perso** | CRUD, types, validation | I | ⬜ |
| D03 | **Champ fautif** (focus + contour rouge) | libellé manquant, id dupliqué, perso obligatoire/hors bornes | I `test_modals_focus` | ✅ (libellé manquant, **id dupliqué** → focus/`.field-bad` + message) · ⬜ perso obligatoire/hors bornes |
| D04 | **Empilement / focus / inert** | confirmation par-dessus modale, restitution focus, Échap | I `test_modals_focus` | ✅ (confirmation empilée → modale sous-jacente `inert`, retour actif après fermeture) · ⬜ restitution focus précis, Échap |
| D05 | **Lightbox** image | ouverture/fermeture, depuis modale | I `test_modals_focus` | ✅ (ouverture, fermeture programmée, **fermeture par Échap**) · ⬜ depuis modale, clic fond/croix |
| D06 | **Import CSV** (risques/mesures/liens/objets) | mappage colonnes, erreurs par ligne, commit | I `test_import_csv` | 🟡 (ouverture modale + collage + commit risques/mesures) · ⬜ mappage colonnes, erreurs par ligne, liens/objets |
| D07 | **Filtres** (natifs + champs perso) | application, recherche, reset | I `test_filters_sort_columns` | ✅ (catégorie, recherche) · ⬜ champs perso, propagation liens |
| D08 | **Tri** (3 états) & **colonnes perso** (menu, ordre, épingle) | | I `test_filters_sort_columns` + `test_columns` | ✅ (**tri 3 états** registre + objets, menu colonnes, **visibilité + ordre**, **colonne épinglée reste en tête**) |
| D09 | **Glisser-déposer** (kanban, lignes, pastilles matrices) + alternatives clavier | | I `test_keyboard` | ✅ (**alternatives clavier** : kanban Ctrl+flèches, réordonnancement de ligne, nav onglets/menu) · ⬜ glisser-déposer souris, pastilles matrices |
| D10 | **Persistance** save→reload, **autosave**, restauration | | I `test_persistence` | ✅ (aller-retour sérialisation, **autosave IndexedDB** write→read→clear) · ⬜ restauration au démarrage, récents |
| D11 | **i18n** parité + rendu fr/en/it | | U `test_i18n` + I | ✅ (parité unit + rendu smoke fr/en/it) |
| D12 | **Accessibilité** (ARIA tablist, roving tabindex, focus visible) | | I | ⬜ |
| D13 | **Toasts** (notification, action/annulation) | message affiché, bouton d'action déclenche le callback + masque, toast réel sur suppression | I `test_toasts` | ✅ |

## 5. Exports bureautiques

| # | Export | À couvrir | Suite | Statut |
|---|---|---|---|---|
| X01 | **Rapport HTML** | sections, détail risques (2 panneaux) | I `test_report` | ✅ (rendu écran, panneaux, volumineuse) · ⬜ éclaté |
| X02 | **Word natif** (`buildDocx`) | paquet OOXML, détail, matrices (image), champs perso couleur/image | X `test_word_native` | ✅ (paquet valide, risque+panneaux, médias, image cf) · ⬜ radars/stats détaillés |
| X03 | **Word via gabarit** (`tmpl*`) | boucles, conditions, blocs, images, objets | X `test_word_template` | ✅ (11 gabarits valides rendus) |
| X04 | Word gabarit — **cas d'erreur** | messages non bloquants | X `test_word_template` | ✅ (**31 gabarits d'erreur → avertissement**, sans plantage) |
| X05 | **Excel** (`buildXlsx`) | paquet OOXML, données | X `test_excel` | ✅ (paquet valide, libellé de risque présent) |
| X06 | **CSV** export + import + **round-trip** | export, analyse, et **aller-retour export→réimport** | X `test_csv_export` (+ objets : `test_computed_advanced` IMP3) | ✅ round-trip risques/mesures/liens + objets |

## 6. Moteurs internes (unit)

| # | Domaine | À couvrir | Suite | Statut |
|---|---|---|---|---|
| U01 | **Moteur d'expression** | lexer, précédence, fonctions, IF, dates, texte, erreurs, agrégats, traversée réf. | U `test_expression` + `test_computed_fields` | ✅ (68 cas + entité/référence/cycle) |
| U02 | **Modèle & grille** | `scoreOf`, `critFor`, `residual`, `validateStructure`, transposition | U `test_model` | ✅ |
| U03 | **Champs perso** (18 types) | `cfControlHTML` / `cfValidate` par type | U `test_custom_fields` | ✅ (validation + contrôle des 18 types) |
| U04 | **i18n** | parité des clés fr/en/it (pas d'orphelin en/it, clés à espace de noms identiques) | U `test_i18n` | ✅ |
| U05 | **CSV** | parse (séparateur, guillemets) | U `test_csv` | ✅ |
| U06 | **OOXML** | primitives `dx*` (fragments bien formés) + `buildDocx`/`buildXlsx` (export) | U `test_ooxml` + X | ✅ |
| U07 | **Markdown** | sous-ensemble GFM, sécurité (échappement, filtrage URL) | U `test_markdown` | ✅ |

## 7. Lanes optionnelles

| # | Lane | À couvrir | Suite | Statut |
|---|---|---|---|---|
| P01 | **PDF** (LibreOffice) | Word natif + gabarit convertis en PDF, non-plantage | X `test_pdf` `@pdf` | ✅ (2 conversions) |
| Vz1 | **Visuel** (captures) | baseline par écran, tolérance | V `test_screenshots` + `test_visual_ui` `@visual` | ✅ (84 baselines **pleine page** : chrome barre haut/nav + 11 onglets + matrices trajectoire/8 dispositions + radars 4 modes + menu Fichier + 7 sous-onglets + 8 modales, × fr clair/sombre) · ⬜ en/it |

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
