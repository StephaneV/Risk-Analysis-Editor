"""Export/Import CSV : contenu de l'export et analyse d'un CSV d'import."""
import pytest

from harness import exports
from harness.browser import FIXTURES

pytestmark = pytest.mark.export


def _csv_text(rows):
    def q(x):
        s = "" if x is None else str(x)
        return '"' + s.replace('"', '""') + '"' if any(c in s for c in ',";\n') else s
    return "\n".join(",".join(q(c) for c in row) for row in rows)

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
    exports.save("export-risques-ebios.csv", _csv_text(cap["rows"]))
    n = app.js("analyse.risks.length")
    # en-tête + une ligne par risque
    assert len(cap["rows"]) == n + 1
    header = ",".join(str(x) for x in cap["rows"][0]).lower()
    assert "id" in header and "label" in header


def test_export_measures_csv(app):
    app.load("ebios.rae.json")
    cap = app.js(CAPTURE_EXPORT, "exportMeasuresCSV")
    assert cap and len(cap["rows"]) == app.js("analyse.measures.length") + 1
    exports.save("export-mesures-ebios.csv", _csv_text(cap["rows"]))


def test_import_risks_csv(app):
    app.load("ebios.rae.json")
    text = (FIXTURES / "csv" / "analyse-si-risks.csv").read_text(encoding="utf-8")
    res = app.js("t => analyzeRisksCSV(t)", text)
    assert res["items"], "aucun risque analysé depuis le CSV"
    assert isinstance(res["errors"], list)


# --- Aller-retour export -> réimport (round-trip) ------------------------------------------

# Construit le texte CSV depuis les lignes capturées, vide la collection, réimporte, compare.
ROUNDTRIP = r"""
kind => {
  const q = s => { s = String(s==null?'':s); return /[",;\n]/.test(s) ? '"'+s.replace(/"/g,'""')+'"' : s; };
  const dumpR = () => analyse.risks.map(r=>({id:r.id,label:r.label,cat:r.category||'',
      ip:r.initial_assessment.probability, ig:r.initial_assessment.severity,
      rp:(r.residual_assessment||r.initial_assessment).probability, rg:(r.residual_assessment||r.initial_assessment).severity}))
      .sort((a,b)=>a.id<b.id?-1:1);
  const dumpM = () => analyse.measures.map(m=>({id:m.id,label:m.label,type:m.type||'',status:m.status||'',
      resp:m.responsible||'',due:m.due_date||'',cost:m.cost==null?'':String(m.cost)})).sort((a,b)=>a.id<b.id?-1:1);
  const dumpL = () => analyse.treatments.map(t=>t.risk+'|'+t.measure).sort();
  const capture = fn => { let cap=null; const dl=window.downloadCSV; window.downloadCSV=(rows)=>{cap={rows};};
      fn(); window.downloadCSV=dl; return cap.rows.map(row=>row.map(q).join(',')).join('\n'); };

  if (kind === 'risks') {
    const before = dumpR();
    const text = capture(exportRisksCSV);
    analyse.risks = []; analyse.treatments = [];
    const an = analyzeRisksCSV(text); commitImport('risks', an.items);
    return { before, after: dumpR(), errors: an.errors };
  }
  if (kind === 'measures') {
    const before = dumpM();
    const text = capture(exportMeasuresCSV);
    analyse.measures = []; analyse.treatments = [];
    const an = analyzeMeasuresCSV(text); commitImport('measures', an.items);
    return { before, after: dumpM(), errors: an.errors };
  }
  if (kind === 'links') {
    const before = dumpL();
    const text = capture(exportLinksCSV);
    analyse.treatments = [];                    // on garde risques & mesures
    const an = analyzeLinksCSV(text); commitImportLinks(an.items);
    return { before, after: dumpL(), errors: an.errors };
  }
}
"""


@pytest.mark.parametrize("kind", ["risks", "measures", "links"])
def test_csv_export_reimport_roundtrip(app, kind):
    app.load("ebios.rae.json")
    r = app.js(ROUNDTRIP, kind)
    assert not r["errors"], f"{kind} : erreurs d'import {r['errors']}"
    assert r["before"], f"{kind} : rien à exporter"
    assert r["after"] == r["before"], f"{kind} : données altérées par l'aller-retour"
