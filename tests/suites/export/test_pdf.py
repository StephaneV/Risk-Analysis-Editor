"""Lane PDF (@pdf, optionnelle) : les exports Word se convertissent en PDF via LibreOffice.

Sautée automatiquement si LibreOffice (soffice) est absent (voir conftest).
"""
import base64

import pytest

from harness import render
from harness.browser import ARTIFACTS, FIXTURES

pytestmark = [pytest.mark.export, pytest.mark.pdf]

EXPORTS = ARTIFACTS / "exports"
RENDERS = ARTIFACTS / "render"


def test_native_word_to_pdf(app):
    app.load("ebios.rae.json")
    EXPORTS.mkdir(parents=True, exist_ok=True)
    docx = EXPORTS / "ebios-natif.docx"
    docx.write_bytes(app.docx_bytes())
    pdf = render.docx_to_pdf(docx, RENDERS)
    assert pdf.exists() and pdf.stat().st_size > 1000, "PDF vide ou non produit"


def test_template_word_to_pdf(app):
    app.load("ebios-objets.rae.json")
    tpl = FIXTURES / "word-templates" / "modele-boucle-paragraphes.docx"
    b64 = base64.b64encode(tpl.read_bytes()).decode()
    out_b64 = app.js(r"""
      async (b64) => {
        const bin=atob(b64); const u8=new Uint8Array(bin.length);
        for(let i=0;i<bin.length;i++) u8[i]=bin.charCodeAt(i);
        const parts=await tmplLoadDocx(new File([u8],'t.docx'));
        const bl=await tmplRender(parts); const o=new Uint8Array(await bl.arrayBuffer());
        let s=''; const CH=0x8000; for(let i=0;i<o.length;i+=CH) s+=String.fromCharCode.apply(null,o.subarray(i,i+CH));
        return btoa(s);
      }""", b64)
    EXPORTS.mkdir(parents=True, exist_ok=True)
    docx = EXPORTS / "ebios-gabarit.docx"
    docx.write_bytes(base64.b64decode(out_b64))
    pdf = render.docx_to_pdf(docx, RENDERS)
    assert pdf.exists() and pdf.stat().st_size > 1000
