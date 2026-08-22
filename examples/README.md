# Analyses de démonstration

Ce dossier contient des **analyses de risques prêtes à ouvrir**, au format `.rae.json`
(voir la [spécification du format](../specs/SPEC-format-analyse-risque.md) et son
[schéma JSON](../specs/schema-analyse-risque.json)). Elles servent à **découvrir l'outil**,
d'appui aux [tutoriels](https://www.youtube.com/@RiskAnalysisEditor) et de **point de départ**
réutilisable. Chacune met en avant les fonctionnalités de l'éditeur (descriptions et notes en
Markdown, **étiquettes** colorées, **barres de progression**, propriétaires, justification par lien,
champs personnalisés, objets et références, etc.).

> ⚠️ Ces analyses sont **fictives** et à visée **pédagogique** (données inventées). Elles ne
> constituent **ni des analyses réelles, ni des modèles officiels ou une preuve de conformité**.
> Elles sont seulement **inspirées** des démarches citées : elles n'en appliquent pas
> intégralement le formalisme et n'engagent **ni l'ANSSI ni la CNIL**, qui n'en sont pas à l'origine.

## Les exemples

| Fichier | Langue | Cadre | Contenu |
|---|---|---|---|
| [`demo-ebios-rm-systeme-d-information.rae.json`](demo-ebios-rm-systeme-d-information.rae.json) | 🇫🇷 fr | Inspiré d'**EBIOS RM** (ANSSI) et d'ISO 27005 | 12 risques · 11 mesures · 10 champs perso |
| [`demo-ebios-rm-systeme-d-information-objets.rae.json`](demo-ebios-rm-systeme-d-information-objets.rae.json) | 🇫🇷 fr | Inspiré d'**EBIOS RM** (ANSSI) et d'ISO 27005 | 12 risques · 11 mesures · 15 champs perso · **5 types d'objets, 32 objets** |
| [`demo-ebios-rm-information-system.rae.json`](demo-ebios-rm-information-system.rae.json) | 🇬🇧 en | **EBIOS RM**-inspired (ANSSI) & ISO 27005 | 12 risques · 11 mesures · 10 champs perso |
| [`demo-aipd-sst.rae.json`](demo-aipd-sst.rae.json) | 🇫🇷 fr | Volet analyse de risques d'une **AIPD**, inspiré de la méthode **PIA de la CNIL** (RGPD art. 35) | 12 risques · 12 mesures · 9 champs perso |
| [`demo-aipd-sst-objets.rae.json`](demo-aipd-sst-objets.rae.json) | 🇫🇷 fr | Volet analyse de risques d'une **AIPD**, inspiré de la méthode **PIA de la CNIL** (RGPD art. 35) | 12 risques · 12 mesures · 12 champs perso · **6 types d'objets, 32 objets** |
| [`demo-dpia-ohs.rae.json`](demo-dpia-ohs.rae.json) | 🇬🇧 en | Risk-analysis part of a **DPIA**, inspired by the CNIL **PIA** method (GDPR art. 35) | 12 risques · 12 mesures · 9 champs perso |

Les variantes **« avec objets »** (`…-objets`) reprennent l'analyse correspondante en y ajoutant un
**inventaire d'objets** (valeurs métier, biens supports, parties prenantes…) reliés aux risques par
des **champs de référence**, pour illustrer l'onglet *Objets* et les valeurs calculées par référence.

## Ouvrir un exemple

- **Depuis l'application en ligne** (ou servie par un serveur local) : à l'écran d'accueil, bouton
  **« Ouvrir une analyse de démonstration »** ; ou en passant le fichier en paramètre d'URL, par ex.
  `…/app/risk-analysis-editor.html?file=../examples/demo-ebios-rm-systeme-d-information.rae.json`.
- **En local, par double-clic sur le fichier HTML** (mode `file://`) : les navigateurs interdisent la
  lecture d'un fichier voisin, donc le bouton de démonstration est masqué. Utilisez alors le menu
  **Fichier › Charger un fichier `.rae.json`…** et choisissez l'un des fichiers de ce dossier.

> Les exemples ouverts par le bouton d'accueil de l'application sont
> [`demo-ebios-rm-systeme-d-information.rae.json`](demo-ebios-rm-systeme-d-information.rae.json) (interface en
> français) et [`demo-ebios-rm-information-system.rae.json`](demo-ebios-rm-information-system.rae.json)
> (interface en anglais).

Pour prendre l'outil en main écran par écran, voir le **[guide utilisateur](../docs/guide-utilisateur.md)**.
