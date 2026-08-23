"""Moteur d'expression des champs calculés (échantillon pilote).

Généralise travaux/test-champs-calcules : appelle `calcEvaluate(expr, env)` in-page.
L'`env` est construit EN LIGNE (et non via `calcEnv`, code mort voué à suppression au Lot 0).
"""
import pytest

pytestmark = pytest.mark.unit

TODAY = "2026-01-01"

# (id, expression, valeur attendue, type attendu | None)
CASES = [
    ("A1", "42", 42, "num"),
    ("A3", ".5", 0.5, "num"),
    ("A4", '"bonjour"', "bonjour", "text"),
    ("A6", "TRUE", True, "bool"),
    ("A7", "=1+1", 2, "num"),
    ("B1", "2+3*4", 14, "num"),
    ("B2", "(2+3)*4", 20, "num"),
    ("B3", "2^3^2", 512, "num"),          # puissance associative à droite
    ("B4", "-2^2", 4, "num"),             # unaire lié plus fort (comme Excel)
    ("B5", "10/4", 2.5, "num"),
    ("B8", '"x=" & (1+1)', "x=2", "text"),
    ("C1", "3>2", True, "bool"),
    ("C6", "NOT(1>2)", True, "bool"),
    ("D1", "SUM(1,2,3,4)", 10, "num"),
    ("D3", "MEDIAN(1,2,3,4)", 2.5, "num"),
    ("D6", "MAX(3,-1,7)", 7, "num"),
    ("E1", 'IF(3>2,"oui","non")', "oui", "text"),
    ("H1", 'CONCAT("a","b","c")', "abc", "text"),
    ("H2", 'LEN("abcd")', 4, "num"),
]

EVAL = "([e,t]) => { const env={ get:()=>null, today:()=>t }; return calcEvaluate(e, env); }"


@pytest.mark.parametrize("cid,expr,expected,typ", CASES, ids=[c[0] for c in CASES])
def test_expression(app, cid, expr, expected, typ):
    res = app.js(EVAL, [expr, TODAY])
    assert res["ok"] is True, f"{cid}: erreur {res.get('error')}"
    if isinstance(expected, float):
        assert abs(res["value"] - expected) < 1e-9, f"{cid}: {res['value']} != {expected}"
    else:
        assert res["value"] == expected, f"{cid}: {res['value']!r} != {expected!r}"
    if typ:
        assert res["type"] == typ, f"{cid}: type {res['type']} != {typ}"


def test_error_is_non_blocking(app):
    """Une expression invalide renvoie {ok:false, error} sans lever."""
    res = app.js(EVAL, ["1+", TODAY])
    assert res["ok"] is False and res["error"]
