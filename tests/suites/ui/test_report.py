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


def test_exploded_report_has_chapters(app):
    """Rapport éclaté (HTML) : un chapitre .rp-chapter par groupe (X01/T10)."""
    app.load("rapport-eclate-risque.rae.json")
    app.goto("report")
    n = app.js("document.querySelectorAll('#view-report .rp-chapter').length")
    assert n >= 2, f"rapport éclaté : {n} chapitre(s) (attendu ≥ 2)"
    assert not app.console_errors()
