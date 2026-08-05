/* Génère les modèles méthodologiques (squelettes vierges), un fichier PAR LANGUE.
   Nommage : <slug>.template.<lang>.rae.json  (fr | en | it).

   Le format .rae.json n'est multilingue que pour les libellés de champs personnalisés
   (objets {fr,en,it}). Les axes de la grille, les niveaux de criticité et les métadonnées
   sont des chaines uniques : on produit donc un fichier par langue, chacun avec ces chaines
   dans sa langue. Les champs personnalises restent, eux, pleinement {fr,en,it} dans tous les
   fichiers, afin que le changement de langue apres ouverture les traduise aussi.

   vertical_axis = vraisemblance (= probability du code), horizontal_axis = gravité (severity).
   Chaque modèle porte metadata.kind="template" ; risks/measures/treatments vides. */
const fs = require("fs");
const path = require("path");
const OUT = __dirname;
const LANGS = ["fr", "en", "it"];

const CRIT = { green:"#2e9e5b", yellow:"#e0b93a", orange:"#e6862e", red:"#d64545" };
const T = (fr,en,it)=>({fr,en,it});
const pick = (o,l)=>o&&(o[l]!=null?o[l]:o.fr);
const tag = (code,label,color)=>({code,label,color});     // label = objet {fr,en,it}
const opt = (code,label)=>({code,label});

/* Résout un modèle « source » (chaines en objets {fr,en,it}) pour une langue donnée :
   grille et metadonnees deviennent des chaines ; les champs personnalises gardent {fr,en,it}. */
function resolve(spec, lang){
  const axis = a=>({label:pick(a.label,lang), description:pick(a.description,lang),
    levels:a.levels.map(l=>({value:l.value,label:pick(l.label,lang),description:pick(l.description,lang)}))});
  const grid = {
    vertical_axis: axis(spec.grid.vertical_axis),
    horizontal_axis: axis(spec.grid.horizontal_axis),
    score: spec.grid.score,
    criticality_levels: spec.grid.criticality_levels.map(c=>({
      code:c.code,label:pick(c.label,lang),score_min:c.score_min,score_max:c.score_max,
      color:c.color,acceptance:c.acceptance,order:c.order,description:pick(c.description,lang)}))
  };
  const metadata = {
    title:pick(spec.meta.title,lang), description:pick(spec.meta.description,lang),
    author:"", organization:"", scope:"",
    methodology_reference:pick(spec.meta.methodology_reference,lang),
    revision:"1.0", status:"draft", language:lang, kind:"template"
  };
  return {format:"risk-analysis-editor", version:"1.0", metadata, grid,
    custom_fields:spec.fields||[], custom:{}, risks:[], measures:[], treatments:[]};
}
/* Descriptions des valeurs (items) des champs à valeurs fermées, ancrées sur les méthodes.
   Format « <slug>.<champ>.<code> = FR ||| EN ||| IT ». Appliquées dans emit(). */
const ITEM_DESC = (function(){
  const raw = `
ebios-rm.source_risque.etatique = État ou entité agissant pour son compte, disposant de moyens élevés et visant le renseignement ou la déstabilisation stratégique ||| State or state-backed entity with substantial resources, pursuing intelligence gathering or strategic destabilisation ||| Stato o entità che agisce per suo conto, dotata di ingenti risorse e orientata allo spionaggio o alla destabilizzazione strategica
ebios-rm.source_risque.cybercriminel = Individu ou groupe organisé recherchant un gain financier par extorsion, fraude ou revente de données ||| Individual or organised group seeking financial gain through extortion, fraud or resale of data ||| Individuo o gruppo organizzato che cerca un guadagno economico tramite estorsione, frode o rivendita di dati
ebios-rm.source_risque.terroriste = Acteur cherchant à provoquer terreur ou dommages graves au service d'une cause politique ou religieuse ||| Actor seeking to cause terror or serious harm in support of a political or religious cause ||| Attore che mira a provocare terrore o gravi danni al servizio di una causa politica o religiosa
ebios-rm.source_risque.activiste = Militant motivé par une idéologie, cherchant à nuire à l'image de la cible ou à médiatiser une cause ||| Militant driven by an ideology, aiming to damage the target's image or publicise a cause ||| Militante mosso da un'ideologia, che mira a danneggiare l'immagine del bersaglio o a dare risalto a una causa
ebios-rm.source_risque.officine = Prestataire privé fournissant des services offensifs (renseignement, intrusion) pour le compte d'un commanditaire ||| Private provider offering offensive services (intelligence, intrusion) on behalf of a sponsor ||| Fornitore privato che offre servizi offensivi (spionaggio, intrusione) per conto di un committente
ebios-rm.source_risque.amateur = Attaquant peu qualifié agissant par curiosité ou opportunisme, avec des moyens limités ||| Low-skilled attacker acting out of curiosity or opportunism, with limited resources ||| Attaccante poco qualificato che agisce per curiosità o opportunismo, con risorse limitate
ebios-rm.source_risque.vengeur = Personne animée par une rancune personnelle envers l'organisation, souvent ancien membre ou usager ||| Individual driven by a personal grievance against the organisation, often a former member or user ||| Persona mossa da un rancore personale verso l'organizzazione, spesso ex membro o utente
ebios-rm.source_risque.initie = Membre interne exploitant ses accès légitimes à des fins malveillantes ||| Insider abusing their legitimate access for malicious purposes ||| Membro interno che sfrutta i propri accessi legittimi a fini malevoli
ebios-rm.source_risque.concurrent = Entreprise rivale recherchant un avantage économique par espionnage ou déstabilisation ||| Rival company seeking an economic advantage through espionage or destabilisation ||| Azienda concorrente che cerca un vantaggio economico tramite spionaggio o destabilizzazione
ebios-rm.objectif_vise.espionnage = Obtenir des informations confidentielles ou stratégiques à l'insu de l'organisation ||| Obtaining confidential or strategic information without the organisation's knowledge ||| Ottenere informazioni riservate o strategiche all'insaputa dell'organizzazione
ebios-rm.objectif_vise.prepos = S'implanter durablement et discrètement dans le système pour pouvoir agir ultérieurement ||| Establishing a lasting, covert foothold in the system in order to act later ||| Insediarsi in modo duraturo e discreto nel sistema per poter agire in seguito
ebios-rm.objectif_vise.entrave = Perturber, dégrader ou interrompre le fonctionnement d'une activité ou d'un système ||| Disrupting, degrading or halting the operation of an activity or system ||| Perturbare, degradare o interrompere il funzionamento di un'attività o di un sistema
ebios-rm.objectif_vise.influence = Peser sur les opinions, décisions ou la réputation par la manipulation de l'information ||| Swaying opinions, decisions or reputation through the manipulation of information ||| Influenzare opinioni, decisioni o reputazione tramite la manipolazione dell'informazione
ebios-rm.objectif_vise.lucratif = Tirer un profit financier direct de l'attaque (rançon, fraude, revente) ||| Deriving direct financial profit from the attack (ransom, fraud, resale) ||| Trarre un profitto economico diretto dall'attacco (riscatto, frode, rivendita)
ebios-rm.objectif_vise.defi = Agir par jeu, défi technique ou recherche de notoriété, sans finalité matérielle ||| Acting for fun, technical challenge or notoriety, with no material aim ||| Agire per gioco, sfida tecnica o ricerca di notorietà, senza finalità materiali
ebios-rm.type_scenario.strategique = Chemin d'attaque de haut niveau reliant une source de risque à son objectif à travers l'écosystème (atelier 3) ||| High-level attack path linking a risk source to its objective across the ecosystem (workshop 3) ||| Percorso d'attacco di alto livello che collega una fonte di rischio al suo obiettivo attraverso l'ecosistema (workshop 3)
ebios-rm.type_scenario.operationnel = Enchaînement technique détaillé des modes opératoires empruntés sur les biens supports (atelier 4) ||| Detailed technical sequence of the modes of operation used against supporting assets (workshop 4) ||| Sequenza tecnica dettagliata dei modi operativi impiegati sui beni di supporto (workshop 4)
ebios-rm.biens_supports.poste = Équipement utilisateur (ordinateur, portable, terminal) sur lequel reposent des valeurs métier ||| User device (desktop, laptop, terminal) on which business values rely ||| Dispositivo utente (computer, portatile, terminale) su cui poggiano i valori aziendali
ebios-rm.biens_supports.serveur = Infrastructure de traitement ou de stockage hébergeant applications et données ||| Processing or storage infrastructure hosting applications and data ||| Infrastruttura di elaborazione o archiviazione che ospita applicazioni e dati
ebios-rm.biens_supports.appli = Logiciel ou service assurant une fonction métier ou technique ||| Software or service delivering a business or technical function ||| Software o servizio che svolge una funzione aziendale o tecnica
ebios-rm.biens_supports.reseau = Composants et liaisons assurant la transmission des données (LAN, WAN, interconnexions) ||| Components and links carrying data transmission (LAN, WAN, interconnections) ||| Componenti e collegamenti che assicurano la trasmissione dei dati (LAN, WAN, interconnessioni)
ebios-rm.biens_supports.donnees = Ensembles d'informations manipulées, stockées ou échangées par le système ||| Sets of information handled, stored or exchanged by the system ||| Insiemi di informazioni trattate, archiviate o scambiate dal sistema
ebios-rm.biens_supports.prestataire = Tiers externe intervenant dans le fonctionnement ou la maintenance du système ||| External third party involved in the operation or maintenance of the system ||| Terzo esterno che interviene nel funzionamento o nella manutenzione del sistema
ebios-rm.biens_supports.local = Emplacement physique (site, salle, bâtiment) abritant des biens supports ||| Physical location (site, room, building) housing supporting assets ||| Luogo fisico (sito, sala, edificio) che ospita beni di supporto
ebios-rm.biens_supports.personne = Individu (agent, utilisateur) dont l'action ou la présence conditionne une valeur métier ||| Individual (staff member, user) whose action or presence underpins a business value ||| Individuo (dipendente, utente) la cui azione o presenza condiziona un valore aziendale
ebios-rm.socle.gouvernance = Mesures d'organisation, de pilotage et de conformité encadrant la sécurité ||| Organisational, steering and compliance measures framing security ||| Misure di organizzazione, governo e conformità che inquadrano la sicurezza
ebios-rm.socle.protection = Mesures réduisant la probabilité ou l'ampleur d'une attaque (barrières préventives) ||| Measures reducing the likelihood or scale of an attack (preventive barriers) ||| Misure che riducono la probabilità o l'entità di un attacco (barriere preventive)
ebios-rm.socle.defense = Mesures de détection et de réaction face aux attaques en cours ||| Detection and response measures against ongoing attacks ||| Misure di rilevamento e risposta agli attacchi in corso
ebios-rm.socle.resilience = Mesures assurant la continuité d'activité et le retour à un état nominal après incident ||| Measures ensuring business continuity and return to a nominal state after an incident ||| Misure che garantiscono la continuità operativa e il ripristino dello stato nominale dopo un incidente
cnil-pia.evenement_redoute.acces = Violation de confidentialité : des données personnelles sont consultées par des personnes non autorisées ||| Confidentiality breach: personal data is accessed by unauthorised persons ||| Violazione della riservatezza: dati personali consultati da persone non autorizzate
cnil-pia.evenement_redoute.modif = Violation d'intégrité : des données sont altérées, faussées ou modifiées de façon non voulue ||| Integrity breach: data is altered, corrupted or changed in an unintended way ||| Violazione dell'integrità: dati alterati, falsati o modificati in modo indesiderato
cnil-pia.evenement_redoute.indispo = Violation de disponibilité : des données deviennent inaccessibles, perdues ou détruites ||| Availability breach: data becomes inaccessible, lost or destroyed ||| Violazione della disponibilità: dati resi inaccessibili, persi o distrutti
cnil-pia.sources_risque.interne-mal = Personne interne à l'organisme agissant intentionnellement pour nuire ||| Person inside the organisation acting deliberately to cause harm ||| Persona interna all'organismo che agisce intenzionalmente per nuocere
cnil-pia.sources_risque.interne-acc = Personne interne provoquant un dommage par erreur, négligence ou méconnaissance ||| Insider causing harm through error, negligence or lack of awareness ||| Persona interna che provoca un danno per errore, negligenza o inconsapevolezza
cnil-pia.sources_risque.externe = Acteur extérieur à l'organisme cherchant à exploiter ou compromettre les données ||| Actor outside the organisation seeking to exploit or compromise the data ||| Attore esterno all'organismo che cerca di sfruttare o compromettere i dati
cnil-pia.sources_risque.prestataire = Sous-traitant ou fournisseur ayant accès aux données dans le cadre de sa prestation ||| Subcontractor or supplier with access to the data as part of its service ||| Subappaltatore o fornitore con accesso ai dati nell'ambito della propria prestazione
cnil-pia.sources_risque.environnement = Source non humaine : défaillance matérielle, sinistre ou événement naturel affectant les supports ||| Non-human source: hardware failure, disaster or natural event affecting the media ||| Fonte non umana: guasto materiale, sinistro o evento naturale che colpisce i supporti
cnil-pia.supports.materiel = Équipements physiques hébergeant les données (serveurs, postes, supports amovibles) ||| Physical equipment hosting the data (servers, workstations, removable media) ||| Apparecchiature fisiche che ospitano i dati (server, postazioni, supporti rimovibili)
cnil-pia.supports.logiciel = Programmes et systèmes d'exploitation traitant les données personnelles ||| Programs and operating systems processing the personal data ||| Programmi e sistemi operativi che trattano i dati personali
cnil-pia.supports.canal-info = Voie de transmission électronique des données (réseaux, connexions informatiques) ||| Electronic channel transmitting the data (networks, IT connections) ||| Canale di trasmissione elettronica dei dati (reti, connessioni informatiche)
cnil-pia.supports.papier = Documents imprimés ou manuscrits contenant des données personnelles ||| Printed or handwritten documents containing personal data ||| Documenti stampati o manoscritti contenenti dati personali
cnil-pia.supports.canal-papier = Moyen d'acheminement physique des documents (courrier, transport de papier) ||| Physical means of conveying documents (mail, transport of paper) ||| Mezzo di trasporto fisico dei documenti (posta, trasporto cartaceo)
cnil-pia.supports.personne = Individu détenteur ou porteur de connaissances relatives aux données ||| Individual holding or possessing knowledge relating to the data ||| Individuo detentore o portatore di conoscenze relative ai dati
cnil-pia.impacts.corporel = Atteinte à l'intégrité physique de la personne concernée (blessure, atteinte à la santé) ||| Harm to the physical integrity of the data subject (injury, harm to health) ||| Lesione dell'integrità fisica dell'interessato (ferite, danno alla salute)
cnil-pia.impacts.materiel-imp = Préjudice patrimonial ou financier subi par la personne (perte, fraude, coûts) ||| Material or financial loss suffered by the data subject (loss, fraud, costs) ||| Pregiudizio patrimoniale o finanziario subito dalla persona (perdita, frode, costi)
cnil-pia.impacts.moral = Atteinte psychologique ou à la réputation (détresse, discrimination, humiliation) ||| Psychological or reputational harm (distress, discrimination, humiliation) ||| Danno psicologico o alla reputazione (sofferenza, discriminazione, umiliazione)
cnil-pia.origine.complementaire = Mesure ajoutée spécifiquement pour réduire un risque identifié ||| Measure added specifically to reduce an identified risk ||| Misura aggiunta specificamente per ridurre un rischio individuato
cnil-pia.origine.ajustement = Renforcement ou adaptation d'une mesure déjà en place ||| Strengthening or adaptation of a measure already in place ||| Rafforzamento o adattamento di una misura già in essere
cnil-pia.origine.principe = Exigence fondamentale du RGPD (finalité, minimisation, base légale) à respecter en tout état de cause ||| Fundamental GDPR requirement (purpose, minimisation, legal basis) to be met in all cases ||| Requisito fondamentale del GDPR (finalità, minimizzazione, base giuridica) da rispettare in ogni caso
iso-27005.type_actif.primaire = Information ou processus métier essentiel dont dépend directement l'activité de l'organisation ||| Essential information or business process on which the organisation's activity directly depends ||| Informazione o processo aziendale essenziale da cui dipende direttamente l'attività dell'organizzazione
iso-27005.type_actif.support = Élément (matériel, logiciel, réseau, personnel, site) sur lequel reposent les actifs primaires ||| Element (hardware, software, network, personnel, site) underpinning the primary assets ||| Elemento (hardware, software, rete, personale, sito) su cui poggiano gli asset primari
iso-27005.menace.acces-na = Obtention d'un accès aux systèmes ou aux informations sans autorisation ||| Gaining access to systems or information without authorisation ||| Ottenimento di un accesso ai sistemi o alle informazioni senza autorizzazione
iso-27005.menace.compromission-info = Atteinte à la confidentialité ou à l'intégrité de l'information (interception, divulgation, vol) ||| Compromise of the confidentiality or integrity of information (interception, disclosure, theft) ||| Compromissione della riservatezza o dell'integrità dell'informazione (intercettazione, divulgazione, furto)
iso-27005.menace.defaillance = Panne ou dysfonctionnement d'un équipement ou d'un logiciel ||| Failure or malfunction of equipment or software ||| Guasto o malfunzionamento di un'apparecchiatura o di un software
iso-27005.menace.actions-na = Utilisation illicite ou détournée de ressources (usage non autorisé, copie frauduleuse) ||| Unlawful or improper use of resources (unauthorised use, fraudulent copying) ||| Uso illecito o improprio delle risorse (utilizzo non autorizzato, copia fraudolenta)
iso-27005.menace.compromission-fct = Altération du bon fonctionnement (abus de droits, erreur d'exploitation, reniement d'actions) ||| Impairment of proper functioning (abuse of rights, operating error, repudiation of actions) ||| Alterazione del corretto funzionamento (abuso di diritti, errore d'esercizio, disconoscimento di azioni)
iso-27005.menace.dommages = Atteintes physiques aux biens (incendie, dégât des eaux, destruction, vol de matériel) ||| Physical damage to assets (fire, water damage, destruction, theft of equipment) ||| Danni fisici ai beni (incendio, danni da acqua, distruzione, furto di apparecchiature)
iso-27005.menace.naturel = Phénomène naturel affectant les installations (séisme, inondation, conditions climatiques) ||| Natural phenomenon affecting facilities (earthquake, flood, climatic conditions) ||| Fenomeno naturale che colpisce gli impianti (sisma, inondazione, condizioni climatiche)
iso-27005.menace.perte-service = Interruption d'un service essentiel (alimentation électrique, climatisation, télécommunications) ||| Loss of an essential service (power supply, air conditioning, telecommunications) ||| Perdita di un servizio essenziale (alimentazione elettrica, climatizzazione, telecomunicazioni)
iso-27005.option_traitement.reduire = Mettre en place des mesures de sécurité pour ramener le risque à un niveau acceptable ||| Implementing security controls to bring the risk down to an acceptable level ||| Attuare misure di sicurezza per riportare il rischio a un livello accettabile
iso-27005.option_traitement.accepter = Assumer le risque en connaissance de cause, sans mesure de traitement supplémentaire ||| Knowingly accepting the risk without any further treatment ||| Assumere consapevolmente il rischio, senza ulteriori misure di trattamento
iso-27005.option_traitement.eviter = Supprimer la source du risque en renonçant à l'activité ou au bien concerné ||| Removing the source of the risk by abandoning the activity or asset concerned ||| Eliminare la fonte del rischio rinunciando all'attività o al bene interessato
iso-27005.option_traitement.partager = Transférer tout ou partie du risque à un tiers (assurance, sous-traitance) ||| Transferring all or part of the risk to a third party (insurance, outsourcing) ||| Trasferire in tutto o in parte il rischio a un terzo (assicurazione, esternalizzazione)`;
  const m={};
  raw.trim().split("\n").forEach(line=>{const eq=line.indexOf(" = ");if(eq<0)return;
    const key=line.slice(0,eq).trim();const parts=line.slice(eq+3).split(" ||| ");
    if(parts.length===3)m[key]=T(parts[0].trim(),parts[1].trim(),parts[2].trim());});
  return m;
})();
function emit(slug, spec){
  (spec.fields||[]).forEach(f=>(f.items||[]).forEach(it=>{const d=ITEM_DESC[slug+"."+f.code+"."+it.code];if(d)it.description=d;}));
  LANGS.forEach(lang=>{
    const file = slug+".template."+lang+".rae.json";
    fs.writeFileSync(path.join(OUT,file), JSON.stringify(resolve(spec,lang),null,2), "utf8");
  });
  console.log("écrit :", slug, "×", LANGS.length, "langues | champs perso :", (spec.fields||[]).length);
}

/* ============================================================ échelles */
const VRAIS4 = [
  {value:1,label:T("Minime","Minimal","Minima"),description:T(
    "La source de risque ne devrait pas agir, ou le mode opératoire est très difficile à mettre en œuvre.",
    "The risk source is unlikely to act, or the mode of operation is very hard to carry out.",
    "È improbabile che la fonte di rischio agisca, o il modo operativo è molto difficile da attuare.")},
  {value:2,label:T("Significative","Significant","Significativa"),description:T(
    "La source de risque pourrait agir ; le mode opératoire reste réalisable avec un effort modéré.",
    "The risk source could act; the mode of operation remains feasible with moderate effort.",
    "La fonte di rischio potrebbe agire; il modo operativo resta realizzabile con uno sforzo moderato.")},
  {value:3,label:T("Forte","Strong","Forte"),description:T(
    "La source de risque a de bonnes raisons d'agir et le mode opératoire est accessible.",
    "The risk source has good reasons to act and the mode of operation is accessible.",
    "La fonte di rischio ha buoni motivi per agire e il modo operativo è accessibile.")},
  {value:4,label:T("Maximale","Maximum","Massima"),description:T(
    "La source de risque va très probablement agir ; le mode opératoire est trivial.",
    "The risk source will very likely act; the mode of operation is trivial.",
    "La fonte di rischio agirà molto probabilmente; il modo operativo è banale.")}
];
const GRAV4_EBIOS = [
  {value:1,label:T("Mineure","Minor","Minore"),description:T(
    "Aucun impact opérationnel ou juridique notable ; gêne surmontable.",
    "No notable operational or legal impact; a surmountable nuisance.",
    "Nessun impatto operativo o giuridico rilevante; disagio superabile.")},
  {value:2,label:T("Significative","Significant","Significativa"),description:T(
    "Impact réel mais maîtrisable, sans conséquence durable.",
    "Real but manageable impact, with no lasting consequence.",
    "Impatto reale ma gestibile, senza conseguenze durature.")},
  {value:3,label:T("Grave","Serious","Grave"),description:T(
    "Impact important, difficilement réversible, sur l'activité ou les personnes.",
    "Major impact on operations or people, hard to reverse.",
    "Impatto importante, difficilmente reversibile, su attività o persone.")},
  {value:4,label:T("Critique","Critical","Critica"),description:T(
    "Impact majeur, potentiellement irréversible, mettant en cause la pérennité ou la sécurité.",
    "Major, potentially irreversible impact threatening viability or safety.",
    "Impatto grave, potenzialmente irreversibile, che mette a rischio la continuità o la sicurezza.")}
];
const critEbios = [
  {code:"faible",label:T("Faible","Low","Basso"),score_min:1,score_max:3,color:CRIT.green,acceptance:"acceptable",order:1,
   description:T("Risque faible : acceptable en l'état, à surveiller lors des revues.",
     "Low risk: acceptable as is, to be monitored during reviews.",
     "Rischio basso: accettabile così com'è, da monitorare nelle revisioni.")},
  {code:"modere",label:T("Modéré","Moderate","Moderato"),score_min:4,score_max:6,color:CRIT.yellow,acceptance:"tolerable",order:2,
   description:T("Risque modéré : tolérable sous conditions ; des mesures de réduction sont à envisager.",
     "Moderate risk: tolerable under conditions; reduction measures should be considered.",
     "Rischio moderato: tollerabile a condizioni; valutare misure di riduzione.")},
  {code:"eleve",label:T("Élevé","High","Elevato"),score_min:7,score_max:11,color:CRIT.orange,acceptance:"to_treat",order:3,
   description:T("Risque élevé : un traitement est attendu pour ramener le risque à un niveau acceptable.",
     "High risk: treatment is expected to bring the risk to an acceptable level.",
     "Rischio elevato: è previsto un trattamento per riportare il rischio a un livello accettabile.")},
  {code:"critique",label:T("Critique","Critical","Critico"),score_min:12,score_max:16,color:CRIT.red,acceptance:"unacceptable",order:4,
   description:T("Risque critique : inacceptable en l'état ; traitement prioritaire requis.",
     "Critical risk: unacceptable as is; priority treatment required.",
     "Rischio critico: inaccettabile così com'è; trattamento prioritario richiesto.")}
];

/* ============================================================ 1. EBIOS RM */
emit("ebios-rm", {
  meta:{
    title:T("Modèle EBIOS RM (ANSSI)","EBIOS RM template (ANSSI)","Modello EBIOS RM (ANSSI)"),
    description:T(
      "Squelette d'analyse inspiré d'**EBIOS Risk Manager** (ANSSI). Grille de vraisemblance × gravité, niveaux de risque et champs personnalisés préconfigurés.\n\nÀ compléter : valeurs métier et biens supports (atelier 1), sources de risque et objectifs visés (atelier 2), scénarios stratégiques (atelier 3) puis opérationnels (atelier 4), et le traitement (atelier 5).",
      "Analysis skeleton inspired by **EBIOS Risk Manager** (ANSSI). Likelihood × severity grid, risk levels and custom fields preconfigured.\n\nTo complete: business values and supporting assets (workshop 1), risk sources and target objectives (workshop 2), strategic scenarios (workshop 3) then operational ones (workshop 4), and treatment (workshop 5).",
      "Scheletro di analisi ispirato a **EBIOS Risk Manager** (ANSSI). Griglia verosimiglianza × gravità, livelli di rischio e campi personalizzati preconfigurati.\n\nDa completare: valori di business e beni di supporto (workshop 1), fonti di rischio e obiettivi (workshop 2), scenari strategici (workshop 3) e operativi (workshop 4), e il trattamento (workshop 5)."),
    methodology_reference:T("EBIOS Risk Manager (ANSSI)","EBIOS Risk Manager (ANSSI)","EBIOS Risk Manager (ANSSI)")},
  grid:{
    vertical_axis:{label:T("Vraisemblance","Likelihood","Verosimiglianza"),
      description:T("Possibilité que le scénario se réalise, au regard des sources de risque et des modes opératoires.",
        "Possibility that the scenario occurs, given risk sources and modes of operation.",
        "Possibilità che lo scenario si verifichi, viste le fonti di rischio e i modi operativi."),levels:VRAIS4},
    horizontal_axis:{label:T("Gravité","Severity","Gravità"),
      description:T("Ampleur des conséquences pour l'organisation et les personnes.",
        "Extent of consequences for the organisation and people.",
        "Entità delle conseguenze per l'organizzazione e le persone."),levels:GRAV4_EBIOS},
    score:{method:"product"}, criticality_levels:critEbios},
  fields:[
    {code:"referentiels",target:"analysis",type:"tags",multiple:true,order:1,
     label:T("Référentiels","Frameworks","Riferimenti"),
     items:[tag("ebios-rm",T("EBIOS RM","EBIOS RM","EBIOS RM"),"#3a63d6"),tag("iso-27005",T("ISO 27005","ISO 27005","ISO 27005"),"#4c7dff"),
            tag("rgpd",T("RGPD","GDPR","GDPR"),"#e25631"),tag("nis2",T("NIS2","NIS2","NIS2"),"#8e44ad"),tag("pssi",T("PSSI","ISSP","PSSI"),"#16a085")]},
    {code:"socle_securite",target:"analysis",type:"textarea",order:2,label:T("Socle de sécurité","Security baseline","Base di sicurezza"),
     description:T("Référentiels applicables, écarts identifiés et justification (atelier 1).",
       "Applicable frameworks, identified gaps and justification (workshop 1).",
       "Riferimenti applicabili, scostamenti individuati e giustificazione (workshop 1).")},
    {code:"type_scenario",target:"risk",type:"select",order:1,filterable:true,label:T("Type de scénario","Scenario type","Tipo di scenario"),
     items:[opt("strategique",T("Scénario stratégique","Strategic scenario","Scenario strategico")),opt("operationnel",T("Scénario opérationnel","Operational scenario","Scenario operativo"))]},
    {code:"source_risque",target:"risk",type:"tags",multiple:true,order:2,filterable:true,label:T("Source de risque","Risk source","Fonte di rischio"),
     items:[tag("etatique",T("Étatique","State-sponsored","Statale"),"#6c3483"),tag("cybercriminel",T("Cybercriminel","Cybercriminal","Cybercriminale"),"#c0392b"),
            tag("terroriste",T("Terroriste","Terrorist","Terrorista"),"#7b241c"),tag("activiste",T("Activiste idéologique","Ideological activist","Attivista ideologico"),"#d35400"),
            tag("officine",T("Officine spécialisée","Specialised firm","Struttura specializzata"),"#b7950b"),tag("amateur",T("Amateur","Amateur","Dilettante"),"#2980b9"),
            tag("vengeur",T("Vengeur","Avenger","Vendicatore"),"#a04000"),tag("initie",T("Initié malveillant","Malicious insider","Insider malevolo"),"#922b21"),
            tag("concurrent",T("Concurrent","Competitor","Concorrente"),"#1f618d")]},
    {code:"objectif_vise",target:"risk",type:"tags",multiple:true,order:3,filterable:true,label:T("Objectif visé","Target objective","Obiettivo"),
     items:[tag("espionnage",T("Espionnage","Espionage","Spionaggio"),"#6c3483"),tag("prepos",T("Pré-positionnement","Pre-positioning","Pre-posizionamento"),"#5d6d7e"),
            tag("entrave",T("Sabotage / entrave","Sabotage / disruption","Sabotaggio / ostruzione"),"#c0392b"),tag("influence",T("Influence","Influence","Influenza"),"#8e44ad"),
            tag("lucratif",T("Lucratif","Financial gain","Lucro"),"#b7950b"),tag("defi",T("Défi / amusement","Challenge / fun","Sfida / divertimento"),"#2980b9")]},
    {code:"valeur_metier",target:"risk",type:"text",order:4,label:T("Valeur métier visée","Targeted business value","Valore di business")},
    {code:"biens_supports",target:"risk",type:"tags",multiple:true,order:5,filterable:true,label:T("Biens supports","Supporting assets","Beni di supporto"),
     items:[tag("poste",T("Poste de travail","Workstation","Postazione di lavoro"),"#2e86de"),tag("serveur",T("Serveur / stockage","Server / storage","Server / storage"),"#117864"),
            tag("appli",T("Application","Application","Applicazione"),"#148f77"),tag("reseau",T("Réseau","Network","Rete"),"#1f618d"),
            tag("donnees",T("Données","Data","Dati"),"#7d6608"),tag("prestataire",T("Prestataire","Third party","Fornitore"),"#1abc9c"),
            tag("local",T("Site / local","Site / premises","Sito / locale"),"#b9770e"),tag("personne",T("Personne","Person","Persona"),"#af7ac5")]},
    {code:"socle",target:"measure",type:"select",order:1,filterable:true,label:T("Catégorie de sécurité","Security category","Categoria di sicurezza"),
     items:[opt("gouvernance",T("Gouvernance","Governance","Governance")),opt("protection",T("Protection","Protection","Protezione")),
            opt("defense",T("Défense","Defence","Difesa")),opt("resilience",T("Résilience","Resilience","Resilienza"))]},
    {code:"avancement",target:"measure",type:"progress",order:2,label:T("Avancement","Progress","Avanzamento"),palette:"red-orange-green",step:10},
    {code:"effet",target:"link",type:"tags",multiple:true,order:1,filterable:true,label:T("Effet attendu","Expected effect","Effetto atteso"),
     items:[tag("vraisemblance",T("Réduit la vraisemblance","Reduces likelihood","Riduce la verosimiglianza"),"#2471a3"),
            tag("gravite",T("Réduit la gravité","Reduces severity","Riduce la gravità"),"#b9770e")]},
    {code:"justification",target:"cotation",type:"textarea",order:1,label:T("Justification","Justification","Motivazione"),
     description:T("Justification de la cotation : choix de la vraisemblance et de la gravité.","Rationale for the assessment: choice of likelihood and severity.","Motivazione della valutazione: scelta di verosimiglianza e gravità.")},
    {code:"date_cotation",target:"cotation",type:"date",order:2,label:T("Date de cotation","Assessment date","Data di valutazione")}
  ]
});

/* ============================================================ 2. CNIL PIA */
const GRAV4_PIA = [
  {value:1,label:T("Négligeable","Negligible","Trascurabile"),description:T(
    "Les personnes ne seront pas impactées ou surmonteront quelques désagréments sans difficulté.",
    "Data subjects will not be affected or will overcome minor inconveniences without difficulty.",
    "Le persone non subiranno impatti o supereranno lievi disagi senza difficoltà.")},
  {value:2,label:T("Limitée","Limited","Limitata"),description:T(
    "Les personnes pourraient connaître des désagréments significatifs, surmontables malgré des difficultés.",
    "Data subjects may face significant inconveniences, surmountable despite difficulties.",
    "Le persone potrebbero subire disagi significativi, superabili nonostante alcune difficoltà.")},
  {value:3,label:T("Importante","Significant","Importante"),description:T(
    "Les personnes pourraient connaître des conséquences significatives, surmontables mais avec de réelles difficultés.",
    "Data subjects may face significant consequences, surmountable but with real difficulties.",
    "Le persone potrebbero subire conseguenze significative, superabili ma con reali difficoltà.")},
  {value:4,label:T("Maximale","Maximum","Massima"),description:T(
    "Les personnes pourraient connaître des conséquences significatives, voire irrémédiables, qu'elles pourraient ne pas surmonter.",
    "Data subjects may face significant, even irreversible consequences they might not overcome.",
    "Le persone potrebbero subire conseguenze significative, persino irreversibili, che potrebbero non superare.")}
];
const VRAIS4_PIA = [
  {value:1,label:T("Négligeable","Negligible","Trascurabile"),description:T("Il ne semble pas possible que la menace se réalise.","It does not seem possible for the threat to occur.","Non sembra possibile che la minaccia si realizzi.")},
  {value:2,label:T("Limitée","Limited","Limitata"),description:T("Il semble difficile pour les sources de risques de réaliser la menace.","It seems difficult for risk sources to carry out the threat.","Sembra difficile per le fonti di rischio realizzare la minaccia.")},
  {value:3,label:T("Importante","Significant","Importante"),description:T("Il semble possible pour les sources de risques de réaliser la menace.","It seems possible for risk sources to carry out the threat.","Sembra possibile per le fonti di rischio realizzare la minaccia.")},
  {value:4,label:T("Maximale","Maximum","Massima"),description:T("Il semble extrêmement facile pour les sources de risques de réaliser la menace.","It seems extremely easy for risk sources to carry out the threat.","Sembra estremamente facile per le fonti di rischio realizzare la minaccia.")}
];
const MATRIX_PIA = [[1,1,2,3],[1,2,2,3],[2,2,3,4],[3,3,4,4]];
const critPia = [
  {code:"negligeable",label:T("Négligeable","Negligible","Trascurabile"),score_min:1,score_max:1,color:CRIT.green,acceptance:"acceptable",order:1,
   description:T("Niveau de risque négligeable au sens de la méthode PIA.","Negligible risk level per the PIA method.","Livello di rischio trascurabile secondo il metodo PIA.")},
  {code:"limite",label:T("Limité","Limited","Limitato"),score_min:2,score_max:2,color:CRIT.yellow,acceptance:"acceptable",order:2,
   description:T("Niveau de risque limité au sens de la méthode PIA.","Limited risk level per the PIA method.","Livello di rischio limitato secondo il metodo PIA.")},
  {code:"important",label:T("Important","Significant","Importante"),score_min:3,score_max:3,color:CRIT.orange,acceptance:"tolerable",order:3,
   description:T("Niveau de risque important : des mesures de réduction sont attendues.","Significant risk level: reduction measures are expected.","Livello di rischio importante: sono attese misure di riduzione.")},
  {code:"maximal",label:T("Maximal","Maximum","Massimo"),score_min:4,score_max:4,color:CRIT.red,acceptance:"unacceptable",order:4,
   description:T("Niveau de risque maximal : le traitement ne peut être conduit en l'état.","Maximum risk level: the processing cannot be carried out as is.","Livello di rischio massimo: il trattamento non può essere svolto così com'è.")}
];
emit("cnil-pia", {
  meta:{
    title:T("Modèle AIPD — CNIL PIA","DPIA template — CNIL PIA","Modello DPIA — CNIL PIA"),
    description:T(
      "Squelette d'**Analyse d'Impact sur la Protection des Données** inspiré de la méthode **CNIL PIA**. Grille à quatre niveaux dont le niveau de risque est défini **par cellule** (et non par produit), et champs personnalisés propres à la démarche.\n\nÀ compléter : contexte et sous-traitants, puis pour chaque événement redouté (accès illégitime, modification non désirée, indisponibilité) les scénarios, leur cotation initiale et résiduelle, et le plan d'action.",
      "**Data Protection Impact Assessment** skeleton inspired by the **CNIL PIA** method. Four-level grid whose risk level is defined **per cell** (not by product), with custom fields specific to the approach.\n\nTo complete: context and processors, then for each feared event (illegitimate access, unwanted modification, unavailability) the scenarios, their initial and residual rating, and the action plan.",
      "Scheletro di **Valutazione d'Impatto sulla Protezione dei Dati** ispirato al metodo **CNIL PIA**. Griglia a quattro livelli il cui livello di rischio è definito **per cella** (non per prodotto), con campi personalizzati propri all'approccio.\n\nDa completare: contesto e responsabili del trattamento, poi per ogni evento temuto (accesso illegittimo, modifica indesiderata, indisponibilità) gli scenari, la valutazione iniziale e residua, e il piano d'azione."),
    methodology_reference:T("Méthode CNIL PIA (Privacy Impact Assessment)","CNIL PIA method (Privacy Impact Assessment)","Metodo CNIL PIA (Privacy Impact Assessment)")},
  grid:{
    vertical_axis:{label:T("Vraisemblance","Likelihood","Verosimiglianza"),
      description:T("Possibilité qu'un risque se réalise, au regard des vulnérabilités des supports et des sources de risques.",
        "Possibility that a risk occurs, given asset vulnerabilities and risk sources.",
        "Possibilità che un rischio si verifichi, viste le vulnerabilità dei supporti e le fonti di rischio."),levels:VRAIS4_PIA},
    horizontal_axis:{label:T("Gravité","Severity","Gravità"),
      description:T("Ampleur du risque, estimée au regard des impacts potentiels sur les personnes concernées.",
        "Extent of the risk, assessed against potential impacts on data subjects.",
        "Entità del rischio, stimata rispetto ai potenziali impatti sulle persone interessate."),levels:GRAV4_PIA},
    score:{method:"matrix",matrix:MATRIX_PIA}, criticality_levels:critPia},
  fields:[
    {code:"responsable_traitement",target:"analysis",type:"text",order:1,label:T("Responsable du traitement","Data controller","Titolare del trattamento")},
    {code:"sous_traitants",target:"analysis",type:"textarea",order:2,label:T("Sous-traitants","Processors","Responsabili del trattamento"),
     description:T("Sous-traitants au sens de l'article 28 du RGPD (ou équivalent), et objet de leur intervention.",
       "Processors within the meaning of Article 28 GDPR (or equivalent), and the purpose of their involvement.",
       "Responsabili del trattamento ai sensi dell'articolo 28 GDPR (o equivalente), e oggetto del loro intervento.")},
    {code:"referentiels",target:"analysis",type:"textarea",order:3,label:T("Référentiels applicables","Applicable frameworks","Riferimenti applicabili")},
    {code:"avis_dpo",target:"analysis",type:"textarea",order:4,label:T("Avis du DPO","DPO opinion","Parere del DPO")},
    {code:"mesures_existantes",target:"analysis",type:"textarea",order:5,label:T("Mesures existantes","Existing measures","Misure esistenti"),
     description:T("Catalogue des mesures déjà en place, tenues hors du registre des mesures (réservé aux actions du plan d'action).",
       "Catalogue of measures already in place, kept out of the measures register (reserved for action-plan items).",
       "Catalogo delle misure già in atto, tenute fuori dal registro delle misure (riservato alle azioni del piano d'azione).")},
    {code:"evenement_redoute",target:"risk",type:"select",order:1,required:true,filterable:true,label:T("Événement redouté","Feared event","Evento temuto"),
     items:[opt("acces",T("Accès illégitime à des données","Illegitimate access to data","Accesso illegittimo ai dati")),
            opt("modif",T("Modification non désirée de données","Unwanted modification of data","Modifica indesiderata dei dati")),
            opt("indispo",T("Indisponibilité ou disparition de données","Unavailability or loss of data","Indisponibilità o perdita di dati"))]},
    {code:"sources_risque",target:"risk",type:"tags",multiple:true,order:2,filterable:true,label:T("Sources de risque","Risk sources","Fonti di rischio"),
     items:[tag("interne-mal",T("Source interne malveillante","Malicious internal source","Fonte interna malevola"),"#922b21"),
            tag("interne-acc",T("Source interne accidentelle","Accidental internal source","Fonte interna accidentale"),"#e67e22"),
            tag("externe",T("Source externe","External source","Fonte esterna"),"#c0392b"),tag("prestataire",T("Prestataire","Third party","Fornitore"),"#1abc9c"),
            tag("environnement",T("Environnement / matériel","Environmental / hardware","Ambiente / hardware"),"#7f8c8d")]},
    {code:"supports",target:"risk",type:"tags",multiple:true,order:3,filterable:true,label:T("Supports concernés","Affected assets","Supporti interessati"),
     items:[tag("materiel",T("Matériel","Hardware","Hardware"),"#2e86de"),tag("logiciel",T("Logiciel","Software","Software"),"#148f77"),
            tag("canal-info",T("Canal informatique","Digital channel","Canale informatico"),"#1f618d"),tag("papier",T("Support papier","Paper","Supporto cartaceo"),"#b9770e"),
            tag("canal-papier",T("Canal papier","Paper channel","Canale cartaceo"),"#ca6f1e"),tag("personne",T("Personne","Person","Persona"),"#af7ac5")]},
    {code:"impacts",target:"risk",type:"tags",multiple:true,order:4,filterable:true,label:T("Impacts sur les personnes","Impacts on individuals","Impatti sulle persone"),
     items:[tag("corporel",T("Corporel","Physical","Fisico"),"#c0392b"),tag("materiel-imp",T("Matériel","Material","Materiale"),"#b7950b"),tag("moral",T("Moral","Moral","Morale"),"#6c3483")]},
    {code:"origine",target:"measure",type:"select",order:1,filterable:true,label:T("Origine","Origin","Origine"),
     items:[opt("complementaire",T("Mesure complémentaire","Additional measure","Misura aggiuntiva")),
            opt("ajustement",T("Ajustement d'une mesure existante","Adjustment of an existing measure","Adeguamento di una misura esistente")),
            opt("principe",T("Principe fondamental","Fundamental principle","Principio fondamentale"))]},
    {code:"bloquante",target:"measure",type:"boolean",order:2,filterable:true,label:T("Bloquante","Blocking","Bloccante"),
     description:T("Action à mettre en œuvre au plus vite : le traitement ne peut être conduit sans elle.",
       "Action to implement as soon as possible: the processing cannot proceed without it.",
       "Azione da attuare al più presto: il trattamento non può procedere senza di essa.")},
    {code:"effet",target:"link",type:"tags",multiple:true,order:1,filterable:true,label:T("Effet attendu","Expected effect","Effetto atteso"),
     items:[tag("vraisemblance",T("Réduit la vraisemblance","Reduces likelihood","Riduce la verosimiglianza"),"#2471a3"),
            tag("gravite",T("Réduit la gravité","Reduces severity","Riduce la gravità"),"#b9770e")]}
  ]
});

/* ============================================================ 3. ISO 27005 */
const VRAIS5 = [
  {value:1,label:T("Très faible","Very low","Molto bassa"),description:T("Réalisation très improbable dans la période considérée.","Very unlikely to occur within the period.","Molto improbabile nel periodo considerato.")},
  {value:2,label:T("Faible","Low","Bassa"),description:T("Réalisation peu probable.","Unlikely to occur.","Poco probabile.")},
  {value:3,label:T("Moyenne","Medium","Media"),description:T("Réalisation plausible.","Plausible occurrence.","Realizzazione plausibile.")},
  {value:4,label:T("Élevée","High","Alta"),description:T("Réalisation probable.","Likely occurrence.","Realizzazione probabile.")},
  {value:5,label:T("Très élevée","Very high","Molto alta"),description:T("Réalisation quasi certaine.","Almost certain occurrence.","Realizzazione quasi certa.")}
];
const IMPACT5 = [
  {value:1,label:T("Négligeable","Negligible","Trascurabile"),description:T("Conséquences insignifiantes pour l'organisation.","Insignificant consequences for the organisation.","Conseguenze insignificanti per l'organizzazione.")},
  {value:2,label:T("Faible","Low","Basso"),description:T("Conséquences mineures, absorbées sans difficulté.","Minor consequences, absorbed without difficulty.","Conseguenze minori, assorbite senza difficoltà.")},
  {value:3,label:T("Moyen","Medium","Medio"),description:T("Conséquences notables mais maîtrisables.","Notable but manageable consequences.","Conseguenze notevoli ma gestibili.")},
  {value:4,label:T("Important","Significant","Importante"),description:T("Conséquences sérieuses, difficilement réversibles.","Serious consequences, hard to reverse.","Conseguenze serie, difficilmente reversibili.")},
  {value:5,label:T("Critique","Critical","Critico"),description:T("Conséquences majeures, mettant en cause l'activité.","Major consequences, threatening operations.","Conseguenze gravi, che mettono a rischio l'attività.")}
];
const crit5 = [
  {code:"faible",label:T("Faible","Low","Basso"),score_min:1,score_max:4,color:CRIT.green,acceptance:"acceptable",order:1,
   description:T("Risque faible : acceptable, à surveiller.","Low risk: acceptable, to be monitored.","Rischio basso: accettabile, da monitorare.")},
  {code:"moyen",label:T("Moyen","Medium","Medio"),score_min:5,score_max:10,color:CRIT.yellow,acceptance:"tolerable",order:2,
   description:T("Risque moyen : tolérable sous conditions ; réduction à envisager.","Medium risk: tolerable under conditions; reduction to consider.","Rischio medio: tollerabile a condizioni; valutare la riduzione.")},
  {code:"eleve",label:T("Élevé","High","Elevato"),score_min:11,score_max:16,color:CRIT.orange,acceptance:"to_treat",order:3,
   description:T("Risque élevé : traitement attendu.","High risk: treatment expected.","Rischio elevato: trattamento previsto.")},
  {code:"critique",label:T("Critique","Critical","Critico"),score_min:17,score_max:25,color:CRIT.red,acceptance:"unacceptable",order:4,
   description:T("Risque critique : inacceptable en l'état ; traitement prioritaire.","Critical risk: unacceptable as is; priority treatment.","Rischio critico: inaccettabile così com'è; trattamento prioritario.")}
];
emit("iso-27005", {
  meta:{
    title:T("Modèle ISO/IEC 27005","ISO/IEC 27005 template","Modello ISO/IEC 27005"),
    description:T(
      "Squelette d'appréciation du risque inspiré d'**ISO/IEC 27005**. Grille vraisemblance × impact sur cinq niveaux (score = produit), et champs personnalisés orientés actifs, menaces et vulnérabilités.\n\nÀ compléter : périmètre et critères d'acceptation, identification des actifs, des menaces et vulnérabilités, estimation puis évaluation du risque, et choix des options de traitement.",
      "Risk assessment skeleton inspired by **ISO/IEC 27005**. Five-level likelihood × impact grid (score = product), with custom fields oriented towards assets, threats and vulnerabilities.\n\nTo complete: scope and acceptance criteria, identification of assets, threats and vulnerabilities, risk estimation then evaluation, and choice of treatment options.",
      "Scheletro di valutazione del rischio ispirato a **ISO/IEC 27005**. Griglia verosimiglianza × impatto su cinque livelli (punteggio = prodotto), con campi personalizzati orientati a beni, minacce e vulnerabilità.\n\nDa completare: ambito e criteri di accettazione, identificazione di beni, minacce e vulnerabilità, stima e valutazione del rischio, e scelta delle opzioni di trattamento."),
    methodology_reference:T("ISO/IEC 27005 — Gestion des risques liés à la sécurité de l'information","ISO/IEC 27005 — Information security risk management","ISO/IEC 27005 — Gestione dei rischi per la sicurezza delle informazioni")},
  grid:{
    vertical_axis:{label:T("Vraisemblance","Likelihood","Verosimiglianza"),
      description:T("Probabilité de réalisation du scénario de risque.","Probability that the risk scenario occurs.","Probabilità che lo scenario di rischio si verifichi."),levels:VRAIS5},
    horizontal_axis:{label:T("Impact","Impact","Impatto"),
      description:T("Conséquences pour l'organisation en cas de réalisation.","Consequences for the organisation if it occurs.","Conseguenze per l'organizzazione in caso di realizzazione."),levels:IMPACT5},
    score:{method:"product"}, criticality_levels:crit5},
  fields:[
    {code:"referentiels",target:"analysis",type:"tags",multiple:true,order:1,label:T("Référentiels","Frameworks","Riferimenti"),
     items:[tag("iso-27005",T("ISO 27005","ISO 27005","ISO 27005"),"#3a63d6"),tag("iso-27001",T("ISO 27001","ISO 27001","ISO 27001"),"#4c7dff"),
            tag("iso-27002",T("ISO 27002","ISO 27002","ISO 27002"),"#16a085"),tag("rgpd",T("RGPD","GDPR","GDPR"),"#e25631")]},
    {code:"perimetre",target:"analysis",type:"textarea",order:2,label:T("Périmètre","Scope","Ambito")},
    {code:"critere_acceptation",target:"analysis",type:"textarea",order:3,label:T("Critères d'acceptation du risque","Risk acceptance criteria","Criteri di accettazione del rischio")},
    {code:"actif",target:"risk",type:"text",order:1,label:T("Actif concerné","Affected asset","Bene interessato")},
    {code:"type_actif",target:"risk",type:"select",order:2,filterable:true,label:T("Type d'actif","Asset type","Tipo di bene"),
     items:[opt("primaire",T("Actif primaire (information, processus)","Primary asset (information, process)","Bene primario (informazione, processo)")),
            opt("support",T("Actif support (matériel, logiciel, réseau, personne, site)","Supporting asset (hardware, software, network, person, site)","Bene di supporto (hardware, software, rete, persona, sito)"))]},
    {code:"menace",target:"risk",type:"tags",multiple:true,order:3,filterable:true,label:T("Menace","Threat","Minaccia"),
     items:[tag("acces-na",T("Accès non autorisé","Unauthorised access","Accesso non autorizzato"),"#c0392b"),
            tag("compromission-info",T("Compromission d'informations","Compromise of information","Compromissione di informazioni"),"#922b21"),
            tag("defaillance",T("Défaillance technique","Technical failure","Guasto tecnico"),"#7f8c8d"),
            tag("actions-na",T("Actions non autorisées","Unauthorised actions","Azioni non autorizzate"),"#a04000"),
            tag("compromission-fct",T("Compromission de fonctions","Compromise of functions","Compromissione di funzioni"),"#6c3483"),
            tag("dommages",T("Dommages physiques","Physical damage","Danni fisici"),"#b9770e"),
            tag("naturel",T("Événement naturel","Natural event","Evento naturale"),"#16a085"),
            tag("perte-service",T("Perte de services essentiels","Loss of essential services","Perdita di servizi essenziali"),"#1f618d")]},
    {code:"vulnerabilite",target:"risk",type:"text",order:4,label:T("Vulnérabilité exploitée","Exploited vulnerability","Vulnerabilità sfruttata")},
    {code:"option_traitement",target:"risk",type:"select",order:5,filterable:true,label:T("Option de traitement","Treatment option","Opzione di trattamento"),
     items:[opt("reduire",T("Réduire (modifier)","Reduce (modify)","Ridurre (modificare)")),opt("accepter",T("Accepter (maintenir)","Accept (retain)","Accettare (mantenere)")),
            opt("eviter",T("Éviter (supprimer)","Avoid (remove)","Evitare (eliminare)")),opt("partager",T("Partager (transférer)","Share (transfer)","Condividere (trasferire)"))]},
    {code:"proprietaire_risque",target:"risk",type:"text",order:6,label:T("Propriétaire du risque","Risk owner","Titolare del rischio")},
    {code:"reference_controle",target:"measure",type:"text",order:1,label:T("Réf. mesure (ISO 27002)","Control ref. (ISO 27002)","Rif. controllo (ISO 27002)"),
     description:T("Référence de la mesure de sécurité applicable, p. ex. A.8.16.","Reference of the applicable security control, e.g. A.8.16.","Riferimento del controllo di sicurezza applicabile, es. A.8.16.")},
    {code:"avancement",target:"measure",type:"progress",order:2,label:T("Avancement","Progress","Avanzamento"),palette:"red-orange-green",step:10},
    {code:"effet",target:"link",type:"tags",multiple:true,order:1,filterable:true,label:T("Effet attendu","Expected effect","Effetto atteso"),
     items:[tag("vraisemblance",T("Réduit la vraisemblance","Reduces likelihood","Riduce la verosimiglianza"),"#2471a3"),
            tag("gravite",T("Réduit l'impact","Reduces impact","Riduce l'impatto"),"#b9770e")]},
    {code:"justification",target:"cotation",type:"textarea",order:1,label:T("Justification","Justification","Motivazione"),
     description:T("Justification de la cotation : choix de la vraisemblance et de la gravité.","Rationale for the assessment: choice of likelihood and severity.","Motivazione della valutazione: scelta di verosimiglianza e gravità.")},
    {code:"date_cotation",target:"cotation",type:"date",order:2,label:T("Date de cotation","Assessment date","Data di valutazione")}
  ]
});

/* ============================================================ 4. Générique */
const PROBA5 = [
  {value:1,label:T("Très faible","Very low","Molto bassa"),description:T("Réalisation très improbable.","Very unlikely.","Molto improbabile.")},
  {value:2,label:T("Faible","Low","Bassa"),description:T("Réalisation peu probable.","Unlikely.","Poco probabile.")},
  {value:3,label:T("Moyenne","Medium","Media"),description:T("Réalisation plausible.","Plausible.","Plausibile.")},
  {value:4,label:T("Élevée","High","Alta"),description:T("Réalisation probable.","Likely.","Probabile.")},
  {value:5,label:T("Très élevée","Very high","Molto alta"),description:T("Réalisation quasi certaine.","Almost certain.","Quasi certa.")}
];
const IMPACTG5 = [
  {value:1,label:T("Très faible","Very low","Molto basso"),description:T("Conséquences insignifiantes.","Insignificant consequences.","Conseguenze insignificanti.")},
  {value:2,label:T("Faible","Low","Basso"),description:T("Conséquences mineures.","Minor consequences.","Conseguenze minori.")},
  {value:3,label:T("Moyen","Medium","Medio"),description:T("Conséquences notables.","Notable consequences.","Conseguenze notevoli.")},
  {value:4,label:T("Élevé","High","Elevato"),description:T("Conséquences sérieuses.","Serious consequences.","Conseguenze serie.")},
  {value:5,label:T("Très élevé","Very high","Molto elevato"),description:T("Conséquences majeures.","Major consequences.","Conseguenze gravi.")}
];
emit("generique", {
  meta:{
    title:T("Modèle générique","Generic template","Modello generico"),
    description:T(
      "Squelette neutre : grille probabilité × impact sur cinq niveaux (score = produit) et quatre niveaux de criticité, **sans champ personnalisé imposé**. Point de départ pour une analyse de risques ne suivant pas une méthode particulière.",
      "Neutral skeleton: probability × impact grid over five levels (score = product) and four criticality levels, **with no imposed custom field**. A starting point for a risk analysis not following a specific method.",
      "Scheletro neutro: griglia probabilità × impatto su cinque livelli (punteggio = prodotto) e quattro livelli di criticità, **senza campi personalizzati imposti**. Punto di partenza per un'analisi dei rischi non legata a un metodo specifico."),
    methodology_reference:T("Analyse de risques — grille générique 5×5","Risk analysis — generic 5×5 grid","Analisi dei rischi — griglia generica 5×5")},
  grid:{
    vertical_axis:{label:T("Probabilité","Probability","Probabilità"),
      description:T("Probabilité de survenue du risque.","Probability of the risk occurring.","Probabilità che il rischio si verifichi."),levels:PROBA5},
    horizontal_axis:{label:T("Impact","Impact","Impatto"),
      description:T("Ampleur des conséquences en cas de survenue.","Extent of consequences if it occurs.","Entità delle conseguenze in caso di accadimento."),levels:IMPACTG5},
    score:{method:"product"}, criticality_levels:crit5},
  fields:[]
});

console.log("Terminé.");
