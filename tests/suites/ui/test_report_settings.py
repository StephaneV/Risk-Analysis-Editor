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


def test_orientation_applies_to_report(app):
    """Orientation paysage : reportCfg la reflète et le rendu ajoute .report-landscape (S05)."""
    app.load("ebios.rae.json")
    app.js("()=>{reportCfgStore().orientation='landscape'; markDirty();}")
    app.goto("report")
    assert app.js("reportCfg().orientation") == "landscape"
    assert app.js("!!document.querySelector('#view-report .report.report-landscape')"), \
        "classe report-landscape absente du rendu"


def test_cover_section_toggle_render(app):
    """Activer/désactiver la page de garde change sa présence dans le rendu (S05)."""
    app.load("ebios.rae.json")
    app.js("()=>{reportCfgStore().cover={on:true}; markDirty();}")
    app.goto("report")
    with_cover = app.js("!!document.querySelector('#view-report .rp-cover')")
    app.js("()=>{reportCfgStore().cover={on:false}; markDirty(); renderReport();}")
    without_cover = app.js("!!document.querySelector('#view-report .rp-cover')")
    assert with_cover and not without_cover, \
        f"page de garde : avec={with_cover} sans={without_cover}"
    assert not app.console_errors()


FX3 = "trois-cotations.rae.json"


def test_multiple_trajectory_sections_mode3(app):
    """Mode 3 : on peut ajouter plusieurs matrices trajectoires indépendantes (cotation + titre + position),
    puis en supprimer. Le rendu produit une matrice distincte par section, dans l'ordre."""
    app.load(FX3)
    app.settings_subtab("report")
    # bouton d'ajout présent en mode 3 ; une seule section trajectoire au départ
    assert app.js("!!document.getElementById('rcAddTraj')"), "bouton d'ajout absent en mode 3"
    assert app.js("reportCfg().sections.filter(s=>s.id.indexOf('matrix_traj')===0).length") == 1
    # ajouter deux exemplaires → identifiants uniques, dans l'ordre
    app.js("document.getElementById('rcAddTraj').click()")
    app.js("document.getElementById('rcAddTraj').click()")
    ids = app.js("reportCfg().sections.filter(s=>s.id.indexOf('matrix_traj')===0).map(s=>s.id)")
    assert ids == ["matrix_traj", "matrix_traj__2", "matrix_traj__3"], ids
    # régler des cotations et des titres distincts
    app.js("""()=>{
      const rows=[...document.querySelectorAll('#rcSeclist .rc-secitem')].filter(it=>it.dataset.sec.indexOf('matrix_traj')===0);
      const want=[['iar','Vue globale'],['ia','Avant mesures'],['ar','Après mesures']];
      rows.forEach((it,k)=>{
        const ss=it.querySelector('[data-role=subset]'); ss.value=want[k][0]; ss.dispatchEvent(new Event('change',{bubbles:true}));
        const ti=it.querySelector('[data-role=sectitle]'); ti.value=want[k][1]; ti.dispatchEvent(new Event('input',{bubbles:true}));
      });
      reportCfgStore().iteration={by:'none',sort:'criticality'}; markDirty();
    }""")
    app.goto("report")
    cards = app.js("[...document.querySelectorAll('#view-report [id^=\"rsec-matrix_traj\"]')].map(c=>({id:c.id,h2:c.querySelector('h2').textContent,svg:c.querySelectorAll('svg').length}))")
    assert [c["id"] for c in cards] == ["rsec-matrix_traj", "rsec-matrix_traj__2", "rsec-matrix_traj__3"], cards
    assert [c["h2"] for c in cards] == ["Vue globale", "Avant mesures", "Après mesures"], cards
    assert all(c["svg"] >= 1 for c in cards), "une matrice n'a pas été tracée"
    # supprimer l'exemplaire du milieu → il ne reste que les deux autres
    app.settings_subtab("report")
    app.js("""()=>{const it=[...document.querySelectorAll('#rcSeclist .rc-secitem')].find(x=>x.dataset.sec==='matrix_traj__2');
      it.querySelector('.rc-rmsec').click();}""")
    ids2 = app.js("reportCfg().sections.filter(s=>s.id.indexOf('matrix_traj')===0).map(s=>s.id)")
    assert ids2 == ["matrix_traj", "matrix_traj__3"], ids2
    assert not app.console_errors()


def test_no_trajectory_instances_in_mode2(app):
    """Mode 2 : la trajectoire reste une section unique (ni bouton d'ajout, ni contrôle de cotation/titre)."""
    app.load("ebios.rae.json")
    app.settings_subtab("report")
    assert not app.js("!!document.getElementById('rcAddTraj')"), "bouton d'ajout présent à tort en mode 2"
    row = app.js("""()=>{const it=[...document.querySelectorAll('#rcSeclist .rc-secitem')].find(x=>x.dataset.sec==='matrix_traj');
      return it?{subset:!!it.querySelector('[data-role=subset]'),title:!!it.querySelector('[data-role=sectitle]'),rm:!!it.querySelector('.rc-rmsec')}:null;}""")
    assert row == {"subset": False, "title": False, "rm": False}, row
    assert not app.console_errors()
