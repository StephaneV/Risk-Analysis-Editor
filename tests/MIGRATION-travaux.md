# Migration des anciens tests de `travaux/`

Correspondance entre les tests historiques (dans `travaux/`, **gitignoré/jetable**) et la nouvelle
suite versionnée `tests/`. Sert à décider, **avec l'accord de l'utilisateur**, quels dossiers de
`travaux/` peuvent être supprimés.

**Verdict** : ✅ supersédé (supprimable) · 🟡 partiellement migré (porter les vérifications fines
avant suppression) · ⬜ non migré (garder tel quel pour l'instant).

> Principe d'honnêteté : la nouvelle suite couvre **largement les fonctionnalités** (smoke + fonctionnel
> + export + rendu des 31 gabarits d'erreur), mais plusieurs anciens tests portent des **assertions
> plus fines** (valeurs exactes, tailles EMU, combinaisons de mise en page) qui ne sont pas encore
> reproduites. Rien n'est supprimé sans validation.

| Dossier `travaux/` | Couvert par `tests/` | Verdict | À porter avant suppression |
|---|---|---|---|
| `test-modeles-erreurs/` (30+1 cas) | `export/test_word_template` (les 31 gabarits → avertissement) + gabarits repris dans `fixtures/word-templates/erreurs/` | ✅ **supersédé** | rien (éventuellement garder `cas-d-erreurs.md` comme doc) |
| `test-champs-calcules/` (127 cas) | `unit/test_expression` (68 purs) + `unit/test_computed_advanced` (53 : J/E/LF/MV/RH/IMP/CI, JS rejoué à l'identique) + `unit/test_computed_fields` (4) | ✅ **supersédé** (127/127 portés et verts) | rien |
| `test-objets/` (sections A–N) | `ui/test_objects` + `ui/test_persistence` + `unit/test_computed_fields` | 🟡 **partiel** | **contexte fantôme** (collisions d'id entre modales), **CRUD** instance complet, **intégrité référentielle**, **filtres sur références** |
| `test-rapport-word/` (classique + éclaté) | `export/test_word_native` (natif) + `ui/test_report` | 🟡 **partiel** | rapport **éclaté** (par catégorie / par risque) |
| `test-rapport-images/` (images/couleur/calculé) | `export/test_word_native` (présence de médias + image cf) | 🟡 **partiel** | **tailles EMU** exactes (`width`/`height`), modes de rendu couleur (both/swatch/hex) |
| `test-stats/` (stats en gabarit) | `export/test_word_template` (rendu des gabarits `modele-stats*`) | 🟡 **partiel** | assertions de **mise en page** / combinaisons de graphiques |
| `test-conditions/` (conditions gabarit) | `export/test_word_template` (rendu des gabarits `modele-conditions*`) | 🟡 **partiel** | **résultats** attendus des conditions (branches prises/omises) |
| `test-modele-word-objets/` (generic + lot9) | `export/test_word_template` (rendu de `generic-modele`) | 🟡 **partiel** | spécificités **lot9** (restitution générique par type) |
| `test-image-dims/` | — | ⬜ **non migré** | dimensionnement d'image `width`/`height` (EMU) |
| `test-badges/` | — | ⬜ **non migré** | rendu des badges (chip/pill/flat) en Word |
| `test-prooferr/` | — | ⬜ **non migré** | erreurs de relecture (prooferr) |

## Recommandation

- **Supprimables maintenant** (supersédés et vérifiés) :
  - `travaux/test-champs-calcules/` — les **127 cas** sont portés et verts (`test_expression` + `test_computed_advanced` + `test_computed_fields`).
  - `travaux/test-modeles-erreurs/` — gabarits repris en fixtures + contrôle automatisé « chaque cas produit un avertissement » (plus robuste que l'ancien).
- **À conserver pour l'instant** : tous les autres dossiers 🟡/⬜, tant que leurs vérifications fines
  n'ont pas été portées. Je peux les **porter** (par priorité : les 127 cas de calcul complets, le
  contexte fantôme des objets, les tailles EMU d'images, le rapport éclaté), après quoi ils
  deviendront supprimables à leur tour.

> Note : les **jeux de données** épars de `travaux/` (`acme-test/`, `aipd*/`, `.tuto-serve/`, `tests/`…)
> utiles aux tests ont été repris dans `tests/fixtures/`. Les autres contenus de `travaux/` (maquettes,
> plan de communication, revues, SVG…) **ne sont pas des tests** et sortent de ce périmètre.
