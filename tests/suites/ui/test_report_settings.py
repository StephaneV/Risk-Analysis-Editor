"""Paramètres › Rapport : sections (rendu + activation/désactivation), structure."""
import pytest

pytestmark = pytest.mark.ui


def test_sections_render(app):
    app.load("ebios.rae.json")
    app.settings_subtab("report")
    assert app.js("document.querySelectorAll('#reportCfgPanel .rc-secitem').length") > 3


def test_toggle_section(app):
    app.load("ebios.rae.json")
    app.settings_subtab("report")
    r = app.js("""()=>{
      const it = document.querySelector('#reportCfgPanel .rc-secitem');
      const id = it.dataset.sec;
      const cb = it.querySelector('.rc-secrow input[type=checkbox]');
      const before = cb.checked;
      cb.click();                                   // bascule + événements
      const cfgOn = (reportCfg().sections.find(s=>s.id===id)||{}).on;
      return { id, before, checkedNow: cb.checked, offClass: it.classList.contains('rc-off'), cfgOn };
    }""")
    assert r["checkedNow"] != r["before"], "la case ne bascule pas"
    assert r["offClass"] == (not r["checkedNow"]), "retour visuel rc-off incohérent"
    # la configuration (reportCfg) reflète l'état de la case
    assert r["cfgOn"] == r["checkedNow"], "reportCfg ne reflète pas la bascule"


def test_structure_controls_present(app):
    app.load("ebios.rae.json")
    app.settings_subtab("report")
    has_iter = app.js("!!document.getElementById('rcIterBy')")
    has_radio = app.js("document.querySelectorAll('#reportCfgPanel .rc-radio input, #reportCfgPanel input[type=radio]').length > 0")
    assert has_iter or has_radio, "aucun contrôle de structure du rapport"
