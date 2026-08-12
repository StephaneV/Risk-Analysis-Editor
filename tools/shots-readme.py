# -*- coding: utf-8 -*-
"""
Génère les captures d'écran du README (docs/images/) à partir de l'application,
en anglais et thème clair :

  - capture-trajectoire.png     : Matrices › Trajectoire, avec le curseur survolant
                                   la flèche du risque R1 et l'infobulle du lien visible ;
  - capture-statistiques.png    : onglet Statistiques (tableau de bord) ;
  - capture-plan-echeancier.png : Plan d'action, vue échéancier.

Playwright ne capture pas le curseur de l'OS : un faux curseur (flèche) est injecté
au point survolé.

Utilisation (depuis la racine du dépôt) :
  1) servir le dépôt :        python -m http.server 4599 --bind 127.0.0.1
  2) lancer le script :       python tools/shots-readme.py
     (autre origine au besoin : SHOTS_ORIGIN=http://localhost:PORT python tools/shots-readme.py)
"""
import os
from playwright.sync_api import sync_playwright

ORIGIN = os.environ.get("SHOTS_ORIGIN", "http://localhost:4599")
BASE = ORIGIN + "/app/risk-analysis-editor.html"
OUT = "docs/images/"

# Faux curseur (flèche) — le tip est à ~(1.5, 1) dans le viewBox.
CURSOR = ('<svg width="21" height="30" viewBox="0 0 21 30" xmlns="http://www.w3.org/2000/svg" '
          'style="display:block;filter:drop-shadow(1px 1px 1.5px rgba(0,0,0,.45))">'
          '<path d="M1.5 1 L1.5 22.5 L7 17.2 L10.6 25.6 L14.2 24 L10.6 15.8 L18 15.8 Z" '
          'fill="#1b1b1b" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/></svg>')

def ctx(browser, height):
    return browser.new_context(locale="en-US", color_scheme="light",
                               viewport={"width": 1180, "height": height},
                               device_scale_factor=2)

def prep(page):
    page.wait_for_timeout(600)
    page.evaluate("try{var t=document.getElementById('toast');if(t){t.classList.remove('show');t.style.display='none';}}catch(e){}")
    page.add_style_tag(content="html,body{background-attachment:scroll !important}")
    page.wait_for_timeout(120)

def hero(browser):
    c = ctx(browser, 1160); page = c.new_page()
    page.goto(BASE + "?file=../examples/demo-ebios-rm-information-system.rae.json&lang=en&tab=matrices.traj",
              wait_until="networkidle")
    page.wait_for_function("() => document.querySelector('#matrixArea svg line')", timeout=12000)
    prep(page)
    # Milieu de la flèche du risque R1 (moyenne des centres de ses deux pastilles).
    RID = "R1"
    p = page.evaluate("""(rid) => {
      const els = [...document.querySelectorAll('#matrixArea [data-rid="' + rid + '"]')];
      if (els.length < 2) return null;
      const pts = els.map(e => { const r = e.getBoundingClientRect(); return {x:r.left+r.width/2, y:r.top+r.height/2}; });
      return { x: (pts[0].x+pts[1].x)/2, y: (pts[0].y+pts[1].y)/2 };
    }""", RID)
    if p:
        page.mouse.move(p["x"], p["y"]); page.wait_for_timeout(80)   # surligne la flèche
        # Infobulle du lien, affichée de façon déterministe (mêmes contenus que attachArrowTip).
        page.evaluate("""(a) => {
          const el = document.elementFromPoint(a.x, a.y);
          if (el) el.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true, clientX:a.x, clientY:a.y}));  // surlignage de la flèche
          // Contenu autonome (mêmes données que l'infobulle de lien), en anglais.
          const esc = s => String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
          const STL = {proposed:'Proposed', planned:'Planned', in_progress:'In progress', implemented:'Implemented', abandoned:'Abandoned'};
          const COL = {proposed:'#94a3b8', planned:'#4c7dff', in_progress:'#e0b93a', implemented:'#2e9e5b', abandoned:'#c0505a'};
          const FG  = {in_progress:'#3a2e05'};
          const risk = analyse.risks.find(r => r.id === a.rid); if (!risk) return;
          const seen = {};
          const mids = analyse.treatments.filter(x => x.risk === a.rid).map(x => x.measure).filter(id => seen[id] ? false : (seen[id] = 1));
          const rows = mids.map(id => {
            const m = analyse.measures.find(x => x.id === id), st = m && m.status;
            const badge = st ? ' <span style="background:' + (COL[st]||'#94a3b8') + ';color:' + (FG[st]||'#fff')
                + ';border-radius:4px;padding:1px 6px;font-size:11px;font-weight:700">' + esc(STL[st]||st) + '</span>' : '';
            return '• ' + esc(id) + (m ? ' · ' + esc(m.label) : '') + badge;
          });
          const list = rows.length ? rows.join('<br>') : '<span class="t-cat">No linked control</span>';
          tip.classList.remove('tt-link');
          tip.innerHTML = '<b>' + esc(risk.id) + ' — ' + esc(risk.label) + '</b><br><span class="t-cat">Linked controls</span><br>' + list;
          tip.style.opacity = 1; tip.style.left = (a.x + 16) + 'px'; tip.style.top = (a.y + 16) + 'px';
        }""", {"x": p["x"], "y": p["y"], "rid": RID})
        page.wait_for_timeout(120)
        # Faux curseur au milieu de la flèche.
        page.evaluate("""(a) => { const c = document.createElement('div'); c.id='__cursor';
          c.style.cssText = 'position:fixed;left:'+(a.x-2)+'px;top:'+(a.y-1)+'px;z-index:2147483647;pointer-events:none';
          c.innerHTML = a.cursor; document.body.appendChild(c); }""", {"x": p["x"], "y": p["y"], "cursor": CURSOR})
    page.wait_for_timeout(120)
    page.screenshot(path=OUT + "capture-trajectoire.png", full_page=False)
    print("écrit :", OUT + "capture-trajectoire.png"); c.close()

def statistiques(browser):
    c = ctx(browser, 1000); page = c.new_page()
    page.goto(BASE + "?file=../examples/demo-ebios-rm-information-system.rae.json&lang=en&tab=stats", wait_until="networkidle")
    page.wait_for_function("() => document.querySelectorAll('#stats .st-card').length > 0", timeout=12000)
    prep(page)
    page.screenshot(path=OUT + "capture-statistiques.png", full_page=False)
    print("écrit :", OUT + "capture-statistiques.png"); c.close()

def plan(browser):
    c = ctx(browser, 900); page = c.new_page()
    page.goto(BASE + "?file=../examples/demo-ebios-rm-information-system.rae.json&lang=en&tab=plan", wait_until="networkidle")
    page.wait_for_function("() => document.querySelector('#planArea table')", timeout=12000)
    prep(page)
    page.screenshot(path=OUT + "capture-plan-echeancier.png", full_page=False)
    print("écrit :", OUT + "capture-plan-echeancier.png"); c.close()

def run():
    with sync_playwright() as p:
        # Mode HEADED (comme tools/shots-guide.py) : en headless, Chromium ne rend aucune barre de
        # défilement (cf. playwright#5778). Nécessite un environnement graphique.
        b = p.chromium.launch(channel="msedge", headless=False)
        hero(b); statistiques(b); plan(b)
        b.close()

run()
print("Terminé.")
