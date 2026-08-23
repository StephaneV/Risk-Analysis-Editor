"""Modales : champ fautif (focus + contour rouge), lightbox."""
import pytest

pytestmark = pytest.mark.ui

PNG = ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4"
       "2mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")


def test_faulty_field_focus_and_mark(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    app.js("openRiskModal(null)")   # libellé vide
    app.click("#modalOk")           # « Créer » -> refus
    assert app.modal_open(), "la modale doit rester ouverte"
    assert app.js("!!document.querySelector('#modalBody .field-bad')"), "champ fautif non marqué"
    assert app.js("document.getElementById('modalMsg').textContent"), "message d'erreur absent"


def test_duplicate_id_rejected_and_marked(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    app.js("openRiskModal(null)")                 # nouveau risque (id frais)
    app.set_input("#f_label", "Risque de test")   # libellé valide → l'id sera le seul fautif
    app.set_input("#f_id", "R1")                   # id déjà pris
    app.click("#modalOk")
    assert app.modal_open(), "la modale doit rester ouverte sur id dupliqué"
    assert app.js("!!document.querySelector('#f_id.field-bad')") or \
        app.js("document.activeElement && document.activeElement.id === 'f_id'"), \
        "le champ id dupliqué n'est ni marqué ni focalisé"
    assert app.js("document.getElementById('modalMsg').textContent"), "message d'erreur absent"


def test_cell_click_opens_modal(app):
    """Clic sur une cellule de registre → ouverture de la fiche (D01)."""
    app.load("ebios.rae.json")
    app.goto("risks")
    app.js("""()=>{
      const tr = document.querySelector('#risksTable tr');
      const td = [...tr.querySelectorAll('td[data-col]')].find(td=>!td.querySelector('button,.pill,.row-grip'));
      td.click();
    }""")
    assert app.modal_open(), "le clic sur une cellule n'a pas ouvert la fiche"
    app.close_modals()


def test_escape_closes_modal(app):
    """Échap ferme la modale du dessus (D04)."""
    app.load("ebios.rae.json")
    app.goto("risks")
    app.js("openRiskModal(null)")
    assert app.modal_open()
    app.js("()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))")
    assert not app.modal_open(), "Échap n'a pas fermé la modale"


def test_lightbox_closes_on_cross(app):
    """Fermeture de la lightbox par le bouton croix (D05)."""
    app.load("ebios.rae.json")
    app.js("src=>openImageLightbox(src)", PNG)
    assert app.js("document.getElementById('imgLightbox').classList.contains('open')")
    clicked = app.js("()=>{const c=document.querySelector('#imgLightbox .imglb-close'); if(c){c.click(); return true;} return false;}")
    assert clicked, "bouton de fermeture (croix) introuvable"
    assert not app.js("document.getElementById('imgLightbox').classList.contains('open')"), "la croix n'a pas fermé la lightbox"


def test_stacked_modal_inert(app):
    app.load("ebios.rae.json")
    app.goto("risks")
    app.js("openRiskModal(null)")
    assert app.js("!document.getElementById('modalBg').hasAttribute('inert')"), \
        "la modale seule ne doit pas être inerte"
    app.js("()=>confirmModal('Confirmer ?', ()=>{})")   # confirmation empilée au-dessus
    assert app.js("document.getElementById('modalBg').hasAttribute('inert')"), \
        "la modale sous-jacente doit devenir inerte"
    app.top_modal_confirm()                              # répondre à la confirmation
    assert app.js("!document.getElementById('modalBg').hasAttribute('inert')"), \
        "la modale doit redevenir active après fermeture de la confirmation"
    app.close_modals()


def test_lightbox_opens_and_closes(app):
    app.load("ebios.rae.json")
    app.js("src=>openImageLightbox(src)", PNG)
    assert app.js("()=>{const lb=document.getElementById('imgLightbox');return !!lb && lb.classList.contains('open');}"), "lightbox non ouverte"
    app.js("()=>{ if(typeof closeImageLightbox==='function') closeImageLightbox(); }")
    assert app.js("()=>{const lb=document.getElementById('imgLightbox');return !lb || !lb.classList.contains('open');}"), "lightbox non fermée"


def test_lightbox_closes_on_escape(app):
    app.load("ebios.rae.json")
    app.js("src=>openImageLightbox(src)", PNG)
    assert app.js("document.getElementById('imgLightbox').classList.contains('open')"), "lightbox non ouverte"
    app.js("()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}))")
    assert app.js("!document.getElementById('imgLightbox').classList.contains('open')"), "Échap n'a pas fermé la lightbox"
