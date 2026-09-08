# Modèles de démarrage (`templates/`)

Ce dossier contient les **modèles méthodologiques** livrés avec l'application : des **squelettes
d'analyse** prêts à remplir, au format `.rae.json`, **un fichier par langue** (`fr`, `en`, `it`) —
nommage `<base>.template.<lang>.rae.json`. À l'ouverture, un modèle démarre une **nouvelle analyse
non reliée** ; on peut aussi transformer l'analyse courante en modèle via *Fichier › Enregistrer
comme modèle…*.

> ⚠️ Ces fichiers sont **générés** (voir « Régénération » plus bas) : ne les éditez pas à la main,
> modifiez la source puis régénérez. `metadata.kind = "template"` ; risques / mesures / liens vides.

## Les modèles

**Modèles simples** (grille + niveaux de criticité + champs personnalisés préconfigurés, sans types
d'objets) :

| Base | Méthode |
|---|---|
| `ebios-rm.template` | EBIOS RM (ANSSI) — vraisemblance × gravité, grille 4×4 |
| `cnil-pia.template` | AIPD / PIA CNIL — grille 4×4 |
| `iso-27005.template` | ISO/IEC 27005 — vraisemblance × impact, grille 5×5 |
| `generique.template` | Générique — probabilité × impact 5×5, sans champ imposé |

**Modèles enrichis « objets »** (en plus : **types d'objets**, champs de référence et **rapport
pré-paramétré** ; dérivés des exemples enrichis correspondants) :

| Base | Méthode | Contenu |
|---|---|---|
| `ebios-rm-objets.template` | EBIOS RM (ANSSI) | 8 types d'objets · 19 champs · rapport |
| `cnil-pia-objets.template` | AIPD / PIA CNIL | 7 types d'objets · 19 champs · rapport |

Tous les modèles existent en **français, anglais et italien** et sont listés sous *Démarrer d'un
modèle* dans le bloc d'accueil de l'application.

## Régénération

Les deux familles ont des générateurs distincts. Après toute modification, régénérez **puis
ré-embarquez** dans l'application.

```bash
# 1a) modèles SIMPLES (depuis une définition unique par méthode) :
node templates/build-templates.js            # voir build-templates.md

# 1b) modèles ENRICHIS (dérivés des exemples enrichis de ../examples/) :
python templates/build-templates-enrichi.py  # libellés {fr,en,it}, sans données

# 2) ré-embarquer TOUS les modèles dans l'application :
python ../tools/embed-templates.py           # voir ../tools/embed-templates.md
```

- [`build-templates.md`](build-templates.md) — documentation du générateur des modèles **simples**.
- `build-templates-enrichi.py` — dérive les modèles **enrichis** des exemples
  [`../examples/`](../examples/) : grille + types d'objets + champs + rapport, **sans données**.
  Libellés multilingues `{fr,en,it}` (fr = exemple FR, en = exemple EN, it = récupéré des modèles
  existants + dictionnaire interne) ; toute chaîne italienne manquante est signalée. Codes
  identiques aux exemples.
- L'**embarquement** ([`../tools/embed-templates.py`](../tools/embed-templates.py)) réécrit le bloc
  `TEMPLATE_DATA` de l'application afin que les modèles s'ouvrent même en `file://`. Chaque nouveau
  modèle doit aussi être ajouté à la liste `TEMPLATES` de l'application (écran d'accueil).

Valider chaque fichier avec l'outil [`rae-validator`](../tools/rae-validator/) (cible : 0 erreur /
0 avertissement ; un modèle a des tableaux de données vides).
