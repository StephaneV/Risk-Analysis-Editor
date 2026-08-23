"""Vue Rapport : sections rendues + panneaux de cotation (Détail des risques)."""
import pytest

pytestmark = pytest.mark.ui


def test_sections_render(app):
    app.load("ebios.rae.json")
    app.goto("report")
    assert app.js("document.querySelectorAll('#view-report .rp-card').length") > 0
    assert not app.console_errors()


def test_detail_panels_present(app):
    # ebios porte des champs perso de cotation -> panneaux Initial/Résiduel
    app.load("ebios.rae.json")
    app.goto("report")
    assert app.js("document.querySelectorAll('#view-report .rp-phases').length") > 0


def test_report_filtered_scope(app):
    app.load("volumineuse.rae.json")
    app.goto("report")
    # rendu sans erreur sur une analyse volumineuse
    assert app.js("document.querySelectorAll('#view-report .rp-card').length") > 0
    assert not app.console_errors()
