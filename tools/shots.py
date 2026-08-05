# -*- coding: utf-8 -*-
# Génère les captures d'écran du guide utilisateur à partir de la démo AIPD.
# Playwright (Edge/Chromium), interface FR, thème clair, viewport 1280.
# Réexécutable : re-génère toutes les images dans docs/images/.
import os
from PIL import Image
from playwright.sync_api import sync_playwright

# Origine du serveur statique (repertoire du depot). Surchargée par SHOTS_ORIGIN si defini.
ORIGIN = os.environ.get("SHOTS_ORIGIN", "http://localhost:4599")
BASE = ORIGIN + "/app/risk-analysis-editor.html"
MAX_H = 1400     # hauteur maximale d'une capture : au-dela, l'image est coupee (recadrage)
FADE  = 120      # hauteur du degrade de fondu applique au bas des captures coupees
DEMO = "?file=../examples/demo-aipd-sst.rae.json&lang=fr"
OUT  = "docs/images/"

def fondu_bas(im):
    """Fond le bas de l'image vers la transparence : signale que le contenu est tronque.
    N'est applique qu'aux captures depassant MAX_H (donc reellement coupees)."""
    im = im.convert("RGBA")
    w, h = im.size
    col = Image.new("L", (1, FADE))                       # degrade vertical 1 px de large
    for i in range(FADE):
        col.putpixel((0, i), round(255 * (1 - i / (FADE - 1))))   # 255 en haut -> 0 en bas
    grad = col.resize((w, FADE))                          # etire sur toute la largeur
    alpha = im.getchannel("A")
    alpha.paste(grad, (0, h - FADE))                      # applique au bas de l'image
    im.putalpha(alpha)
    return im

# (nom, suffixe URL, prep JS après chargement, pleine page ?, hauteur viewport)
SHOTS = [
    ("guide-01-accueil",            "?lang=fr",                 None, True,  940),
    ("guide-02-presentation",       DEMO+"&tab=presentation",   None, True,  940),
    ("guide-03-parametres-grille",  DEMO+"&tab=settings.grid",  None, True,  940),
    ("guide-04-parametres-affichage",DEMO+"&tab=settings.display",None,True, 940),
    ("guide-05-parametres-champs",  DEMO+"&tab=settings.fields",None, False, 940),
    ("guide-06-champ-editeur",      DEMO+"&tab=settings.fields",
        "document.querySelector('[data-cf-edit=\"2\"]').click();var s=document.getElementById('cfTagPalette');if(s){s.value='vives';s.dispatchEvent(new Event('change',{bubbles:true}));}", False, 1120),
    ("guide-07-risques",            DEMO+"&tab=risks",          None, True,  940),
    ("guide-08-fiche-risque",       DEMO+"&tab=risks",
        "openRiskModal('R1')", False, 1120),
    ("guide-09-mesures",            DEMO+"&tab=measures",       None, True,  940),
    ("guide-10-fiche-mesure",       DEMO+"&tab=measures",
        "openMeasureModal('M1')", False, 1120),
    ("guide-11-liens-associations", DEMO+"&tab=links",          None, True,  940),
    ("guide-12-liens-details",      DEMO+"&tab=links.details",  None, True,  940),
    ("guide-13-fiche-lien",         DEMO+"&tab=links.details",
        "openLinkModal('R1','M1')", False, 1040),
    ("guide-14-matrices-ir",        DEMO+"&tab=matrices",       None, True,  1120),
    ("guide-15-matrices-trajectoire",DEMO+"&tab=matrices.traj", None, True,  1120),
    ("guide-23-statistiques",       DEMO+"&tab=stats",          None, True,  1180),
    ("guide-16-plan-echeancier",    DEMO+"&tab=plan",           None, True,  940),
    ("guide-17-plan-kanban",        DEMO+"&tab=plan.status",    None, True,  1040),
    ("guide-18-rapport",            DEMO+"&tab=report",         None, False, 1180),
    ("guide-22-parametres-rapport", DEMO+"&tab=settings.report",
        "setParamMode('report')", True,  1180),
    ("guide-19-menu-colonnes",      DEMO+"&tab=risks",
        "document.querySelector('#risksTableEl thead .colgear').click()", False, 940),
    ("guide-20-menu-fichier",       DEMO+"&tab=risks",
        "document.getElementById('btnFile').click()", False, 620),
    ("guide-21-aide-raccourcis",    DEMO+"&tab=risks",
        "openHelpModal()", False, 1040),
]

def run():
    only = os.environ.get("SHOTS_ONLY")
    only = set(x.strip() for x in only.split(",")) if only else None
    with sync_playwright() as p:
        # Mode HEADED (non-headless) : en headless, Chromium ne rend AUCUNE scrollbar
        # (cf. playwright#5778) — les modales scrollables (ex. guide-06) apparaissaient sans barre.
        browser = p.chromium.launch(channel="msedge", headless=False)
        for name, url, prep, full, h in SHOTS:
            if only and name not in only: continue
            ctx = browser.new_context(locale="fr-FR", color_scheme="light",
                                      viewport={"width":1280,"height":h},
                                      device_scale_factor=1)
            page = ctx.new_page()
            page.goto(BASE+url, wait_until="networkidle")
            # attendre l'initialisation
            if "accueil" in name:
                page.wait_for_selector("#startCard", state="visible", timeout=8000)
            else:
                page.wait_for_function("() => typeof analyse!=='undefined' && analyse.risks && analyse.risks.length>0", timeout=12000)
            page.wait_for_timeout(500)
            if prep:
                page.evaluate(prep)
                page.wait_for_timeout(600)
            # masquer le toast « Analyse chargée » (retrait instantané, pas de fondu résiduel)
            page.evaluate("try{var t=document.getElementById('toast');if(t){t.classList.remove('show');t.style.display='none';}}catch(e){}")
            # Le fond (degrade) est en background-attachment:fixed : en capture pleine page il ne
            # couvrirait que la hauteur du viewport initial (gris qui « ne descend pas jusqu'en bas »).
            # On le repasse en 'scroll' pour qu'il couvre toute la hauteur du contenu capture.
            page.add_style_tag(content="html,body{background-attachment:scroll !important}")
            page.wait_for_timeout(120)
            page.screenshot(path=OUT+name+".png", full_page=full)
            # Plafonner la hauteur a MAX_H ; sur les captures ainsi coupees, appliquer un
            # degrade de fondu en bas pour signaler que le contenu se poursuit.
            img = Image.open(OUT+name+".png")
            if img.height > MAX_H:
                fondu_bas(img.crop((0, 0, img.width, MAX_H))).save(OUT+name+".png")
            img.close()
            print("écrit :", OUT+name+".png")
            ctx.close()
        browser.close()

run()
print("Terminé.")
