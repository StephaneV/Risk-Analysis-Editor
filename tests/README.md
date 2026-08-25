# Tests — Risk Analysis Editor

Suite de tests **complète, reproductible et versionnée** de l'application `app/risk-analysis-editor.html`.
Objectif : couvrir **chaque écran, onglet, sous-onglet, menu et modale**, les moteurs internes (expression,
champs perso, export Word/Excel/CSV), l'i18n (fr/en/it) et les thèmes (clair/sombre).

> Ce dossier est **versionné** (contrairement à `travaux/`, qui reste un bac à sable jetable et gitignoré).
> Les scripts et les fixtures sont suivis par Git ; **seuls les artefacts générés** (`_artifacts/`) sont ignorés.

---

## 1. Stack technique

| Rôle | Outil | Notes |
|---|---|---|
| Runner de tests | **pytest** | sélection, paramétrage (langue × thème), marqueurs de lane, rapport JUnit |
| Pilotage navigateur | **Playwright (API sync, Python)** | charge une **copie** de l'app, exécute du JS in-page, pilote l'UI |
| Navigateur | **Chromium embarqué** (`playwright install chromium`) | versionné avec Playwright → reproductible, indépendant du navigateur système |
| Inspection export | **unzip OOXML** maison (`harness/ooxml.py`) | ouvre `.docx`/`.xlsx`, asserte le XML/structure |
| Rendu PDF *(lane optionnelle)* | **LibreOffice** (`soffice --headless`) | conversion `.docx` → `.pdf` |
| PDF → PNG *(lane optionnelle)* | **poppler** (`pdftoppm`) | pour l'inspection/visuel |

**Pourquoi un vrai navigateur (et pas jsdom/Vitest)** : l'application utilise des API navigateur réelles —
File System Access, IndexedDB (autosave/récents), `<canvas>`, mesure géométrique SVG, impression, presse-papiers.
Seul un navigateur piloté (Playwright) permet de les exercer fidèlement **et** d'appeler les fonctions internes.

---

## 2. Arborescence

```
tests/
├── README.md                     # ce fichier
├── TEST-PLAN.md                  # MATRICE DE COUVERTURE : chaque écran/onglet/menu/modale → IDs de test
├── requirements.txt              # dépendances Python (pytest, playwright, Pillow)
├── pytest.ini                    # config pytest (marqueurs, pythonpath)
├── conftest.py                   # fixtures pytest (browser, base_url, app), options --lang/--theme,
│                                 #   skip des lanes, écriture TEST-REPORT.md / results.json / junit.xml
├── run-all.py                    # point d'entrée unique : lance les suites et agrège le rapport
│
├── harness/                      # socle technique partagé (pas des tests)
│   ├── __init__.py
│   ├── browser.py                #   serveur HTTP local + chemins du dépôt
│   ├── app.py                    #   « page-object » : goto/settings_subtab/open_file_menu, load,
│   │                             #   set_lang/set_theme, click/set_input/modal_open,
│   │                             #   view/element/full_screenshot, docx_bytes…
│   ├── ooxml.py                  #   unzip + inspection docx/xlsx
│   ├── render.py                 #   conversion .docx → PDF via LibreOffice (lane PDF)
│   ├── exports.py                #   sauvegarde des livrables produits → _artifacts/exports/ (examen humain)
│   └── visual.py                 #   comparaison d'images (Pillow) + conservation des captures / diff
│
├── fixtures/                     # jeux de données de test (VERSIONNÉS)
│   ├── README.md                 #   description de chaque fixture
│   ├── analyses/                 #   21 analyses .rae.json (vide, minimale, ebios(-objets/-en), aipd(-objets),
│   │   │                         #   dpia-en, si, tous-types-champs, échelles/calculés, images/couleurs,
│   │   │                         #   grilles 3×3/5×5/transposée, titre-long, volumineuse, contrôle stats/conditions/
│   │   │                         #   badges, configs rapport classique/éclaté…)
│   │   └── malformes/            #     3 fichiers invalides (chemin d'erreur)
│   ├── csv/                      #   3 imports « Système d'information »
│   ├── word-templates/           #   14 gabarits .docx + erreurs/ (31 cas e01..e30) — fixtures binaires
│   └── generators/
│       └── make_fixtures.py      #   (re)génère les fixtures synthétiques, auto-validées
│
├── suites/                       # les tests, par couche
│   ├── unit/                     #   fonctions internes (JS in-page) — rapide, sans UI
│   │   ├── test_expression.py        #  moteur de formules (68 cas)
│   │   ├── test_computed_advanced.py #  cas avancés J/E/LF/MV/RH/IMP/CI (porté de test-champs-calcules)
│   │   ├── test_computed_fields.py   #  cfComputedValue sur la fixture kitchen-sink
│   │   ├── test_model.py             #  scoreOf/critFor/residual/transpose/validateStructure
│   │   ├── test_i18n.py              #  parité des clés fr/en/it
│   │   ├── test_custom_fields.py     #  cfValidate/cfControlHTML par type (18)
│   │   ├── test_csv.py               #  parseCSV
│   │   ├── test_ooxml.py             #  primitives dx*
│   │   └── test_markdown.py          #  rendu + sécurité
│   ├── ui/                       #   fonctionnel : pilotage de la vraie UI
│   │   ├── test_smoke_sweep.py       #  EXHAUSTIF : chaque écran/sous-onglet — fr/en/it × clair/sombre
│   │   ├── test_fixtures_load.py     #  chargement des fixtures + rejet des malformées
│   │   ├── test_presentation.py  test_risks.py  test_measures.py  test_links.py  test_objects.py
│   │   ├── test_matrices.py  test_radars.py  test_stats.py  test_plan.py  test_report.py
│   │   ├── test_settings.py          #  7 sous-onglets + champ perso + mode contraste
│   │   ├── test_report_settings.py   #  Paramètres › Rapport : sections (on/off), structure
│   │   ├── test_grid.py              #  grille : niveaux d'axe, méthode de score, criticité
│   │   ├── test_columns.py           #  colonnes des registres : visibilité + ordre
│   │   ├── test_keyboard.py          #  navigation clavier (onglets, kanban, réordonnancement)
│   │   ├── test_import_csv.py        #  modale d'import CSV (risques/mesures)
│   │   ├── test_menus.py             #  menu Fichier + nouvelle analyse
│   │   ├── test_crud.py              #  CRUD : risques/mesures/champs perso/types & instances/blocs stats
│   │   ├── test_filters_sort_columns.py  #  filtres + tri 3 états (registre & objets)
│   │   ├── test_modals_focus.py      #  champ fautif, id dupliqué, clic cellule, empilement/inert, Échap, lightbox, URL sans modale
│   │   ├── test_reference_entities.py #  champ « référence » ciblant risques/mesures (picker, affichage, filtre)
│   │   ├── test_a11y.py              #  ARIA tablist/tab + aria-selected suit l'onglet actif
│   │   ├── test_toasts.py            #  notifications (message, action/annulation)
│   │   └── test_persistence.py       #  aller-retour sérialisation + sauvegarde auto (IndexedDB)
│   ├── export/                   #   artefacts bureautiques + inspection OOXML
│   │   ├── test_word_native.py       #  buildDocx + rapport éclaté
│   │   ├── test_word_template.py     #  moteur de gabarit (valides + 31 cas d'erreur)
│   │   ├── test_word_template_control.py  #  conditions/prooferr/badges/lot9 (analyses de contrôle)
│   │   ├── test_word_images.py       #  images/couleur/calculé + tailles EMU
│   │   ├── test_excel.py             #  buildXlsx
│   │   ├── test_csv_export.py        #  export/import + aller-retour (round-trip)
│   │   └── test_pdf.py               #  @pdf : conversion PDF (LibreOffice)
│   └── visual/                   #   régression visuelle (lane @visual)
│       ├── test_screenshots.py       #  scènes PLEINE PAGE : chrome (barre haut/nav), 11 onglets,
│       │                             #  matrices (trajectoire + 8 dispositions), radars (4 modes)
│       ├── test_visual_ui.py         #  menu Fichier, 7 sous-onglets Paramètres, 8 modales (bornés à l'élément)
│       └── baselines/                #  84 PNG de référence (VERSIONNÉS)
│
└── _artifacts/                   # SORTIES GÉNÉRÉES — gitignoré (tout sauf .gitignore)
    ├── .gitignore                #   ignore tout sauf lui-même
    └── exports/                  #   livrables produits par les tests d'export (Word/Excel/CSV/PDF),
                                  #   conservés pour examen — jamais effacés, jamais versionnés
```

> Le rapport agrégé (`TEST-REPORT.md`, `results.json`, `junit.xml`) est écrit par un hook de
> `conftest.py`, pas par un module dédié. Le rendu du rapport HTML de l'application est un test
> **UI** (`suites/ui/test_report.py`), pas un export de fichier.

---

## 3. Prérequis & installation

```bash
# 1) Dépendances Python (cœur)
pip install -r tests/requirements.txt
python -m playwright install chromium

# 2) (Lane PDF, optionnelle) LibreOffice installé sur la machine (fournit `soffice`)
# 3) (Lane visuelle) Pillow — déjà dans requirements.txt ; captures via Playwright (pas de poppler requis)
```

Le **cœur** (unit + UI + export/OOXML) ne dépend que de **Python + Playwright + Chromium**. La lane **PDF**
requiert **LibreOffice** ; la lane **visuelle** requiert **Pillow** (dans `requirements.txt`) et compare des
**captures Playwright** (aucun rendu PDF ni poppler). Les deux lanes sont **isolées** (voir §5).

---

## 4. Commandes

Toutes les commandes se lancent **depuis la racine du dépôt**.

```bash
# Tout le cœur (sans les lanes lourdes) — la commande du quotidien
pytest tests -m "not pdf and not visual"
```

```bash
# Suite unique
pytest tests/suites/ui/test_risks.py
```

```bash
# Un seul écran / un seul cas (par nom)
pytest tests -k "matrices and trajectoire"
```

```bash
# Une langue / un thème précis (paramétrage)
pytest tests -k "smoke" --lang fr --theme dark
```

```bash
# Inclure la lane PDF (nécessite LibreOffice)
pytest tests -m "pdf"
```

```bash
# Inclure / mettre à jour la lane visuelle (captures)
pytest tests -m "visual"            # compare aux baselines
pytest tests -m "visual" --update-baselines   # régénère les PNG de référence
```

```bash
# Point d'entrée unique : lance TOUTES les suites activées et agrège le rapport
python tests/run-all.py                 # cœur seul
python tests/run-all.py --with-pdf --with-visual   # tout
```

> `run-all.py` renvoie un **code de sortie non nul** si un test échoue (utilisable en pré-commit).

---

## 5. Emplacement des résultats

| Sortie | Emplacement | Suivi Git |
|---|---|---|
| Rapport lisible agrégé | `tests/_artifacts/TEST-REPORT.md` | non (généré) |
| Résultats machine | `tests/_artifacts/results.json` | non |
| Rapport JUnit (CI éventuelle) | `tests/_artifacts/junit.xml` | non |
| Exports produits pendant les tests (Word/Excel/CSV + `gabarits/`) — **conservés pour examen** | `tests/_artifacts/exports/` | non |
| Rendus PDF/PNG (lane PDF) | `tests/_artifacts/render/*.pdf|png` | non |
| Captures de la lane visuelle (chaque run, **conservées pour examen**) | `tests/_artifacts/visual/<scène>.png` | non |
| Comparatif en cas d'écart : capture courante + baseline + différence amplifiée | `tests/_artifacts/visual/_diff/<scène>.{current,baseline,diff}.png` | non |
| **Baselines visuelles de référence** | `tests/suites/visual/baselines/*.png` | **oui** (versionnées) |

**Règle** : tout ce qui est **généré** va dans `tests/_artifacts/` (gitignoré). Seuls **scripts, fixtures et
baselines** sont versionnés. Ne jamais committer le contenu de `_artifacts/`.

---

## 6. Grands principes

- **Auto-contenu.** Aucune dépendance à un fichier hors dépôt : toutes les fixtures vivent dans
  `tests/fixtures/`. (Corrige notamment l'ancien `travaux/test-objets` qui pointait vers un dépôt Website
  externe.) Les gabarits Word sont des **fixtures binaires versionnées** — pas de génération Node au moment des tests.
- **Déterminisme.** Chaque test fixe explicitement **langue** et **thème**, **réinitialise IndexedDB**
  (autosave + récents) et l'état global avant de s'exécuter, **désactive les animations**, et n'utilise pas
  `Date.now()`/`Math.random()` sans les neutraliser. Deux exécutions successives → résultat identique.
- **Lanes optionnelles isolées.** Les lanes à prérequis lourds (**PDF** via LibreOffice, **visuelle** via
  captures) sont marquées (`@pytest.mark.pdf`, `@pytest.mark.visual`) et **exclues par défaut**. Le cœur reste
  **vert sur une machine minimale** (Python + Playwright uniquement).
- **Couverture à 2 niveaux.** (1) un **smoke sweep exhaustif** paramétré `écran × langue × thème` garantit que
  chaque onglet/sous-onglet/menu/modale **s'ouvre et se rend sans erreur console** ; (2) des **tests fonctionnels
  ciblés** vérifient en profondeur les comportements de chaque feature.
- **`TEST-PLAN.md` = contrat d'exhaustivité.** La matrice de couverture y liste **chaque** écran/onglet/menu/modale
  et l'associe à des **IDs de test**. C'est la référence pour juger l'exhaustivité et repérer les trous.
- **Pyramide.** Beaucoup d'**unit** (rapides, ciblent les fonctions internes), une couche **UI** solide, une couche
  **export** qui inspecte réellement les fichiers produits (OOXML/CSV), une lane **visuelle** en complément.
- **Mono-fichier respecté.** Les tests chargent l'app telle qu'elle est livrée (un seul HTML) ; ils ne
  présupposent aucun découpage en modules.
- **Isolation.** Chaque test repart d'un état propre (fixture chargée via `applyLoadedData`, DOM/modales purgés) ;
  aucun test ne dépend de l'ordre d'exécution.

---

## 7. Points d'attention

- **Copie de l'app.** Les tests chargent une **copie** de `app/risk-analysis-editor.html` (jamais l'original en
  écriture) pour éviter tout effet de bord ; le chemin de l'app est centralisé dans le harnais.
- **IndexedDB partagée.** Autosave et récents persistent entre exécutions dans le profil du navigateur → le harnais
  **vide ces stores** en début de test, sinon la boîte « analyse non enregistrée retrouvée » et les récents
  polluent l'UI (piège rencontré pendant l'audit).
- **Modales résiduelles.** Après un test qui ouvre des modales empilées, purger `dynModals` et les `.modal-bg`
  fantômes, sinon le focus/`inert` d'un test fuit sur le suivant.
- **File System Access / téléchargements.** `showSaveFilePicker` et les téléchargements réels ne sont pas pilotables
  simplement : les tests d'export **interceptent le blob** en interne (`buildDocx()`/`buildXlsx()`/CSV) plutôt que
  de cliquer « Enregistrer », puis inspectent l'OOXML.
- **Lane visuelle fragile.** Les captures dépendent des polices et de l'anticrénelage de la machine : comparer avec
  une **tolérance**, et **ne régénérer les baselines** (`--update-baselines`) qu'après revue humaine.
- **Prérequis des lanes.** Si LibreOffice/poppler manquent, la lane PDF est **sautée** (skip), pas en échec.
- **Durée.** Le smoke sweep multiplie écrans × langues × thèmes : garder chaque cas court (ouvrir + vérifier),
  réserver les assertions lourdes aux tests fonctionnels ciblés.
- **Ne pas committer `_artifacts/`.** Vérifier que le `.gitignore` du dossier est en place avant tout commit.

---

## 8. Statut de construction

La suite est bâtie par **phases** (voir l'historique de mise en place) : socle & matrice de couverture →
fixtures → unit → UI → export → lanes PDF/visuelle → finalisation. L'état d'avancement détaillé et la
correspondance avec les tests existants de `travaux/` sont tenus dans **[TEST-PLAN.md](TEST-PLAN.md)**.
