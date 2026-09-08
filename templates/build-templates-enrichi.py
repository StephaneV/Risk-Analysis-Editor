#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E14/E15 — construit les DEUX templates enrichis (objets) à partir des exemples enrichis :
- EBIOS RM objets  -> ebios-rm-objets.template.{fr,en,it}.rae.json
- AIPD/CNIL objets -> cnil-pia-objets.template.{fr,en,it}.rae.json
Contenu : grille + types d'objets + champs personnalisés + rapport pré-paramétré, SANS données.
Libellés multilingues {fr,en,it} : fr = exemple FR, en = exemple EN déjà produit, it = IT_AUTO
(récupéré des templates existants) + IT_DELTA (ci-dessous). Toute chaîne IT manquante est signalée.
"""
import json, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples"); TP = os.path.join(ROOT, "templates")
def load(p): return json.load(open(p, encoding="utf-8"))
def save(d, name):
    p = os.path.join(TP, name)
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(p, "a", encoding="utf-8").write("\n")
    print("écrit:", os.path.relpath(p, ROOT))

# ---- IT_AUTO : italien récupéré des templates existants (fr <-> it) ----
def harvest_it():
    IT = {}
    def put(a, b):
        if isinstance(a, str) and isinstance(b, str) and a.strip(): IT[a] = b
    for f in glob.glob(os.path.join(TP, "*.template.fr.rae.json")):
        base = os.path.basename(f).split(".template.")[0]
        itf = os.path.join(TP, base+".template.it.rae.json")
        if not os.path.exists(itf): continue
        fr = load(f); it = load(itf)
        for k in ("title", "description", "methodology_reference"):
            put(fr["metadata"].get(k), it["metadata"].get(k))
        for ax in ("vertical_axis", "horizontal_axis"):
            put(fr["grid"][ax].get("label"), it["grid"][ax].get("label"))
            for a, b in zip(fr["grid"][ax].get("levels", []), it["grid"][ax].get("levels", [])):
                put(a.get("label"), b.get("label"))
        for key in ("criticality", "criticality_levels"):
            for a, b in zip(fr["grid"].get(key, []), it["grid"].get(key, [])):
                put(a.get("label"), b.get("label"))
        for cf in fr.get("custom_fields", []):
            lab = cf.get("label") or {}; put(lab.get("fr"), lab.get("it"))
            hlp = cf.get("help") or {}; put(hlp.get("fr"), hlp.get("it"))
            for it2 in cf.get("items", []):
                l = it2.get("label") or {}; put(l.get("fr"), l.get("it"))
                de = it2.get("description") or {}; put(de.get("fr"), de.get("it"))
    return IT

# ---- IT_DELTA : traductions italiennes manuelles (structure des exemples enrichis) ----
IT_DELTA = {
 # ---- AIPD ----
 "AIPD (méthode CNIL) enrichie — SI d'un service de santé au travail":
   "DPIA (metodo CNIL) arricchita — SI di un servizio di medicina del lavoro",
 "Variante enrichie de l'exemple AIPD : le traitement est décrit sous forme d'OBJETS réutilisables suivant l'esprit de la méthode PIA de la CNIL — personnes concernées, données personnelles (dont données de santé sensibles), finalités et bases légales, sous-traitants (dont hébergeur HDS), supports et sources de risque. Chaque scénario de risque référence les données et supports concernés et ses sources de risque ; les mesures référencent les supports qu'elles protègent. Analyse de démonstration, illustrative et fictive, générée par IA (Claude Opus 4.8).":
   "Variante arricchita dell'esempio DPIA: il trattamento è descritto sotto forma di OGGETTI riutilizzabili secondo lo spirito del metodo PIA della CNIL — interessati, dati personali (compresi i dati sanitari sensibili), finalità e basi giuridiche, responsabili del trattamento (compreso l'hosting HDS), beni di supporto e fonti di rischio. Ogni scenario di rischio riferisce i dati e i beni coinvolti e le sue fonti di rischio; le misure riferiscono i beni che proteggono. Analisi dimostrativa, illustrativa e fittizia, generata dall'IA (Claude Opus 4.8).",
 "SI du service de santé au travail : logiciel métier de gestion des dossiers médicaux, messagerie, serveurs, postes de travail, imprimantes et supports papier":
   "SI del servizio di medicina del lavoro: software gestionale delle cartelle sanitarie, posta elettronica, server, postazioni di lavoro, stampanti e supporti cartacei",
 "Volet analyse de risques d'une AIPD, inspiré de la méthode PIA de la CNIL (RGPD art. 35)":
   "Parte di analisi dei rischi di una DPIA, ispirata al metodo PIA della CNIL (GDPR art. 35)",
 "Règlement général sur la protection des données, socle des obligations de traitement des données de santé des salariés":
   "Regolamento generale sulla protezione dei dati, base degli obblighi di trattamento dei dati sanitari dei dipendenti",
 "Méthode PIA (CNIL)": "Metodo PIA (CNIL)",
 "Méthode d'analyse d'impact de la CNIL, structurant l'appréciation des risques sur la vie privée des personnes concernées":
   "Metodo di valutazione d'impatto della CNIL, che struttura la valutazione dei rischi per la vita privata degli interessati",
 "Code du travail": "Codice del lavoro",
 "Dispositions du Code du travail encadrant la santé au travail et le suivi médical des salariés":
   "Disposizioni del Codice del lavoro che disciplinano la medicina del lavoro e la sorveglianza sanitaria dei dipendenti",
 "Secret médical": "Segreto medico",
 "Obligation légale de confidentialité protégeant les informations médicales relatives aux personnes concernées":
   "Obbligo legale di riservatezza a tutela delle informazioni mediche relative agli interessati",
 "Hébergeur HDS": "Hosting HDS",
 "Certification exigée pour héberger des données de santé, garantissant la sécurité et la confidentialité de l'hébergement":
   "Certificazione richiesta per l'hosting di dati sanitari, che garantisce la sicurezza e la riservatezza dell'hosting",
 "Logiciel métier (DMST)": "Software gestionale (cartella sanitaria)",
 "Messagerie": "Posta elettronica", "Serveurs": "Server", "Postes de travail": "Postazioni di lavoro",
 "Imprimantes & papier": "Stampanti e carta", "Sauvegardes": "Backup",
 "Finalités": "Finalità", "Personnes concernées": "Interessati", "Destinataires": "Destinatari",
 "Droits des personnes assurés": "Diritti degli interessati garantiti",
 "Information": "Informazione", "Accès": "Accesso", "Rectification": "Rettifica",
 "Opposition": "Opposizione", "Effacement": "Cancellazione", "Portabilité": "Portabilità", "Limitation": "Limitazione",
 "Modalités d'exercice des droits": "Modalità di esercizio dei diritti",
 "Avis des personnes concernées": "Parere degli interessati",
 "Décision de validation": "Decisione di convalida",
 "Validée": "Approvata", "Validée avec réserves": "Approvata con riserve",
 "À revoir": "Da rivedere", "Refusée": "Respinta",
 "Données concernées": "Dati coinvolti",
 "Atteinte au secret médical": "Violazione del segreto medico",
 "Événement redouté où la divulgation d'informations médicales rompt le secret médical des personnes concernées":
   "Evento temuto in cui la divulgazione di informazioni mediche viola il segreto medico degli interessati",
 "Atteinte à la vie privée": "Violazione della vita privata",
 "Atteinte à la vie privée des personnes concernées par l'exposition d'informations sensibles les concernant":
   "Violazione della vita privata degli interessati dovuta all'esposizione di informazioni sensibili che li riguardano",
 "Discrimination à l'emploi": "Discriminazione nel lavoro",
 "Usage détourné des données de santé conduisant à une discrimination à l'emploi des personnes concernées":
   "Uso improprio dei dati sanitari che porta a una discriminazione nel lavoro degli interessati",
 "Préjudice moral": "Danno morale",
 "Préjudice moral subi par les personnes concernées : stress, sentiment d'atteinte ou perte de confiance":
   "Danno morale subito dagli interessati: stress, senso di lesione o perdita di fiducia",
 "Perte de suivi médical": "Perdita della sorveglianza sanitaria",
 "Perte ou altération des données compromettant la continuité du suivi médical des personnes concernées":
   "Perdita o alterazione dei dati che compromette la continuità della sorveglianza sanitaria degli interessati",
 "Préjudice financier": "Danno economico",
 "Préjudice financier pour les personnes concernées, par exemple refus d'assurance ou d'emploi lié à leurs données":
   "Danno economico per gli interessati, ad esempio rifiuto di assicurazione o di impiego legato ai loro dati",
 "Nature de la mesure": "Natura della misura",
 "Juridique": "Giuridica",
 "Mesure de nature contractuelle ou réglementaire : clauses de confidentialité, engagements de conformité et encadrement de la sous-traitance":
   "Misura di natura contrattuale o normativa: clausole di riservatezza, impegni di conformità e disciplina del trattamento affidato a terzi",
 "Organisationnelle": "Organizzativa",
 "Mesure de gouvernance et de procédure : habilitations, sensibilisation du personnel et gestion des accès aux dossiers":
   "Misura di governance e di procedura: autorizzazioni, sensibilizzazione del personale e gestione degli accessi alle cartelle",
 "Technique": "Tecnica",
 "Mesure technologique protégeant les données de santé : chiffrement, journalisation, cloisonnement et contrôle d'accès":
   "Misura tecnologica a protezione dei dati sanitari: cifratura, registrazione dei log, segmentazione e controllo degli accessi",
 "Physique": "Fisica",
 "Mesure de sécurité physique protégeant locaux, dossiers et supports médicaux contre les accès non autorisés":
   "Misura di sicurezza fisica a protezione di locali, cartelle e supporti medici da accessi non autorizzati",
 "Objectif de sécurité": "Obiettivo di sicurezza",
 "Confidentialité": "Riservatezza",
 "Garantir que les données de santé ne sont accessibles qu'aux personnes dûment habilitées":
   "Garantire che i dati sanitari siano accessibili solo alle persone debitamente autorizzate",
 "Intégrité": "Integrità",
 "Préserver l'exactitude et l'intégrité des données de santé contre toute altération non autorisée":
   "Preservare l'esattezza e l'integrità dei dati sanitari da qualsiasi alterazione non autorizzata",
 "Disponibilité": "Disponibilità",
 "Assurer l'accès aux données de santé au moment voulu par les personnes autorisées":
   "Garantire l'accesso ai dati sanitari nel momento voluto dalle persone autorizzate",
 "Traçabilité": "Tracciabilità",
 "Conserver la trace des accès et actions sur les données de santé afin de les imputer":
   "Conservare la traccia degli accessi e delle azioni sui dati sanitari per poterli imputare",
 "Minimisation": "Minimizzazione",
 "Limiter la collecte et la conservation des données de santé au strict nécessaire à la finalité":
   "Limitare la raccolta e la conservazione dei dati sanitari allo stretto necessario alla finalità",
 "Droits des personnes": "Diritti degli interessati",
 "Permettre l'exercice effectif des droits des personnes concernées : information, accès, rectification et opposition":
   "Consentire l'esercizio effettivo dei diritti degli interessati: informazione, accesso, rettifica e opposizione",
 "Effet sur le risque": "Effetto sul rischio",
 "Mesure diminuant la probabilité que l'événement redouté se réalise":
   "Misura che riduce la probabilità che l'evento temuto si realizzi",
 "Mesure limitant l'ampleur des conséquences pour les personnes concernées si l'événement redouté survient":
   "Misura che limita l'entità delle conseguenze per gli interessati se l'evento temuto si verifica",
 "Détecte": "Rileva",
 "Mesure permettant de repérer la survenue de l'événement redouté afin de réagir":
   "Misura che consente di rilevare il verificarsi dell'evento temuto per potervi reagire",
 "Transfère": "Trasferisce",
 "Mesure reportant tout ou partie du risque vers un tiers, par assurance ou externalisation":
   "Misura che trasferisce in tutto o in parte il rischio a un terzo, tramite assicurazione o esternalizzazione",
 "Personne concernée": "Interessato",
 "Catégorie de personnes": "Categoria di persone",
 "Type": "Tipo",
 "Salarié / travailleur suivi": "Dipendente / lavoratore sorvegliato",
 "Candidat / embauche": "Candidato / assunzione",
 "Ancien travailleur": "Ex lavoratore",
 "Intérimaire / externe": "Interinale / esterno",
 "Personnel du service": "Personale del servizio",
 "Personnes vulnérables": "Persone vulnerabili", "Oui": "Sì", "Non": "No",
 "Volume approximatif": "Volume approssimativo",
 "Donnée personnelle": "Dato personale",
 "Catégorie de données": "Categoria di dati",
 "Nature": "Natura",
 "Identification": "Identificazione", "Santé": "Salute", "Vie professionnelle": "Vita professionale",
 "Connexion / journaux": "Connessione / log", "Vie personnelle": "Vita personale",
 "Sensibilité": "Sensibilità",
 "Ordinaire": "Ordinario", "Sensible (art. 9 RGPD)": "Sensibile (art. 9 GDPR)",
 "Perception particulière": "Percepito come sensibile",
 "Durée de conservation": "Periodo di conservazione",
 "Destinataires des données": "Destinatari dei dati",
 "Origine des données": "Origine dei dati",
 "Collectée auprès de la personne": "Raccolto presso la persona",
 "Obtenue d'un tiers": "Ottenuto da un terzo",
 "Produite par observation / examen": "Prodotto tramite osservazione / esame",
 "Justification de la minimisation": "Giustificazione della minimizzazione",
 "Finalité": "Finalità",
 "Base légale": "Base giuridica",
 "Obligation légale": "Obbligo legale", "Mission d'intérêt public": "Compito di interesse pubblico",
 "Contrat": "Contratto", "Consentement": "Consenso", "Intérêt légitime": "Legittimo interesse",
 "Description": "Descrizione",
 "Données utilisées": "Dati utilizzati",
 "Sous-traitants impliqués": "Responsabili del trattamento coinvolti",
 "Nécessité & proportionnalité": "Necessità e proporzionalità",
 "Sous-traitant": "Responsabile del trattamento",
 "Prestation": "Prestazione",
 "Hébergeur de données de santé (HDS) certifié": "Hosting di dati sanitari (HDS) certificato",
 "Localisation / transferts": "Ubicazione / trasferimenti",
 "Garanties (art. 28 RGPD)": "Garanzie (art. 28 GDPR)",
 "Données confiées": "Dati affidati",
 "Transfert hors-UE": "Trasferimento extra-UE",
 "Support": "Bene di supporto",
 "Papier": "Carta", "Personnel": "Personale", "Local": "Locali", "Canal": "Canale",
 "Responsable": "Responsabile",
 "Données portées": "Dati veicolati",
 "Opérateur / hébergeur": "Operatore / hosting",
 "Finalités servies": "Finalità servite",
 "Catégorie": "Categoria",
 "Interne — malveillante": "Interna — dolosa", "Interne — accidentelle": "Interna — accidentale",
 "Externe — humaine": "Esterna — umana", "Source non humaine": "Fonte non umana",
 "Motivation / mode opératoire": "Motivazione / modus operandi",
 "Pertinence": "Pertinenza",
 "1 — Faible": "1 — Bassa", "2 — Modéré": "2 — Moderata", "3 — Fort": "3 — Alta", "4 — Maximal": "4 — Massima",
 "Destinataire": "Destinatario",
 "Service interne / équipe pluridisciplinaire": "Servizio interno / squadra multidisciplinare",
 "Tiers autorisé": "Terzo autorizzato",
 "Autorité / organisme public": "Autorità / ente pubblico",
 "Autre responsable de traitement": "Altro titolare del trattamento",
 "Finalité de la transmission": "Finalità della trasmissione",
 "Données reçues": "Dati ricevuti",
 "Localisation": "Ubicazione",
 "Union européenne / EEE": "Unione europea / SEE",
 "Hors UE — pays adéquat": "Extra-UE — paese adeguato",
 "Hors UE — garanties appropriées": "Extra-UE — garanzie adeguate",
 "Garanties de transfert (hors-UE)": "Garanzie di trasferimento (extra-UE)",
 # ---- EBIOS ----
 "EBIOS RM enrichi — Système d'information de gestion":
   "EBIOS RM arricchito — Sistema informativo gestionale",
 "Variante enrichie de l'exemple EBIOS RM : le socle (atelier 1) et l'écosystème sont modélisés sous forme d'OBJETS réutilisables — valeurs métier (avec besoins DICP), biens supports (rattachés aux valeurs métier soutenues), événements redoutés (ciblant une valeur métier), parties prenantes de l'écosystème et sources de risque. Les scénarios de risque et les mesures référencent ces objets (valeurs métier impactées, événements, sources, parties prenantes, biens supports protégés). Analyse de démonstration, illustrative et fictive, générée par IA (Claude Opus 4.8).":
   "Variante arricchita dell'esempio EBIOS RM: la base di sicurezza (workshop 1) e l'ecosistema sono modellati sotto forma di OGGETTI riutilizzabili — valori aziendali (con esigenze DICP), beni di supporto (collegati ai valori aziendali sostenuti), eventi temuti (che colpiscono un valore aziendale), parti interessate dell'ecosistema e fonti di rischio. Gli scenari di rischio e le misure riferiscono questi oggetti (valori aziendali impattati, eventi, fonti, parti interessate, beni di supporto protetti). Analisi dimostrativa, illustrativa e fittizia, generata dall'IA (Claude Opus 4.8).",
 "SI de gestion — services numériques critiques (métier, hébergement, postes, interconnexions partenaires)":
   "SI gestionale — servizi digitali critici (business, hosting, postazioni, interconnessioni con partner)",
 "Inspiré d'EBIOS RM (ANSSI) et d'ISO 27005": "Ispirato a EBIOS RM (ANSSI) e ISO 27005",
 "Méthode EBIOS Risk Manager de l'ANSSI pour apprécier et traiter les risques numériques par scénarios stratégiques et opérationnels":
   "Metodo EBIOS Risk Manager dell'ANSSI per valutare e trattare i rischi digitali tramite scenari strategici e operativi",
 "Norme internationale de gestion des risques liés à la sécurité de l'information, complémentaire à l'ISO 27001":
   "Norma internazionale di gestione dei rischi per la sicurezza delle informazioni, complementare alla ISO 27001",
 "Règlement européen encadrant le traitement des données à caractère personnel et les obligations de protection associées":
   "Regolamento europeo che disciplina il trattamento dei dati personali e i relativi obblighi di protezione",
 "Directive européenne renforçant la cybersécurité des entités essentielles et importantes et leurs obligations de gestion des risques":
   "Direttiva europea che rafforza la cibersicurezza dei soggetti essenziali e importanti e i loro obblighi di gestione dei rischi",
 "Politique de sécurité du système d'information définissant les règles et objectifs de sécurité de l'organisation":
   "Politica di sicurezza del sistema informativo che definisce le regole e gli obiettivi di sicurezza dell'organizzazione",
 "SI métier": "SI di business", "Hébergement": "Hosting", "Interconnexions partenaires": "Interconnessioni con partner",
 "Socle de sécurité de référence": "Base di sicurezza di riferimento",
 "Recevabilité de l'étude": "Ammissibilità dello studio",
 "Valeurs métier impactées": "Valori aziendali impattati",
 "Biens supports concernés": "Beni di supporto coinvolti",
 "Événements redoutés": "Eventi temuti",
 "Impacts redoutés": "Impatti temuti",
 "Financier": "Economico",
 "Pertes financières directes ou indirectes : fraude, interruption d'activité, sanctions ou coûts de remédiation":
   "Perdite economiche dirette o indirette: frode, interruzione dell'attività, sanzioni o costi di rimedio",
 "Juridique / RGPD": "Giuridico / GDPR",
 "Conséquences légales et réglementaires, notamment sanctions RGPD, contentieux ou manquements contractuels":
   "Conseguenze legali e normative, in particolare sanzioni GDPR, contenziosi o inadempienze contrattuali",
 "Réputation": "Reputazione",
 "Atteinte à l'image et à la confiance des clients, partenaires et du public envers l'organisation":
   "Danno all'immagine e alla fiducia di clienti, partner e pubblico verso l'organizzazione",
 "Opérationnel": "Operativo",
 "Perturbation des activités et processus métier : indisponibilité, dégradation de service ou perte de production":
   "Perturbazione delle attività e dei processi aziendali: indisponibilità, degrado del servizio o perdita di produzione",
 "Humain": "Umano",
 "Atteinte à la sécurité ou à l'intégrité des personnes, incluant les risques pour la santé et la sûreté":
   "Lesione della sicurezza o dell'integrità delle persone, compresi i rischi per la salute e l'incolumità",
 "Données personnelles": "Dati personali",
 "Compromission de données personnelles : divulgation, altération ou perte affectant les personnes concernées":
   "Compromissione di dati personali: divulgazione, alterazione o perdita che colpisce gli interessati",
 "Niveau de risque (source)": "Livello di rischio (fonte)",
 "Parties prenantes": "Parti interessate",
 "Fonction de sécurité": "Funzione di sicurezza",
 "Identifier": "Identificare",
 "Comprendre le contexte, les actifs et les risques pour gouverner la cybersécurité (fonction Identify du NIST CSF)":
   "Comprendere il contesto, gli asset e i rischi per governare la cibersicurezza (funzione Identify del NIST CSF)",
 "Protéger": "Proteggere",
 "Mettre en place les mesures de protection limitant l'impact d'un incident (fonction Protect du NIST CSF)":
   "Attuare le misure di protezione che limitano l'impatto di un incidente (funzione Protect del NIST CSF)",
 "Détecter": "Rilevare",
 "Identifier rapidement la survenue d'un événement de cybersécurité (fonction Detect du NIST CSF)":
   "Individuare rapidamente il verificarsi di un evento di cibersicurezza (funzione Detect del NIST CSF)",
 "Répondre": "Rispondere",
 "Agir face à un incident détecté pour en contenir et réduire les effets (fonction Respond du NIST CSF)":
   "Agire di fronte a un incidente rilevato per contenerne e ridurne gli effetti (funzione Respond del NIST CSF)",
 "Rétablir": "Ripristinare",
 "Restaurer les capacités et services altérés par un incident (fonction Recover du NIST CSF)":
   "Ripristinare le capacità e i servizi compromessi da un incidente (funzione Recover del NIST CSF)",
 "Domaine": "Ambito",
 "Mesure reposant sur des dispositifs technologiques : chiffrement, cloisonnement, journalisation ou contrôle d'accès":
   "Misura basata su dispositivi tecnologici: cifratura, segmentazione, registrazione dei log o controllo degli accessi",
 "Organisationnel": "Organizzativo",
 "Mesure relevant de la gouvernance et des procédures : politiques, sensibilisation, gestion des rôles et responsabilités":
   "Misura di governance e di procedura: politiche, sensibilizzazione, gestione di ruoli e responsabilità",
 "Mesure de sécurité physique protégeant locaux, équipements et supports contre les accès et sinistres":
   "Misura di sicurezza fisica a protezione di locali, apparecchiature e supporti da accessi e sinistri",
 "Mesure de nature contractuelle ou réglementaire : clauses, engagements de conformité et obligations de sous-traitance":
   "Misura di natura contrattuale o normativa: clausole, impegni di conformità e obblighi verso i fornitori",
 "Mesure diminuant la probabilité qu'un scénario de risque se réalise":
   "Misura che riduce la probabilità che uno scenario di rischio si realizzi",
 "Mesure limitant l'ampleur des conséquences si le scénario de risque se produit":
   "Misura che limita l'entità delle conseguenze se lo scenario di rischio si verifica",
 "Mesure permettant de repérer la survenue du scénario de risque afin de réagir":
   "Misura che consente di rilevare il verificarsi dello scenario di rischio per potervi reagire",
 "Valeur métier": "Valore aziendale",
 "Nom": "Nome", "Processus": "Processo",
 "Entité / dépositaire": "Entità / depositario",
 "Preuve / Traçabilité": "Prova / Tracciabilità",
 "Bien support": "Bene di supporto",
 "Organisation": "Organizzazione",
 "Valeurs métier soutenues": "Valori aziendali sostenuti",
 "Valeur métier ciblée": "Valore aziendale preso di mira",
 "Critères de sécurité impactés": "Criteri di sicurezza impattati",
 "Type d'impact": "Tipo di impatto",
 "Réglementaire": "Normativo", "Réputationnel": "Reputazionale",
 "Exigence du socle de sécurité": "Requisito della base di sicurezza",
 "Exigence": "Requisito", "Statut": "Stato",
 "Appliqué": "Applicato", "Partiel": "Parziale", "Non appliqué": "Non applicato",
 "Référence": "Riferimento", "Écart constaté": "Scostamento rilevato", "Remédiation": "Rimedio",
 "Profil": "Profilo",
 "Crime organisé": "Criminalità organizzata", "Interne malveillant": "Insider doloso",
 "Motivation": "Motivazione", "Ressources": "Risorse",
 "Niveau de motivation": "Livello di motivazione", "Niveau d'activité": "Livello di attività",
 "Pertinence (SR/OV)": "Pertinenza (FR/OP)", "Niveau de pertinence": "Livello di pertinenza",
 "Source retenue": "Fonte selezionata", "Justification de la décision": "Motivazione della decisione",
 "Partie prenante de l'écosystème": "Parte interessata dell'ecosistema",
 "Client": "Cliente", "Fournisseur": "Fornitore", "Partenaire": "Partner", "Autorité": "Autorità",
 "Dépendance": "Dipendenza", "Fort": "Alto", "Pénétration": "Penetrazione",
 "Maturité cyber": "Maturità cyber", "Confiance": "Fiducia",
 "Niveau de menace": "Livello di minaccia", "Zone": "Zona",
 "Intitulé": "Titolo",
 "Parties prenantes de l'écosystème": "Parti interessate dell'ecosistema",
 "Chemin d'attaque": "Percorso d'attacco", "Écosystème concerné": "Ecosistema coinvolto",
 "Mesures sur l'écosystème": "Misure sull'ecosistema",
 "Réduire": "Ridurre", "Partager": "Condividere", "Éviter": "Evitare", "Accepter": "Accettare",
 "Gravité retenue": "Gravità adottata",
 "Mode opératoire": "Modus operandi", "Séquence MITRE ATT&CK": "Sequenza MITRE ATT&CK",
 "Faisabilité": "Fattibilità", "Difficile": "Difficile",
 "Vraisemblance globale": "Verosimiglianza complessiva",
 "Peu vraisemblable": "Poco verosimile", "Vraisemblable": "Verosimile",
 "Très vraisemblable": "Molto verosimile", "Quasi-certain": "Quasi certo",
 "Maillon limitant": "Anello limitante", "Niveau de risque": "Livello di rischio",
}

# ---- construction ----
TEXTATTR = {"text", "textarea"}
MISSING = set()

def build(method_fr, method_en, base_out, IT, META3):
    fr = load(os.path.join(EX, method_fr)); en = load(os.path.join(EX, method_en))
    def it_of(s):
        if not isinstance(s, str) or not s.strip(): return s
        if s in IT: return IT[s]
        MISSING.add(s); return s
    # index EN par code
    en_ot = {o["code"]: o for o in en.get("object_types", [])}
    en_cf = {f["code"]: f for f in en.get("custom_fields", [])}
    def ml(fr_lbl, en_lbl):   # libellé multilingue {fr,en,it}
        f = (fr_lbl or {}).get("fr") if isinstance(fr_lbl, dict) else None
        e = (en_lbl or {}).get("en") if isinstance(en_lbl, dict) else None
        return {"fr": f, "en": e, "it": it_of(f)} if f is not None else fr_lbl

    # custom_fields multilingues
    cfs = []
    for f in fr.get("custom_fields", []):
        g = en_cf.get(f["code"], {})
        nf = json.loads(json.dumps(f))
        if f.get("label"): nf["label"] = ml(f.get("label"), g.get("label"))
        if f.get("help"): nf["help"] = ml(f.get("help"), g.get("help"))
        gi = g.get("items", [])
        for i, it2 in enumerate(nf.get("items", [])):
            h = gi[i] if i < len(gi) else {}
            if it2.get("label"): it2["label"] = ml(it2.get("label"), h.get("label"))
            if it2.get("description"): it2["description"] = ml(it2.get("description"), h.get("description"))
        cfs.append(nf)

    # object_types multilingues
    ots = []
    for o in fr.get("object_types", []):
        g = en_ot.get(o["code"], {}); ga = {a["code"]: a for a in g.get("attributes", [])}
        no = json.loads(json.dumps(o))
        if o.get("label"): no["label"] = ml(o.get("label"), g.get("label"))
        for a in no.get("attributes", []):
            h = ga.get(a["code"], {})
            if a.get("label"): a["label"] = ml(a.get("label"), h.get("label"))
            hi = h.get("items", [])
            for i, it2 in enumerate(a.get("items", [])):
                hh = hi[i] if i < len(hi) else {}
                if it2.get("label"): it2["label"] = ml(it2.get("label"), hh.get("label"))
                if it2.get("description"): it2["description"] = ml(it2.get("description"), hh.get("description"))
        ots.append(no)

    report = (fr.get("extensions", {}).get("display", {}) or {}).get("report")

    def grid_for(src, lang):
        g = json.loads(json.dumps(src["grid"]))
        if lang == "it":
            for ax in ("vertical_axis", "horizontal_axis"):
                a = g.get(ax, {})
                if a.get("label"): a["label"] = it_of(a["label"])
                for lv in a.get("levels", []):
                    if lv.get("label"): lv["label"] = it_of(lv["label"])
            for key in ("criticality", "criticality_levels"):
                for c in g.get(key, []):
                    if c.get("label"): c["label"] = it_of(c["label"])
        return g

    src_by_lang = {"fr": fr, "en": en}
    for lang in ("fr", "en", "it"):
        meta = {
            "title": META3["title"][lang],
            "description": META3["description"][lang],
            "author": "", "organization": "", "scope": "",
            "methodology_reference": META3["methodology_reference"][lang],
            "revision": "1.0", "status": "draft", "language": lang, "kind": "template",
        }
        d = {"format": "risk-analysis-editor", "version": "1.0", "metadata": meta,
             "grid": grid_for(src_by_lang.get(lang, fr), lang),
             "custom_fields": json.loads(json.dumps(cfs)),
             "custom": {},
             "object_types": json.loads(json.dumps(ots)),
             "objects": [], "risks": [], "measures": [], "treatments": []}
        if report: d["extensions"] = {"display": {"report": json.loads(json.dumps(report))}}
        save(d, f"{base_out}.template.{lang}.rae.json")

META_EBIOS = {
 "title": {"fr": "Modèle EBIOS RM enrichi (objets)", "en": "Enriched EBIOS RM template (objects)",
           "it": "Modello EBIOS RM arricchito (oggetti)"},
 "description": {
   "fr": "Squelette d'analyse **EBIOS RM (ANSSI)** avec **types d'objets** et **champs personnalisés** préconfigurés (valeurs métier, biens supports, événements redoutés, socle de sécurité, sources de risque, parties prenantes, scénarios stratégiques et opérationnels) et un **rapport pré-paramétré**.\n\nÀ compléter : instances d'objets (ateliers 1–4), puis risques, mesures et liens (traitement, atelier 5).",
   "en": "**EBIOS RM (ANSSI)** analysis skeleton with preconfigured **object types** and **custom fields** (business values, supporting assets, feared events, security baseline, risk sources, stakeholders, strategic and operational scenarios) and a **preconfigured report**.\n\nTo complete: object instances (workshops 1–4), then risks, measures and links (treatment, workshop 5).",
   "it": "Scheletro di analisi **EBIOS RM (ANSSI)** con **tipi di oggetti** e **campi personalizzati** preconfigurati (valori aziendali, beni di supporto, eventi temuti, base di sicurezza, fonti di rischio, parti interessate, scenari strategici e operativi) e un **report preconfigurato**.\n\nDa completare: istanze di oggetti (workshop 1–4), poi rischi, misure e collegamenti (trattamento, workshop 5)."},
 "methodology_reference": {"fr": "EBIOS Risk Manager (ANSSI)", "en": "EBIOS Risk Manager (ANSSI)",
                           "it": "EBIOS Risk Manager (ANSSI)"},
}
META_CNIL = {
 "title": {"fr": "Modèle AIPD (CNIL PIA) enrichi (objets)", "en": "Enriched DPIA (CNIL PIA) template (objects)",
           "it": "Modello DPIA (CNIL PIA) arricchito (oggetti)"},
 "description": {
   "fr": "Squelette d'**analyse d'impact (AIPD / PIA CNIL)** avec **types d'objets** et **champs personnalisés** préconfigurés (personnes concernées, données personnelles, finalités, sous-traitants, destinataires, supports, sources de risque) et un **rapport pré-paramétré**.\n\nÀ compléter : instances d'objets (contexte), puis risques, mesures et liens (traitement).",
   "en": "**Data protection impact assessment (DPIA / CNIL PIA)** skeleton with preconfigured **object types** and **custom fields** (data subjects, personal data, purposes, processors, recipients, supporting assets, risk sources) and a **preconfigured report**.\n\nTo complete: object instances (context), then risks, measures and links (treatment).",
   "it": "Scheletro di **valutazione d'impatto (DPIA / CNIL PIA)** con **tipi di oggetti** e **campi personalizzati** preconfigurati (interessati, dati personali, finalità, responsabili del trattamento, destinatari, beni di supporto, fonti di rischio) e un **report preconfigurato**.\n\nDa completare: istanze di oggetti (contesto), poi rischi, misure e collegamenti (trattamento)."},
 "methodology_reference": {"fr": "Méthode PIA de la CNIL (RGPD art. 35)", "en": "CNIL PIA method (GDPR art. 35)",
                           "it": "Metodo PIA della CNIL (GDPR art. 35)"},
}

if __name__ == "__main__":
    IT = harvest_it(); IT.update(IT_DELTA)
    print("IT total (auto+delta):", len(IT))
    build("demo-ebios-rm-systeme-d-information-objets-enrichi.rae.json",
          "demo-ebios-rm-information-system-enriched.rae.json", "ebios-rm-objets", IT, META_EBIOS)
    build("demo-aipd-sst-objets-enrichi.rae.json", "demo-dpia-ohs-enriched.rae.json", "cnil-pia-objets", IT, META_CNIL)
    if MISSING:
        print("\n!!! IT MANQUANT (%d) :" % len(MISSING))
        for s in sorted(MISSING): print("   ", s)
    else:
        print("Italien complet : aucune chaîne manquante.")
