"""Rapport Word à partir d'un gabarit (moteur tmpl*) : rendu des gabarits valides + cas d'erreur.

Généralise travaux/test-conditions, test-stats, test-modeles-erreurs.
"""
import base64

import pytest

from harness import exports, ooxml
from harness.browser import FIXTURES

pytestmark = pytest.mark.export

TPL_DIR = FIXTURES / "word-templates"

# Charge un .docx (base64) comme gabarit, le rend, renvoie {docx(base64), warnings[]}.
RENDER = r"""
async (b64) => {
  const bin = atob(b64);
  const u8 = new Uint8Array(bin.length);
  for (let i=0;i<bin.length;i++) u8[i] = bin.charCodeAt(i);
  const file = new File([u8], 't.docx');
  tmplWarnings.length = 0;
  try {
    const parts = await tmplLoadDocx(file);
    if (!parts || !parts['word/document.xml']) return { docx:null, warnings: tmplWarnings.concat(['DOCX_INVALIDE']) };
    const blob = await tmplRender(parts);
    const o = new Uint8Array(await blob.arrayBuffer());
    let s=''; const CH=0x8000;
    for (let i=0;i<o.length;i+=CH) s += String.fromCharCode.apply(null, o.subarray(i,i+CH));
    return { docx: btoa(s), warnings: tmplWarnings.slice() };
  } catch (e) {
    // erreur structurelle (zip corrompu, non-docx) : normalement traitée par tmplExport
    return { docx:null, warnings: tmplWarnings.concat(['LOAD_ERROR: ' + ((e&&e.message)||e)]) };
  }
}
"""


def _render(app, path):
    b64 = base64.b64encode(path.read_bytes()).decode()
    return app.js(RENDER, b64)


VALID_TEMPLATES = sorted(p for p in TPL_DIR.glob("*.docx"))
ERROR_TEMPLATES = sorted((TPL_DIR / "erreurs").glob("*.docx"))

# Analyse adaptée à chaque gabarit : le rendu sauvegardé « pour examen » est alors
# sémantiquement correct (au lieu d'un rendu contre une analyse quelconque, truffé de
# balises non résolues) et l'on peut durcir l'assertion là où les données résolvent tout.
DEFAULT_FIXTURE = "ebios-objets"
TPL_FIXTURE = {
    "modele-badges": "demo-badges",
    "modele-conditions-paragraphe": "analyse-test-conditions",
    "modele-conditions-tableau": "analyse-test-conditions",
    "modele-conditions-operateurs": "analyse-test-conditions",
    "modele-prooferr": "ebios",
    "modele-stats": "analyse-test-stats",
    "modele-stats-combinaisons": "analyse-test-stats",
    "modele-stats-graphiques": "analyse-test-stats",
    "modele-image-dims": "analyse-test-stats",
    # Démos cf couleur/photo/calc : ces cf n'existent dans AUCUNE fixture (ils sont
    # construits en mémoire par test_word_images.py, qui vérifie finement leur rendu).
    # Rendus ici en « fumée » seulement, contre l'analyse par défaut.
}

# Gabarits dont toutes les balises se résolvent avec la fixture associée : on exige
# 0 balise résiduelle (vrai garde-fou anti-régression). Les autres ne sont vérifiés
# qu'en « fumée » (docx valide) car ils exercent volontairement des cas non résolus :
# cf de démo absents des fixtures (boucle-paragraphes/tableau), cas limite intentionnel
# (modele-stats contient stat type="inexistant" ; image-dims référence un logo/radar).
NO_UNRESOLVED = {
    "modele-badges",
    "modele-conditions-paragraphe", "modele-conditions-tableau", "modele-conditions-operateurs",
    "modele-prooferr", "lot9-modele", "generic-modele", "modele-bloc-table",
    "modele-stats-combinaisons", "modele-stats-graphiques",
}

# Parmi ceux-ci, ceux dont le rendu est en outre totalement silencieux (0 avertissement).
# Sont exclus les gabarits qui EXHIBENT un cas limite non bloquant : conditions-paragraphe
# (condition sur un chemin invalide) et bloc-table (colonnes cf de démo « inconnues ignorées »).
NO_WARNING = NO_UNRESOLVED - {"modele-conditions-paragraphe", "modele-bloc-table"}


def test_valid_templates_render(app):
    """Chaque gabarit valide se rend en docx valide contre une analyse adaptée ; ceux dont les
    données résolvent tout ne laissent aucune balise (NO_UNRESOLVED) ni, hors cas limite
    volontaire, aucun avertissement (NO_WARNING)."""
    failures = []
    loaded = None
    # regroupé par fixture pour limiter les rechargements
    for tpl in sorted(VALID_TEMPLATES, key=lambda p: (TPL_FIXTURE.get(p.stem, DEFAULT_FIXTURE), p.stem)):
        fixture = TPL_FIXTURE.get(tpl.stem, DEFAULT_FIXTURE)
        if fixture != loaded:
            app.load(fixture + ".rae.json")
            loaded = fixture
        try:
            res = _render(app, tpl)
            data = base64.b64decode(res["docx"])
            exports.save(f"gabarits/{tpl.stem}-rendu.docx", data)  # rendu conservé pour examen
            xml = ooxml.document_xml(data)
            if not xml or "<w:document" not in xml:
                failures.append((tpl.name, "document.xml vide/invalide"))
                continue
            if tpl.stem in NO_UNRESOLVED:
                braces = xml.count("{{")
                if braces:
                    failures.append((tpl.name, f"{braces} balise(s) non résolue(s) avec {fixture}"))
            if tpl.stem in NO_WARNING and res["warnings"]:
                failures.append((tpl.name, f"avertissements avec {fixture} : {res['warnings']}"))
        except Exception as e:  # noqa: BLE001
            failures.append((tpl.name, str(e)[:120]))
    assert not failures, "gabarits valides en échec : " + str(failures)


def test_error_templates_report_warnings(app):
    app.load("ebios-objets.rae.json")
    silent = []
    for tpl in ERROR_TEMPLATES:
        res = _render(app, tpl)
        if not res["warnings"]:
            silent.append(tpl.name)
    # chaque gabarit « erreur » doit produire au moins un avertissement (message non bloquant)
    assert not silent, "gabarits d'erreur SANS avertissement : " + str(silent)


def test_error_templates_do_not_crash(app):
    app.load("ebios-objets.rae.json")
    for tpl in ERROR_TEMPLATES[:5]:
        res = _render(app, tpl)
        # rendu produit malgré l'erreur (moteur non bloquant)
        assert res["docx"], f"{tpl.name} : aucun docx produit"
    assert not app.console_errors()
