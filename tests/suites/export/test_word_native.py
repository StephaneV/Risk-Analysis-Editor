"""Export Word natif (buildDocx) : paquet OOXML valide, contenu et médias attendus."""
import base64

import pytest

from harness import exports, ooxml

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


def document_xml_of(app):
    return ooxml.document_xml(_docx(app))


def test_docx_is_valid_package(app):
    app.load("ebios.rae.json")
    data = _docx(app)
    exports.save("rapport-word-natif-ebios.docx", data)
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


def _page_breaks(xml):
    return xml.count('<w:br w:type="page"/>') + xml.count("<w:pageBreakBefore/>")


def test_report_exploded_has_more_chapters(app):
    """Rapport éclaté (par risque) vs classique : plus de sauts de page (un chapitre par groupe)."""
    app.load("rapport-classique.rae.json")
    classic = _page_breaks(document_xml_of(app))
    exports.save("rapport-word-classique.docx", _docx(app))  # analyse classique encore chargée
    app.load("rapport-eclate-risque.rae.json")
    exploded = _page_breaks(document_xml_of(app))
    exports.save("rapport-word-eclate-risque.docx", _docx(app))
    assert exploded > classic, f"éclaté ({exploded}) devrait avoir plus de sauts que classique ({classic})"


def test_report_exploded_by_category_renders(app):
    app.load("rapport-eclate-categorie.rae.json")
    xml = document_xml_of(app)
    assert "<w:document" in xml and _page_breaks(xml) >= 1
    assert not app.console_errors()


def _set_section(app, sec_id, on):
    app.js("([s,v])=>{reportCfgStore().sections=[{id:s,on:v}]; markDirty();}", [sec_id, on])


def test_word_radar_section_embeds_image(app):
    """X02 : activer la section Radar ajoute une image (le radar) au Word natif."""
    app.load("ebios.rae.json")
    _set_section(app, "radar", False)
    off = len(ooxml.media_names(_docx(app)))
    _set_section(app, "radar", True)
    on = len(ooxml.media_names(_docx(app)))
    assert on > off, f"la section Radar n'ajoute pas d'image ({off} -> {on})"


def test_word_stats_distribution_section_present(app):
    """X02 : activer la section « répartition » (stats) enrichit le Word natif (tableaux)."""
    app.load("ebios.rae.json")
    _set_section(app, "summary_distribution", False)
    off = ooxml.document_xml(_docx(app))
    _set_section(app, "summary_distribution", True)
    on = ooxml.document_xml(_docx(app))
    assert on.count("<w:tbl>") > off.count("<w:tbl>"), \
        f"la section « répartition » n'ajoute pas de tableau ({off.count('<w:tbl>')} -> {on.count('<w:tbl>')})"


def test_docx_with_color_and_image_fields(app):
    app.load("tous-types-champs.rae.json")
    data = _docx(app)
    parts = ooxml.open_pkg(data)
    assert "word/document.xml" in parts
    # le champ image du kitchen-sink -> au moins un média embarqué
    assert ooxml.media_names(data), "champ image non embarqué"
