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
| `test-objets/` (sections A–N) | `ui/test_objects` (types/instances, **création d'instance**, **nettoyage anti-fantôme**, **cascade/intégrité référentielle**, référence) + `ui/test_persistence` + `unit/test_computed_advanced` (RH + round-trip objet) | ✅ **supersédé** | (mineur : filtres UI sur références) |
| `test-rapport-word/` (classique + éclaté) | `export/test_word_native` (natif + **rapport éclaté** par risque/catégorie) + `ui/test_report` | ✅ **supersédé** | rien |
| `test-rapport-images/` (images/couleur/calculé) | `export/test_word_images` (**médias, dessins, couleur both/swatch/hex, ■, tailles EMU**) | ✅ **supersédé** | rien |
| `test-image-dims/` (EMU) | `export/test_word_images` (`width=4`→1440000×720000, `height=1`→720000×360000, W4H1) | ✅ **supersédé** | rien |
| `test-stats/` (stats) | `export/test_word_template` (rendu `modele-stats*`) + `ui/test_stats` (**statCounters** sur analyse de contrôle) | ✅ **supersédé** | rien |
| `test-conditions/` (conditions gabarit) | `export/test_word_template_control` (**branches CACHÉ non rendues, 0 balise résiduelle**) | ✅ **supersédé** | rien |
| `test-modele-word-objets/` (generic + lot9) | `export/test_word_template` (`generic-modele`) + `export/test_word_template_control` (**lot9** : 0 avertissement/accolade) | ✅ **supersédé** | rien |
| `test-badges/` | `export/test_word_template_control` (badges → cellules teintées, 0 avertissement) | ✅ **supersédé** | rien |
| `test-prooferr/` | `export/test_word_template_control` (**balises scindées par proofErr résolues**, 0 avertissement/accolade) | ✅ **supersédé** | rien |

## Recommandation

**Tous les dossiers `travaux/test-*` sont désormais supersédés et vérifiés** (259 tests verts). Ils sont
**supprimables** :

```
travaux/test-badges/         travaux/test-champs-calcules/  travaux/test-conditions/
travaux/test-image-dims/     travaux/test-modele-word-objets/  travaux/test-modeles-erreurs/
travaux/test-objets/         travaux/test-prooferr/         travaux/test-rapport-images/
travaux/test-rapport-word/   travaux/test-stats/
```

Reste un point mineur non porté : les **filtres UI sur champs de référence** (le reste des objets est
couvert). `travaux/` étant gitignoré, la suppression est un simple `rm` local (réversible seulement par
recréation), à faire sur ton accord explicite.

> Note : les **jeux de données** épars de `travaux/` (`acme-test/`, `aipd*/`, `.tuto-serve/`, `tests/`…)
> utiles aux tests ont été repris dans `tests/fixtures/`. Les autres contenus de `travaux/` (maquettes,
> plan de communication, revues, SVG…) **ne sont pas des tests** et sortent de ce périmètre.
