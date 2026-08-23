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
