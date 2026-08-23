"""Export Word natif (buildDocx) : paquet OOXML valide, contenu et médias attendus."""
import base64

import pytest

from harness import ooxml

pytestmark = pytest.mark.export

# Récupère les octets du .docx produit par buildDocx() en base64.
DOCX_B64 = r"""
async () => {
  const blob = await buildDocx();
  const u8 = new Uint8Array(await blob.arrayBuffer());
  let s=''; const CH=0x8000;
  for (let i=0;i<u8.length;i+=CH) s += String.fromCharCode.apply(null, u8.subarray(i,i+CH));
  return btoa(s);
}
"""


def _docx(app):
    return base64.b64decode(app.js(DOCX_B64))


def test_docx_is_valid_package(app):
    app.load("ebios.rae.json")
    data = _docx(app)
    parts = ooxml.open_pkg(data)
    assert "word/document.xml" in parts
    assert "[Content_Types].xml" in parts


def test_docx_contains_risk_and_panels(app):
    app.load("ebios.rae.json")
    xml = ooxml.document_xml(_docx(app))
    # un libellé de risque connu de la démo
    assert "Fuite de données clients" in xml
    # panneaux de cotation Initial/Résiduel (Détail des risques)
    assert "Initial" in xml and "Résiduel" in xml
    # au moins un tableau
    assert "<w:tbl>" in xml


def test_docx_embeds_matrix_images(app):
    app.load("ebios.rae.json")
    media = ooxml.media_names(_docx(app))
    assert len(media) >= 1, "aucune image (matrice) embarquée dans le Word"


def test_docx_with_color_and_image_fields(app):
    app.load("tous-types-champs.rae.json")
    data = _docx(app)
    parts = ooxml.open_pkg(data)
    assert "word/document.xml" in parts
    # le champ image du kitchen-sink -> au moins un média embarqué
    assert ooxml.media_names(data), "champ image non embarqué"
