"""Gabarits Word — vérifications fines sur analyses de contrôle.

Porté de travaux/test-conditions, test-prooferr, test-badges, test-modele-word-objets (lot9).
"""
import base64

import pytest

from harness.browser import FIXTURES

pytestmark = pytest.mark.export

TPL = FIXTURES / "word-templates"

METRICS = r"""
async (b64) => {
  const bin=atob(b64); const u8=new Uint8Array(bin.length);
  for(let i=0;i<bin.length;i++) u8[i]=bin.charCodeAt(i);
  tmplWarnings.length=0;
  const parts=await tmplLoadDocx(new File([u8],'t.docx'));
  const blob=await tmplRender(parts); const o=new Uint8Array(await blob.arrayBuffer());
  const doc=fflate.strFromU8(fflate.unzipSync(o)['word/document.xml']);
  return {
    warns: tmplWarnings.slice(),
    croix: (doc.match(/✘/g)||[]).length,
    coche: (doc.match(/✔/g)||[]).length,
    braces: (doc.match(/\{\{/g)||[]).length,
    fills: (doc.match(/w:fill="[0-9A-Fa-f]{6}"/g)||[]).length,
    hasEbios: doc.indexOf('EBIOS')>=0,
    len: doc.length,
  };
}
"""


def _metrics(app, tpl_name):
    b64 = base64.b64encode((TPL / tpl_name).read_bytes()).decode()
    return app.js(METRICS, b64)


@pytest.mark.parametrize("tpl", [
    "modele-conditions-paragraphe.docx",
    "modele-conditions-tableau.docx",
    "modele-conditions-operateurs.docx",
])
def test_conditions_hide_false_branches(app, tpl):
    """Sur l'analyse de contrôle, aucune ligne ✘ CACHÉ conditionnelle ne doit apparaître
    (seule la ligne de LÉGENDE contient un ✘), et aucune balise ne doit rester non résolue."""
    app.load("analyse-test-conditions.rae.json")
    m = _metrics(app, tpl)
    assert m["croix"] <= 1, f"{tpl} : {m['croix']} ✘ (ligne conditionnelle CACHÉE fuit)"
    assert m["braces"] == 0, f"{tpl} : balises non résolues"


def test_prooferr_split_tags_resolved(app):
    """Balises scindées par des w:proofErr (comme Word) : résolues, 0 avertissement, 0 accolade."""
    app.load("ebios.rae.json")
    m = _metrics(app, "modele-prooferr.docx")
    assert m["warns"] == [], f"avertissements : {m['warns']}"
    assert m["braces"] == 0, "accolades résiduelles"
    assert m["hasEbios"], "le titre (balise scindée) n'a pas été résolu"


def test_badges_rendered(app):
    """Le modificateur | badge produit des cellules/puces teintées (fills)."""
    app.load("demo-badges.rae.json")
    m = _metrics(app, "modele-badges.docx")
    assert m["warns"] == [], f"avertissements : {m['warns']}"
    assert m["fills"] > 0, "aucun badge teinté produit"
    assert m["braces"] == 0


def test_objects_template_lot9(app):
    """Objets dans un gabarit (boucles, attributs, références) : rendu sans avertissement/accolade."""
    app.load("ebios-objets.rae.json")
    m = _metrics(app, "lot9-modele.docx")
    assert m["warns"] == [], f"avertissements : {m['warns']}"
    assert m["braces"] == 0
    assert m["len"] > 1000
