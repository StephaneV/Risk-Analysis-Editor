# Ressources — bibliothèques tierces embarquées

Ce dossier conserve les **bibliothèques tierces** intégrées (inlinées) dans l'application
`app/risk-analysis-editor.html`. L'application est **un fichier HTML autonome** : ses dépendances y
sont copiées directement plutôt que chargées depuis le réseau. On garde ici l'original de chaque
bibliothèque pour la **traçabilité** (version, licence) et pour faciliter les **mises à jour**.

| Fichier | Bibliothèque | Version | Licence | Source |
|---|---|---|---|---|
| `fflate-0.8.2.umd.js` | [fflate](https://github.com/101arrowz/fflate) — compression/décompression DEFLATE et archives ZIP, en JavaScript pur | 0.8.2 | MIT — © 2020-2023 Arjun Barrett | https://github.com/101arrowz/fflate · https://www.npmjs.com/package/fflate |

## Usage dans l'application

`fflate` sert à produire les **exports bureautiques**, qui sont des archives **ZIP** : le document
Word (`.docx`) et le classeur Excel (`.xlsx`). Le build **UMD** (ce fichier) est copié tel quel dans le
`<script>` de l'application.

## Mettre à jour une bibliothèque

1. Remplacer le fichier de ce dossier par la nouvelle version (même nommage `nom-version.umd.js`).
2. Reporter son contenu dans le bloc `<script>` correspondant de `app/risk-analysis-editor.html`
   (repérable par la bannière de licence `/*! fflate v… */`).
3. Mettre à jour le tableau ci-dessus (version, licence si besoin).
