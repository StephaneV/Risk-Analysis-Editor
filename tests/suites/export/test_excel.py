"""Export Excel (buildXlsx) : paquet OOXML valide + données présentes."""
import base64

import pytest

from harness import exports, ooxml

pytestmark = pytest.mark.export

XLSX_B64 = r"""
async () => {
  const blob = buildXlsx();
  const u8 = new Uint8Array(await blob.arrayBuffer());
  let s=''; const CH=0x8000;
  for (let i=0;i<u8.length;i+=CH) s += String.fromCharCode.apply(null, u8.subarray(i,i+CH));
  return btoa(s);
}
"""


def test_xlsx_is_valid_package(app):
    app.load("ebios.rae.json")
    data = base64.b64decode(app.js(XLSX_B64))
    exports.save("export-excel-ebios.xlsx", data)
    parts = ooxml.open_pkg(data)
    assert "xl/workbook.xml" in parts
    assert any(n.startswith("xl/worksheets/") for n in parts)


def test_xlsx_contains_risk_label(app):
    app.load("ebios.rae.json")
    parts = ooxml.open_pkg(base64.b64decode(app.js(XLSX_B64)))
    # les chaînes sont dans sharedStrings.xml (ou inline dans une feuille)
    blob = b"".join(v for k, v in parts.items() if k.startswith("xl/"))
    assert b"Fuite de donn" in blob  # un libellé de risque de la démo


def test_xlsx_includes_object_sheets(app):
    """Une feuille par type d'objet renseigné (id + attributs), en plus des 4 feuilles fixes."""
    app.load("ebios-objets.rae.json")
    parts = ooxml.open_pkg(base64.b64decode(app.js(XLSX_B64)))
    exports.save("export-excel-ebios-objets.xlsx", base64.b64decode(app.js(XLSX_B64)))
    wb = parts["xl/workbook.xml"].decode("utf-8")
    # 4 feuilles fixes (Synthèse, Risques, Mesures, Liens) + 5 types d'objet de la démo
    assert wb.count("<sheet ") == 9, f"nombre de feuilles inattendu :\n{wb}"
    assert "Valeur m" in wb, "aucune feuille pour le type d'objet « Valeur métier »"
    # une instance d'objet et la valeur d'un de ses attributs
    blob = b"".join(v for k, v in parts.items() if k.startswith("xl/"))
    assert b"VM1" in blob and b"Gestion de la relation client" in blob, "instance d'objet absente de l'export"
