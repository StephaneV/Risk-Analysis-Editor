"""Vue Risques : registre, ouverture de fiche, création via modale."""
import pytest

pytestmark = pytest.mark.ui


def test_registry_row_count_matches_model(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    n = app.js("(analyse.risks||[]).length")
    rows = app.js("document.querySelectorAll('#risksTable tr').length")
    assert n > 0 and rows == n


def test_open_risk_modal_prefilled(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    app.js("openRiskModal('R1', null, null)")
    assert app.modal_open()
    assert app.js("document.getElementById('f_label').value")  # libellé pré-rempli


def test_create_risk_via_modal(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    before = app.js("analyse.risks.length")
    app.js("openRiskModal(null)")
    app.set_input("#f_label", "Nouveau risque de test")
    app.click("#modalOk")   # « Créer »
    assert app.js("analyse.risks.length") == before + 1
    assert not app.console_errors()


# Cadre figé (piste 1) : la 1re colonne (ID) et la dernière (Actions) sont sticky, à fond
# opaque, pour rester visibles au défilement horizontal des registres larges.
FROZEN = r"""
() => {
  const t = document.getElementById('risksTableEl');
  const row = t.querySelector('tbody tr'); if(!row) return null;
  const first = row.children[0], last = row.children[row.children.length-1];
  return {
    reg: t.classList.contains('reg'),
    first: getComputedStyle(first).position,
    last: getComputedStyle(last).position,
    opaque: getComputedStyle(first).backgroundColor !== 'rgba(0, 0, 0, 0)'
  };
}
"""


def test_registre_frozen_id_and_actions(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    r = app.js(FROZEN)
    assert r, "aucune ligne de risque"
    assert r["reg"], "table du registre sans classe .reg"
    assert r["first"] == "sticky" and r["last"] == "sticky", "colonnes ID/Actions non figées"
    assert r["opaque"], "colonne figée sans fond opaque"
