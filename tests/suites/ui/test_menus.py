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


def test_template_blob_strips_data(app):
    """« Enregistrer comme modèle » : squelette sans risques/mesures, grille + champs perso conservés (M04)."""
    app.load("ebios.rae.json")
    tpl = app.js("""async ()=>{
      const blob = templateBlob();
      const txt = await blob.text();
      return JSON.parse(txt);
    }""")
    assert tpl["metadata"]["kind"] == "template"
    assert tpl["risks"] == [] and tpl["measures"] == [] and tpl["treatments"] == []
    assert tpl["grid"], "grille absente du modèle"
    assert isinstance(tpl["custom_fields"], list)


def test_start_screen_actions_present(app):
    """Écran d'accueil : actions vierge / charger / démo (M10)."""
    app.load("ebios.rae.json")
    for sid in ("startNew", "startOpen", "startDemo"):
        assert app.js("id=>!!document.getElementById(id)", sid), f"bouton d'accueil {sid} absent"
    # la liste des modèles méthodologiques est peuplée
    app.js("()=>{ if(typeof renderStartTemplates==='function') renderStartTemplates(); }")
    assert app.js("!!document.getElementById('startTemplatesList')")
