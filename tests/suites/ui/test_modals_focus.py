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


def test_cell_dblclick_opens_modal(app):
    """Double-clic sur une cellule de registre → ouverture de la fiche ; simple-clic inerte (D01)."""
    app.load("ebios.rae.json")
    app.goto("risks")
    r = app.js("""()=>{
      const tr = document.querySelector('#risksTable tr');
      const td = [...tr.querySelectorAll('td[data-col]')].find(td=>!td.querySelector('button,.pill,.row-grip'));
      const fire = t => td.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,view:window}));
      const open = () => !!document.querySelector('body > .modal-bg.open');
      fire('click');    const single = open();
      fire('dblclick'); const dbl = open();
      return { single, dbl };
    }""")
    assert not r["single"], "un simple-clic sur une cellule ne doit plus ouvrir la fiche"
    assert r["dbl"], "le double-clic sur une cellule n'a pas ouvert la fiche"
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


D03_SETUP = r"""
() => {
  analyse.custom_fields = [
    {code:'oblig', target:'risk', type:'text', required:true, label:{fr:'Obligatoire'}},
    {code:'note',  target:'risk', type:'integer', min:0, max:10, label:{fr:'Note'}}];
  analyse.risks = []; analyse.measures = []; analyse.treatments = [];
}
"""


def test_required_custom_field_blocks_save(app):
    """D03 : un champ perso obligatoire vide bloque l'enregistrement (message + .field-bad)."""
    app.load("ebios.rae.json")
    app.js(D03_SETUP)
    app.goto("risks")
    app.js("openRiskModal(null)")
    app.set_input("#f_label", "Risque de test")   # libellé OK → le champ obligatoire est le fautif
    app.click("#modalOk")
    assert app.modal_open(), "la modale doit rester ouverte (champ obligatoire vide)"
    assert app.js("!!document.querySelector('#modalBody .field-bad')"), "champ obligatoire non marqué"
    assert app.js("document.getElementById('modalMsg').textContent"), "message d'erreur absent"


def test_out_of_bounds_custom_field_blocks_save(app):
    """D03 : une valeur numérique hors bornes bloque l'enregistrement."""
    app.load("ebios.rae.json")
    app.js(D03_SETUP)
    app.goto("risks")
    app.js("openRiskModal(null)")
    app.set_input("#f_label", "Risque de test")
    app.set_input("#modalBody [data-cf='oblig'] input", "rempli")   # satisfait l'obligatoire
    app.set_input("#modalBody [data-cf='note'] input", "99")        # > max (10)
    app.click("#modalOk")
    assert app.modal_open(), "la modale doit rester ouverte (valeur hors bornes)"
    assert app.js("!!document.querySelector('#modalBody .field-bad')"), "champ hors bornes non marqué"


def test_object_type_modal_validation(app):
    """D02 : la modale « type d'objet » refuse un code vide."""
    app.load("ebios-objets.rae.json")
    before = app.js("objectTypes().length")
    app.js("()=>openObjectTypeModal(null)")     # nouveau type (modale empilée)
    app.top_modal_confirm()                     # « Créer » avec des champs vides
    assert app.js("document.getElementById('otMsg').textContent"), "aucun message de validation (type d'objet)"
    assert app.js("objectTypes().length") == before, "un type invalide a été créé"
    app.close_modals()


def test_custom_field_modal_validation(app):
    """D02 : la modale « champ personnalisé » refuse un code/libellé vide."""
    app.load("ebios.rae.json")
    app.settings_subtab("fields")
    before = app.js("(analyse.custom_fields||[]).length")
    app.js("openCustomFieldModal(null)")
    app.click("#modalOk")                       # « Créer » sans rien saisir
    assert app.modal_open(), "la modale champ perso doit rester ouverte"
    assert app.js("(analyse.custom_fields||[]).length") == before, "un champ invalide a été créé"


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


def test_url_value_click_does_not_open_modal(app):
    """Clic sur une valeur de champ perso URL : ouvre le lien (nouvel onglet) sans ouvrir la fiche."""
    app.load("ebios-objets.rae.json")
    app.js("""()=>{
      const ot=analyse.object_types[0];
      if(!ot.attributes.some(a=>a.code==='lien')) ot.attributes.push({code:'lien',type:'url',label:{fr:'Lien'}});
      const inst=objectsOfType(ot.code)[0]; inst.values=inst.values||{}; inst.values.lien='https://example.org/';
      renderAll();
    }""")
    app.goto("objects")
    r = app.js("""()=>{
      const a=document.querySelector('#view-objects a[href=\"https://example.org/\"]');
      if(!a) return {anchor:false};
      a.addEventListener('click',e=>e.preventDefault());   // évite l'ouverture réelle d'un onglet en test
      a.click();
      const dyn=[...document.querySelectorAll('body>.modal-bg.open')].length;
      return {anchor:true, target:a.getAttribute('target'),
              modalOpen: !!(document.getElementById('modalBg')||{}).classList?.contains('open') || dyn>0};
    }""")
    assert r["anchor"], "lien URL non rendu dans la vue objets"
    assert r["target"] == "_blank", "le lien doit s'ouvrir dans un nouvel onglet"
    assert r["modalOpen"] is False, "le clic sur le lien ne doit pas ouvrir la fiche d'édition"
    assert not app.console_errors()


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
