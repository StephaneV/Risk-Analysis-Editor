# Outils

Scripts d'appoint pour la documentation et la fabrication de l'application, et un validateur de
fichiers. Chaque outil a sa documentation `.md` du même nom.

| Outil | Rôle | Documentation |
|---|---|---|
| `shots-guide.py` | Captures du **guide utilisateur** (démo AIPD, FR, thème clair, 1280 px) → `docs/images/guide-*.png`. | [`shots-guide.md`](shots-guide.md) |
| `shots-readme.py` | Captures des **README** (démo EBIOS RM, EN, thème clair, 1180 px, ×2) → `docs/images/capture-*.png`. | [`shots-readme.md`](shots-readme.md) |
| `embed-templates.py` | **Embarque les modèles** (`templates/*.rae.json`) dans l'application → `app/risk-analysis-editor.html`. | [`embed-templates.md`](embed-templates.md) |
| `rae-validator/` | **Valide un fichier `.rae.json`** (format + cohérence : références/champs orphelins, doublons, obligatoires, formules…). Outil HTML autonome, hors‑ligne. | [`rae-validator/README.md`](rae-validator/README.md) |

Toutes les commandes se lancent **depuis la racine du dépôt**. Reportez-vous à la documentation de
chaque outil pour les prérequis, l'utilisation détaillée et les options.
