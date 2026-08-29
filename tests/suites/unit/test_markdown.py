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


# --- Couleur de texte (span Pandoc [texte]{.nom}) et surlignage ==texte== ---

def test_color_span_known(app):
    assert '<span style="color:#d64545">urgent</span>' in app.js(MD, "[urgent]{.red}")


def test_color_span_unknown_is_plain(app):
    out = app.js(MD, "[texte]{.banana}")
    assert "texte" in out and "<span" not in out and "banana" not in out   # classe inconnue -> texte sans couleur


def test_highlight(app):
    assert "<mark>important</mark>" in app.js(MD, "==important==")


def test_color_span_no_injection(app):
    # La classe est bornée à [a-zA-Z][\w-]* : un style/attribut arbitraire ne matche pas.
    out = app.js(MD, "[x]{.red;background:url(y)}")
    assert "<span" not in out
    assert "background:url" in out            # reste littéral


def test_color_and_bold_combined(app):
    assert '<span style="color:#d64545"><strong>alerte</strong></span>' in app.js(MD, "[**alerte**]{.red}")


# --- Rendu Word : Markdown inline -> descripteurs de runs -> XML de run ---

def test_md_inline_descs(app):
    descs = app.js("s => mdInlineToDescs(s)", "[r]{.red} ==h== **b**")
    assert "d64545" in [d.get("color") for d in descs]
    assert "FFF2A8" in [d.get("fill") for d in descs]
    assert True in [d.get("b") for d in descs]


def test_md_word_run_xml(app):
    xml = app.js("s => mdInlineToDescs(s).map(d => tmplRunFromDesc('', d)).join('')",
                 "[r]{.red} ==h== **b**\nligne2")
    assert '<w:color w:val="d64545"/>' in xml    # couleur
    assert 'w:fill="FFF2A8"' in xml              # surlignage (ombrage)
    assert "<w:b/>" in xml                        # gras
    assert "<w:br/>" in xml                       # saut de ligne
