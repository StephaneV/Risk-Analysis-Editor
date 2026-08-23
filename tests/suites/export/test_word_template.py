"""Rapport Word à partir d'un gabarit (moteur tmpl*) : rendu des gabarits valides + cas d'erreur.

Généralise travaux/test-conditions, test-stats, test-modeles-erreurs.
"""
import base64

import pytest

from harness import ooxml
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


def test_valid_templates_render(app):
    app.load("ebios-objets.rae.json")
    failures = []
    for tpl in VALID_TEMPLATES:
        try:
            res = _render(app, tpl)
            xml = ooxml.document_xml(base64.b64decode(res["docx"]))
            if not xml or "<w:document" not in xml:
                failures.append((tpl.name, "document.xml vide/invalide"))
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
