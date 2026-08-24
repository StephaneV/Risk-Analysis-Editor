"""Moteur d'expression des champs calculés — couverture complète (lexer → dates → erreurs).

Généralise travaux/test-champs-calcules (partie « pure expression », lots A–I). L'`env` est construit
EN LIGNE (get sur un dictionnaire de variables ; today optionnel) — indépendant de `calcEnv`
(code mort voué au Lot 0). Le jeu de cas et l'oracle sont embarqués (auto-contenu).
"""
import pytest

pytestmark = pytest.mark.unit

# Bloc JS : jeu de cas + oracle ; renvoie [{id,pass,detail,expr}]
JS_SUITE = r"""
() => {
  const near=(a,b)=>typeof a==='number'&&Math.abs(a-b)<1e-9;
  const D=s=>({date:s});
  const run=(expr,vars,today)=>{
    vars=vars||{};
    const env={ get:n=>Object.prototype.hasOwnProperty.call(vars,n)?vars[n]:null,
                today:()=>{ if(!today) throw new Error('TODAY indisponible'); return today; } };
    return calcEvaluate(expr, env);
  };
  const C=[
    // A — lexer & littéraux
    {id:'A1',expr:'42',exp:42,type:'num'},
    {id:'A2',expr:'3.5',exp:3.5},
    {id:'A3',expr:'.5',exp:0.5},
    {id:'A4',expr:'"bonjour"',exp:'bonjour',type:'text'},
    {id:'A6',expr:'TRUE',exp:true,type:'bool'},
    {id:'A7',expr:'=1+1',exp:2},
    {id:'A8',expr:'  2   *   3  ',exp:6},
    // B — opérateurs & précédence
    {id:'B1',expr:'2+3*4',exp:14},
    {id:'B2',expr:'(2+3)*4',exp:20},
    {id:'B3',expr:'2^3^2',exp:512},
    {id:'B4',expr:'-2^2',exp:4},
    {id:'B5',expr:'10/4',exp:2.5},
    {id:'B6',expr:'10-4-3',exp:3},
    {id:'B7',expr:'2*3+4',exp:10},
    {id:'B8',expr:'"x=" & (1+1)',exp:'x=2'},
    {id:'B9',expr:'MOD(7,3)',exp:1},
    {id:'B10',expr:'POWER(2,10)',exp:1024},
    // C — comparaisons & logique
    {id:'C1',expr:'3>2',exp:true,type:'bool'},
    {id:'C2',expr:'3<>2',exp:true},
    {id:'C3',expr:'2=2',exp:true},
    {id:'C4',expr:'"a" < "b"',exp:true},
    {id:'C5',expr:'TRUE AND FALSE',exp:false},
    {id:'C6',expr:'NOT(1>2)',exp:true},
    {id:'C7',expr:'(1>0) OR (2>3)',exp:true},
    {id:'C8',expr:'NOT FALSE AND TRUE',exp:true},
    // D — numériques / agrégation
    {id:'D1',expr:'SUM(1,2,3,4)',exp:10},
    {id:'D2',expr:'AVERAGE(2,4)',exp:3},
    {id:'D3',expr:'MEDIAN(1,2,3,4)',exp:2.5},
    {id:'D5',expr:'MIN(3,-1,7)',exp:-1},
    {id:'D6',expr:'MAX(3,-1,7)',exp:7},
    {id:'D7',expr:'ROUND(3.14159,2)',exp:3.14},
    {id:'D8',expr:'ROUNDUP(1.01,0)',exp:2},
    {id:'D9',expr:'ROUNDDOWN(1.99,0)',exp:1},
    {id:'D10',expr:'INT(2.7)',exp:2},
    {id:'D11',expr:'INT(-2.1)',exp:-3},
    {id:'D12',expr:'ABS(-5)',exp:5},
    {id:'D13',expr:'SQRT(9)',exp:3},
    {id:'D14',expr:'COUNT(cf.a,cf.b,cf.c)',vars:{'cf.a':1,'cf.c':3},exp:2},
    {id:'D15',expr:'AVERAGE(cf.a,cf.b,cf.c)',vars:{'cf.a':2,'cf.c':4},exp:3},
    {id:'D16',expr:'AVERAGE(cf.x,cf.y)',vars:{},nil:true},
    // E — IF
    {id:'E1',expr:'IF(1>0,"oui","non")',exp:'oui'},
    {id:'E2',expr:'IF(0,"a","b")',exp:'b'},
    {id:'E3',expr:'IF(TRUE,1,1/0)',exp:1},
    {id:'E4',expr:'IF(cf.j<0,"Retard",IF(cf.j<=7,"Bientôt","OK"))',vars:{'cf.j':3},exp:'Bientôt'},
    // F — dates
    {id:'F1',expr:'DATE(2026,1,15)',exp:'2026-01-15',type:'date'},
    {id:'F2',expr:'cf.due - TODAY()',vars:{'cf.due':D('2026-08-30')},today:'2026-08-20',exp:10},
    {id:'F3',expr:'TODAY() + 30',today:'2026-08-20',exp:'2026-09-19',type:'date'},
    {id:'F4',expr:'YEAR(cf.d)',vars:{'cf.d':D('2026-08-20')},exp:2026},
    {id:'F5',expr:'MONTH(cf.d)',vars:{'cf.d':D('2026-08-20')},exp:8},
    {id:'F6',expr:'DAY(cf.d)',vars:{'cf.d':D('2026-08-20')},exp:20},
    {id:'F7',expr:'EDATE(cf.d,1)',vars:{'cf.d':D('2026-01-31')},exp:'2026-02-28',type:'date'},
    {id:'F8',expr:'EDATE(cf.d,-2)',vars:{'cf.d':D('2026-03-15')},exp:'2026-01-15',type:'date'},
    {id:'F9',expr:'DATEDIF(cf.a,cf.b,"D")',vars:{'cf.a':D('2026-01-01'),'cf.b':D('2026-01-11')},exp:10},
    {id:'F10',expr:'DATEDIF(cf.a,cf.b,"M")',vars:{'cf.a':D('2026-01-15'),'cf.b':D('2026-03-10')},exp:1},
    // G — références & absents
    {id:'G1',expr:'cf.gravite * 2',vars:{'cf.gravite':3},exp:6},
    {id:'G2',expr:'cf.x + 1',vars:{},nil:true},
    {id:'G3',expr:'IF(cf.x=cf.x,"nil","x")',vars:{},exp:'nil'},
    {id:'G4',expr:'(cf.expo*2 + cf.impact)/3',vars:{'cf.expo':4,'cf.impact':2},exp:3.3333333333},
    // H — texte
    {id:'H1',expr:'CONCAT("a","b","c")',exp:'abc'},
    {id:'H2',expr:'LEN("abcde")',exp:5},
    {id:'H3',expr:'1 & 2 & 3',exp:'123'},
    // I — erreurs (non bloquantes)
    {id:'I1',expr:'1 +',err:true},
    {id:'I2',expr:'SUM(1,2',err:true},
    {id:'I4',expr:'1/0',err:true},
    {id:'I5',expr:'FOO(1)',err:true},
    {id:'I6',expr:'ROUND(1)',err:true},
    {id:'I8',expr:'TODAY()',err:true},
    {id:'I9',expr:'"abc" + 1',err:true},
    {id:'I10',expr:'1.2.3',err:true},   // nombre à deux points -> rejeté (robustesse 3.1)
  ];
  return C.map(c=>{
    let ok=false, detail='';
    try{
      const r=run(c.expr,c.vars,c.today);
      if(c.err){ ok=!r.ok; detail=r.ok?('attendu ERREUR, obtenu '+JSON.stringify(r.value)):('err OK'); }
      else if(!r.ok){ ok=false; detail='ERREUR inattendue: '+r.error; }
      else if(c.nil){ ok=(r.value===null&&r.type==='nil'); detail='='+JSON.stringify(r.value)+' ('+r.type+')'; }
      else {
        const v=r.value;
        if(typeof c.exp==='number') ok=near(v,c.exp);
        else if(typeof c.exp==='boolean') ok=(v===c.exp);
        else ok=(String(v)===String(c.exp));
        if(c.type && r.type!==c.type) ok=false;
        detail='='+JSON.stringify(v)+' ('+r.type+')';
      }
    }catch(e){ ok=false; detail='EXCEPTION '+((e&&e.message)||e); }
    return {id:c.id, expr:c.expr, pass:ok, detail};
  });
}
"""


def test_expression_engine(app):
    results = app.js(JS_SUITE)
    failed = [r for r in results if not r["pass"]]
    assert not failed, "Cas en échec :\n" + "\n".join(
        f"  {r['id']}  {r['expr']}  -> {r['detail']}" for r in failed
    )
    assert len(results) >= 60, f"trop peu de cas exécutés : {len(results)}"
