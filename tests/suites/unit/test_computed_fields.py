"""Champs calculés liés à l'entité : cfComputedValue (arithmétique, traversée de référence, cycle).

Utilise la fixture kitchen-sink `tous-types-champs` (f_int=7, f_ref=[SRV1(niveau3),SRV2(niveau1)]).
"""
import pytest

pytestmark = pytest.mark.unit


def _compute(app, code):
    return app.js("""c => {
      const f = analyse.custom_fields.find(x=>x.code===c);
      return cfComputedValue(f, 'risk', analyse.risks[0]);
    }""", code)


def test_arithmetic_on_field(app):
    app.load("tous-types-champs.rae.json")
    r = _compute(app, "f_calc")           # = cf.f_int * 2 = 14
    assert r["ok"] is True and r["value"] == 14


def test_reference_traversal_sum(app):
    app.load("tous-types-champs.rae.json")
    r = _compute(app, "f_calc_ref")       # = SUM(cf.f_ref.cf.niveau) = 3 + 1 = 4
    assert r["ok"] is True and r["value"] == 4


def test_object_attribute_computed(app):
    app.load("tous-types-champs.rae.json")
    r = app.js("""() => {
      const ot = analyse.object_types.find(t=>t.code==='srv');
      const attr = ot.attributes.find(a=>a.code==='crit');   // = cf.niveau * 10
      const inst = analyse.objects.find(o=>o.id==='SRV1');    // niveau 3
      return cfComputedValue(attr, ot, inst);
    }""")
    assert r["ok"] is True and r["value"] == 30


def test_cycle_detected(app):
    app.load("tous-types-champs.rae.json")
    r = app.js("""() => {
      analyse.custom_fields.push({code:'c1',target:'risk',type:'computed',expression:'cf.c2',label:{fr:'c1'}});
      analyse.custom_fields.push({code:'c2',target:'risk',type:'computed',expression:'cf.c1',label:{fr:'c2'}});
      const f = analyse.custom_fields.find(x=>x.code==='c1');
      return cfComputedValue(f, 'risk', analyse.risks[0]);
    }""")
    assert r["ok"] is False and r["error"]


# Champ calculé à résultat texte : la valeur est rendue en Markdown (inline) à l'écran
# et exportée en runs Markdown côté Word (kind:"md").
COMPUTED_TEXT_MD = r"""
() => {
  const f = { type:'computed', result_type:'text', code:'_mdt', label:{fr:'T'},
              expression:'"[rouge]{.red} et ==surl== et **g**"' };
  const web = cfComputedDisplayHTML(f, 'analysis', analyse);
  const desc = tmplComputedDesc(f, 'analysis', analyse);
  return {
    color: /color:#d64545/.test(web),
    mark: /<mark>/.test(web),
    bold: /<strong>/.test(web),
    inline: !/<p>/.test(web),        // rendu inline (pas de bloc <p>)
    wordKind: desc.kind
  };
}
"""


def test_computed_text_result_supports_markdown(app):
    app.load("tous-types-champs.rae.json")
    r = app.js(COMPUTED_TEXT_MD)
    assert r["color"] and r["mark"] and r["bold"], f"Markdown non rendu (web) : {r}"
    assert r["inline"], "le résultat texte doit être rendu inline (sans <p>)"
    assert r["wordKind"] == "md", "l'export Word doit traiter le calculé texte comme du Markdown"
