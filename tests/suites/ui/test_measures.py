"""Vue Mesures : registre, ouverture de fiche, création via modale."""
import pytest

pytestmark = pytest.mark.ui


def test_registry_row_count_matches_model(app):
    app.load("ebios.rae.json")
    app.goto("measures")
    n = app.js("(analyse.measures||[]).length")
    rows = app.js("document.querySelectorAll('#measuresTable tr').length")
    assert n > 0 and rows == n


def test_open_measure_modal_prefilled(app):
    app.load("ebios.rae.json")
    app.goto("measures")
    mid = app.js("analyse.measures[0].id")
    app.js("id=>openMeasureModal(id, null, null)", mid)
    assert app.modal_open()
    assert app.js("document.getElementById('f_label').value")


def test_create_measure_via_modal(app):
    app.load("ebios.rae.json")
    app.goto("measures")
    before = app.js("analyse.measures.length")
    app.js("openMeasureModal(null)")
    app.set_input("#f_label", "Nouvelle mesure de test")
    app.click("#modalOk")
    assert app.js("analyse.measures.length") == before + 1
    assert not app.console_errors()


def test_measures_cards_view(app):
    """Registre Mesures : vue Cartes (fiche par mesure, clic ouvre l'éditeur)."""
    app.load("ebios.rae.json")
    app.goto("measures")
    app.js("document.querySelector('#view-measures .view-seg [data-view-mode=\"cards\"]').click()")
    assert app.js("document.querySelectorAll('#view-measures .reg-cards-host .obj-card').length") == app.js("analyse.measures.length")
    assert app.js("document.querySelector('#view-measures .table-scroll').hidden")
    app.js("document.querySelector('#view-measures .obj-card [data-edit-m]').click()")
    assert app.modal_open()
    app.close_modals()
    assert not app.console_errors()


def test_measures_no_column_hidden_by_default(app):
    """Régression : par défaut aucune colonne n'est « Masqué » ; l'auto place « En ligne » ou « En
    détail ». Les colonnes secondaires (def:false : Échéance cible, Coût) passent « En détail »."""
    app.load("ebios.rae.json")
    app.goto("measures")
    hidden = app.js("allCols('measures').filter(c=>!c.pinned&&colState('measures',c.key)==='hidden').map(c=>c.key)")
    assert hidden == [], f"des colonnes sont Masquées par défaut : {hidden}"
    assert app.js("colState('measures','due')") == "detail", "colonne secondaire 'due' devrait être « en détail »"
    assert app.js("colState('measures','cost')") == "detail", "colonne secondaire 'cost' devrait être « en détail »"
    assert not app.console_errors()
