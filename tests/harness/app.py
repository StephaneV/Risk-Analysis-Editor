"""« Page-object » de l'application : charge l'app, pilote onglets/menus/langue/thème,
charge des fixtures, expose les erreurs console. Une instance par test (voir conftest).
"""
import json
from pathlib import Path

from .browser import FIXTURES, app_url

VIEWS = [
    "presentation", "risks", "measures", "links", "objects",
    "matrices", "radars", "stats", "plan", "report", "settings",
]
SETTINGS_SUBTABS = ["display", "grid", "fields", "objtypes", "report", "stats", "radars"]
LANGS = ["fr", "en", "it"]
THEMES = ["light", "dark"]

# Bruit console à ignorer (non significatif pour l'app).
_IGNORE = ("favicon", "ERR_FILE_NOT_FOUND", "net::ERR")


class App:
    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url
        self._errors = []

    # ---- cycle de vie ----
    def open(self):
        self.page.on("console", self._on_console)
        self.page.on("pageerror", lambda e: self._errors.append("PAGEERROR: " + str(e)))
        self.page.goto(app_url(self.base_url), wait_until="load")
        self.page.wait_for_function("typeof applyLoadedData === 'function' && typeof calcEvaluate === 'function'")
        # neutralise les animations pour le déterminisme visuel
        self.page.add_style_tag(content="*{transition:none!important;animation:none!important;caret-color:transparent!important}")
        return self

    def _on_console(self, msg):
        if msg.type == "error":
            txt = msg.text or ""
            if not any(k in txt for k in _IGNORE):
                self._errors.append(txt)

    def console_errors(self):
        return list(self._errors)

    def clear_errors(self):
        self._errors.clear()

    # ---- données ----
    def load(self, name):
        """Charge une analyse fictive depuis tests/fixtures/analyses/<name>."""
        p = Path(name)
        path = p if p.is_absolute() else (FIXTURES / "analyses" / name)
        text = Path(path).read_text(encoding="utf-8")
        self.load_json_text(text, Path(path).name)
        return self

    def load_json_text(self, text, name="fixture.rae.json"):
        self.page.evaluate(
            "([j,n]) => applyLoadedData(JSON.parse(j), n, false)", [text, name]
        )
        return self

    def load_obj(self, obj, name="fixture.rae.json"):
        return self.load_json_text(json.dumps(obj), name)

    # ---- i18n & thème ----
    def set_lang(self, code):
        self._set_select("langSel", code)
        return self

    def set_theme(self, mode):
        self._set_select("themeSel", mode)
        return self

    def _set_select(self, sel_id, value):
        self.page.evaluate(
            "([id,v])=>{const s=document.getElementById(id);if(!s)throw new Error('select '+id+' absent');s.value=v;s.dispatchEvent(new Event('change',{bubbles:true}));}",
            [sel_id, value],
        )

    # ---- navigation ----
    def goto(self, view):
        assert view in VIEWS, f"vue inconnue: {view}"
        self.page.evaluate(
            "v=>{const b=document.querySelector('#tabs [data-view=\"'+v+'\"]');if(!b)throw new Error('onglet '+v+' absent');b.click();}",
            view,
        )
        active = self.page.evaluate(
            "v=>{const s=document.getElementById('view-'+v);return !!(s&&s.classList.contains('active'));}", view
        )
        assert active, f"la vue {view} n'est pas active après clic"
        return self

    def settings_subtab(self, pmode):
        self.goto("settings")
        self.page.evaluate(
            "m=>{const b=document.querySelector('#view-settings [data-pmode=\"'+m+'\"]');if(!b)throw new Error('sous-onglet '+m+' absent');b.click();}",
            pmode,
        )
        return self

    def open_file_menu(self):
        self.page.evaluate("document.getElementById('btnFile').click()")
        return self

    # ---- pilotage DOM ----
    def click(self, selector):
        self.page.evaluate("s=>{const e=document.querySelector(s);if(!e)throw new Error('absent: '+s);e.click();}", selector)
        return self

    def set_input(self, selector, value):
        self.page.evaluate(
            "([s,v])=>{const e=document.querySelector(s);if(!e)throw new Error('absent: '+s);e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));}",
            [selector, value])
        return self

    def modal_open(self):
        return self.page.evaluate("()=>{const m=document.getElementById('modalBg');return !!(m&&m.classList.contains('open'));}")

    def top_modal_click(self, label):
        """Clique le bouton portant `label` dans la modale du dessus (statique ou empilée)."""
        self.page.evaluate(
            "lbl=>{const layers=[...document.querySelectorAll('body > .modal-bg.open')];const top=layers[layers.length-1];const b=[...top.querySelectorAll('footer button')].find(x=>x.textContent.trim()===lbl);if(!b)throw new Error('bouton \"'+lbl+'\" absent');b.click();}",
            label)
        return self

    def top_modal_confirm(self):
        """Clique le bouton primaire (dernier du pied) de la modale empilée du dessus."""
        self.page.evaluate("()=>{const l=[...document.querySelectorAll('body > .modal-bg.open')];const top=l[l.length-1];const bs=[...top.querySelectorAll('footer button')];if(!bs.length)throw new Error('aucun bouton');bs[bs.length-1].click();}")
        return self

    def close_modals(self):
        self.page.evaluate("()=>{try{[...document.querySelectorAll('body > .modal-bg')].forEach(bg=>{if(bg.id!=='modalBg')bg.remove();});if(typeof dynModals!=='undefined')dynModals.length=0;if(typeof closeModal==='function')closeModal();}catch(e){}}")
        return self

    # ---- utilitaires ----
    def js(self, expr, arg=None):
        return self.page.evaluate(expr, arg) if arg is not None else self.page.evaluate(expr)

    def title(self):
        return self.page.title()

    def screenshot(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(path), full_page=True)
        return path

    def view_screenshot(self, view):
        """Capture PNG (octets) de la section de vue active — déterministe (bornée à l'élément)."""
        return self.page.locator(f"#view-{view}").screenshot()

    def docx_bytes(self):
        """Octets du .docx produit par buildDocx() (via base64)."""
        import base64
        b64 = self.page.evaluate(
            "async () => { const bl=await buildDocx(); const u8=new Uint8Array(await bl.arrayBuffer());"
            " let s=''; const CH=0x8000; for(let i=0;i<u8.length;i+=CH) s+=String.fromCharCode.apply(null,u8.subarray(i,i+CH));"
            " return btoa(s); }")
        return base64.b64decode(b64)
