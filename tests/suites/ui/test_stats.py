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
