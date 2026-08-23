"""Menu Fichier + nouvelle analyse."""
import pytest

pytestmark = pytest.mark.ui


def test_file_menu_opens(app):
    app.load("ebios.rae.json")
    app.click("#btnFile")
    vis = app.js("()=>{const m=document.getElementById('fileMenu');return !!m && getComputedStyle(m).display!=='none';}")
    assert vis


def test_new_analysis_resets(app):
    app.load("ebios.rae.json")
    assert app.js("analyse.risks.length") > 0
    app.js("newAnalysis()")        # ouvre en principe une confirmation
    if app.js("!!document.querySelector('body > .modal-bg.open')"):
        app.top_modal_confirm()    # confirmer si une modale est présente
    assert app.js("(analyse.risks||[]).length") == 0
    assert not app.console_errors()
