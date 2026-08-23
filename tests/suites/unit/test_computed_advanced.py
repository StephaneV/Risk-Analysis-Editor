"""Champs calculés — cas avancés (portés fidèlement de travaux/test-champs-calcules).

Couvre : J (liaison à l'entité / dérivées / cycles / cotation / attribut objet), E (agrégats de
collection), LF (restitution/filtre/radar/stats sur calculés & échelles), MV (multivalué), RH
(traversée de référence un saut), IMP (import CSV : calculés exclus, échelle, round-trip objet),
CI (types couleur & image). Le JS validé est rejoué tel quel ; l'analyse ebios fournit la grille.
"""
import pytest

pytestmark = pytest.mark.unit

JS = r"""
() => {
  const results=[];
  const J=(id,name,fn)=>{let p=false,d='';try{const r=fn();p=r.pass!==false;d=r.detail||'';}catch(e){d='EXCEPTION '+((e&&e.message)||e);}results.push({id,name,pass:p,detail:d});};

  // ---- J — liaison à l'entité (cfComputedValue) ----
  const setupCalc=()=>{
    analyse.custom_fields=[
      {code:'impact',target:'risk',type:'scale',label:{fr:'Impact'},items:[{value:1,label:{fr:'F'}},{value:3,label:{fr:'Fort'}}]},
      {code:'sc2',target:'risk',type:'computed',label:{fr:'x2'},expression:'score_initial * 2',result_type:'integer'},
      {code:'som',target:'risk',type:'computed',label:{fr:'som'},expression:'cf.impact + score_residual',result_type:'number',decimals:1,unit:'pts'},
      {code:'lvl',target:'risk',type:'computed',label:{fr:'lvl'},expression:'IF(cf.impact>=3,"ELEVE","ok")',result_type:'text'},
      {code:'chain',target:'risk',type:'computed',label:{fr:'chain'},expression:'cf.sc2 + 1',result_type:'integer'},
      {code:'al',target:'risk',type:'computed',label:{fr:'al'},expression:'score_initial - 20',result_type:'integer',alert:{min:0,color:'#c0505a'}},
      {code:'err',target:'risk',type:'computed',label:{fr:'err'},expression:'cf.nope + 1'},
      {code:'c1',target:'risk',type:'computed',label:{fr:'c1'},expression:'cf.c2'},
      {code:'c2',target:'risk',type:'computed',label:{fr:'c2'},expression:'cf.c1'},
      {code:'jours',target:'measure',type:'computed',label:{fr:'j'},expression:'due_date - TODAY()',result_type:'integer'},
      {code:'ov',target:'measure',type:'computed',label:{fr:'ov'},expression:'IF(overdue,"RETARD","ok")',result_type:'text'}
    ];
    analyse.risks=[{id:'R1',label:'A',initial_assessment:{probability:4,severity:3},residual_assessment:{probability:2,severity:2},custom:{impact:3}}];
    analyse.measures=[{id:'M1',label:'M',status:'planned',due_date:'2099-01-01'}];
    return {r:analyse.risks[0],m:analyse.measures[0]};
  };
  const cf=code=>analyse.custom_fields.find(f=>f.code===code);
  J('J1','Dérivée risque score_initial*2',()=>{const{r}=setupCalc();const v=cfComputedValue(cf('sc2'),'risk',r);return{pass:v.ok&&v.value===24,detail:JSON.stringify(v)};});
  J('J2','cf.<code> (échelle) + score_residual, decimals',()=>{const{r}=setupCalc();const v=cfComputedValue(cf('som'),'risk',r);return{pass:v.ok&&v.value===7,detail:'='+v.value+' fmt='+cfComputedText(cf('som'),v)};});
  J('J3','IF sur cf : texte',()=>{const{r}=setupCalc();const v=cfComputedValue(cf('lvl'),'risk',r);return{pass:v.ok&&v.value==='ELEVE',detail:JSON.stringify(v)};});
  J('J4','computed → computed',()=>{const{r}=setupCalc();const v=cfComputedValue(cf('chain'),'risk',r);return{pass:v.ok&&v.value===25,detail:JSON.stringify(v)};});
  J('J5','champ inconnu → erreur #ERR',()=>{const{r}=setupCalc();const v=cfComputedValue(cf('err'),'risk',r);const h=cfComputedDisplayHTML(cf('err'),'risk',r);return{pass:!v.ok&&/#ERR/.test(h),detail:v.error};});
  J('J6','référence circulaire détectée',()=>{const{r}=setupCalc();const v=cfComputedValue(cf('c1'),'risk',r);return{pass:!v.ok&&/circ/i.test(v.error),detail:v.error};});
  J('J7','alerte : valeur hors plage colorée',()=>{const{r}=setupCalc();const h=cfComputedDisplayHTML(cf('al'),'risk',r);return{pass:/color:#c0505a/.test(h)&&/-8/.test(h),detail:h};});
  J('J8','mesure : due_date - TODAY() (entier)',()=>{const{m}=setupCalc();const v=cfComputedValue(cf('jours'),'measure',m);return{pass:v.ok&&v.type==='num'&&v.value>1000,detail:'='+v.value};});
  J('J9','mesure : overdue (dérivée booléenne)',()=>{const{m}=setupCalc();const v=cfComputedValue(cf('ov'),'measure',m);return{pass:v.ok&&v.value==='ok',detail:JSON.stringify(v)};});
  J('J10','champ de base : label du risque (texte)',()=>{const{r}=setupCalc();const f={code:'lb',target:'risk',type:'computed',expression:'label',result_type:'text'};const v=cfComputedValue(f,'risk',r);return{pass:v.ok&&v.value==='A',detail:JSON.stringify(v)};});
  J('J11','champ de base : catégorie absente → nil',()=>{const{r}=setupCalc();const f={code:'ct',target:'risk',type:'computed',expression:'category',result_type:'text'};const v=cfComputedValue(f,'risk',r);return{pass:v.ok&&v.type==='nil',detail:JSON.stringify(v)};});
  J('J12','cotation : score = P×G (dérivée)',()=>{const f={code:'sc',target:'cotation',type:'computed',expression:'score',result_type:'integer'};const v=cfComputedValue(f,'cotation',{probability:4,severity:3});return{pass:v.ok&&v.value===12,detail:JSON.stringify(v)};});
  J('J13','cotation : criticité (texte) via seuils',()=>{const f={code:'cr',target:'cotation',type:'computed',expression:'criticality',result_type:'text'};const v=cfComputedValue(f,'cotation',{probability:5,severity:5});return{pass:v.ok&&v.type==='text'&&v.value.length>0,detail:JSON.stringify(v)};});
  J('J14','attribut objet : cf.<code> entre attributs de l instance',()=>{
    const ot={code:'vm',attributes:[{code:'d',type:'scale',items:[{value:1},{value:4}]},{code:'i',type:'scale',items:[{value:1},{value:4}]},{code:'m',type:'computed',expression:'MAX(cf.d, cf.i)',result_type:'integer'}]};
    const inst={type:'vm',values:{d:4,i:1}};const v=cfComputedValue(ot.attributes[2],ot,inst);return{pass:v.ok&&v.value===4,detail:JSON.stringify(v)};});

  // ---- E — agrégats de collection (cible analyse) ----
  const setupAgg=()=>{
    analyse.custom_fields=[{code:'grav',target:'risk',type:'scale',label:{fr:'g'},items:[{value:1},{value:2},{value:4}]}];
    analyse.risks=[
      {id:'R1',label:'a',initial_assessment:{probability:2,severity:2},custom:{grav:4}},
      {id:'R2',label:'b',initial_assessment:{probability:1,severity:1},custom:{grav:2}},
      {id:'R3',label:'c',initial_assessment:{probability:3,severity:3},custom:{grav:2}},
      {id:'R4',label:'d',initial_assessment:{probability:1,severity:1}}];
    analyse.measures=[{id:'M1',cost:'100'},{id:'M2',cost:'300'}];
    analyse.treatments=[{risk:'R1',measure:'M1'}];
  };
  const evA=(expr,rt)=>{setupAgg();return cfComputedValue({code:'x',target:'analysis',type:'computed',expression:expr,result_type:rt||'number'},'analysis',analyse);};
  J('E1','COUNT(risks) = effectif',()=>{const v=evA('COUNT(risks)','integer');return{pass:v.ok&&v.value===4,detail:JSON.stringify(v)};});
  J('E2','risks_count (effectif direct)',()=>{const v=evA('risks_count','integer');return{pass:v.ok&&v.value===4,detail:JSON.stringify(v)};});
  J('E3','MEDIAN(risks.cf.grav) ignore les absents',()=>{const v=evA('MEDIAN(risks.cf.grav)');return{pass:v.ok&&v.value===2,detail:JSON.stringify(v)};});
  J('E4','AVERAGE(risks.cf.grav) = 8/3',()=>{const v=evA('AVERAGE(risks.cf.grav)');return{pass:v.ok&&Math.abs(v.value-2.6666667)<1e-4,detail:JSON.stringify(v)};});
  J('E5','SUM(measures.cost)',()=>{const v=evA('SUM(measures.cost)');return{pass:v.ok&&v.value===400,detail:JSON.stringify(v)};});
  J('E6','AVERAGE(risks.score_initial) sur dérivée',()=>{const v=evA('AVERAGE(risks.score_initial)');return{pass:v.ok&&Math.abs(v.value-3.75)<1e-6,detail:JSON.stringify(v)};});
  J('E7','COUNT(measures) via collection',()=>{const v=evA('COUNT(measures)','integer');return{pass:v.ok&&v.value===2,detail:JSON.stringify(v)};});

  // ---- LF — restitution / filtre / radar / stats sur calculés & échelles ----
  const setupF=()=>{
    analyse.custom_fields=[
      {code:'impact',target:'risk',type:'scale',label:{fr:'Impact'},filterable:true,items:[{value:1},{value:2},{value:3},{value:4}]},
      {code:'ratio',target:'risk',type:'computed',label:{fr:'Ratio'},filterable:true,expression:'cf.impact * 5',result_type:'number',decimals:1,unit:'pts',alert:{max:12,color:'#c0505a'}},
      {code:'fort',target:'risk',type:'computed',label:{fr:'Fort'},filterable:true,expression:'cf.impact >= 3',result_type:'boolean'},
      {code:'cont',target:'risk',type:'computed',label:{fr:'Cont'},filterable:true,expression:'cf.impact + 0.5',result_type:'number'}
    ];
    const mk=(id,imp)=>({id:id,label:id,category:'C',initial_assessment:{probability:2,severity:2},residual_assessment:{probability:1,severity:1},custom:{impact:imp}});
    analyse.risks=[mk('R1',1),mk('R2',3),mk('R3',4),mk('R4',null)];
    analyse.measures=[];analyse.treatments=[];
    return {r1:analyse.risks[0],r2:analyse.risks[1]};
  };
  const cfF=code=>analyse.custom_fields.find(f=>f.code===code);
  J('LF1','cfNumericValue : échelle & calculé numérique',()=>{const{r2}=setupF();const a=cfNumericValue(cfF('impact'),r2,'risk'),b=cfNumericValue(cfF('ratio'),r2,'risk');return{pass:a===3&&b===15,detail:'impact='+a+' ratio='+b};});
  J('LF2','cfComputedFilterKind : alert / bool / continu(null)',()=>{setupF();const k1=cfComputedFilterKind(cfF('ratio')),k2=cfComputedFilterKind(cfF('fort')),k3=cfComputedFilterKind(cfF('cont'));return{pass:k1==='alert'&&k2==='bool'&&k3===null,detail:k1+','+k2+','+String(k3)};});
  J('LF3','cfFilterableFields : calculé alert/bool inclus, continu exclu',()=>{setupF();const codes=cfFilterableFields('risk').map(f=>f.code);return{pass:codes.indexOf('ratio')>=0&&codes.indexOf('fort')>=0&&codes.indexOf('cont')<0,detail:codes.join(',')};});
  J('LF4','cfEntityMatches : alerte on/off + booléen',()=>{const{r1,r2}=setupF();
    cfFilters={ratio:'alert'};const a1=cfEntityMatches(r2,'risk'),a2=cfEntityMatches(r1,'risk');
    cfFilters={fort:'true'};const b1=cfEntityMatches(r2,'risk'),b2=cfEntityMatches(r1,'risk');
    cfFilters={};
    return{pass:a1&&!a2&&b1&&!b2,detail:'alerte R2='+a1+' R1='+a2+' | fort R2='+b1+' R1='+b2};});
  J('LF5','radar : métrique champ numérique (moyenne / max / somme)',()=>{setupF();const codes=radarMetricFields().map(f=>f.code);const fm=radarFieldMetric('cf:impact:max');const av=radarFieldValues(analyse.risks,'cat',['C'],{code:'impact',agg:'avg'})[0];const mx=radarFieldValues(analyse.risks,'cat',['C'],{code:'impact',agg:'max'})[0];const sm=radarFieldValues(analyse.risks,'cat',['C'],{code:'impact',agg:'sum'})[0];return{pass:codes.indexOf('impact')>=0&&codes.indexOf('fort')<0&&!!fm&&fm.agg==='max'&&Math.abs(av-2.6666667)<1e-4&&mx===4&&sm===8,detail:'champs='+codes.join(',')+' moy='+av+' max='+mx+' somme='+sm};});
  J('LF6','stats : agrégat numérique (n / moyenne / somme / min / max)',()=>{setupF();const f=cfF('ratio');const blk=normStatBlock({id:statNumId('risk','ratio'),type:'num_agg',target:'risk',field:'ratio'});const html=statBlockBody(blk);const ok=statNumField(f)&&/13\.3 pts/.test(html)&&/40\.0 pts/.test(html)&&/5\.0 pts/.test(html)&&/20\.0 pts/.test(html)&&/>3</.test(html);return{pass:ok,detail:html.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim()};});
  J('LF7','restitution : attribut objet calculé (texte & HTML)',()=>{
    const ot={code:'vm',label:{fr:'VM'},attributes:[{code:'d',type:'scale',items:[{value:1},{value:4}]},{code:'m',type:'computed',label:{fr:'m'},expression:'cf.d * 3',result_type:'integer',unit:'u'}]};
    analyse.object_types=[ot];analyse.objects=[{id:'O1',type:'vm',values:{d:4}}];
    const inst=analyse.objects[0],a=ot.attributes[1];const txt=cfObjAttrText(a,ot,inst),html=cfObjAttrHTML(a,ot,inst);
    return{pass:txt==='12 u'&&/12 u/.test(html),detail:'txt='+txt+' html='+html};});

  // ---- MV — champs multivalués (tags / checklist / reference) ----
  const setupMV=()=>{
    analyse.custom_fields=[
      {code:'dom',target:'risk',type:'tags',label:{fr:'Domaines'},items:[{code:'rh'},{code:'it'},{code:'jur'}]},
      {code:'ctrl',target:'risk',type:'checklist',label:{fr:'Ctrls'},items:[{code:'a'},{code:'b'}]},
      {code:'refs',target:'risk',type:'reference',object_type:'x',label:{fr:'Refs'}},
      {code:'nb',target:'risk',type:'computed',label:{fr:'nb'},expression:'COUNT(cf.dom)',result_type:'integer'},
      {code:'nbc',target:'risk',type:'computed',label:{fr:'nbc'},expression:'COUNT(cf.ctrl)',result_type:'integer'},
      {code:'txt',target:'risk',type:'computed',label:{fr:'txt'},expression:'CONCAT(cf.dom)',result_type:'text'},
      {code:'amp',target:'risk',type:'computed',label:{fr:'amp'},expression:'cf.dom & " (" & COUNT(cf.dom) & ")"',result_type:'text'}
    ];
    analyse.risks=[
      {id:'R1',label:'a',initial_assessment:{probability:1,severity:1},custom:{dom:['rh','it','jur'],ctrl:['a'],refs:['O1','O2']}},
      {id:'R2',label:'b',initial_assessment:{probability:1,severity:1},custom:{dom:[]}},
      {id:'R3',label:'c',initial_assessment:{probability:1,severity:1},custom:{}}];
    return {r1:analyse.risks[0],r2:analyse.risks[1],r3:analyse.risks[2]};
  };
  const cfM=code=>analyse.custom_fields.find(f=>f.code===code);
  J('MV1','cf.<tags> résout en LISTE (pas une chaîne)',()=>{const{r1}=setupMV();const v=calcResolveField('cf.dom','risk',r1,[]);return{pass:Array.isArray(v)&&v.length===3,detail:JSON.stringify(v)};});
  J('MV2','COUNT(cf.dom) = nombre de valeurs (tags multivalué)',()=>{const{r1}=setupMV();const v=cfComputedValue(cfM('nb'),'risk',r1);return{pass:v.ok&&v.value===3,detail:JSON.stringify(v)};});
  J('MV3','COUNT sur multivalué VIDE = 0',()=>{const{r2}=setupMV();const v=cfComputedValue(cfM('nb'),'risk',r2);return{pass:v.ok&&v.value===0,detail:JSON.stringify(v)};});
  J('MV4','COUNT sur multivalué ABSENT = 0',()=>{const{r3}=setupMV();const v=cfComputedValue(cfM('nb'),'risk',r3);return{pass:v.ok&&v.value===0,detail:JSON.stringify(v)};});
  J('MV5','COUNT(cf.ctrl) = nombre de cases cochées (checklist)',()=>{const{r1}=setupMV();const v=cfComputedValue(cfM('nbc'),'risk',r1);return{pass:v.ok&&v.value===1,detail:JSON.stringify(v)};});
  J('MV6','COUNT(cf.refs) = nombre de références (reference multi)',()=>{const{r1}=setupMV();const f={code:'nr',target:'risk',type:'computed',expression:'COUNT(cf.refs)',result_type:'integer'};const v=cfComputedValue(f,'risk',r1);return{pass:v.ok&&v.value===2,detail:JSON.stringify(v)};});
  J('MV7','texte préservé : CONCAT(cf.dom) = valeurs jointes',()=>{const{r1}=setupMV();const v=cfComputedValue(cfM('txt'),'risk',r1);return{pass:v.ok&&v.value==='rh, it, jur',detail:JSON.stringify(v)};});
  J('MV8','multivalué en & avec décompte',()=>{const{r1}=setupMV();const v=cfComputedValue(cfM('amp'),'risk',r1);return{pass:v.ok&&v.value==='rh, it, jur (3)',detail:JSON.stringify(v)};});
  J('MV9','texte d un multivalué VIDE = chaîne vide',()=>{const{r2}=setupMV();const v=cfComputedValue(cfM('txt'),'risk',r2);return{pass:v.ok&&(v.value===''||v.type==='nil'),detail:JSON.stringify(v)};});

  // ---- RH — traversée de référence (un saut) ----
  const setupRH=()=>{
    analyse.object_types=[{code:'vm',label:{fr:'VM'},attributes:[
      {code:'niv',type:'scale',label:{fr:'Niveau'},items:[{value:1},{value:2},{value:4}]},
      {code:'dbl',type:'computed',label:{fr:'Double'},expression:'cf.niv * 2',result_type:'integer'}]}];
    analyse.objects=[{id:'O1',type:'vm',values:{niv:4}},{id:'O2',type:'vm',values:{niv:2}},{id:'O3',type:'vm',values:{}}];
    analyse.custom_fields=[
      {code:'vmref',target:'risk',type:'reference',object_type:'vm',label:{fr:'VM liées'}},
      {code:'vmmono',target:'risk',type:'reference',object_type:'vm',label:{fr:'VM'}}];
    analyse.risks=[
      {id:'R1',label:'a',initial_assessment:{probability:1,severity:1},custom:{vmref:['O1','O2','O3'],vmmono:'O1'}},
      {id:'R2',label:'b',initial_assessment:{probability:1,severity:1},custom:{vmref:[]}}];
    return {r1:analyse.risks[0],r2:analyse.risks[1]};
  };
  const rhCf=(expr,rt)=>({code:'x',target:'risk',type:'computed',expression:expr,result_type:rt||'number'});
  const rhEval=(expr,r,rt)=>cfComputedValue(rhCf(expr,rt),'risk',r);
  J('RH1','COUNT(cf.ref) = nombre d objets référencés',()=>{const{r1}=setupRH();const v=rhEval('COUNT(cf.vmref)',r1,'integer');return{pass:v.ok&&v.value===3,detail:JSON.stringify(v)};});
  J('RH2','SUM(cf.ref.cf.attr) = somme des attributs (absents ignorés)',()=>{const{r1}=setupRH();const v=rhEval('SUM(cf.vmref.cf.niv)',r1);return{pass:v.ok&&v.value===6,detail:JSON.stringify(v)};});
  J('RH3','AVERAGE(cf.ref.cf.attr) = moyenne des renseignés',()=>{const{r1}=setupRH();const v=rhEval('AVERAGE(cf.vmref.cf.niv)',r1);return{pass:v.ok&&v.value===3,detail:JSON.stringify(v)};});
  J('RH4','MAX(cf.ref.cf.attr)',()=>{const{r1}=setupRH();const v=rhEval('MAX(cf.vmref.cf.niv)',r1);return{pass:v.ok&&v.value===4,detail:JSON.stringify(v)};});
  J('RH5','COUNT(cf.ref.cf.attr) = nombre de valeurs renseignées',()=>{const{r1}=setupRH();const v=rhEval('COUNT(cf.vmref.cf.niv)',r1,'integer');return{pass:v.ok&&v.value===2,detail:JSON.stringify(v)};});
  J('RH6','traversée vers un attribut CALCULÉ de l objet',()=>{const{r1}=setupRH();const v=rhEval('SUM(cf.vmref.cf.dbl)',r1);return{pass:v.ok&&v.value===12,detail:JSON.stringify(v)};});
  J('RH7','référence MONO (une seule instance)',()=>{const{r1}=setupRH();const v=rhEval('SUM(cf.vmmono.cf.niv)',r1);return{pass:v.ok&&v.value===4,detail:JSON.stringify(v)};});
  J('RH8','référence VIDE → agrégat absent / COUNT 0',()=>{const{r2}=setupRH();const a=rhEval('AVERAGE(cf.vmref.cf.niv)',r2);const c=rhEval('COUNT(cf.vmref.cf.niv)',r2,'integer');return{pass:a.ok&&a.type==='nil'&&c.ok&&c.value===0,detail:'avg='+JSON.stringify(a)+' count='+JSON.stringify(c)};});
  J('RH9','picker : groupe « Objets liés »',()=>{setupRH();const gs=calcLinkedGroupsFrom(customFieldsFor('risk').filter(f=>f.type==='reference'));const g=gs.find(x=>x.ref.k==='cf.vmref');const ks=g?g.attrs.map(a=>a.k):[];return{pass:!!g&&ks.indexOf('cf.vmref.cf.niv')>=0&&ks.indexOf('cf.vmref.cf.dbl')>=0,detail:JSON.stringify({ref:g&&g.ref.k,attrs:ks})};});

  // ---- IMP — import CSV ----
  J('IMP1','cfParseValue ignore un champ calculé',()=>{const v=cfParseValue({type:'computed',expression:'1'},'42');return{pass:v===undefined,detail:'='+JSON.stringify(v)};});
  J('IMP2','cfParseValue échelle : libellé et valeur',()=>{const f={type:'scale',items:[{value:1,label:{fr:'Faible'}},{value:3,label:{fr:'Fort'}}]};return{pass:cfParseValue(f,'Fort')===3&&cfParseValue(f,'1')===1,detail:'Fort='+cfParseValue(f,'Fort')+' 1='+cfParseValue(f,'1')};});
  J('IMP3','objets : export → import round-trip',()=>{
    analyse.object_types=[{code:'vm',label:{fr:'VM'},attributes:[{code:'d',type:'scale',items:[{value:1,label:{fr:'Faible'}},{value:4,label:{fr:'Critique'}}]},{code:'s',type:'computed',expression:'cf.d+1',result_type:'integer'}]}];
    analyse.objects=[{id:'O1',type:'vm',values:{d:4}}];
    let cap=null;const dl=window.downloadCSV;window.downloadCSV=(rows)=>{cap={rows};};exportObjectTypeCSV('vm');window.downloadCSV=dl;
    const txt=cap.rows.map(r=>r.map(String).join(',')).join('\n').replace('O1,Critique','O1,Faible');
    const an=analyzeObjectsCSV('vm',txt);commitObjectImport('vm',an.items);
    const v=objectById('O1').values;
    return{pass:v.d===1&&v.s===undefined,detail:JSON.stringify(v)+' hdr='+JSON.stringify(cap.rows[0])};});

  // ---- CI — types couleur & image ----
  J('CI1','types couleur/image enregistrés + triabilité',()=>{const ok=CF_TYPES.indexOf('color')>=0&&CF_TYPES.indexOf('image')>=0&&cfColSortable({type:'color'})&&!cfColSortable({type:'image'});return{pass:ok,detail:'sortable color='+cfColSortable({type:'color'})+' image='+cfColSortable({type:'image'})};});
  J('CI2','couleur : parse CSV (hex avec/sans #, invalide)',()=>{const f={type:'color'};const a=cfParseValue(f,'#AABBCC'),b=cfParseValue(f,'aabbcc'),c=cfParseValue(f,'rouge');return{pass:a==='#aabbcc'&&b==='#aabbcc'&&c===undefined,detail:a+','+b+','+String(c)};});
  J('CI3','image : parse ignoré + marqueur en texte',()=>{const f={type:'image'};const p=cfParseValue(f,'data:image/png;base64,AA');const d=cfDisplay(f,'data:image/png;base64,AA');return{pass:p===undefined&&d==='[image]',detail:'parse='+String(p)+' disp='+d};});
  J('CI4','affichage HTML : pastille couleur & vignette image',()=>{const hc=cfDisplayHTML({type:'color'},'#1a2b3c',true);const hi=cfDisplayHTML({type:'image'},'data:image/png;base64,AA',true);return{pass:/cf-swatch/.test(hc)&&/#1a2b3c/.test(hc)&&/cf-img-thumb/.test(hi)&&/<img/.test(hi),detail:'color='+/cf-swatch/.test(hc)+' image='+/cf-img-thumb/.test(hi)};});

  return results;
}
"""


def test_computed_advanced_suite(app):
    app.load("ebios.rae.json")   # fournit une grille valide (score/criticité)
    results = app.js(JS)
    failed = [r for r in results if not r["pass"]]
    assert not failed, "Cas avancés en échec :\n" + "\n".join(
        f"  {r['id']}  {r['name']}  -> {r['detail']}" for r in failed)
    assert len(results) >= 49, f"trop peu de cas exécutés : {len(results)}"
