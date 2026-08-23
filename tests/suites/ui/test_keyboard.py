"""Navigation & manipulation clavier : onglets (ARIA tablist), kanban, réordonnancement de lignes,
menu Fichier."""
import pytest

pytestmark = pytest.mark.ui


def test_tablist_arrow_navigation(app):
    app.load("ebios.rae.json")
    r = app.js("""()=>{
      const tab=document.querySelector('#tabs [data-view="risks"]'); tab.focus();
      tab.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
      return document.activeElement.getAttribute('data-view');
    }""")
    assert r and r != "risks", "flèche droite dans la tablist ne déplace pas le focus"


def test_kanban_ctrl_arrow_moves_card(app):
    app.load("ebios.rae.json")
    app.goto("plan")
    r = app.js("""()=>{
      planMode='status'; renderPlan();
      let card=document.querySelector('#view-plan .plan-card'); if(!card) return null;
      const mid=card.dataset.mid;
      measureById(mid).status='proposed'; renderPlan();
      card=[...document.querySelectorAll('#view-plan .plan-card')].find(c=>c.dataset.mid===mid);
      card.focus();
      card.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',ctrlKey:true,bubbles:true}));
      return measureById(mid).status;
    }""")
    assert r == "planned", f"Ctrl+→ devrait faire passer proposed→planned (obtenu {r})"


def test_row_reorder_ctrl_arrow(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    r = app.js("""()=>{
      const before = analyse.risks.map(x=>x.id);
      const grip = document.querySelector('#risksTable tr .row-grip');   // poignée focalisable
      if(!grip) return {err:'pas de poignée'};
      grip.focus();
      grip.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowDown',ctrlKey:true,bubbles:true}));
      return { before, after: analyse.risks.map(x=>x.id) };
    }""")
    assert "err" not in r, r.get("err")
    assert r["after"] != r["before"], "Ctrl+↓ ne réordonne pas les lignes"
    assert r["after"][1] == r["before"][0], "le 1er risque devrait descendre d'un cran"


def test_file_menu_arrow_navigation(app):
    app.load("ebios.rae.json")
    r = app.js("""()=>{
      document.getElementById('btnFile').click();
      const menu=document.getElementById('fileMenu');
      menu.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true}));
      const el=document.activeElement;
      return { open: menu.classList.contains('open'), focusedInMenu: menu.contains(el) };
    }""")
    assert r["open"] and r["focusedInMenu"], "navigation clavier du menu Fichier inopérante"
