"""Markdown maison : rendu de base + sécurité (échappement HTML, filtrage des URL)."""
import pytest

pytestmark = pytest.mark.unit

MD = "s => mdToHTML(s)"


def test_bold_and_italic(app):
    assert "<strong>gras</strong>" in app.js(MD, "**gras**")
    assert "<em>italique</em>" in app.js(MD, "_italique_")


def test_link_https_allowed(app):
    out = app.js(MD, "[lien](https://example.org)")
    assert 'href="https://example.org"' in out


def test_raw_html_is_escaped(app):
    out = app.js(MD, "<script>alert(1)</script>")
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


def test_javascript_url_is_filtered(app):
    out = app.js(MD, "[x](javascript:alert(1))")
    assert "javascript:" not in out          # URL rejetée
    assert "<a" not in out                    # pas de lien produit


def test_image_javascript_url_filtered(app):
    out = app.js(MD, "![alt](javascript:alert(1))")
    assert "javascript:" not in out
    assert "<img" not in out
