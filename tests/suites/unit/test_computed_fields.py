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
