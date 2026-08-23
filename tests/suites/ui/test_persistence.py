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
