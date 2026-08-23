"""i18n : présence des 3 langues, absence de clés orphelines, parité des clés à espace de noms."""
import pytest

pytestmark = pytest.mark.unit


def test_three_languages_present(app):
    langs = app.js("Object.keys(I18N)")
    for l in ("fr", "en", "it"):
        assert l in langs


def test_no_orphan_keys_in_en_it(app):
    """en/it ne doivent pas contenir de clé absente du fr (le fr est la référence ; le repli
    runtime va lang→fr→clé, donc une clé en/it sans équivalent fr serait un bug)."""
    orphans = app.js("""() => {
      const fr = new Set(Object.keys(I18N.fr));
      const of = l => Object.keys(I18N[l]).filter(k => !fr.has(k));
      return { en: of('en'), it: of('it') };
    }""")
    assert not orphans["en"], f"clés en absentes du fr : {orphans['en'][:20]}"
    assert not orphans["it"], f"clés it absentes du fr : {orphans['it'][:20]}"


def test_namespaced_keys_parity(app):
    """Les clés à espace de noms (contenant un '.') doivent être identiques dans les 3 langues."""
    diff = app.js("""() => {
      const ns = o => Object.keys(o).filter(k => k.includes('.')).sort();
      const fr = ns(I18N.fr), en = ns(I18N.en), it = ns(I18N.it);
      const eq = (a,b) => a.length===b.length && a.every((k,i)=>k===b[i]);
      return { fr_count: fr.length, en_ok: eq(fr,en), it_ok: eq(fr,it) };
    }""")
    assert diff["fr_count"] > 0
    assert diff["en_ok"] and diff["it_ok"], f"parité clés à espace de noms rompue : {diff}"


def test_known_keys_translated(app):
    for lang in ("fr", "en", "it"):
        app.set_lang(lang)
        for key in ("tab_risks", "tab_measures", "tab_report"):
            val = app.js("k => t(k)", key)
            assert val and val != key, f"{lang}/{key} non traduit : {val!r}"
