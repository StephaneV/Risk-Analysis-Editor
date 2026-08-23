"""Champs personnalisés : validation par type et génération du contrôle HTML."""
import pytest

pytestmark = pytest.mark.unit

# cfValidate(f, v) -> null si OK, sinon message d'erreur (string).
VALIDATE = "([f,v]) => cfValidate(f, v)"


def _valid(app, f, v):
    return app.js(VALIDATE, [f, v]) is None


def _invalid(app, f, v):
    return app.js(VALIDATE, [f, v]) is not None


def test_required_text(app):
    f = {"code": "x", "target": "risk", "type": "text", "required": True, "label": {"fr": "X"}}
    assert _invalid(app, f, "")      # manquant -> erreur
    assert _valid(app, f, "présent")


def test_integer_bounds(app):
    f = {"code": "n", "target": "risk", "type": "integer", "min": 0, "max": 10, "label": {"fr": "N"}}
    assert _valid(app, f, 5)
    assert _invalid(app, f, -1)
    assert _invalid(app, f, 11)


@pytest.mark.parametrize("typ,ok,bad", [
    ("url", "https://example.org", "pas-une-url"),
    ("email", "a@b.co", "pas-un-email"),
    ("tel", "+33123456789", "abc"),
])
def test_format_validators(app, typ, ok, bad):
    f = {"code": "c", "target": "risk", "type": typ, "label": {"fr": "C"}}
    assert _valid(app, f, ok)
    assert _invalid(app, f, bad)


def test_regexp_pattern(app):
    f = {"code": "r", "target": "risk", "type": "regexp", "pattern": "[A-Z]{2}-\\d{4}", "label": {"fr": "R"}}
    assert _valid(app, f, "AB-1234")
    assert _invalid(app, f, "zz-1")


# Génération du contrôle : cfControlHTML(f, v) renvoie un fragment contenant [data-cf].
CONTROL = "([f,v]) => { const d=document.createElement('div'); d.innerHTML=cfControlHTML(f,v); const el=d.querySelector('[data-cf]'); return el ? {cf:el.getAttribute('data-cf'), cft:el.getAttribute('data-cft')} : null; }"

CTRL_TYPES = [
    ("boolean", {}), ("integer", {}), ("float", {}), ("date", {}), ("text", {}),
    ("textarea", {}), ("url", {}), ("email", {}), ("tel", {}),
    ("regexp", {"pattern": "[0-9]+"}), ("color", {"color_mode": "both"}), ("image", {}),
    ("select", {"items": [{"code": "a", "label": "A"}]}),
    ("checklist", {"items": [{"code": "a", "label": "A"}]}),
    ("tags", {"items": [{"code": "a", "label": "A", "color": "#123456"}]}),
    ("scale", {"items": [{"value": 1, "label": "Bas"}]}),
    ("progress", {}),
    ("computed", {"expression": "=1+1", "result_type": "integer"}),
]


@pytest.mark.parametrize("typ,extra", CTRL_TYPES, ids=[t for t, _ in CTRL_TYPES])
def test_control_html_has_data_cf(app, typ, extra):
    f = dict({"code": "fld", "target": "risk", "type": typ, "label": {"fr": "F"}}, **extra)
    res = app.js(CONTROL, [f, None])
    assert res is not None, f"cfControlHTML({typ}) ne produit pas d'élément [data-cf]"
    assert res["cf"] == "fld"
    assert res["cft"] == typ
