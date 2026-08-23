"""Export/Import CSV : contenu de l'export et analyse d'un CSV d'import."""
import pytest

from harness.browser import FIXTURES

pytestmark = pytest.mark.export

# Intercepte downloadCSV(rows,name) pour capturer les lignes produites.
CAPTURE_EXPORT = r"""
fnName => {
  let cap = null;
  const orig = window.downloadCSV;
  window.downloadCSV = (rows, name) => { cap = { rows, name }; };
  try { window[fnName](); } finally { window.downloadCSV = orig; }
  return cap;
}
"""


def test_export_risks_csv(app):
    app.load("ebios.rae.json")
    cap = app.js(CAPTURE_EXPORT, "exportRisksCSV")
    assert cap and cap["rows"], "aucune ligne CSV capturée"
    n = app.js("analyse.risks.length")
    # en-tête + une ligne par risque
    assert len(cap["rows"]) == n + 1
    header = ",".join(str(x) for x in cap["rows"][0]).lower()
    assert "id" in header and "label" in header


def test_export_measures_csv(app):
    app.load("ebios.rae.json")
    cap = app.js(CAPTURE_EXPORT, "exportMeasuresCSV")
    assert cap and len(cap["rows"]) == app.js("analyse.measures.length") + 1


def test_import_risks_csv(app):
    app.load("ebios.rae.json")
    text = (FIXTURES / "csv" / "analyse-si-risks.csv").read_text(encoding="utf-8")
    res = app.js("t => analyzeRisksCSV(t)", text)
    assert res["items"], "aucun risque analysé depuis le CSV"
    assert isinstance(res["errors"], list)
