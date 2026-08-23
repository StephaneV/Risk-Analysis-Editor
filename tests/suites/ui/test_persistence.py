"""Persistance : aller-retour sérialisation → rechargement."""
import pytest

pytestmark = pytest.mark.ui


def test_serialize_reload_roundtrip(app):
    app.load("ebios.rae.json")
    title = app.js("analyse.metadata.title")
    nr = app.js("analyse.risks.length")
    nm = app.js("analyse.measures.length")
    dump = app.js("JSON.stringify(analyse)")
    app.js("j=>applyLoadedData(JSON.parse(j),'reload',false)", dump)
    assert app.js("analyse.metadata.title") == title
    assert app.js("analyse.risks.length") == nr
    assert app.js("analyse.measures.length") == nm
    assert not app.console_errors()


def test_roundtrip_with_objects_and_fields(app):
    app.load("tous-types-champs.rae.json")
    dump = app.js("JSON.stringify(analyse)")
    ncf = app.js("analyse.custom_fields.length")
    nobj = app.js("analyse.objects.length")
    app.js("j=>applyLoadedData(JSON.parse(j),'reload',false)", dump)
    assert app.js("analyse.custom_fields.length") == ncf
    assert app.js("analyse.objects.length") == nobj
    assert not app.console_errors()


def test_autosave_roundtrip(app):
    app.load("ebios.rae.json")
    title = app.js("analyse.metadata.title")
    nr = app.js("analyse.risks.length")
    # autosaveWrite ne persiste que si l'analyse est « sale » et non vierge
    snap = app.js("""async () => {
      dirty = true; isFresh = false;
      await autosaveWrite();
      return await autosaveRead();
    }""")
    assert snap is not None, "aucun instantané de sauvegarde auto"
    assert snap["title"] == title
    assert snap["risks"] == nr
    assert "json" in snap and title in snap["json"]
    # nettoyage du magasin de sauvegarde auto
    app.js("async () => { await autosaveClear(); }")
    assert app.js("async () => await autosaveRead()") is None


def test_autosave_restore_offer(app):
    """D10 : au démarrage, autosaveOffer propose de restaurer l'instantané ; confirmer le restaure."""
    app.load("ebios.rae.json")
    title = app.js("analyse.metadata.title")
    nr = app.js("analyse.risks.length")
    # écrit un instantané puis simule un démarrage « frais » avec une analyse différente
    app.js("""async () => {
      dirty = true; isFresh = false;
      await autosaveWrite();
      isFresh = true;                       // rien chargé par ailleurs -> l'offre s'affiche
      analyse = { format:'x', metadata:{title:'AUTRE'}, grid:analyse.grid, risks:[], measures:[], treatments:[] };
    }""")
    app.js("async () => { await autosaveOffer(); }")   # ouvre la confirmation
    assert app.js("!!document.querySelector('body > .modal-bg.open')"), "aucune offre de restauration"
    app.top_modal_confirm()                            # « Restaurer »
    assert app.js("analyse.metadata.title") == title, "analyse non restaurée"
    assert app.js("analyse.risks.length") == nr
    app.js("async () => { await autosaveClear(); }")


def test_recents_store_add_and_clear(app):
    """D10/M11 : magasin des récents (IndexedDB) — écriture d'une entrée puis vidage."""
    entry = app.js("""async () => {
      // insère une entrée factice directement dans le magasin (sans handle FS réel)
      await rcTx('readwrite', st => st.put({id:'rec-test', name:'demo.rae.json', at:'2026-01-01'}));
      return (await rcGetAll()).map(r => r.id);
    }""")
    assert "rec-test" in (entry or []), "entrée récente non stockée"
    empty = app.js("async () => { await recentClear(); return (await rcGetAll()).length; }")
    assert empty == 0, "recentClear n'a pas vidé le magasin"
