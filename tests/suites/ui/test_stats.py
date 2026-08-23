"""Vue Statistiques : blocs rendus, contenu non vide."""
import pytest

pytestmark = pytest.mark.ui


def test_stats_render(app):
    app.load("ebios.rae.json")
    app.goto("stats")
    # au moins quelques éléments rendus dans la vue
    assert app.js("document.getElementById('view-stats').querySelectorAll('*').length") > 20
    assert not app.console_errors()


def test_stats_on_objects_fixture(app):
    app.load("ebios-objets.rae.json")
    app.goto("stats")
    assert not app.console_errors()
    assert app.js("document.getElementById('view-stats').querySelectorAll('*').length") > 20


def test_stat_counters_control(app):
    """Analyse de contrôle (6 risques, 4 mesures, 3 réduits → 50 %) — porté de test-stats."""
    app.load("analyse-test-stats.rae.json")
    c = app.js("statCounters()")
    assert c["nR"] == 6 and c["nM"] == 4
    assert c["treated"] == 3 and c["pct"] == 50


def test_stats_settings_toggle_and_reset(app):
    """Paramètres › Statistiques (S06) : bascule on/off d'un bloc + réinitialisation."""
    app.load("ebios.rae.json")
    app.settings_subtab("stats")
    assert app.js("document.querySelectorAll('#statsCfgPanel .st2-row').length") > 0
    r = app.js("""()=>{
      const b = statsCfg()[0]; const on = b.on !== false;
      statsUpdate(b.id, {on: !on});
      return { on, after: statsCfg().find(x=>x.id===b.id).on !== false, id: b.id };
    }""")
    assert r["after"] != r["on"], "bascule on/off d'un bloc stats sans effet"
    # la réinitialisation supprime la config stockée et restaure l'état par défaut du bloc
    app.js("()=>statsReset()")
    assert app.js("statsCfg().length") > 0
    assert app.js("s=>statsCfg().find(x=>x.id===s).on !== false", r["id"]) == r["on"], \
        "la réinitialisation n'a pas restauré l'état par défaut du bloc"
    assert not app.console_errors()


def test_stats_add_num_block(app):
    """S06 : ajout d'un bloc « agrégat numérique » (tuile, affichage tableau)."""
    app.load("tous-types-champs.rae.json")
    app.settings_subtab("stats")
    if not app.js("statNumCandidates().length"):
        pytest.skip("aucun champ numérique agrégable dans la fixture")
    before = app.js("statsCfg().length")
    app.js("()=>statsAddNum()")
    assert app.js("statsCfg().length") == before + 1
    b = app.js("statsCfg().find(x=>x.type==='num_agg')")
    assert b and b["display"] == "table", "le bloc num_agg devrait s'afficher en tableau"
    assert not app.console_errors()


def test_stats_custom_block_shape_and_display(app):
    """S06 : forme (donut/pie) et affichage (table/chart/both) d'un bloc perso."""
    app.load("tous-types-champs.rae.json")
    app.settings_subtab("stats")
    if not app.js("statCustomCandidates().length"):
        pytest.skip("aucun champ à valeurs fermées pour un bloc perso")
    app.js("()=>statsAddCustom()")
    r = app.js("""()=>{
      const b = statsCfg().find(x=>x.type==='custom'); if(!b) return null;
      statsUpdate(b.id, {shape:'pie', display:'chart'});
      const nb = statsCfg().find(x=>x.id===b.id);
      return { shape: nb.shape, display: nb.display };
    }""")
    assert r and r["shape"] == "pie" and r["display"] == "chart", f"forme/affichage non appliqués : {r}"
    assert not app.console_errors()


def test_stats_reorder(app):
    """Réordonnancement d'un bloc stats via statsMove (alternative au glisser) — T08."""
    app.load("ebios.rae.json")
    app.settings_subtab("stats")
    before = app.js("statsCfg().map(b=>b.id)")
    if len(before) < 3:
        pytest.skip("pas assez de blocs pour réordonner")
    # place le 1er bloc juste avant le 3e
    r = app.js("""()=>{
      const ids = statsCfg().map(b=>b.id);
      statsMove(ids[0], ids[2]);
      return statsCfg().map(b=>b.id);
    }""")
    assert r != before, "statsMove n'a pas changé l'ordre"
    assert sorted(r) == sorted(before), "statsMove a ajouté/perdu un bloc"
    assert not app.console_errors()
