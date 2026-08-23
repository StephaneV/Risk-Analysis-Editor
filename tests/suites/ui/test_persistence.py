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
