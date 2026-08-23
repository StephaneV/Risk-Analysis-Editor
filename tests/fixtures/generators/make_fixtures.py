#!/usr/bin/env python3
"""Génère les fixtures d'analyses SYNTHÉTIQUES, auto-validées.

Chaque fixture est construite in-page (à partir de emptyAnalysis ou d'une base chargée), passée par
`applyLoadedData` (normalisation), puis sérialisée. Elle est ensuite RECHARGÉE pour vérifier qu'elle
est acceptée sans erreur console. Écrit dans tests/fixtures/analyses/.

Usage : python tests/fixtures/generators/make_fixtures.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "tests"))

from playwright.sync_api import sync_playwright
from harness.browser import start_server, app_url  # noqa: E402

OUT = ROOT / "tests" / "fixtures" / "analyses"

PNG_1x1 = ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4"
           "2mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")

# --- builders JS (retournent la chaîne JSON de l'analyse normalisée) ---
BUILDERS = {

"vide": """
() => { applyLoadedData(emptyAnalysis('fr'), 'x', false); return JSON.stringify(analyse); }
""",

"minimale": """
() => {
  const a = emptyAnalysis('fr');
  a.metadata.title = 'Analyse minimale';
  a.risks.push({id:'R1', label:'Risque unique', category:'Général', owner:'Propriétaire',
    description:'Description **Markdown** du risque.',
    initial_assessment:{probability:4, severity:4}, residual_assessment:{probability:2, severity:3}});
  a.measures.push({id:'M1', label:'Mesure unique', type:'preventive', status:'planned', responsible:'RSSI'});
  a.treatments.push({risk:'R1', measure:'M1'});
  applyLoadedData(a, 'x', false); return JSON.stringify(analyse);
}
""",

"titre-long": """
async () => {
  const r = await fetch('/tests/fixtures/analyses/ebios.rae.json'); const a = await r.json();
  a.metadata.title = "Analyse de risques inspirée d'EBIOS RM — Système d'information critique d'un établissement multi-sites avec sous-traitance et hébergement externalisé (jeu de test au titre volontairement très long pour éprouver le retour à la ligne)";
  applyLoadedData(a, 'x', false); return JSON.stringify(analyse);
}
""",

"volumineuse": """
() => {
  const a = emptyAnalysis('fr');
  a.metadata.title = 'Analyse volumineuse (perf / débordement)';
  const cats = ['Cybersécurité','Infrastructure','RH','Conformité','Supply chain','Juridique','Sûreté'];
  const N = 60;
  for (let i=1;i<=N;i++){
    const p = (i%5)+1, g = ((i*3)%5)+1, rp = Math.max(1,p-1), rg = Math.max(1,g-1);
    a.risks.push({id:'R'+i, label:'Risque numéro '+i, category:cats[i%cats.length], owner:'Resp '+(i%7),
      initial_assessment:{probability:p, severity:g}, residual_assessment:{probability:rp, severity:rg}});
  }
  for (let j=1;j<=20;j++) a.measures.push({id:'M'+j, label:'Mesure '+j, type:'preventive', status:'planned'});
  for (let i=1;i<=N;i++) a.treatments.push({risk:'R'+i, measure:'M'+((i%20)+1)});
  applyLoadedData(a, 'x', false); return JSON.stringify(analyse);
}
""",

"grille-3x3": """
() => {
  const a = emptyAnalysis('fr');
  a.metadata.title = 'Grille 3×3';
  const lv = [['Faible',1],['Moyen',2],['Fort',3]].map(([label,value])=>({value,label}));
  a.grid.vertical_axis = {label:'Vraisemblance', levels:lv};
  a.grid.horizontal_axis = {label:'Gravité', levels:lv};
  a.grid.criticality_levels = [
    {code:'faible', label:'Faible', score_min:1, score_max:2, color:'#2e9e5b', acceptance:'acceptable', order:1},
    {code:'modere', label:'Modéré', score_min:3, score_max:4, color:'#e0b93a', acceptance:'tolerable', order:2},
    {code:'eleve', label:'Élevé', score_min:5, score_max:6, color:'#e6862e', acceptance:'to_treat', order:3},
    {code:'critique', label:'Critique', score_min:7, score_max:9, color:'#d64545', acceptance:'unacceptable', order:4}];
  a.risks.push({id:'R1', label:'Risque 3×3', category:'Général',
    initial_assessment:{probability:3, severity:3}, residual_assessment:{probability:1, severity:2}});
  applyLoadedData(a, 'x', false); return JSON.stringify(analyse);
}
""",

"grille-5x5": """
() => {
  const a = emptyAnalysis('fr');   // la grille par défaut est déjà 5×5
  a.metadata.title = 'Grille 5×5';
  a.risks.push({id:'R1', label:'Risque 5×5 max', category:'Général',
    initial_assessment:{probability:5, severity:5}, residual_assessment:{probability:2, severity:3}});
  a.risks.push({id:'R2', label:'Risque 5×5 bas', category:'Général',
    initial_assessment:{probability:2, severity:2}, residual_assessment:{probability:1, severity:1}});
  applyLoadedData(a, 'x', false); return JSON.stringify(analyse);
}
""",

"grille-transposee": """
async () => {
  const r = await fetch('/tests/fixtures/analyses/ebios.rae.json'); const a = await r.json();
  a.metadata.title = 'Grille transposée (axes échangés)';
  applyLoadedData(a, 'x', false);
  transposeAxes();               // échange axe vertical/horizontal + cotations
  return JSON.stringify(analyse);
}
""",

"tous-types-champs": """
(PNG) => {
  const a = emptyAnalysis('fr');
  a.metadata.title = 'Tous les types de champs personnalisés';
  // type d'objet référencé (pour le champ 'reference')
  a.object_types.push({code:'srv', prefix:'SRV', label:{fr:'Serveur'}, attributes:[
    {code:'nom', type:'text', label:{fr:'Nom'}},
    {code:'niveau', type:'scale', label:{fr:'Niveau'}, items:[{value:1,label:'Bas'},{value:2,label:'Moyen'},{value:3,label:'Haut'}]},
    {code:'crit', type:'computed', label:{fr:'Niveau ×10'}, expr:'=cf.niveau*10', result_type:'integer'},
    {code:'couleur', type:'color', label:{fr:'Couleur'}, color_mode:'both'}
  ]});
  a.objects.push({id:'SRV1', type:'srv', values:{nom:'Serveur A', niveau:3, couleur:'#c0392b'}});
  a.objects.push({id:'SRV2', type:'srv', values:{nom:'Serveur B', niveau:1, couleur:'#2980b9'}});
  // un champ perso par type, cible 'risk'
  const cf = a.custom_fields = [];
  cf.push({code:'f_bool', target:'risk', type:'boolean', label:{fr:'Booléen'}});
  cf.push({code:'f_int', target:'risk', type:'integer', min:0, max:100, label:{fr:'Entier'}});
  cf.push({code:'f_float', target:'risk', type:'float', label:{fr:'Décimal'}});
  cf.push({code:'f_date', target:'risk', type:'date', label:{fr:'Date'}});
  cf.push({code:'f_text', target:'risk', type:'text', label:{fr:'Texte'}});
  cf.push({code:'f_textarea', target:'risk', type:'textarea', label:{fr:'Texte long'}});
  cf.push({code:'f_url', target:'risk', type:'url', label:{fr:'URL'}});
  cf.push({code:'f_email', target:'risk', type:'email', label:{fr:'Email'}});
  cf.push({code:'f_tel', target:'risk', type:'tel', label:{fr:'Téléphone'}});
  cf.push({code:'f_regexp', target:'risk', type:'regexp', pattern:'[A-Z]{2}-\\\\d{4}', label:{fr:'Motif'}});
  cf.push({code:'f_color', target:'risk', type:'color', color_mode:'both', label:{fr:'Couleur'}});
  cf.push({code:'f_image', target:'risk', type:'image', label:{fr:'Image'}});
  cf.push({code:'f_select', target:'risk', type:'select', items:[{code:'a',label:'A'},{code:'b',label:'B'}], label:{fr:'Liste'}});
  cf.push({code:'f_checklist', target:'risk', type:'checklist', items:[{code:'x',label:'X'},{code:'y',label:'Y'},{code:'z',label:'Z'}], label:{fr:'Cases'}});
  cf.push({code:'f_tags', target:'risk', type:'tags', items:[{code:'t1',label:'Tag 1',color:'#922b21'},{code:'t2',label:'Tag 2',color:'#1abc9c'}], label:{fr:'Étiquettes'}});
  cf.push({code:'f_scale', target:'risk', type:'scale', items:[{value:1,label:'Bas',color:'#2e9e5b'},{value:2,label:'Moyen',color:'#e0b93a'},{value:3,label:'Haut',color:'#d64545'}], label:{fr:'Échelle'}});
  cf.push({code:'f_progress', target:'risk', type:'progress', label:{fr:'Progression'}});
  cf.push({code:'f_ref', target:'risk', type:'reference', object_type:'srv', multiple:true, label:{fr:'Serveurs liés'}});
  cf.push({code:'f_calc', target:'risk', type:'computed', expr:'=cf.f_int*2', result_type:'integer', label:{fr:'Entier ×2'}});
  cf.push({code:'f_calc_ref', target:'risk', type:'computed', expr:'=SUM(cf.f_ref.cf.niveau)', result_type:'integer', label:{fr:'Somme niveaux serveurs'}});
  // un champ perso de cotation + un champ d'analyse
  cf.push({code:'f_just', target:'cotation', type:'textarea', label:{fr:'Justification'}});
  cf.push({code:'f_ana', target:'analysis', type:'text', label:{fr:'Champ analyse'}});
  // un risque portant une valeur pour chaque champ
  a.risks.push({id:'R1', label:'Risque « tous champs »', category:'Général',
    initial_assessment:{probability:4, severity:5, custom:{f_just:'Coté au plus haut.'}},
    residual_assessment:{probability:2, severity:3, custom:{f_just:'Après traitement.'}},
    custom:{
      f_bool:true, f_int:7, f_float:3.14, f_date:'2026-06-15', f_text:'Valeur texte',
      f_textarea:'Ligne 1\\nLigne 2 en **gras**', f_url:'https://example.org', f_email:'test@example.org',
      f_tel:'+33123456789', f_regexp:'AB-1234', f_color:'#3366cc', f_image:PNG,
      f_select:'a', f_checklist:['x','z'], f_tags:['t1','t2'], f_scale:3, f_progress:60,
      f_ref:['SRV1','SRV2']
    }});
  a.custom = {f_ana:'Valeur du champ analyse'};
  applyLoadedData(a, 'x', false); return JSON.stringify(analyse);
}
""",
}


def main():
    httpd, base = start_server()
    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            errors = []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" and "favicon" not in (m.text or "") else None)
            page.on("pageerror", lambda e: errors.append("PAGEERROR: " + str(e)))
            page.goto(app_url(base), wait_until="load")
            page.wait_for_function("typeof applyLoadedData==='function' && typeof emptyAnalysis==='function'")
            for name, js in BUILDERS.items():
                arg = PNG_1x1 if name == "tous-types-champs" else None
                text = page.evaluate(js, arg) if arg is not None else page.evaluate(js)
                path = OUT / (name + ".rae.json")
                path.write_text(text, encoding="utf-8")
                # revalidation : recharger la fixture écrite
                before = len(errors)
                page.evaluate("j => applyLoadedData(JSON.parse(j), 'reload', false)", text)
                fmt = page.evaluate("(analyse&&analyse.format)||''")
                nr = page.evaluate("(analyse.risks||[]).length")
                ok = (fmt == "risk-analysis-editor") and (len(errors) == before)
                results.append((name, ok, nr, len(text), errors[before:]))
            browser.close()
    finally:
        httpd.shutdown()

    print(f"{'fixture':22} {'ok':3} {'risks':6} {'octets':8} erreurs")
    allok = True
    for name, ok, nr, size, errs in results:
        allok = allok and ok
        print(f"{name:22} {'OUI' if ok else 'NON':3} {nr:<6} {size:<8} {errs if errs else ''}")
    print("\nRESULTAT :", "toutes valides" if allok else "ECHECS, voir ci-dessus")
    return 0 if allok else 1


if __name__ == "__main__":
    raise SystemExit(main())
