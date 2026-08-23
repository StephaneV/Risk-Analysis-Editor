"""Analyse CSV bas niveau : parseCSV (séparateur, guillemets, lignes)."""
import pytest

pytestmark = pytest.mark.unit

PARSE = "s => parseCSV(s)"


def test_comma_separated(app):
    r = app.js(PARSE, "a,b,c\n1,2,3")
    assert r["sep"] == ","
    assert r["rows"][0] == ["a", "b", "c"]
    assert r["rows"][1] == ["1", "2", "3"]


def test_semicolon_detected(app):
    r = app.js(PARSE, "a;b;c\n1;2;3")
    assert r["sep"] == ";"
    assert r["rows"][0] == ["a", "b", "c"]


def test_quoted_field_with_separator(app):
    r = app.js(PARSE, '"a,b",c\n"x""y",z')
    assert r["rows"][0] == ["a,b", "c"]
    assert r["rows"][1] == ['x"y', "z"]   # guillemet échappé ""


def test_fixture_csv_parses(app):
    from harness.browser import FIXTURES
    text = (FIXTURES / "csv" / "analyse-si-risks.csv").read_text(encoding="utf-8")
    r = app.js(PARSE, text)
    assert len(r["rows"]) >= 2          # en-tête + au moins une ligne
    assert len(r["rows"][0]) >= 2       # plusieurs colonnes
