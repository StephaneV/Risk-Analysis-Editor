/* Génère les modèles méthodologiques (squelettes vierges) dans le dossier templates/.
   vertical_axis = vraisemblance (= probability du code), horizontal_axis = gravité (= severity).
   Chaque modèle porte metadata.kind="template" ; risks/measures/treatments vides. */
const fs = require("fs");
const path = require("path");
const OUT = __dirname;   // les modèles sont écrits à côté de ce script (dossier templates/)
fs.mkdirSync(OUT, { recursive: true });

const CRIT = {
  green:"#2e9e5b", yellow:"#e0b93a", orange:"#e6862e", red:"#d64545"
};
const tag = (code,label,color)=>({code,label:{fr:label},color});
const opt = (code,label)=>({code,label:{fr:label}});
const axis = (label,description,rows)=>({label,description,levels:rows.map(([value,l,d])=>({value,label:l,description:d}))});

function write(file,obj){
  fs.writeFileSync(path.join(OUT,file),JSON.stringify(obj,null,2),"utf8");
  console.log("écrit :",file,"| champs perso :",(obj.custom_fields||[]).length);
}
function base(meta,grid,fields){
  return {
    format:"risk-analysis-editor", version:"1.0",
    metadata:Object.assign({author:"",organization:"",scope:"",revision:"1.0",status:"draft",language:"fr",kind:"template"},meta),
    grid, custom_fields:fields||[], custom:{}, risks:[], measures:[], treatments:[]
  };
}

/* ================= échelles réutilisables ================= */
const VRAIS4 = [
  [1,"Minime","La source de risque ne devrait pas agir, ou le mode opératoire est très difficile à mettre en œuvre."],
  [2,"Significative","La source de risque pourrait agir ; le mode opératoire reste réalisable avec un effort modéré."],
  [3,"Forte","La source de risque a de bonnes raisons d'agir et le mode opératoire est accessible."],
  [4,"Maximale","La source de risque va très probablement agir ; le mode opératoire est trivial."]
];
const GRAV4_EBIOS = [
  [1,"Mineure","Aucun impact opérationnel ou juridique notable ; gêne surmontable."],
  [2,"Significative","Impact réel mais maîtrisable, sans conséquence durable."],
  [3,"Grave","Impact important, difficilement réversible, sur l'activité ou les personnes."],
  [4,"Critique","Impact majeur, potentiellement irréversible, mettant en cause la pérennité ou la sécurité."]
];
const critEbios = [
  {code:"faible",label:"Faible",score_min:1,score_max:3,color:CRIT.green,acceptance:"acceptable",order:1,
   description:"Risque faible : acceptable en l'état, à surveiller lors des revues."},
  {code:"modere",label:"Modéré",score_min:4,score_max:6,color:CRIT.yellow,acceptance:"tolerable",order:2,
   description:"Risque modéré : tolérable sous conditions ; des mesures de réduction sont à envisager."},
  {code:"eleve",label:"Élevé",score_min:7,score_max:11,color:CRIT.orange,acceptance:"to_treat",order:3,
   description:"Risque élevé : un traitement est attendu pour ramener le risque à un niveau acceptable."},
  {code:"critique",label:"Critique",score_min:12,score_max:16,color:CRIT.red,acceptance:"unacceptable",order:4,
   description:"Risque critique : inacceptable en l'état ; traitement prioritaire requis."}
];

/* ================= 1. EBIOS RM ================= */
write("ebios-rm.template.rae.json", base(
  {title:"Modèle EBIOS RM (ANSSI)",
   description:"Squelette d'analyse selon **EBIOS Risk Manager** (ANSSI). Grille de vraisemblance × gravité, niveaux de risque et champs personnalisés préconfigurés.\n\nÀ compléter : valeurs métier et biens supports (atelier 1), sources de risque et objectifs visés (atelier 2), scénarios stratégiques (atelier 3) puis opérationnels (atelier 4), et le traitement (atelier 5).",
   methodology_reference:"EBIOS Risk Manager (ANSSI)"},
  {vertical_axis:axis("Vraisemblance","Possibilité que le scénario se réalise, au regard des sources de risque et des modes opératoires.",VRAIS4),
   horizontal_axis:axis("Gravité","Ampleur des conséquences pour l'organisation et les personnes.",GRAV4_EBIOS),
   score:{method:"product"}, criticality_levels:critEbios},
  [
    {code:"referentiels",target:"analysis",type:"tags",multiple:true,order:1,label:{fr:"Référentiels"},
     items:[tag("ebios-rm","EBIOS RM","#3a63d6"),tag("iso-27005","ISO 27005","#4c7dff"),tag("rgpd","RGPD","#e25631"),tag("nis2","NIS2","#8e44ad"),tag("pssi","PSSI","#16a085")]},
    {code:"socle_securite",target:"analysis",type:"textarea",order:2,label:{fr:"Socle de sécurité"},
     description:{fr:"Référentiels applicables, écarts identifiés et justification (atelier 1)."}},
    {code:"type_scenario",target:"risk",type:"select",order:1,filterable:true,label:{fr:"Type de scénario"},
     items:[opt("strategique","Scénario stratégique"),opt("operationnel","Scénario opérationnel")]},
    {code:"source_risque",target:"risk",type:"tags",multiple:true,order:2,filterable:true,label:{fr:"Source de risque"},
     items:[tag("etatique","Étatique","#6c3483"),tag("cybercriminel","Cybercriminel","#c0392b"),tag("terroriste","Terroriste","#7b241c"),
            tag("activiste","Activiste idéologique","#d35400"),tag("officine","Officine spécialisée","#b7950b"),tag("amateur","Amateur","#2980b9"),
            tag("vengeur","Vengeur","#a04000"),tag("initie","Initié malveillant","#922b21"),tag("concurrent","Concurrent","#1f618d")]},
    {code:"objectif_vise",target:"risk",type:"tags",multiple:true,order:3,filterable:true,label:{fr:"Objectif visé"},
     items:[tag("espionnage","Espionnage","#6c3483"),tag("prepos","Pré-positionnement","#5d6d7e"),tag("entrave","Sabotage / entrave","#c0392b"),
            tag("influence","Influence","#8e44ad"),tag("lucratif","Lucratif","#b7950b"),tag("defi","Défi / amusement","#2980b9")]},
    {code:"valeur_metier",target:"risk",type:"text",order:4,label:{fr:"Valeur métier visée"}},
    {code:"biens_supports",target:"risk",type:"tags",multiple:true,order:5,filterable:true,label:{fr:"Biens supports"},
     items:[tag("poste","Poste de travail","#2e86de"),tag("serveur","Serveur / stockage","#117864"),tag("appli","Application","#148f77"),
            tag("reseau","Réseau","#1f618d"),tag("donnees","Données","#7d6608"),tag("prestataire","Prestataire","#1abc9c"),
            tag("local","Site / local","#b9770e"),tag("personne","Personne","#af7ac5")]},
    {code:"socle",target:"measure",type:"select",order:1,filterable:true,label:{fr:"Catégorie de sécurité"},
     items:[opt("gouvernance","Gouvernance"),opt("protection","Protection"),opt("defense","Défense"),opt("resilience","Résilience")]},
    {code:"avancement",target:"measure",type:"progress",order:2,label:{fr:"Avancement"},palette:"red-orange-green",step:10},
    {code:"effet",target:"link",type:"tags",multiple:true,order:1,filterable:true,label:{fr:"Effet attendu"},
     items:[tag("vraisemblance","Réduit la vraisemblance","#2471a3"),tag("gravite","Réduit la gravité","#b9770e")]}
  ]
));

/* ================= 2. CNIL PIA / AIPD ================= */
const GRAV4_PIA = [
  [1,"Négligeable","Les personnes ne seront pas impactées ou surmonteront quelques désagréments sans difficulté."],
  [2,"Limitée","Les personnes pourraient connaître des désagréments significatifs, surmontables malgré des difficultés."],
  [3,"Importante","Les personnes pourraient connaître des conséquences significatives, surmontables mais avec de réelles difficultés."],
  [4,"Maximale","Les personnes pourraient connaître des conséquences significatives, voire irrémédiables, qu'elles pourraient ne pas surmonter."]
];
const VRAIS4_PIA = [
  [1,"Négligeable","Il ne semble pas possible que la menace se réalise."],
  [2,"Limitée","Il semble difficile pour les sources de risques de réaliser la menace."],
  [3,"Importante","Il semble possible pour les sources de risques de réaliser la menace."],
  [4,"Maximale","Il semble extrêmement facile pour les sources de risques de réaliser la menace."]
];
/* Niveau défini par cellule : lignes = vraisemblance 1→4, colonnes = gravité 1→4. */
const MATRIX_PIA = [[1,1,2,3],[1,2,2,3],[2,2,3,4],[3,3,4,4]];
write("cnil-pia.template.rae.json", base(
  {title:"Modèle AIPD — CNIL PIA",
   description:"Squelette d'**Analyse d'Impact sur la Protection des Données** selon la méthode **CNIL PIA**. Grille à quatre niveaux dont le niveau de risque est défini **par cellule** (et non par produit), et champs personnalisés propres à la démarche.\n\nÀ compléter : contexte et sous-traitants, puis pour chaque événement redouté (accès illégitime, modification non désirée, indisponibilité) les scénarios, leur cotation initiale et résiduelle, et le plan d'action.",
   methodology_reference:"Méthode CNIL PIA (Privacy Impact Assessment)"},
  {vertical_axis:axis("Vraisemblance","Possibilité qu'un risque se réalise, au regard des vulnérabilités des supports et des sources de risques.",VRAIS4_PIA),
   horizontal_axis:axis("Gravité","Ampleur du risque, estimée au regard des impacts potentiels sur les personnes concernées.",GRAV4_PIA),
   score:{method:"matrix",matrix:MATRIX_PIA},
   criticality_levels:[
     {code:"negligeable",label:"Négligeable",score_min:1,score_max:1,color:"#8CC63E",acceptance:"acceptable",order:1,description:"Niveau de risque négligeable au sens de la méthode PIA."},
     {code:"limite",label:"Limité",score_min:2,score_max:2,color:"#FFF166",acceptance:"acceptable",order:2,description:"Niveau de risque limité au sens de la méthode PIA."},
     {code:"important",label:"Important",score_min:3,score_max:3,color:"#F2B33D",acceptance:"tolerable",order:3,description:"Niveau de risque important : des mesures de réduction sont attendues."},
     {code:"maximal",label:"Maximal",score_min:4,score_max:4,color:"#E8291C",acceptance:"unacceptable",order:4,description:"Niveau de risque maximal : le traitement ne peut être conduit en l'état."}
   ]},
  [
    {code:"responsable_traitement",target:"analysis",type:"text",order:1,label:{fr:"Responsable du traitement"}},
    {code:"sous_traitants",target:"analysis",type:"textarea",order:2,label:{fr:"Sous-traitants"},description:{fr:"Sous-traitants au sens de l'article 28 du RGPD (ou équivalent), et objet de leur intervention."}},
    {code:"referentiels",target:"analysis",type:"textarea",order:3,label:{fr:"Référentiels applicables"}},
    {code:"avis_dpo",target:"analysis",type:"textarea",order:4,label:{fr:"Avis du DPO"}},
    {code:"mesures_existantes",target:"analysis",type:"textarea",order:5,label:{fr:"Mesures existantes"},description:{fr:"Catalogue des mesures déjà en place, tenues hors du registre des mesures (réservé aux actions du plan d'action)."}},
    {code:"evenement_redoute",target:"risk",type:"select",order:1,required:true,filterable:true,label:{fr:"Événement redouté"},
     items:[opt("acces","Accès illégitime à des données"),opt("modif","Modification non désirée de données"),opt("indispo","Indisponibilité ou disparition de données")]},
    {code:"sources_risque",target:"risk",type:"tags",multiple:true,order:2,filterable:true,label:{fr:"Sources de risque"},
     items:[tag("interne-mal","Source interne malveillante","#922b21"),tag("interne-acc","Source interne accidentelle","#e67e22"),
            tag("externe","Source externe","#c0392b"),tag("prestataire","Prestataire","#1abc9c"),tag("environnement","Environnement / matériel","#7f8c8d")]},
    {code:"supports",target:"risk",type:"tags",multiple:true,order:3,filterable:true,label:{fr:"Supports concernés"},
     items:[tag("materiel","Matériel","#2e86de"),tag("logiciel","Logiciel","#148f77"),tag("canal-info","Canal informatique","#1f618d"),
            tag("papier","Support papier","#b9770e"),tag("canal-papier","Canal papier","#ca6f1e"),tag("personne","Personne","#af7ac5")]},
    {code:"impacts",target:"risk",type:"tags",multiple:true,order:4,filterable:true,label:{fr:"Impacts sur les personnes"},
     items:[tag("corporel","Corporel","#c0392b"),tag("materiel-imp","Matériel","#b7950b"),tag("moral","Moral","#6c3483")]},
    {code:"origine",target:"measure",type:"select",order:1,filterable:true,label:{fr:"Origine"},
     items:[opt("complementaire","Mesure complémentaire"),opt("ajustement","Ajustement d'une mesure existante"),opt("principe","Principe fondamental")]},
    {code:"bloquante",target:"measure",type:"boolean",order:2,filterable:true,label:{fr:"Bloquante"},
     description:{fr:"Action à mettre en œuvre au plus vite : le traitement ne peut être conduit sans elle."}},
    {code:"effet",target:"link",type:"tags",multiple:true,order:1,filterable:true,label:{fr:"Effet attendu"},
     items:[tag("vraisemblance","Réduit la vraisemblance","#2471a3"),tag("gravite","Réduit la gravité","#b9770e")]}
  ]
));

/* ================= 3. ISO 27005 ================= */
const VRAIS5 = [
  [1,"Très faible","Réalisation très improbable dans la période considérée."],
  [2,"Faible","Réalisation peu probable."],
  [3,"Moyenne","Réalisation plausible."],
  [4,"Élevée","Réalisation probable."],
  [5,"Très élevée","Réalisation quasi certaine."]
];
const IMPACT5 = [
  [1,"Négligeable","Conséquences insignifiantes pour l'organisation."],
  [2,"Faible","Conséquences mineures, absorbées sans difficulté."],
  [3,"Moyen","Conséquences notables mais maîtrisables."],
  [4,"Important","Conséquences sérieuses, difficilement réversibles."],
  [5,"Critique","Conséquences majeures, mettant en cause l'activité."]
];
const crit5 = [
  {code:"faible",label:"Faible",score_min:1,score_max:4,color:CRIT.green,acceptance:"acceptable",order:1,description:"Risque faible : acceptable, à surveiller."},
  {code:"moyen",label:"Moyen",score_min:5,score_max:10,color:CRIT.yellow,acceptance:"tolerable",order:2,description:"Risque moyen : tolérable sous conditions ; réduction à envisager."},
  {code:"eleve",label:"Élevé",score_min:11,score_max:16,color:CRIT.orange,acceptance:"to_treat",order:3,description:"Risque élevé : traitement attendu."},
  {code:"critique",label:"Critique",score_min:17,score_max:25,color:CRIT.red,acceptance:"unacceptable",order:4,description:"Risque critique : inacceptable en l'état ; traitement prioritaire."}
];
write("iso-27005.template.rae.json", base(
  {title:"Modèle ISO/IEC 27005",
   description:"Squelette d'appréciation du risque selon **ISO/IEC 27005**. Grille vraisemblance × impact sur cinq niveaux (score = produit), et champs personnalisés orientés actifs, menaces et vulnérabilités.\n\nÀ compléter : périmètre et critères d'acceptation, identification des actifs, des menaces et vulnérabilités, estimation puis évaluation du risque, et choix des options de traitement.",
   methodology_reference:"ISO/IEC 27005 — Gestion des risques liés à la sécurité de l'information"},
  {vertical_axis:axis("Vraisemblance","Probabilité de réalisation du scénario de risque.",VRAIS5),
   horizontal_axis:axis("Impact","Conséquences pour l'organisation en cas de réalisation.",IMPACT5),
   score:{method:"product"}, criticality_levels:crit5},
  [
    {code:"referentiels",target:"analysis",type:"tags",multiple:true,order:1,label:{fr:"Référentiels"},
     items:[tag("iso-27005","ISO 27005","#3a63d6"),tag("iso-27001","ISO 27001","#4c7dff"),tag("iso-27002","ISO 27002","#16a085"),tag("rgpd","RGPD","#e25631")]},
    {code:"perimetre",target:"analysis",type:"textarea",order:2,label:{fr:"Périmètre"}},
    {code:"critere_acceptation",target:"analysis",type:"textarea",order:3,label:{fr:"Critères d'acceptation du risque"}},
    {code:"actif",target:"risk",type:"text",order:1,label:{fr:"Actif concerné"}},
    {code:"type_actif",target:"risk",type:"select",order:2,filterable:true,label:{fr:"Type d'actif"},
     items:[opt("primaire","Actif primaire (information, processus)"),opt("support","Actif support (matériel, logiciel, réseau, personne, site)")]},
    {code:"menace",target:"risk",type:"tags",multiple:true,order:3,filterable:true,label:{fr:"Menace"},
     items:[tag("acces-na","Accès non autorisé","#c0392b"),tag("compromission-info","Compromission d'informations","#922b21"),
            tag("defaillance","Défaillance technique","#7f8c8d"),tag("actions-na","Actions non autorisées","#a04000"),
            tag("compromission-fct","Compromission de fonctions","#6c3483"),tag("dommages","Dommages physiques","#b9770e"),
            tag("naturel","Événement naturel","#16a085"),tag("perte-service","Perte de services essentiels","#1f618d")]},
    {code:"vulnerabilite",target:"risk",type:"text",order:4,label:{fr:"Vulnérabilité exploitée"}},
    {code:"option_traitement",target:"risk",type:"select",order:5,filterable:true,label:{fr:"Option de traitement"},
     items:[opt("reduire","Réduire (modifier)"),opt("accepter","Accepter (maintenir)"),opt("eviter","Éviter (supprimer)"),opt("partager","Partager (transférer)")]},
    {code:"proprietaire_risque",target:"risk",type:"text",order:6,label:{fr:"Propriétaire du risque"}},
    {code:"reference_controle",target:"measure",type:"text",order:1,label:{fr:"Réf. mesure (ISO 27002)"},description:{fr:"Référence de la mesure de sécurité applicable, p. ex. A.8.16."}},
    {code:"avancement",target:"measure",type:"progress",order:2,label:{fr:"Avancement"},palette:"red-orange-green",step:10},
    {code:"effet",target:"link",type:"tags",multiple:true,order:1,filterable:true,label:{fr:"Effet attendu"},
     items:[tag("vraisemblance","Réduit la vraisemblance","#2471a3"),tag("gravite","Réduit l'impact","#b9770e")]}
  ]
));

/* ================= 4. Générique simple ================= */
const PROBA5 = [
  [1,"Très faible","Réalisation très improbable."],[2,"Faible","Réalisation peu probable."],
  [3,"Moyenne","Réalisation plausible."],[4,"Élevée","Réalisation probable."],[5,"Très élevée","Réalisation quasi certaine."]
];
const IMPACTG5 = [
  [1,"Très faible","Conséquences insignifiantes."],[2,"Faible","Conséquences mineures."],
  [3,"Moyen","Conséquences notables."],[4,"Élevé","Conséquences sérieuses."],[5,"Très élevé","Conséquences majeures."]
];
write("generique.template.rae.json", base(
  {title:"Modèle générique",
   description:"Squelette neutre : grille probabilité × impact sur cinq niveaux (score = produit) et quatre niveaux de criticité, **sans champ personnalisé imposé**. Point de départ pour une analyse de risques ne suivant pas une méthode particulière.",
   methodology_reference:"Analyse de risques — grille générique 5×5"},
  {vertical_axis:axis("Probabilité","Probabilité de survenue du risque.",PROBA5),
   horizontal_axis:axis("Impact","Ampleur des conséquences en cas de survenue.",IMPACTG5),
   score:{method:"product"}, criticality_levels:crit5},
  []
));

console.log("Terminé.");
