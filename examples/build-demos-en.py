#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Traduction EN des démos enrichies (E11/E12). Réutilise les traductions EN existantes des bases
(appariement FR/EN par structure) et complète par un dictionnaire pour le delta (couche objets +
enrichissements). Écrit de NOUVEAUX fichiers EN dans examples/. Toute chaîne non couverte est
signalée (MISSING) — la traduction doit être exhaustive."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples")
TEXT_TYPES = {"text", "textarea"}

def load(n): return json.load(open(os.path.join(EX, n), encoding="utf-8"))
def save(d, n):
    p = os.path.join(EX, n)
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(p, "a", encoding="utf-8").write("\n")
    print("écrit:", os.path.relpath(p, ROOT))

def pair(frbase, enbase):
    """Dict FR->EN par appariement structurel d'une base FR et de sa traduction EN."""
    fr = load(frbase); en = load(enbase); M = {}
    def put(a, b):
        if isinstance(a, str) and isinstance(b, str) and a.strip(): M[a] = b
    for k in ("title", "scope", "methodology_reference", "description"):
        put(fr["metadata"].get(k), en["metadata"].get(k))
    for ax in ("vertical_axis", "horizontal_axis"):
        put(fr["grid"][ax].get("label"), en["grid"][ax].get("label"))
        for a, b in zip(fr["grid"][ax].get("levels", []), en["grid"][ax].get("levels", [])):
            put(a.get("label"), b.get("label"))
    for key in ("criticality", "criticality_levels"):
        for a, b in zip(fr["grid"].get(key, []), en["grid"].get(key, [])):
            put(a.get("label"), b.get("label"))
    for a, b in zip(fr.get("risks", []), en.get("risks", [])):
        for k in ("label", "category", "description", "comment"): put(a.get(k), b.get(k))
    for a, b in zip(fr.get("measures", []), en.get("measures", [])):
        for k in ("label", "description", "comment"): put(a.get(k), b.get(k))
    for a, b in zip(fr.get("treatments", []), en.get("treatments", [])):
        put(a.get("comment"), b.get("comment"))
    encf = {f["code"]: f for f in en.get("custom_fields", [])}
    for f in fr.get("custom_fields", []):
        g = encf.get(f["code"])
        if not g: continue
        put((f.get("label") or {}).get("fr"), (g.get("label") or {}).get("en"))
        put((f.get("help") or {}).get("fr"), (g.get("help") or {}).get("en"))
        for ia, ib in zip(f.get("items", []), g.get("items", [])):
            put((ia.get("label") or {}).get("fr"), (ib.get("label") or {}).get("en"))
            put((ia.get("description") or {}).get("fr"), (ib.get("description") or {}).get("en"))
    return M

MISSING = set()
def translate_file(src, dst, extra):
    d = load(src)
    T = dict(extra)  # combined dict passed in
    def tr(s):
        if not isinstance(s, str) or not s.strip(): return s
        if s in T: return T[s]
        MISSING.add(s); return s
    def loc(lbl):
        """Convertit un libellé localisé {fr:...} (ou {fr,en,...}) en {en: traduction}."""
        if isinstance(lbl, dict) and "fr" in lbl:
            return {"en": tr(lbl["fr"])}
        return lbl
    # metadata
    m = d.get("metadata", {})
    for k in ("title", "description", "scope", "methodology_reference"):
        if m.get(k): m[k] = tr(m[k])
    m["language"] = "en"
    # grid
    g = d.get("grid", {})
    for ax in ("vertical_axis", "horizontal_axis"):
        a = g.get(ax, {})
        if a.get("label"): a["label"] = tr(a["label"])
        for lv in a.get("levels", []):
            if lv.get("label"): lv["label"] = tr(lv["label"])
    for key in ("criticality", "criticality_levels"):
        for c in g.get(key, []):
            if c.get("label"): c["label"] = tr(c["label"])
    # custom_fields
    cf_by_t = {}
    for f in d.get("custom_fields", []):
        cf_by_t.setdefault(f.get("target"), {})[f["code"]] = f.get("type")
        if f.get("label"): f["label"] = loc(f["label"])
        if f.get("help"): f["help"] = loc(f["help"])
        for it in f.get("items", []):
            if it.get("label"): it["label"] = loc(it["label"])
            if it.get("description"): it["description"] = loc(it["description"])
    # object_types
    ot_types = {}
    for ot in d.get("object_types", []):
        if ot.get("label"): ot["label"] = loc(ot["label"])
        at = {}
        for a in ot.get("attributes", []):
            at[a["code"]] = a.get("type")
            if a.get("label"): a["label"] = loc(a["label"])
            for it in a.get("items", []):
                if it.get("label"): it["label"] = loc(it["label"])
                if it.get("description"): it["description"] = loc(it["description"])
        ot_types[ot["code"]] = at
    # objects values (texte)
    for o in d.get("objects", []):
        at = ot_types.get(o.get("type"), {})
        for c in list((o.get("values") or {}).keys()):
            if at.get(c) in TEXT_TYPES: o["values"][c] = tr(o["values"][c])
    # risks
    rt = cf_by_t.get("risk", {}); ct = cf_by_t.get("cotation", {})
    for r in d.get("risks", []):
        for k in ("label", "category", "description", "comment"):
            if r.get(k): r[k] = tr(r[k])
        for c in list((r.get("custom") or {}).keys()):
            if rt.get(c) in TEXT_TYPES: r["custom"][c] = tr(r["custom"][c])
        for ph in ("initial_assessment", "residual_assessment"):
            cu = (r.get(ph) or {}).get("custom") or {}
            for c in list(cu.keys()):
                if ct.get(c) in TEXT_TYPES: cu[c] = tr(cu[c])
    # measures
    mt = cf_by_t.get("measure", {})
    for x in d.get("measures", []):
        for k in ("label", "description", "comment"):
            if x.get(k): x[k] = tr(x[k])
        for c in list((x.get("custom") or {}).keys()):
            if mt.get(c) in TEXT_TYPES: x["custom"][c] = tr(x["custom"][c])
    # treatments
    lt = cf_by_t.get("link", {})
    for treat in d.get("treatments", []):
        if treat.get("comment"): treat["comment"] = tr(treat["comment"])
        for c in list((treat.get("custom") or {}).keys()):
            if lt.get(c) in TEXT_TYPES: treat["custom"][c] = tr(treat["custom"][c])
    # analysis custom (texte)
    at2 = cf_by_t.get("analysis", {})
    for c in list((d.get("custom") or {}).keys()):
        if at2.get(c) in TEXT_TYPES: d["custom"][c] = tr(d["custom"][c])
    save(d, dst)


# ============================ AIPD (DPIA) ============================
DELTA_AIPD = {
 "AIPD (méthode CNIL) enrichie — SI d'un service de santé au travail":
   "Enriched DPIA (CNIL method) — Occupational health service IS",
 "Variante enrichie de l'exemple AIPD : le traitement est décrit sous forme d'OBJETS réutilisables suivant l'esprit de la méthode PIA de la CNIL — personnes concernées, données personnelles (dont données de santé sensibles), finalités et bases légales, sous-traitants (dont hébergeur HDS), supports et sources de risque. Chaque scénario de risque référence les données et supports concernés et ses sources de risque ; les mesures référencent les supports qu'elles protègent. Analyse de démonstration, illustrative et fictive, générée par IA (Claude Opus 4.8).":
   "Enriched variant of the DPIA example: the processing is described as reusable OBJECTS following the spirit of the CNIL PIA method — data subjects, personal data (including sensitive health data), purposes and legal bases, processors (including the HDS host), supporting assets and risk sources. Each risk scenario references the data and assets involved and its risk sources; measures reference the assets they protect. Demonstration analysis, illustrative and fictitious, generated by AI (Claude Opus 4.8).",
 # champs analyse + objets (labels)
 "Finalités": "Purposes",
 "Personnes concernées": "Data subjects",
 "Destinataires": "Recipients",
 "Sous-traitants": "Processors",
 "Droits des personnes assurés": "Data subject rights ensured",
 "Information": "Information", "Accès": "Access", "Rectification": "Rectification",
 "Opposition": "Objection", "Effacement": "Erasure", "Portabilité": "Portability", "Limitation": "Restriction",
 "Modalités d'exercice des droits": "How rights are exercised",
 "Avis des personnes concernées": "Data subjects' opinion",
 "Avis du DPO": "DPO opinion",
 "Décision de validation": "Validation decision",
 "Validée": "Approved", "Validée avec réserves": "Approved with reservations",
 "À revoir": "To be revised", "Refusée": "Rejected",
 "Sources de risque": "Risk sources",
 "Données concernées": "Data involved",
 # type Personne concernée
 "Personne concernée": "Data subject",
 "Catégorie de personnes": "Category of persons",
 "Type": "Type",
 "Salarié / travailleur suivi": "Employee / monitored worker",
 "Candidat / embauche": "Applicant / hiring",
 "Ancien travailleur": "Former worker",
 "Intérimaire / externe": "Temp / external",
 "Personnel du service": "Service staff",
 "Personnes vulnérables": "Vulnerable persons", "Oui": "Yes", "Non": "No",
 "Volume approximatif": "Approximate volume",
 # type Donnée personnelle
 "Donnée personnelle": "Personal data",
 "Catégorie de données": "Data category",
 "Nature": "Nature",
 "Identification": "Identification", "Santé": "Health", "Vie professionnelle": "Professional life",
 "Connexion / journaux": "Connection / logs", "Vie personnelle": "Personal life",
 "Sensibilité": "Sensitivity",
 "Ordinaire": "Ordinary", "Sensible (art. 9 RGPD)": "Sensitive (GDPR art. 9)",
 "Perception particulière": "Perceived as sensitive",
 "Durée de conservation": "Retention period",
 "Destinataires des données": "Data recipients",
 "Origine des données": "Data origin",
 "Collectée auprès de la personne": "Collected from the person",
 "Obtenue d'un tiers": "Obtained from a third party",
 "Produite par observation / examen": "Produced by observation / examination",
 "Justification de la minimisation": "Minimization justification",
 # type Finalité
 "Finalité": "Purpose",
 "Base légale": "Legal basis",
 "Obligation légale": "Legal obligation", "Mission d'intérêt public": "Public interest task",
 "Contrat": "Contract", "Consentement": "Consent", "Intérêt légitime": "Legitimate interest",
 "Description": "Description",
 "Données utilisées": "Data used",
 "Sous-traitants impliqués": "Processors involved",
 "Nécessité & proportionnalité": "Necessity & proportionality",
 # type Sous-traitant
 "Sous-traitant": "Processor",
 "Prestation": "Service provided",
 "Hébergeur de données de santé (HDS) certifié": "Certified health-data host (HDS)",
 "Localisation / transferts": "Location / transfers",
 "Garanties (art. 28 RGPD)": "Safeguards (GDPR art. 28)",
 "Données confiées": "Data entrusted",
 "Transfert hors-UE": "Non-EU transfer",
 # type Support
 "Support": "Supporting asset",
 "Logiciel": "Software", "Matériel": "Hardware", "Papier": "Paper", "Personnel": "Staff",
 "Local": "Premises", "Canal": "Channel",
 "Responsable": "Owner",
 "Données portées": "Data carried",
 "Opérateur / hébergeur": "Operator / host",
 "Finalités servies": "Purposes served",
 # type Source de risque
 "Source de risque": "Risk source",
 "Catégorie": "Category",
 "Interne — malveillante": "Internal — malicious", "Interne — accidentelle": "Internal — accidental",
 "Externe — humaine": "External — human", "Source non humaine": "Non-human source",
 "Motivation / mode opératoire": "Motivation / modus operandi",
 "Pertinence": "Relevance",
 "1 — Faible": "1 — Low", "2 — Modéré": "2 — Moderate", "3 — Fort": "3 — High", "4 — Maximal": "4 — Maximum",
 # type Destinataire
 "Destinataire": "Recipient",
 "Service interne / équipe pluridisciplinaire": "Internal service / multidisciplinary team",
 "Tiers autorisé": "Authorized third party",
 "Autorité / organisme public": "Authority / public body",
 "Autre responsable de traitement": "Other controller",
 "Finalité de la transmission": "Purpose of the transfer",
 "Données reçues": "Data received",
 "Localisation": "Location",
 "Union européenne / EEE": "European Union / EEA",
 "Hors UE — pays adéquat": "Non-EU — adequate country",
 "Hors UE — garanties appropriées": "Non-EU — appropriate safeguards",
 "Garanties de transfert (hors-UE)": "Transfer safeguards (non-EU)",
 # instances : personne_concernee
 "Travailleurs suivis": "Monitored workers",
 "≈ 3 500": "≈ 3,500",
 "Candidats / visites d'embauche": "Applicants / pre-employment visits",
 "≈ 400 / an": "≈ 400 / year",
 "Anciens travailleurs (dossiers archivés)": "Former workers (archived records)",
 "≈ 8 000": "≈ 8,000",
 "Personnel du service de santé": "Occupational health service staff",
 "≈ 40": "≈ 40",
 # instances : donnee_personnelle
 "Identité et coordonnées": "Identity and contact details",
 "Durée du suivi + archivage légal": "Duration of monitoring + legal archiving",
 "Limitée aux coordonnées utiles au suivi et à la convocation aux visites.":
   "Limited to the contact details needed for monitoring and appointment scheduling.",
 "Données de santé (DMST)": "Health data (occupational health record)",
 "40 ans après la dernière visite ou examen (décret n° 2022-1434) ; jusqu'à 50 ans pour certaines expositions (agents chimiques dangereux)":
   "40 years after the last visit or examination (decree no. 2022-1434); up to 50 years for certain exposures (hazardous chemical agents)",
 "Strictement nécessaire au suivi médical ; accès réservé au personnel de santé (secret médical).":
   "Strictly necessary for medical monitoring; access restricted to health staff (medical confidentiality).",
 "Avis d'aptitude": "Fitness opinion",
 "Durée du contrat + archivage": "Duration of the contract + archiving",
 "Seul le sens de l'avis (apte/inapte, aménagements) est transmis à l'employeur, sans donnée de santé.":
   "Only the conclusion (fit/unfit, adjustments) is sent to the employer, without any health data.",
 "Poste de travail et expositions professionnelles": "Workstation and occupational exposures",
 "Jusqu'à 40 ans après la fin de l'exposition (traçabilité des risques particuliers : CMR, amiante, rayonnements ionisants)":
   "Up to 40 years after the end of exposure (traceability of specific risks: CMR, asbestos, ionizing radiation)",
 "Données d'exposition nécessaires à la traçabilité et à la prévention.":
   "Exposure data necessary for traceability and prevention.",
 "Données de connexion et journaux": "Connection data and logs",
 "6 à 12 mois": "6 to 12 months",
 "Journaux limités à la sécurité du SI ; conservation courte.": "Logs limited to IS security; short retention.",
 "Coordonnées professionnelles employeur": "Employer's business contact details",
 "Durée de la convention": "Duration of the agreement",
 "Coordonnées professionnelles strictement nécessaires à la relation avec l'employeur.":
   "Business contact details strictly necessary for the relationship with the employer.",
 # instances : finalite
 "Suivi médical individuel des travailleurs": "Individual medical monitoring of workers",
 "Assurer le suivi de l'état de santé (visites, examens complémentaires).":
   "Monitor health status (visits, additional examinations).",
 "Obligation légale de suivi médical (Code du travail) ; traitement nécessaire à l'exécution de cette mission.":
   "Legal obligation of medical monitoring (Labour Code); processing necessary to carry out this task.",
 "Délivrance des avis d'aptitude": "Issuing fitness opinions",
 "Émettre les avis d'aptitude au poste de travail.": "Issue fitness-for-work opinions.",
 "Nécessaire à la délivrance de l'avis d'aptitude, prévue par les textes.":
   "Necessary to issue the fitness opinion, as provided for by law.",
 "Traçabilité des expositions professionnelles": "Traceability of occupational exposures",
 "Tracer les expositions à des risques (amiante, agents CMR…).": "Track exposures to hazards (asbestos, CMR agents…).",
 "Traçabilité des expositions imposée par la réglementation (prévention des risques professionnels).":
   "Exposure traceability required by regulation (prevention of occupational risks).",
 "Gestion des accès et sécurité du SI": "Access management and IS security",
 "Sécuriser l'accès aux dossiers et journaliser les consultations.": "Secure access to records and log consultations.",
 "Nécessaire à la sécurité du SI et à la protection des données de santé hébergées.":
   "Necessary for IS security and protection of the hosted health data.",
 # instances : sous_traitant
 "Éditeur du logiciel métier (DMST)": "Vendor of the business software (occupational health record)",
 "Édition et maintenance applicative": "Software publishing and application maintenance",
 "France (UE)": "France (EU)",
 "Clauses art. 28, engagement de confidentialité, accès distant tracé.":
   "Art. 28 clauses, confidentiality undertaking, logged remote access.",
 "Hébergeur de données de santé (HDS)": "Health Data Host (HDS)",
 "Hébergement des données de santé": "Hosting of health data",
 "Certification HDS, PRA, chiffrement, réversibilité.": "HDS certification, DRP, encryption, reversibility.",
 "Prestataire d'archivage papier": "Paper archiving provider",
 "Numérisation et archivage des dossiers papier": "Digitization and archiving of paper records",
 "Clauses de confidentialité, destruction sécurisée tracée.": "Confidentiality clauses, logged secure destruction.",
 "Infogérant du parc informatique": "IT infrastructure outsourcer",
 "Support et maintenance des postes et serveurs": "Support and maintenance of workstations and servers",
 "Comptes nominatifs, moindre privilège, engagement de confidentialité.":
   "Named accounts, least privilege, confidentiality undertaking.",
 # instances : support
 "Logiciel métier de gestion des dossiers médicaux": "Business software for managing medical records",
 "DSI du service de santé": "IT department of the health service",
 "Serveur d'hébergement du logiciel métier": "Server hosting the business software",
 "Messagerie professionnelle": "Business email",
 "DSI": "IT department",
 "Postes de travail des médecins et infirmiers": "Workstations of physicians and nurses",
 "Infogérant": "Outsourcer",
 "Sauvegardes (dont hors-ligne)": "Backups (including offline)",
 "Dossiers médicaux papier": "Paper medical records",
 "Secrétariat médical": "Medical secretariat",
 "Imprimantes / photocopieurs": "Printers / photocopiers",
 "Personnel du service (médecins, IDEST, secrétaires)": "Service staff (physicians, occupational nurses, secretaries)",
 "Direction du service": "Service management",
 "Réseau LAN / interconnexions": "LAN / interconnections",
 "Infogérant réseau": "Network outsourcer",
 # instances : source_risque
 "Employeur cherchant à accéder aux données de santé": "Employer seeking access to health data",
 "Connaître l'état de santé d'un salarié pour une décision RH.": "Learn an employee's health status for an HR decision.",
 "Personnel non habilité du service": "Unauthorized service staff",
 "Curiosité, erreur d'habilitation ou de manipulation.": "Curiosity, authorization error or mishandling.",
 "Cybercriminel (rançongiciel)": "Cybercriminal (ransomware)",
 "Extorsion financière par chiffrement et menace de divulgation.": "Financial extortion through encryption and threat of disclosure.",
 "Prestataire / sous-traitant défaillant": "Failing provider / processor",
 "Négligence ou accès mal encadré.": "Negligence or poorly controlled access.",
 "Événement accidentel ou technique (panne, incendie, sinistre)": "Accidental or technical event (failure, fire, disaster)",
 "Défaillance technique ou sinistre non intentionnel (panne matérielle, incendie, dégât des eaux).":
   "Technical failure or unintentional disaster (hardware failure, fire, water damage).",
 "Personne interne malveillante": "Malicious insider",
 "Vengeance ou revente d'informations.": "Revenge or resale of information.",
 "Erreur humaine (saisie, manipulation, négligence)": "Human error (data entry, handling, negligence)",
 "Erreur non intentionnelle d'un utilisateur : saisie, envoi, manipulation ou suppression erronés.":
   "Unintentional user error: incorrect entry, sending, handling or deletion.",
 # instances : destinataire
 "Employeur": "Employer",
 "Notification de l'avis d'aptitude ou d'inaptitude, sans transmission de données de santé (art. R4624-55 du Code du travail).":
   "Notification of the fitness or unfitness opinion, without transferring any health data (art. R4624-55 of the Labour Code).",
 "Médecin traitant / spécialiste": "Treating physician / specialist",
 "Coordination des soins, sur demande et avec l'accord du travailleur.":
   "Care coordination, on request and with the worker's consent.",
 "Médecin inspecteur du travail (inspection médicale du travail)":
   "Labour medical inspector (occupational medical inspectorate)",
 "Contrôle légal des services de santé au travail et accès au dossier médical en santé au travail, dans le cadre prévu par la loi.":
   "Legal oversight of occupational health services and access to the occupational health record, within the framework provided by law.",
 "Salarié concerné": "Employee concerned",
 "Exercice des droits de la personne concernée : accès à son dossier médical en santé au travail et remise de l'avis d'aptitude ou d'inaptitude.":
   "Exercise of the data subject's rights: access to their occupational health record and delivery of the fitness or unfitness opinion.",
 "Équipe pluridisciplinaire de santé au travail": "Multidisciplinary occupational health team",
 "Suivi médical individuel et collectif, dans le respect du secret médical partagé.":
   "Individual and collective medical monitoring, respecting shared medical confidentiality.",
 # analysis
 "Le traitement repose sur une obligation légale (suivi de santé au travail) et sur des données de santé au sens de l'article 9 du RGPD. Les finalités sont déterminées et légitimes, la minimisation est respectée et les durées de conservation sont encadrées. Le cloisonnement des accès (secret médical) et l'hébergement HDS constituent des mesures essentielles. Le DPO émet un avis favorable, sous réserve de finaliser la formalisation des contrats de sous-traitance (art. 28) et le registre des transmissions à l'employeur.":
   "The processing rests on a legal obligation (occupational health monitoring) and on health data within the meaning of GDPR article 9. The purposes are specified and legitimate, minimization is observed and retention periods are framed. Access partitioning (medical confidentiality) and HDS hosting are essential measures. The DPO issues a favourable opinion, subject to finalizing the processor agreements (art. 28) and the register of transfers to the employer.",
 "Le traitement étant imposé et encadré par la loi (suivi de santé au travail), le recueil de l'avis des personnes concernées n'est pas nécessaire au sens de l'article 35 §9 du RGPD (« le cas échéant »). L'information des personnes et l'exercice de leurs droits restent assurés.":
   "As the processing is imposed and framed by law (occupational health monitoring), seeking the data subjects' opinion is not necessary within the meaning of GDPR article 35(9) (“where appropriate”). Information of individuals and the exercise of their rights remain ensured.",
 "Information par notice remise à l'embauche et affichage ; demandes d'accès et de rectification traitées par le médecin du travail dans un délai d'un mois ; opposition et limitation appréciées au regard de l'obligation légale de suivi.":
   "Information via a notice given at hiring and by display; access and rectification requests handled by the occupational physician within one month; objection and restriction assessed against the legal monitoring obligation.",
}

# ============================ EBIOS RM ============================
DELTA_EBIOS = {
 "EBIOS RM enrichi — Système d'information de gestion": "Enriched EBIOS RM — Business information system",
 "Variante enrichie de l'exemple EBIOS RM : le socle (atelier 1) et l'écosystème sont modélisés sous forme d'OBJETS réutilisables — valeurs métier (avec besoins DICP), biens supports (rattachés aux valeurs métier soutenues), événements redoutés (ciblant une valeur métier), parties prenantes de l'écosystème et sources de risque. Les scénarios de risque et les mesures référencent ces objets (valeurs métier impactées, événements, sources, parties prenantes, biens supports protégés). Analyse de démonstration, illustrative et fictive, générée par IA (Claude Opus 4.8).":
   "Enriched variant of the EBIOS RM example: the baseline (workshop 1) and the ecosystem are modelled as reusable OBJECTS — business values (with AICP needs), supporting assets (linked to the business values they support), feared events (targeting a business value), ecosystem stakeholders and risk sources. Risk scenarios and measures reference these objects (business values impacted, events, sources, stakeholders, protected supporting assets). Demonstration analysis, illustrative and fictitious, generated by AI (Claude Opus 4.8).",
 # analyse
 "Socle de sécurité de référence": "Reference security baseline",
 "Recevabilité de l'étude": "Study admissibility",
 # champs risque
 "Valeurs métier impactées": "Business values impacted",
 "Biens supports concernés": "Supporting assets involved",
 "Événements redoutés": "Feared events",
 "Sources de risque": "Risk sources",
 "Niveau de risque (source)": "Risk level (source)",
 "Moyen": "Medium",
 "Parties prenantes": "Stakeholders",
 "Scénario stratégique": "Strategic scenario",
 "Scénario opérationnel": "Operational scenario",
 # type Valeur métier
 "Valeur métier": "Business value",
 "Nom": "Name", "Nature": "Nature", "Processus": "Process", "Information": "Information",
 "Entité / dépositaire": "Entity / custodian",
 "Disponibilité": "Availability", "Intégrité": "Integrity", "Confidentialité": "Confidentiality",
 "Preuve / Traçabilité": "Proof / Traceability",
 # type Bien support
 "Bien support": "Supporting asset",
 "Type": "Type", "Matériel": "Hardware", "Logiciel": "Software", "Réseau": "Network",
 "Personnel": "Staff", "Site / local": "Site / premises", "Organisation": "Organization", "Canal": "Channel",
 "Responsable": "Owner",
 "Valeurs métier soutenues": "Business values supported",
 # type Événement redouté
 "Événement redouté": "Feared event",
 "Valeur métier ciblée": "Targeted business value",
 "Critères de sécurité impactés": "Security criteria impacted",
 "Type d'impact": "Impact type",
 "Réglementaire": "Regulatory", "Réputationnel": "Reputational",
 # type Exigence du socle
 "Exigence du socle de sécurité": "Security baseline requirement",
 "Exigence": "Requirement", "Statut": "Status",
 "Appliqué": "Applied", "Partiel": "Partial", "Non appliqué": "Not applied",
 "Référence": "Reference", "Écart constaté": "Gap identified", "Remédiation": "Remediation",
 # type Source de risque (v1.3)
 "Profil": "Profile",
 "Crime organisé": "Organized crime", "Interne malveillant": "Malicious insider", "Amateur": "Amateur",
 "Activiste idéologique": "Ideological activist", "Vengeur": "Avenger",
 "Description": "Description", "Objectif visé": "Target objective", "Motivation": "Motivation",
 "Ressources": "Resources", "Niveau de motivation": "Motivation level", "Niveau d'activité": "Activity level",
 "Pertinence (SR/OV)": "Relevance (RS/TO)", "Niveau de pertinence": "Relevance level",
 "Source retenue": "Source selected", "Justification de la décision": "Decision rationale",
 # type Partie prenante (v1.3)
 "Partie prenante de l'écosystème": "Ecosystem stakeholder",
 "Catégorie": "Category", "Client": "Customer", "Fournisseur": "Supplier", "Partenaire": "Partner",
 "Autorité": "Authority",
 "Dépendance": "Dependence", "Fort": "High", "Maximal": "Maximum", "Pénétration": "Penetration",
 "Maturité cyber": "Cyber maturity", "Confiance": "Trust", "Niveau de menace": "Threat level", "Zone": "Zone",
 # type Scénario stratégique
 "Intitulé": "Title", "Valeur métier visée": "Targeted business value",
 "Parties prenantes de l'écosystème": "Ecosystem stakeholders",
 "Chemin d'attaque": "Attack path", "Écosystème concerné": "Ecosystem involved",
 "Mesures sur l'écosystème": "Ecosystem measures", "Option de traitement": "Treatment option",
 "Réduire": "Reduce", "Partager": "Share", "Éviter": "Avoid", "Accepter": "Accept",
 "Gravité retenue": "Severity retained",
 # type Scénario opérationnel
 "Mode opératoire": "Modus operandi", "Séquence MITRE ATT&CK": "MITRE ATT&CK sequence",
 "Faisabilité": "Feasibility", "Difficile": "Difficult", "Moyenne": "Medium", "Élevée": "High",
 "Vraisemblance globale": "Overall likelihood",
 "Peu vraisemblable": "Unlikely", "Vraisemblable": "Likely", "Très vraisemblable": "Very likely",
 "Quasi-certain": "Almost certain",
 "Maillon limitant": "Limiting factor", "Niveau de risque": "Risk level",
 # instances valeur_metier + entités
 "Gestion de la relation client": "Customer relationship management",
 "Direction commerciale": "Sales department",
 "Base de données clients": "Customer database",
 "DPO / Marketing": "DPO / Marketing",
 "Facturation et comptabilité": "Billing and accounting",
 "Direction administrative et financière": "Administrative and financial department",
 "Gestion des ressources humaines": "Human resources management",
 "Direction des ressources humaines": "Human resources department",
 "Production applicative (logiciel métier)": "Application production (business software)",
 "Direction des systèmes d'information": "Information systems department",
 "Messagerie et collaboration": "Email and collaboration",
 # instances bien_support + responsables
 "Serveur applicatif principal": "Main application server",
 "DSI — Infrastructure": "IT dept — Infrastructure",
 "Baie de stockage / SAN": "Storage array / SAN",
 "Base de données PostgreSQL": "PostgreSQL database",
 "DSI — Administration BDD": "IT dept — DB administration",
 "Application métier (ERP)": "Business application (ERP)",
 "DSI — Applications": "IT dept — Applications",
 "Réseau LAN et interconnexions": "LAN and interconnections",
 "DSI — Réseau": "IT dept — Network",
 "Support informatique": "IT support",
 "Hébergement cloud (IaaS)": "Cloud hosting (IaaS)",
 "DSI / Hébergeur": "IT dept / Host",
 "Administrateurs systèmes": "System administrators",
 "DSI": "IT dept",
 "Datacenter / site d'hébergement": "Data center / hosting site",
 "Services généraux": "Facilities management",
 # instances evenement_redoute + impacts
 "Divulgation massive de la base clients": "Massive disclosure of the customer database",
 "Sanction RGPD, atteinte à la réputation, perte de confiance des clients.":
   "GDPR fine, reputational harm, loss of customer trust.",
 "Indisponibilité prolongée du logiciel métier": "Prolonged unavailability of the business software",
 "Arrêt de la production, pertes financières, retards de livraison.":
   "Production halt, financial losses, delivery delays.",
 "Altération des données de facturation": "Alteration of billing data",
 "Erreurs comptables, litiges, non-conformité fiscale.": "Accounting errors, disputes, tax non-compliance.",
 "Fuite de données RH": "HR data leak",
 "Atteinte à la vie privée des salariés, sanction RGPD.": "Invasion of employees' privacy, GDPR fine.",
 "Perte d'intégrité des échanges (messagerie)": "Loss of integrity of communications (email)",
 "Fraude au virement, usurpation, décisions erronées.": "Wire-transfer fraud, impersonation, erroneous decisions.",
 "Indisponibilité de la relation client": "Unavailability of customer relations",
 "Perte de chiffre d'affaires, insatisfaction des clients.": "Loss of revenue, customer dissatisfaction.",
 # instances partie_prenante
 "Hébergeur cloud (IaaS)": "Cloud host (IaaS)",
 "Éditeur du logiciel métier (ERP)": "Business software vendor (ERP)",
 "Prestataire d'infogérance": "IT outsourcing provider",
 "Sous-traitant de la paie": "Payroll processor",
 "Client grand compte": "Key account customer",
 # instances source_risque
 "Groupe cybercriminel (rançongiciel)": "Cybercriminal group (ransomware)",
 "Gain financier par extorsion (chiffrement et menace de divulgation).":
   "Financial gain through extortion (encryption and threat of disclosure).",
 "Chiffrer le SI et exiger une rançon.": "Encrypt the IS and demand a ransom.",
 "Menace principale : rançongiciels très actifs contre les PME/ETI.":
   "Primary threat: ransomware very active against SMEs/mid-caps.",
 "Groupes spécialisés dans l'extorsion (ransomware-as-a-service).":
   "Groups specialized in extortion (ransomware-as-a-service).",
 "Groupe étatique (APT)": "State-sponsored group (APT)",
 "Espionnage stratégique et positionnement durable.": "Strategic espionage and long-term positioning.",
 "Exfiltrer des informations sensibles sur la durée.": "Exfiltrate sensitive information over time.",
 "Retenue au regard de la valeur des données et d'un positionnement durable possible.":
   "Retained given the value of the data and possible long-term positioning.",
 "Acteur étatique disposant de moyens importants (APT).": "State actor with significant resources (APT).",
 "Vengeance ou gain personnel.": "Revenge or personal gain.",
 "Détourner ou divulguer des données internes.": "Divert or disclose internal data.",
 "Risque interne significatif (accès légitimes détournés).": "Significant insider risk (legitimate access misused).",
 "Salarié ou prestataire disposant d'accès internes.": "Employee or provider with internal access.",
 "Avantage économique.": "Economic advantage.",
 "Obtenir des informations commerciales.": "Obtain business information.",
 "Écartée : intérêt et capacité jugés faibles dans ce contexte.":
   "Dismissed: interest and capability judged low in this context.",
 "Concurrent cherchant un avantage économique.": "Competitor seeking an economic advantage.",
 "Défense d'une cause idéologique.": "Defence of an ideological cause.",
 "Perturber les services (DDoS) et dégrader l'image.": "Disrupt services (DDoS) and damage reputation.",
 "Écartée : impact limité (indisponibilité temporaire) et faible ciblage.":
   "Dismissed: limited impact (temporary unavailability) and low targeting.",
 "Collectif militant menant des actions de déni de service.":
   "Activist collective carrying out denial-of-service actions.",
 # instances scénario stratégique
 "Rançongiciel paralysant la production applicative": "Ransomware paralyzing application production",
 "Hameçonnage → exécution → propagation → chiffrement des serveurs et des sauvegardes en ligne.":
   "Phishing → execution → propagation → encryption of servers and online backups.",
 "Hébergeur cloud et infogérant fournissent l'accès et l'administration.":
   "Cloud host and outsourcer provide access and administration.",
 "Exiger sauvegardes immuables et cloisonnement des accès d'administration.":
   "Require immutable backups and partitioning of administration access.",
 "Exfiltration de la base clients": "Exfiltration of the customer database",
 "Compromission d'un accès à privilèges → extraction de la base → menace de divulgation.":
   "Compromise of a privileged access → database extraction → threat of disclosure.",
 "Éditeur ERP disposant d'accès distants de maintenance.": "ERP vendor with remote maintenance access.",
 "Encadrer les accès distants de l'éditeur (bastion, MFA, journalisation).":
   "Control the vendor's remote access (bastion, MFA, logging).",
 "Compromission via la chaîne d'approvisionnement (éditeur ERP)": "Compromise via the supply chain (ERP vendor)",
 "Compromission de l'éditeur → mise à jour piégée → altération des données de facturation.":
   "Compromise of the vendor → trojanized update → alteration of billing data.",
 "Éditeur et infogérant dans la chaîne de mise à jour.": "Vendor and outsourcer in the update chain.",
 "Vérifier l'intégrité des mises à jour ; clauses de sécurité contractuelles.":
   "Verify update integrity; contractual security clauses.",
 "Fuite de données RH via le sous-traitant de paie": "HR data leak via the payroll processor",
 "Accès abusif chez le sous-traitant → extraction des données de paie.":
   "Access misuse at the processor → extraction of payroll data.",
 "Sous-traitant de la paie destinataire des données RH.": "Payroll processor receiving the HR data.",
 "Audit du sous-traitant ; minimisation des données transmises.":
   "Audit of the processor; minimization of the data transmitted.",
 "Déni de service sur la relation client": "Denial of service on customer relations",
 "Campagne DDoS → saturation des services exposés → indisponibilité.":
   "DDoS campaign → saturation of exposed services → unavailability.",
 "Hébergeur cloud en première ligne.": "Cloud host on the front line.",
 "Protection anti-DDoS et plan de continuité côté hébergeur.":
   "Anti-DDoS protection and continuity plan on the host side.",
 # instances scénario opérationnel
 "Rançongiciel — chaîne complète": "Ransomware — full chain",
 "Phishing ciblé, exécution d'un loader, élévation de privilèges, latéralisation, désactivation des sauvegardes, chiffrement.":
   "Targeted phishing, loader execution, privilege escalation, lateral movement, backup disabling, encryption.",
 "Sauvegardes hors-ligne immuables": "Immutable offline backups",
 "Exfiltration base clients — vol d'identifiants": "Customer database exfiltration — credential theft",
 "Vol d'identifiants d'administration, accès à la base, extraction chiffrée, exfiltration.":
   "Theft of admin credentials, database access, encrypted extraction, exfiltration.",
 "MFA + cloisonnement des accès": "MFA + access partitioning",
 "Supply chain — mise à jour piégée": "Supply chain — trojanized update",
 "Compromission de l'éditeur, injection dans un correctif, déploiement, altération des données.":
   "Vendor compromise, injection into a patch, deployment, data alteration.",
 "Contrôle d'intégrité des mises à jour": "Update integrity checking",
 "Fuite RH — accès abusif sous-traitant": "HR leak — processor access misuse",
 "Utilisation d'un compte du sous-traitant, extraction des bulletins, transmission externe.":
   "Use of a processor account, extraction of payslips, external transmission.",
 "Journalisation et cloisonnement chez le sous-traitant": "Logging and partitioning at the processor",
 "DDoS volumétrique": "Volumetric DDoS",
 "Botnet, saturation de la bande passante et des services applicatifs exposés.":
   "Botnet, saturation of bandwidth and exposed application services.",
 "Service anti-DDoS de l'hébergeur": "Host's anti-DDoS service",
 # MITRE (déjà en anglais → inchangé)
 "TA0001 Initial Access (Phishing T1566) → TA0002 Execution → TA0004 Privilege Escalation → TA0008 Lateral Movement → TA0040 Impact (Inhibit System Recovery T1490 + Data Encrypted for Impact T1486)":
   "TA0001 Initial Access (Phishing T1566) → TA0002 Execution → TA0004 Privilege Escalation → TA0008 Lateral Movement → TA0040 Impact (Inhibit System Recovery T1490 + Data Encrypted for Impact T1486)",
 "TA0006 Credential Access → TA0007 Discovery → TA0009 Collection (Archive Collected Data T1560) → TA0010 Exfiltration":
   "TA0006 Credential Access → TA0007 Discovery → TA0009 Collection (Archive Collected Data T1560) → TA0010 Exfiltration",
 "TA0001 Initial Access (Supply Chain Compromise T1195) → TA0002 Execution → TA0040 Impact (Data Manipulation T1565)":
   "TA0001 Initial Access (Supply Chain Compromise T1195) → TA0002 Execution → TA0040 Impact (Data Manipulation T1565)",
 "TA0001 Initial Access (Trusted Relationship T1199) → TA0009 Collection → TA0010 Exfiltration":
   "TA0001 Initial Access (Trusted Relationship T1199) → TA0009 Collection → TA0010 Exfiltration",
 "TA0040 Impact (Network Denial of Service T1498)": "TA0040 Impact (Network Denial of Service T1498)",
 # instances exigence_socle (exigence, référence ANSSI, écart, remédiation)
 "Sauvegardes hors-ligne, testées et restaurables": "Offline backups, tested and restorable",
 "Guide d'hygiène ANSSI — mesure 37 : Définir et appliquer une politique de sauvegarde des composants critiques":
   "ANSSI hygiene guide — measure 37: Define and apply a backup policy for critical components",
 "Sauvegardes en ligne exposées au chiffrement.": "Online backups exposed to encryption.",
 "Mettre en place des sauvegardes immuables/hors-ligne et tester les restaurations.":
   "Set up immutable/offline backups and test restorations.",
 "MFA sur les accès à privilèges et les accès distants": "MFA on privileged and remote access",
 "Guide d'hygiène ANSSI — mesure 13 : Privilégier lorsque c'est possible une authentification forte":
   "ANSSI hygiene guide — measure 13: Favour strong authentication wherever possible",
 "MFA absente sur certains accès d'administration.": "MFA missing on some administration access.",
 "Généraliser le MFA et passer par un bastion d'administration.":
   "Generalize MFA and use an administration bastion.",
 "Cloisonnement et segmentation du réseau": "Network partitioning and segmentation",
 "Guide d'hygiène ANSSI — mesure 19 : Segmenter le réseau et mettre en place un cloisonnement entre ces zones":
   "ANSSI hygiene guide — measure 19: Segment the network and set up partitioning between these zones",
 "Journalisation centralisée et supervision (SIEM)": "Centralized logging and monitoring (SIEM)",
 "Guide d'hygiène ANSSI — mesure 36 : Activer et configurer les journaux des composants les plus importants":
   "ANSSI hygiene guide — measure 36: Enable and configure logs on the most important components",
 "Pas de corrélation centralisée des journaux.": "No centralized log correlation.",
 "Déployer une collecte centralisée et des règles de détection.": "Deploy centralized collection and detection rules.",
 "Gestion des vulnérabilités et des correctifs": "Vulnerability and patch management",
 "Guide d'hygiène ANSSI — mesure 34 : Définir une politique de mise à jour des composants du système d'information":
   "ANSSI hygiene guide — measure 34: Define an update policy for information system components",
 "Délais de correctifs trop longs sur l'ERP.": "Patching delays too long on the ERP.",
 "Formaliser un cycle de patch et le suivi des vulnérabilités critiques.":
   "Formalize a patch cycle and tracking of critical vulnerabilities.",
 # cotation.justification (sur risques)
 "Coté en atelier 4 : mode opératoire réalisable sur une cible à forte valeur.":
   "Assessed in workshop 4: modus operandi feasible on a high-value target.",
 "Après mise en place du socle de sécurité et de la supervision (SOC).":
   "After implementing the security baseline and monitoring (SOC).",
 # analysis
 "Guide d'hygiène informatique de l'ANSSI et politique de sécurité interne (PSSI) ; conformité RGPD pour les données personnelles traitées par le SI de gestion.":
   "ANSSI IT hygiene guide and internal security policy (ISSP); GDPR compliance for the personal data processed by the business IS.",
 "Étude recevable : périmètre du SI de gestion cadré, valeurs métier et biens supports identifiés, écosystème et sources de risque appréciés ; socle de sécurité évalué (voir exigences).":
   "Admissible study: scope of the business IS framed, business values and supporting assets identified, ecosystem and risk sources assessed; security baseline evaluated (see requirements).",
}

if __name__ == "__main__":
    AUTO_AIPD = pair("demo-aipd-sst.rae.json", "demo-dpia-ohs.rae.json")
    translate_file("demo-aipd-sst-objets-enrichi.rae.json", "demo-dpia-ohs-enriched.rae.json",
                   {**AUTO_AIPD, **DELTA_AIPD})
    AUTO_EBIOS = pair("demo-ebios-rm-systeme-d-information.rae.json", "demo-ebios-rm-information-system.rae.json")
    translate_file("demo-ebios-rm-systeme-d-information-objets-enrichi.rae.json",
                   "demo-ebios-rm-information-system-enriched.rae.json",
                   {**AUTO_EBIOS, **DELTA_EBIOS})
    if MISSING:
        print("\n!!! MISSING (%d) — chaînes non traduites :" % len(MISSING))
        for s in sorted(MISSING): print("   ", s)
    else:
        print("Traduction complète : aucune chaîne manquante.")
