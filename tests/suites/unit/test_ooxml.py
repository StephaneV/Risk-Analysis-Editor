"""Primitives OOXML « Word natif » (dx*) : fragments WordprocessingML bien formés."""
import pytest

pytestmark = pytest.mark.unit


def test_dxrun_basic(app):
    xml = app.js("dxRun('hello', {})")
    assert "<w:r>" in xml and "</w:r>" in xml
    assert "<w:t" in xml and "hello" in xml


def test_dxrun_bold(app):
    xml = app.js("dxRun('x', {b:true})")
    assert "<w:b/>" in xml


def test_dxrun_escapes_xml(app):
    xml = app.js("dxRun('a < b & c', {})")
    assert "&lt;" in xml and "&amp;" in xml
    assert "< b" not in xml  # le chevron brut ne doit pas subsister


def test_dxp_wraps_paragraph(app):
    xml = app.js("dxP(dxRun('x', {}), {})")
    assert xml.startswith("<w:p>") and "</w:p>" in xml
    assert "<w:t" in xml and "x" in xml


def test_dxtbl_cells(app):
    xml = app.js("dxTbl([['a','b'],['c','d']], [1000,1000])")
    assert "<w:tbl>" in xml and "</w:tbl>" in xml
    assert xml.count("<w:tc>") == 4
    for txt in ("a", "b", "c", "d"):
        assert txt in xml
