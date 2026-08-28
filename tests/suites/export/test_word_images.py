"""Champs perso image/couleur/calculé dans le Word (natif + 3 gabarits) + dimensionnement EMU.

Porté de travaux/test-rapport-images/gen.py : construit 4 gabarits en mémoire, une analyse avec
6 images (canvas) et 3 modes de couleur, rend, et vérifie médias / dessins / cellules teintées /
pastilles ■ / tailles EMU. Auto-contenu (aucune fixture externe).
"""
import io
import zipfile

import pytest

pytestmark = pytest.mark.export

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _p(txt, b=False, sz=None):
    rpr = ("<w:rPr>" + ("<w:b/>" if b else "") + (f'<w:sz w:val="{sz}"/>' if sz else "") + "</w:rPr>") if (b or sz) else ""
    return f'<w:p><w:r>{rpr}<w:t xml:space="preserve">{txt}</w:t></w:r></w:p>'


def _tc(txt):
    return f'<w:tc><w:tcPr><w:tcW w:w="1800" w:type="dxa"/></w:tcPr>{_p(txt)}</w:tc>'


def _tr(cells):
    return "<w:tr>" + "".join(_tc(c) for c in cells) + "</w:tr>"


def _docx(body_xml) -> str:
    import base64
    doc = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{W}"><w:body>{body_xml}<w:sectPr/></w:body></w:document>'
    ct = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
    rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    drels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>'
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", doc)
        z.writestr("word/_rels/document.xml.rels", drels)
    return base64.b64encode(buf.getvalue()).decode()


def _templates():
    para = _docx("".join([
        _p("Risques — boucle de paragraphes", b=True, sz=28),
        _p('{{#each risks sort="id"}}'),
        _p('{{ risk.id }} — {{ risk.label }} | calc={{ risk.cf.calc }}', b=True),
        _p('Couleur both : {{ risk.cf.col_both }} · swatch : {{ risk.cf.col_swatch }} · hex : {{ risk.cf.col_hex }}'),
        _p('Photo (défaut) : {{ risk.cf.photo }} · largeur 3 cm : {{ risk.cf.photo width="3" }}'),
        _p('{{/each}}'),
    ]))
    tbl_body = ('<w:tbl><w:tblPr><w:tblW w:w="9000" w:type="dxa"/><w:tblBorders>'
                + "".join(f'<w:{x} w:val="single" w:sz="4" w:color="CCCCCC"/>' for x in ["top", "left", "bottom", "right", "insideH", "insideV"])
                + "</w:tblBorders></w:tblPr>"
                + _tr(["Réf.", "Risque", "Calc", "Both", "Swatch", "Hex", "Photo"])
                + _tr(['{{#each risks sort="id"}}{{ risk.id }}', '{{ risk.label }}', '{{ risk.cf.calc }}', '{{ risk.cf.col_both }}', '{{ risk.cf.col_swatch }}', '{{ risk.cf.col_hex }}', '{{ risk.cf.photo }}{{/each}}'])
                + "</w:tbl>")
    tbl = _docx(_p("Risques — boucle de ligne de tableau", b=True, sz=28) + tbl_body)
    block = _docx(_p("Risques — bloc « table »", b=True, sz=28)
                  + _p('{{ table source="risks" columns="id,risk,cf:calc,cf:col_both,cf:col_swatch,cf:col_hex,cf:photo" }}'))
    sizes = _docx(_p("Image dimensionnée", b=True, sz=28)
                  + _p('{{#each risks limit="1"}}')
                  + _p('W4 : {{ risk.cf.sized width="4" }}')
                  + _p('H1 : {{ risk.cf.sized height="1" }}')
                  + _p('W4H1 : {{ risk.cf.sized width="4" height="1" }}')
                  + _p('{{/each}}'))
    return {"para": para, "tbl": tbl, "block": block, "sizes": sizes}


JS = r"""
async (args)=>{
  const b64ToU8=b64=>{const s=atob(b64),u=new Uint8Array(s.length);for(let i=0;i<s.length;i++)u[i]=s.charCodeAt(i);return u;};
  const u8ToB64=u=>{let s="";const CH=0x8000;for(let i=0;i<u.length;i+=CH)s+=String.fromCharCode.apply(null,u.subarray(i,i+CH));return btoa(s);};
  const mkPng=(w,h,c1,c2)=>{const cv=document.createElement("canvas");cv.width=w;cv.height=h;const x=cv.getContext("2d");
    const g=x.createLinearGradient(0,0,w,h);g.addColorStop(0,c1);g.addColorStop(1,c2);x.fillStyle=g;x.fillRect(0,0,w,h);
    x.fillStyle="#ffffff";x.font=Math.max(10,Math.round(Math.min(w,h)/5))+"px sans-serif";x.fillText(w+"x"+h,6,Math.round(h/2));return cv.toDataURL("image/png");};
  const mkJpg=(w,h,c1,c2)=>{const cv=document.createElement("canvas");cv.width=w;cv.height=h;const x=cv.getContext("2d");
    const g=x.createLinearGradient(0,0,w,h);g.addColorStop(0,c1);g.addColorStop(1,c2);x.fillStyle=g;x.fillRect(0,0,w,h);return cv.toDataURL("image/jpeg",0.85);};
  const svg="data:image/svg+xml;base64,"+btoa('<svg xmlns="http://www.w3.org/2000/svg" width="220" height="180"><rect width="220" height="180" fill="#2f7fe0"/><circle cx="110" cy="90" r="64" fill="#e0662f"/></svg>');
  const imgs=[
    {n:"PNG 64x64",   v:mkPng(64,64,"#e0662f","#f2b705")},
    {n:"PNG 1400x1000",v:mkPng(1400,1000,"#2f7fe0","#7bd389")},
    {n:"JPEG 520x360", v:mkJpg(520,360,"#8e44ad","#e0662f")},
    {n:"SVG 220x180",  v:svg},
    {n:"PNG 600x160",  v:mkPng(600,160,"#16a085","#f39c12")},
    {n:"PNG 160x600",  v:mkPng(160,600,"#c0392b","#2980b9")},
  ];
  analyse.custom_fields=[
    {code:'calc',target:'risk',type:'computed',label:{fr:'Score×2'},expression:'score_initial * 2',result_type:'integer'},
    {code:'col_both',target:'risk',type:'color',label:{fr:'Coul (both)'},color_mode:'both'},
    {code:'col_swatch',target:'risk',type:'color',label:{fr:'Coul (swatch)'},color_mode:'swatch'},
    {code:'col_hex',target:'risk',type:'color',label:{fr:'Coul (hex)'},color_mode:'hex'},
    {code:'photo',target:'risk',type:'image',label:{fr:'Photo'}},
    {code:'sized',target:'risk',type:'image',label:{fr:'Sized'}},
  ];
  const sized=mkPng(400,200,"#34495e","#95a5a6");
  const palette=["#e0662f","#2f7fe0","#8e44ad","#16a085","#c0392b","#f39c12"];
  analyse.risks=imgs.map((im,k)=>({id:'R'+(k+1),label:im.n,category:'C',
    initial_assessment:{probability:((k)%4)+1,severity:((k+1)%4)+1},
    residual_assessment:{probability:1,severity:1},
    custom:{photo:im.v,sized:sized,col_both:palette[k],col_swatch:palette[k],col_hex:palette[k],calc:0}}));
  analyse.measures=[];analyse.treatments=[];

  const results={};
  analyse.extensions={display:{report:{cover:{on:false},toc:{on:false},
    sections:[{id:"risks_table",on:true,columns:["id","risk","cf:calc","cf:col_both","cf:col_swatch","cf:col_hex","cf:photo"]}]}}};
  {
    const blob=await buildDocx();const u=new Uint8Array(await blob.arrayBuffer());
    const f=fflate.unzipSync(u);const doc=fflate.strFromU8(f["word/document.xml"]);
    results.natif={media:Object.keys(f).filter(n=>/word\/media\//.test(n)).length,
      drawings:(doc.match(/<w:drawing>/g)||[]).length, colorFills:(doc.match(/w:fill="[0-9A-Fa-f]{6}"/g)||[]).filter(x=>!/EEF2F8/i.test(x)).length};
  }
  const renderTpl=async (tplB64)=>{
    const parts=fflate.unzipSync(b64ToU8(tplB64));
    tmplWarnings.length=0;
    const blob=await tmplRender(parts);const u=new Uint8Array(await blob.arrayBuffer());
    const f=fflate.unzipSync(u);const doc=fflate.strFromU8(f["word/document.xml"]);
    return {media:Object.keys(f).filter(n=>/word\/media\//.test(n)).length,
      drawings:(doc.match(/<w:drawing>/g)||[]).length, swatches:(doc.match(/■/g)||[]).length,
      marker:doc.indexOf("[image]")>=0, colorFills:(doc.match(/w:fill="[0-9A-Fa-f]{6}"/g)||[]).filter(x=>!/EEF2F8/i.test(x)).length, warns:tmplWarnings.slice()};
  };
  results.para =await renderTpl(args.para);
  results.tbl  =await renderTpl(args.tbl);
  results.block=await renderTpl(args.block);
  {
    const parts=fflate.unzipSync(b64ToU8(args.sizes));
    tmplWarnings.length=0;
    const blob=await tmplRender(parts);const u=new Uint8Array(await blob.arrayBuffer());
    const doc=fflate.strFromU8(fflate.unzipSync(u)["word/document.xml"]);
    const exts=(doc.match(/<wp:extent cx="(\d+)" cy="(\d+)"\/>/g)||[]).map(s=>{const m=/cx="(\d+)" cy="(\d+)"/.exec(s);return {cx:+m[1],cy:+m[2]};});
    results.sizes={exts, warns:tmplWarnings.slice()};
  }
  results.risks=analyse.risks.length;
  return results;
}
"""


@pytest.fixture
def res(app):
    app.load("vide.rae.json")   # grille par défaut ; l'analyse est reconstruite dans le JS
    return app.js(JS, _templates())


def test_native_images_and_colors(res):
    n = res["risks"]
    assert res["natif"]["media"] >= n, "images non embarquées (natif)"
    assert res["natif"]["drawings"] >= n
    assert res["natif"]["colorFills"] == 2 * n, "couleur both+swatch teintées, hex non (=2×n)"


def test_paragraph_loop(res):
    n = res["risks"]
    assert res["para"]["media"] >= n
    assert res["para"]["drawings"] >= 2 * n, "défaut + width=3cm → 2 dessins/risque"
    assert res["para"]["swatches"] == 2 * n


def test_table_loop(res):
    n = res["risks"]
    assert res["tbl"]["media"] >= n
    assert res["tbl"]["drawings"] >= n
    assert res["tbl"]["swatches"] == 2 * n


def test_table_block(res):
    n = res["risks"]
    assert res["block"]["media"] >= n
    assert res["block"]["drawings"] >= n and not res["block"]["marker"]
    assert res["block"]["colorFills"] == 2 * n


def test_image_sizing_emu(res):
    exts = res["sizes"]["exts"]
    assert len(exts) >= 3, f"3 dessins attendus, {len(exts)}"
    assert exts[0] == {"cx": 1440000, "cy": 720000}, "width=4cm → 1440000×720000"
    assert exts[1] == {"cx": 720000, "cy": 360000}, "height=1cm → 720000×360000"
    assert exts[2] == {"cx": 720000, "cy": 360000}, "width=4+height=1 (boîte max) → 720000×360000"


# --- Attribut d'objet CALCULÉ : object.attr.<calc> doit être RECALCULÉ ------------
# Régression : le résolveur direct object.attr lisait autrefois la valeur stockée
# (vide pour un attribut calculé, jamais persisté) → colonne vide. Il doit recalculer,
# comme risk.cf.<calc>, object.attributes et {{ object_notes }}.
OBJ_CALC_JS = r"""
async (tplB64)=>{
  const b64ToU8=b64=>{const s=atob(b64),u=new Uint8Array(s.length);for(let i=0;i<s.length;i++)u[i]=s.charCodeAt(i);return u;};
  analyse.object_types=[{code:'srv',prefix:'SRV',name_attr:'nom',label:{fr:'Serveur'},attributes:[
    {code:'nom',type:'text',label:{fr:'Nom'}},
    {code:'niveau',type:'scale',label:{fr:'Niveau'},items:[{value:1,label:'Bas'},{value:2,label:'Moyen'},{value:3,label:'Haut'}]},
    {code:'calc',type:'computed',label:{fr:'Niveau ×10'},expression:'=cf.niveau*10',result_type:'integer'}]}];
  analyse.objects=[{id:'SRV1',type:'srv',values:{nom:'A',niveau:3}},{id:'SRV2',type:'srv',values:{nom:'B',niveau:1}}];
  analyse.risks=[];analyse.measures=[];analyse.treatments=[];
  const parts=fflate.unzipSync(b64ToU8(tplB64));
  tmplWarnings.length=0;
  const blob=await tmplRender(parts);
  const doc=fflate.strFromU8(fflate.unzipSync(new Uint8Array(await blob.arrayBuffer()))["word/document.xml"]);
  const text=(doc.match(/<w:t[^>]*>([^<]*)<\/w:t>/g)||[]).map(m=>m.replace(/<[^>]+>/g,'')).join('');
  return {text, braces:(doc.match(/\{\{/g)||[]).length, warns:tmplWarnings.slice()};
}
"""


def test_object_computed_attr_is_recomputed(app):
    """{{ object.attr.<calc> }} rend la valeur RECALCULÉE (jamais stockée) — objet SRV1
    niveau=3 → calc=30, SRV2 niveau=1 → calc=10 ; 0 balise résiduelle, 0 avertissement."""
    app.load("vide.rae.json")
    tpl = _docx(
        _p('{{#each objects type="srv" sort="id"}}')
        + _p('{{ object.id }}:calc={{ object.attr.calc }};')
        + _p('{{/each}}')
    )
    res = app.js(OBJ_CALC_JS, tpl)
    assert "SRV1:calc=30;" in res["text"], res["text"]
    assert "SRV2:calc=10;" in res["text"], res["text"]
    assert res["braces"] == 0, "balise non résolue"
    assert not res["warns"], res["warns"]
