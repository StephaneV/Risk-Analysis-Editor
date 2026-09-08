#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construction des démos enrichies (AIPD/CNIL & EBIOS RM), à partir des démos « objets »
existantes. Ne modifie jamais les fichiers de base ; écrit de NOUVEAUX fichiers dans examples/.
Régénération : voir examples/README.md (puis build-demos-en.py pour les versions EN)."""
import json, datetime, copy, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples")
TODAY = datetime.date.today().isoformat()

def load(name): return json.load(open(os.path.join(EX, name), encoding="utf-8"))
def save(d, name):
    p = os.path.join(EX, name)
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(p, "a", encoding="utf-8").write("\n")
    print("écrit:", os.path.relpath(p, ROOT))

def L(fr): return {"fr": fr}
def items(pairs): return [{"code": c, "label": L(l)} for c, l in pairs]

def add_field(d, f):
    """Ajoute un custom_field (order = max de la cible + 1)."""
    tgt = f["target"]
    orders = [x.get("order", 0) for x in d["custom_fields"] if x.get("target") == tgt]
    f.setdefault("order", (max(orders) + 1) if orders else 1)
    d["custom_fields"].append(f)

def reorder_custom_fields(d, target_seq=("analysis", "risk", "measure", "link")):
    """Regroupe les champs personnalisés par cible dans l'ordre voulu (Analyse, Risque, Mesure,
    Lien), en conservant l'ordre interne (clé 'order') de chaque cible. Tri stable."""
    rank = {t: i for i, t in enumerate(target_seq)}
    d["custom_fields"].sort(key=lambda f: (rank.get(f.get("target"), len(target_seq)), f.get("order", 0)))

def apply_field_order(d, order_map):
    """Réassigne la clé 'order' de chaque champ perso selon une séquence de codes voulue par cible
    (ordre de lecture logique). Les codes absents de la séquence sont renvoyés après, ordre conservé."""
    for tgt, seq in order_map.items():
        idx = {code: i for i, code in enumerate(seq)}
        for f in d["custom_fields"]:
            if f.get("target") == tgt:
                f["order"] = idx.get(f.get("code"), len(seq) + f.get("order", 0)) + 1

def ot_by(d, code): return next(o for o in d["object_types"] if o["code"] == code)
def add_attr(ot, a): ot["attributes"].append(a)
def obj_by(d, oid): return next(o for o in d["objects"] if o["id"] == oid)
def next_obj_num(d, typecode):
    n = 0
    for o in d["objects"]:
        if o["type"] == typecode:
            try: n = max(n, int("".join(ch for ch in o["id"] if ch.isdigit())))
            except: pass
    return n + 1


# =====================================================================
#  AIPD / PIA (CNIL) — français
# =====================================================================
def build_aipd_fr():
    d = load("demo-aipd-sst-objets.rae.json")

    # ---- A.1 nouveau type d'objet « destinataire »
    d["object_types"].append({
        "code": "destinataire", "label": L("Destinataire"), "id_prefix": "DEST", "name_attr": "nom",
        "attributes": [
            {"code": "nom", "type": "text", "label": L("Destinataire")},
            {"code": "categorie", "type": "select", "label": L("Catégorie"), "items": items([
                ("interne", "Service interne / équipe pluridisciplinaire"),
                ("personne_concernee", "Personne concernée"),
                ("tiers_autorise", "Tiers autorisé"),
                ("autorite", "Autorité / organisme public"),
                ("sous_traitant", "Sous-traitant"),
                ("autre_responsable", "Autre responsable de traitement")])},
            {"code": "finalite_transmission", "type": "textarea", "label": L("Finalité de la transmission")},
            {"code": "donnees_recues", "type": "reference", "object_type": "donnee_personnelle",
             "multiple": True, "label": L("Données reçues")},
            {"code": "localisation", "type": "select", "label": L("Localisation"), "items": items([
                ("ue", "Union européenne / EEE"),
                ("hors_ue_adequat", "Hors UE — pays adéquat"),
                ("hors_ue_garanties", "Hors UE — garanties appropriées")])},
            {"code": "garanties_transfert", "type": "textarea", "label": L("Garanties de transfert (hors-UE)")},
        ]})

    # ---- A.2 champs de niveau analyse
    for f in [
        {"code": "avis_dpo", "target": "analysis", "type": "textarea", "label": L("Avis du DPO")},
        {"code": "avis_personnes", "target": "analysis", "type": "textarea", "label": L("Avis des personnes concernées")},
        {"code": "personnes_concernees", "target": "analysis", "type": "reference",
         "object_type": "personne_concernee", "multiple": True, "label": L("Personnes concernées")},
        {"code": "finalites", "target": "analysis", "type": "reference",
         "object_type": "finalite", "multiple": True, "label": L("Finalités")},
        {"code": "sous_traitants", "target": "analysis", "type": "reference",
         "object_type": "sous_traitant", "multiple": True, "label": L("Sous-traitants")},
        {"code": "destinataires", "target": "analysis", "type": "reference",
         "object_type": "destinataire", "multiple": True, "label": L("Destinataires")},
        {"code": "droits_personnes", "target": "analysis", "type": "tags", "multiple": True,
         "label": L("Droits des personnes assurés"), "items": items([
            ("information", "Information"), ("acces", "Accès"), ("rectification", "Rectification"),
            ("opposition", "Opposition"), ("effacement", "Effacement"),
            ("portabilite", "Portabilité"), ("limitation", "Limitation")])},
        {"code": "mesures_droits", "target": "analysis", "type": "textarea", "label": L("Modalités d'exercice des droits")},
        {"code": "decision", "target": "analysis", "type": "select", "label": L("Décision de validation"), "items": items([
            ("validee", "Validée"), ("validee_reserve", "Validée avec réserves"),
            ("a_revoir", "À revoir"), ("refusee", "Refusée")])},
    ]:
        add_field(d, f)

    # ---- A.3/A.4 attributs sur types existants
    dp = ot_by(d, "donnee_personnelle")
    add_attr(dp, {"code": "destinataires", "type": "reference", "object_type": "destinataire",
                  "multiple": True, "label": L("Destinataires des données")})
    add_attr(dp, {"code": "origine", "type": "select", "label": L("Origine des données"), "items": items([
        ("personne", "Collectée auprès de la personne"), ("tiers", "Obtenue d'un tiers"),
        ("observation", "Produite par observation / examen")])})
    add_attr(dp, {"code": "base_minimisation", "type": "textarea", "label": L("Justification de la minimisation")})

    fn = ot_by(d, "finalite")
    add_attr(fn, {"code": "necessite_justifiee", "type": "textarea", "label": L("Nécessité & proportionnalité")})

    st = ot_by(d, "sous_traitant")
    add_attr(st, {"code": "transfert_hors_ue", "type": "boolean", "label": L("Transfert hors-UE")})

    # ---- A.5 instances « destinataire »
    d["objects"] += [
        {"id": "DEST1", "type": "destinataire", "values": {
            "nom": "Employeur", "categorie": "tiers_autorise",
            "finalite_transmission": "Notification de l'avis d'aptitude ou d'inaptitude, sans transmission de données de santé (art. R4624-55 du Code du travail).",
            "donnees_recues": ["DP3"], "localisation": "ue"}},
        {"id": "DEST2", "type": "destinataire", "values": {
            "nom": "Médecin traitant / spécialiste", "categorie": "tiers_autorise",
            "finalite_transmission": "Coordination des soins, sur demande et avec l'accord du travailleur.",
            "donnees_recues": ["DP2"], "localisation": "ue"}},
        {"id": "DEST3", "type": "destinataire", "values": {
            "nom": "Médecin inspecteur du travail (inspection médicale du travail)", "categorie": "autorite",
            "finalite_transmission": "Contrôle légal des services de santé au travail et accès au dossier médical en santé au travail, dans le cadre prévu par la loi.",
            "donnees_recues": ["DP1", "DP2", "DP3", "DP4"], "localisation": "ue"}},
        {"id": "DEST4", "type": "destinataire", "values": {
            "nom": "Salarié concerné", "categorie": "personne_concernee",
            "finalite_transmission": "Exercice des droits de la personne concernée : accès à son dossier médical en santé au travail et remise de l'avis d'aptitude ou d'inaptitude.",
            "donnees_recues": ["DP1", "DP2", "DP3", "DP4"], "localisation": "ue"}},
        {"id": "DEST5", "type": "destinataire", "values": {
            "nom": "Équipe pluridisciplinaire de santé au travail", "categorie": "interne",
            "finalite_transmission": "Suivi médical individuel et collectif, dans le respect du secret médical partagé.",
            "donnees_recues": ["DP1", "DP2", "DP3", "DP4"], "localisation": "ue"}},
    ]

    # ---- câblage : destinataires par donnée
    dest_by_dp = {
        "DP1": ["DEST5", "DEST4", "DEST3"], "DP2": ["DEST2", "DEST3", "DEST4", "DEST5"],
        "DP3": ["DEST1", "DEST4", "DEST5", "DEST3"], "DP4": ["DEST3", "DEST4", "DEST5"],
        "DP5": [], "DP6": ["DEST5"]}   # DP5 = journaux SI : aucun destinataire externe (usage interne sécurité)
    origine_by_dp = {"DP1": "personne", "DP2": "observation", "DP3": "observation",
                     "DP4": "personne", "DP5": "observation", "DP6": "tiers"}
    minim_by_dp = {
        "DP1": "Limitée aux coordonnées utiles au suivi et à la convocation aux visites.",
        "DP2": "Strictement nécessaire au suivi médical ; accès réservé au personnel de santé (secret médical).",
        "DP3": "Seul le sens de l'avis (apte/inapte, aménagements) est transmis à l'employeur, sans donnée de santé.",
        "DP4": "Données d'exposition nécessaires à la traçabilité et à la prévention.",
        "DP5": "Journaux limités à la sécurité du SI ; conservation courte.",
        "DP6": "Coordonnées professionnelles strictement nécessaires à la relation avec l'employeur."}
    for oid in dest_by_dp:
        v = obj_by(d, oid)["values"]
        v["destinataires"] = dest_by_dp[oid]
        v["origine"] = origine_by_dp[oid]
        v["base_minimisation"] = minim_by_dp[oid]

    # DP3 (avis d'aptitude) : conclusion administrative apte/inapte (+ aménagements) transmise à
    # l'employeur, sans détail médical → donnée de vie professionnelle ordinaire, pas une donnée de
    # santé au sens de l'art. 9 du RGPD.
    dp3 = obj_by(d, "DP3")["values"]
    dp3["categorie"] = "professionnelle"
    dp3["sensibilite"] = "ordinaire"

    # DP2 (DMST) : durée de conservation réelle — 40 ans à compter de la dernière visite/examen
    # (décret n° 2022-1434 du 15 nov. 2022), jusqu'à 50 ans pour certaines expositions antérieures.
    obj_by(d, "DP2")["values"]["conservation"] = (
        "40 ans après la dernière visite ou examen (décret n° 2022-1434) ; "
        "jusqu'à 50 ans pour certaines expositions (agents chimiques dangereux)")

    # DP4 (poste / expositions) : traçabilité des expositions conservée sur le long terme, alignée
    # sur le suivi médical (risques particuliers : CMR, amiante, rayonnements ionisants…).
    obj_by(d, "DP4")["values"]["conservation"] = (
        "Jusqu'à 40 ans après la fin de l'exposition (traçabilité des risques particuliers : "
        "CMR, amiante, rayonnements ionisants)")

    necessite_by_fn = {
        "FN1": "Obligation légale de suivi médical (Code du travail) ; traitement nécessaire à l'exécution de cette mission.",
        "FN2": "Nécessaire à la délivrance de l'avis d'aptitude, prévue par les textes.",
        "FN3": "Traçabilité des expositions imposée par la réglementation (prévention des risques professionnels).",
        "FN4": "Nécessaire à la sécurité du SI et à la protection des données de santé hébergées."}
    for fnid, txt in necessite_by_fn.items():
        obj_by(d, fnid)["values"]["necessite_justifiee"] = txt

    for stid in ("ST1", "ST2", "ST3", "ST4"):
        obj_by(d, stid)["values"]["transfert_hors_ue"] = False

    # ---- valeurs de niveau analyse
    d.setdefault("custom", {})
    d["custom"].update({
        "avis_dpo": ("Le traitement repose sur une obligation légale (suivi de santé au travail) et sur des "
                     "données de santé au sens de l'article 9 du RGPD. Les finalités sont déterminées et "
                     "légitimes, la minimisation est respectée et les durées de conservation sont encadrées. "
                     "Le cloisonnement des accès (secret médical) et l'hébergement HDS constituent des mesures "
                     "essentielles. Le DPO émet un avis favorable, sous réserve de finaliser la formalisation "
                     "des contrats de sous-traitance (art. 28) et le registre des transmissions à l'employeur."),
        "avis_personnes": ("Le traitement étant imposé et encadré par la loi (suivi de santé au travail), le recueil "
                           "de l'avis des personnes concernées n'est pas nécessaire au sens de l'article 35 §9 du RGPD "
                           "(« le cas échéant »). L'information des personnes et l'exercice de leurs droits restent assurés."),
        "personnes_concernees": ["PC1", "PC2", "PC3", "PC4"],
        "finalites": ["FN1", "FN2", "FN3", "FN4"],
        "sous_traitants": ["ST1", "ST2", "ST3", "ST4"],
        "destinataires": ["DEST1", "DEST2", "DEST3", "DEST4", "DEST5"],
        "droits_personnes": ["information", "acces", "rectification", "opposition", "limitation"],
        "mesures_droits": ("Information par notice remise à l'embauche et affichage ; demandes d'accès et de "
                           "rectification traitées par le médecin du travail dans un délai d'un mois ; "
                           "opposition et limitation appréciées au regard de l'obligation légale de suivi."),
        "decision": "validee_reserve",
    })

    # ---- métadonnées
    m = d["metadata"]
    m["title"] = "AIPD (méthode CNIL) enrichie — SI d'un service de santé au travail"
    m["description"] = m["description"].replace(
        "illustrative et fictive.",
        "illustrative et fictive, générée par IA (Claude Opus 4.8).")
    m["revision"] = "2.0"
    m["updated_at"] = TODAY
    m["language"] = "fr"

    # ---- A.6 sources de risque : scinder « accidentel/technique » et « erreur humaine »
    sr5 = obj_by(d, "SR5")["values"]
    sr5["nom"] = "Événement accidentel ou technique (panne, incendie, sinistre)"
    sr5["motivation"] = "Défaillance technique ou sinistre non intentionnel (panne matérielle, incendie, dégât des eaux)."
    d["objects"].append({"id": "SR7", "type": "source_risque", "values": {
        "nom": "Erreur humaine (saisie, manipulation, négligence)", "categorie": "interne_accidentelle",
        "motivation": "Erreur non intentionnelle d'un utilisateur : saisie, envoi, manipulation ou suppression erronés.",
        "pertinence": "3"}})

    # ---- A.7 nouveau support « Réseau »
    d["objects"].append({"id": "SP9", "type": "support", "values": {
        "nom": "Réseau LAN / interconnexions", "type": "reseau", "responsable": "Infogérant réseau",
        "donnees_portees": ["DP1", "DP2", "DP3", "DP4"], "operateur": "ST4", "finalites": ["FN1", "FN2", "FN3", "FN4"]}})

    # ---- A.8 recâblage des fiches (sources & supports) puis suppression des tags redondants.
    # Les valeurs du tag `source`/`supports` sont désormais portées par les objets référencés ;
    # SR5 (erreur) est réparti entre SR5 (accidentel/technique) et SR7 (erreur humaine).
    sources_by_risk = {
        "R1": ["SR2", "SR1"], "R2": ["SR1", "SR7"], "R3": ["SR3", "SR7"], "R4": ["SR3"],
        "R5": ["SR2", "SR1", "SR7"], "R6": ["SR2", "SR7"], "R7": ["SR3", "SR6"], "R8": ["SR6", "SR2"],
        "R9": ["SR5"], "R10": ["SR3"], "R11": ["SR4", "SR7"], "R12": ["SR2", "SR7"]}
    supports_by_risk = {
        "R1": ["SP1", "SP8"], "R2": ["SP3", "SP1", "SP6", "SP8"], "R3": ["SP4"], "R4": ["SP3", "SP9"],
        "R5": ["SP6", "SP7"], "R6": ["SP1", "SP8"], "R7": ["SP1", "SP2"], "R8": ["SP1"],
        "R9": ["SP1", "SP2", "SP5"], "R10": ["SP1", "SP2", "SP5", "SP4", "SP9"], "R11": ["SP1", "SP2", "SP5"], "R12": ["SP1", "SP5"]}
    for r in d["risks"]:
        c = r.setdefault("custom", {})
        c["sources_fiche"] = sources_by_risk[r["id"]]
        c["supports_fiche"] = supports_by_risk[r["id"]]
        c.pop("source", None); c.pop("supports", None)   # tags redondants supprimés
    d["custom_fields"] = [f for f in d["custom_fields"] if f.get("code") not in ("source", "supports")]
    # les champs référence deviennent les seuls : on retire le suffixe « (fiches) »
    for f in d["custom_fields"]:
        if f.get("code") == "sources_fiche": f["label"] = L("Sources de risque")
        if f.get("code") == "supports_fiche": f["label"] = L("Supports concernés")

    apply_field_order(d, {   # ordre de lecture logique au sein de chaque cible
        "analysis": ["referentiels", "perimetre", "finalites", "personnes_concernees", "destinataires",
                     "sous_traitants", "droits_personnes", "mesures_droits", "avis_personnes", "avis_dpo", "decision"],
        "risk": ["sources_fiche", "supports_fiche", "donnees_concernees", "impacts"],
        "measure": ["nature", "objectif", "avancement"],
        "link": ["effet"],
    })
    reorder_custom_fields(d)   # Analyse → Risque → Mesure → Lien

    # ---- A.9 configuration du rapport : éclaté par catégorie de risque (ordre alphabétique).
    #  En-tête (une fois) : page de garde + TdM + métadonnées + présentation.
    #  Répété par catégorie : trajectoire, registre, détail des risques, mesures, détail des mesures,
    #                         liens, détail des liens.
    #  Annexe (une fois) : synthèse, plan d'action (échéancier), grille de cotation, niveaux de
    #                      criticité, référentiels, objets (en détail).
    d.setdefault("extensions", {}).setdefault("display", {})["report"] = {
        "scope": "all", "orientation": "portrait",
        "cover": {"on": True}, "toc": {"on": True},
        "iteration": {"by": "risk_category", "sort": "alpha"},
        "sections": [
            {"id": "metadata", "on": True, "zone": "header"},
            {"id": "presentation", "on": True, "zone": "header"},
            # matrices remontées au-dessus de la trajectoire (répétées, décochées)
            {"id": "matrix_ir", "on": False, "zone": "repeated"},
            {"id": "matrix_initial", "on": False, "zone": "repeated"},
            {"id": "matrix_residual", "on": False, "zone": "repeated"},
            {"id": "matrix_traj", "on": True, "zone": "repeated"},
            {"id": "risks_table", "on": True, "zone": "repeated"},
            {"id": "risks_detail", "on": True, "zone": "repeated"},
            {"id": "measures_table", "on": True, "zone": "repeated"},
            {"id": "measures_detail", "on": True, "zone": "repeated"},
            {"id": "links_table", "on": False, "zone": "repeated"},   # tableau des liens retiré
            {"id": "links_detail", "on": True, "zone": "repeated"},
            {"id": "summary_counts", "on": True, "zone": "appendix"},
            {"id": "summary_distribution", "on": True, "zone": "appendix"},   # répartition par criticité, sous la synthèse
            # radar en annexe entre Synthèse/Répartition et Plan d'action
            {"id": "radar", "on": True, "zone": "appendix", "dim": "sources_fiche", "metric": "max", "eval": "both-over"},
            {"id": "action_plan", "on": True, "zone": "appendix", "view": "due_date"},
            {"id": "grid_axes", "on": True, "zone": "appendix"},
            {"id": "grid_criticality", "on": True, "zone": "appendix"},
            {"id": "field_glossary", "on": True, "zone": "appendix"},
            {"id": "objects", "on": True, "zone": "appendix", "view": "detail"},
        ],
    }
    save(d, "demo-aipd-sst-objets-enrichi.rae.json")


# =====================================================================
#  EBIOS RM (SI de gestion) — français — structure v1.3
# =====================================================================
SCALE3 = [{"value": 1, "label": L("Faible"), "color": "#2e9e5b"},
          {"value": 2, "label": L("Moyen"), "color": "#e0b93a"},
          {"value": 3, "label": L("Élevé"), "color": "#e6862e"}]
SCALE4 = [{"value": 1, "label": L("Faible"), "color": "#2e9e5b"}, {"value": 2, "label": L("Modéré"), "color": "#e0b93a"},
          {"value": 3, "label": L("Fort"), "color": "#e6862e"}, {"value": 4, "label": L("Maximal"), "color": "#d64545"}]
SCALE4R = [{"value": 1, "label": L("Faible"), "color": "#d64545"}, {"value": 2, "label": L("Modéré"), "color": "#e6862e"},
           {"value": 3, "label": L("Fort"), "color": "#e0b93a"}, {"value": 4, "label": L("Maximal"), "color": "#2e9e5b"}]
GRAV4 = [{"value": 1, "label": L("Mineure"), "color": "#2e9e5b"}, {"value": 2, "label": L("Significative"), "color": "#e0b93a"},
         {"value": 3, "label": L("Grave"), "color": "#e6862e"}, {"value": 4, "label": L("Critique"), "color": "#d64545"}]
VRAIS4 = [{"value": 1, "label": L("Peu vraisemblable"), "color": "#2e9e5b"}, {"value": 2, "label": L("Vraisemblable"), "color": "#e0b93a"},
          {"value": 3, "label": L("Très vraisemblable"), "color": "#e6862e"}, {"value": 4, "label": L("Quasi-certain"), "color": "#d64545"}]

def build_ebios_fr():
    d = load("demo-ebios-rm-systeme-d-information-objets.rae.json")

    # ---- B.2 source_risque : structure v1.3 (remplacement des attributs + remappage)
    sr = ot_by(d, "source_risque")
    sr["attributes"] = [
        {"code": "nom", "type": "text", "label": L("Nom")},
        {"code": "profil", "type": "select", "label": L("Profil"), "items": items([
            ("crime_organise", "Crime organisé"), ("interne_malveillant", "Interne malveillant"),
            ("amateur", "Amateur"), ("activiste_ideologique", "Activiste idéologique"),
            ("etatique", "Étatique"), ("concurrent", "Concurrent"), ("vengeur", "Vengeur")])},
        {"code": "description", "type": "textarea", "label": L("Description")},
        {"code": "objectif_vise", "type": "textarea", "label": L("Objectif visé")},
        {"code": "motivation", "type": "textarea", "label": L("Motivation")},
        {"code": "ressources", "type": "scale", "label": L("Ressources"), "items": SCALE3},
        {"code": "motivation_niv", "type": "scale", "label": L("Niveau de motivation"), "items": SCALE3},
        {"code": "activite_niv", "type": "scale", "label": L("Niveau d'activité"), "items": SCALE3},
        {"code": "pertinence_score", "type": "computed", "label": L("Pertinence (SR/OV)"),
         "expression": "=cf.motivation_niv+cf.ressources+cf.activite_niv", "result_type": "integer"},
        {"code": "niveau_pertinence", "type": "computed", "label": L("Niveau de pertinence"),
         "expression": '=IF(cf.pertinence_score>=8,"Élevée",IF(cf.pertinence_score>=5,"Moyenne","Faible"))', "result_type": "text"},
        {"code": "retenue", "type": "boolean", "label": L("Source retenue")},
        {"code": "justification", "type": "textarea", "label": L("Justification de la décision")},
    ]
    PROFIL = {"cybercriminel": "crime_organise", "etatique": "etatique", "initie": "interne_malveillant",
              "concurrent": "concurrent", "hacktiviste": "activiste_ideologique"}
    RESS = {"limitees": 1, "significatives": 2, "importantes": 3, "illimitees": 3}
    ACT = {"faible": 1, "moderee": 2, "elevee": 3}
    sr_extra = {  # motivation_niv, retenue, justification, description
        "SR1": (3, True, "Menace principale : rançongiciels très actifs contre les PME/ETI.", "Groupes spécialisés dans l'extorsion (ransomware-as-a-service)."),
        "SR2": (3, True, "Retenue au regard de la valeur des données et d'un positionnement durable possible.", "Acteur étatique disposant de moyens importants (APT)."),
        "SR3": (3, True, "Risque interne significatif (accès légitimes détournés).", "Salarié ou prestataire disposant d'accès internes."),
        "SR4": (2, False, "Écartée : intérêt et capacité jugés faibles dans ce contexte.", "Concurrent cherchant un avantage économique."),
        "SR5": (2, False, "Écartée : impact limité (indisponibilité temporaire) et faible ciblage.", "Collectif militant menant des actions de déni de service."),
    }
    for o in [x for x in d["objects"] if x["type"] == "source_risque"]:
        v = o["values"]
        v["profil"] = PROFIL[v.pop("categorie")]
        v["ressources"] = RESS[v.pop("ressources")]
        v["activite_niv"] = ACT[v.pop("activite")]
        v.pop("pertinence", None)
        mn, ret, just, desc = sr_extra[o["id"]]
        v["motivation_niv"] = mn; v["retenue"] = ret; v["justification"] = just; v["description"] = desc

    # ---- B.2 partie_prenante : structure v1.3 (menace/zone calculés)
    pp = ot_by(d, "partie_prenante")
    pp["attributes"] = [
        {"code": "nom", "type": "text", "label": L("Nom")},
        {"code": "categorie", "type": "select", "label": L("Catégorie"), "items": items([
            ("client", "Client"), ("fournisseur", "Fournisseur"), ("prestataire", "Prestataire"),
            ("partenaire", "Partenaire"), ("autorite", "Autorité")])},
        {"code": "description", "type": "textarea", "label": L("Description")},
        {"code": "dependance", "type": "scale", "label": L("Dépendance"), "items": SCALE4},
        {"code": "penetration", "type": "scale", "label": L("Pénétration"), "items": SCALE4},
        {"code": "maturite", "type": "scale", "label": L("Maturité cyber"), "items": SCALE4R},
        {"code": "confiance", "type": "scale", "label": L("Confiance"), "items": SCALE4R},
        {"code": "menace", "type": "computed", "label": L("Niveau de menace"),
         "expression": "=(cf.dependance*cf.penetration)/(cf.maturite*cf.confiance)", "result_type": "number",
         "decimals": 2, "alert": {"max": 2, "color": "#c0505a"}},
        {"code": "zone", "type": "computed", "label": L("Zone"),
         "expression": '=IF(cf.menace>=4,"Danger",IF(cf.menace>=2,"Contrôle","Veille"))', "result_type": "text"},
    ]
    for o in [x for x in d["objects"] if x["type"] == "partie_prenante"]:
        o["values"].pop("menace", None)   # remplacé par le calcul

    # ---- B.2b PP6 (Autorité de contrôle / CNIL) : un régulateur n'est pas une partie prenante de
    # l'écosystème EBIOS (aucune exposition numérique / dépendance). On le retire ; R4 (RGPD) est
    # rattaché au sous-traitant de paie (PP4), cohérent avec son scénario SS4/SO4.
    d["objects"] = [o for o in d["objects"] if o.get("id") != "PP6"]
    for r in d["risks"]:
        pp = r.get("custom", {}).get("parties_prenantes")
        if isinstance(pp, list) and "PP6" in pp:
            pp[:] = [x for x in pp if x != "PP6"] or ["PP4"]

    # ---- B.2 evenement_redoute : + impact_type
    er = ot_by(d, "evenement_redoute")
    add_attr(er, {"code": "impact_type", "type": "select", "label": L("Type d'impact"), "items": items([
        ("reglementaire", "Réglementaire"), ("operationnel", "Opérationnel"),
        ("humain", "Humain"), ("financier", "Financier"), ("reputationnel", "Réputationnel")])})
    IMPACT = {"ER1": "reputationnel", "ER2": "operationnel", "ER3": "reglementaire",
              "ER4": "reglementaire", "ER5": "operationnel", "ER6": "operationnel"}
    for o in [x for x in d["objects"] if x["type"] == "evenement_redoute"]:
        o["values"]["impact_type"] = IMPACT[o["id"]]

    # ---- B.1 nouveaux types d'objets (defs v1.3)
    d["object_types"].append({"code": "scenario_strategique", "label": L("Scénario stratégique"), "id_prefix": "SS", "name_attr": "nom",
        "attributes": [
            {"code": "nom", "type": "text", "label": L("Intitulé")},
            {"code": "source", "type": "reference", "label": L("Source de risque"), "object_type": "source_risque", "multiple": False},
            {"code": "evenement", "type": "reference", "label": L("Événement redouté"), "object_type": "evenement_redoute", "multiple": False},
            {"code": "valeur_metier", "type": "reference", "label": L("Valeur métier visée"), "object_type": "valeur_metier", "multiple": False},
            {"code": "parties_prenantes", "type": "reference", "label": L("Parties prenantes de l'écosystème"), "object_type": "partie_prenante", "multiple": True},
            {"code": "chemin", "type": "textarea", "label": L("Chemin d'attaque")},
            {"code": "ecosysteme", "type": "textarea", "label": L("Écosystème concerné")},
            {"code": "mesures_ecosysteme", "type": "textarea", "label": L("Mesures sur l'écosystème")},
            {"code": "option_traitement", "type": "select", "label": L("Option de traitement"), "items": items([
                ("reduire", "Réduire"), ("partager", "Partager"), ("eviter", "Éviter"), ("accepter", "Accepter")])},
            {"code": "gravite", "type": "scale", "label": L("Gravité retenue"), "items": GRAV4}]})
    d["object_types"].append({"code": "scenario_operationnel", "label": L("Scénario opérationnel"), "id_prefix": "SO", "name_attr": "nom",
        "attributes": [
            {"code": "nom", "type": "text", "label": L("Intitulé")},
            {"code": "scenario_strategique", "type": "reference", "label": L("Scénario stratégique"), "object_type": "scenario_strategique", "multiple": False},
            {"code": "chemin", "type": "textarea", "label": L("Mode opératoire")},
            {"code": "mitre", "type": "textarea", "label": L("Séquence MITRE ATT&CK")},
            {"code": "faisabilite", "type": "select", "label": L("Faisabilité"), "items": items([
                ("difficile", "Difficile"), ("moyenne", "Moyenne"), ("elevee", "Élevée")])},
            {"code": "vraisemblance", "type": "scale", "label": L("Vraisemblance globale"), "items": VRAIS4},
            {"code": "maillon_limitant", "type": "text", "label": L("Maillon limitant")},
            {"code": "niveau_risque", "type": "select", "label": L("Niveau de risque"), "items": items([
                ("faible", "Faible"), ("moyen", "Moyen"), ("eleve", "Élevé"), ("critique", "Critique")])}]})
    d["object_types"].append({"code": "exigence_socle", "label": L("Exigence du socle de sécurité"), "id_prefix": "EX", "name_attr": "exigence",
        "attributes": [
            {"code": "exigence", "type": "text", "label": L("Exigence")},
            {"code": "statut", "type": "select", "label": L("Statut"), "items": items([
                ("applique", "Appliqué"), ("partiel", "Partiel"), ("non_applique", "Non appliqué")])},
            {"code": "reference", "type": "text", "label": L("Référence")},
            {"code": "ecart", "type": "textarea", "label": L("Écart constaté")},
            {"code": "remediation", "type": "textarea", "label": L("Remédiation")}]})

    # ---- B.4 instances : scénarios stratégiques
    d["objects"] += [
        {"id": "SS1", "type": "scenario_strategique", "values": {
            "nom": "Rançongiciel paralysant la production applicative", "source": "SR1", "evenement": "ER2", "valeur_metier": "VM5",
            "parties_prenantes": ["PP1", "PP3"], "chemin": "Hameçonnage → exécution → propagation → chiffrement des serveurs et des sauvegardes en ligne.",
            "ecosysteme": "Hébergeur cloud et infogérant fournissent l'accès et l'administration.",
            "mesures_ecosysteme": "Exiger sauvegardes immuables et cloisonnement des accès d'administration.",
            "option_traitement": "reduire", "gravite": 4}},
        {"id": "SS2", "type": "scenario_strategique", "values": {
            "nom": "Exfiltration de la base clients", "source": "SR1", "evenement": "ER1", "valeur_metier": "VM2",
            "parties_prenantes": ["PP2"], "chemin": "Compromission d'un accès à privilèges → extraction de la base → menace de divulgation.",
            "ecosysteme": "Éditeur ERP disposant d'accès distants de maintenance.",
            "mesures_ecosysteme": "Encadrer les accès distants de l'éditeur (bastion, MFA, journalisation).",
            "option_traitement": "reduire", "gravite": 4}},
        {"id": "SS3", "type": "scenario_strategique", "values": {
            "nom": "Compromission via la chaîne d'approvisionnement (éditeur ERP)", "source": "SR2", "evenement": "ER3", "valeur_metier": "VM3",
            "parties_prenantes": ["PP2", "PP3"], "chemin": "Compromission de l'éditeur → mise à jour piégée → altération des données de facturation.",
            "ecosysteme": "Éditeur et infogérant dans la chaîne de mise à jour.",
            "mesures_ecosysteme": "Vérifier l'intégrité des mises à jour ; clauses de sécurité contractuelles.",
            "option_traitement": "partager", "gravite": 3}},
        {"id": "SS4", "type": "scenario_strategique", "values": {
            "nom": "Fuite de données RH via le sous-traitant de paie", "source": "SR3", "evenement": "ER4", "valeur_metier": "VM4",
            "parties_prenantes": ["PP4"], "chemin": "Accès abusif chez le sous-traitant → extraction des données de paie.",
            "ecosysteme": "Sous-traitant de la paie destinataire des données RH.",
            "mesures_ecosysteme": "Audit du sous-traitant ; minimisation des données transmises.",
            "option_traitement": "reduire", "gravite": 3}},
        {"id": "SS5", "type": "scenario_strategique", "values": {
            "nom": "Déni de service sur la relation client", "source": "SR5", "evenement": "ER6", "valeur_metier": "VM1",
            "parties_prenantes": ["PP1"], "chemin": "Campagne DDoS → saturation des services exposés → indisponibilité.",
            "ecosysteme": "Hébergeur cloud en première ligne.",
            "mesures_ecosysteme": "Protection anti-DDoS et plan de continuité côté hébergeur.",
            "option_traitement": "reduire", "gravite": 2}},
    ]
    # scénarios opérationnels
    d["objects"] += [
        {"id": "SO1", "type": "scenario_operationnel", "values": {
            "nom": "Rançongiciel — chaîne complète", "scenario_strategique": "SS1",
            "chemin": "Phishing ciblé, exécution d'un loader, élévation de privilèges, latéralisation, désactivation des sauvegardes, chiffrement.",
            "mitre": "TA0001 Initial Access (Phishing T1566) → TA0002 Execution → TA0004 Privilege Escalation → TA0008 Lateral Movement → TA0040 Impact (Inhibit System Recovery T1490 + Data Encrypted for Impact T1486)",
            "faisabilite": "elevee", "vraisemblance": 3, "maillon_limitant": "Sauvegardes hors-ligne immuables", "niveau_risque": "critique"}},
        {"id": "SO2", "type": "scenario_operationnel", "values": {
            "nom": "Exfiltration base clients — vol d'identifiants", "scenario_strategique": "SS2",
            "chemin": "Vol d'identifiants d'administration, accès à la base, extraction chiffrée, exfiltration.",
            "mitre": "TA0006 Credential Access → TA0007 Discovery → TA0009 Collection (Archive Collected Data T1560) → TA0010 Exfiltration",
            "faisabilite": "moyenne", "vraisemblance": 3, "maillon_limitant": "MFA + cloisonnement des accès", "niveau_risque": "eleve"}},
        {"id": "SO3", "type": "scenario_operationnel", "values": {
            "nom": "Supply chain — mise à jour piégée", "scenario_strategique": "SS3",
            "chemin": "Compromission de l'éditeur, injection dans un correctif, déploiement, altération des données.",
            "mitre": "TA0001 Initial Access (Supply Chain Compromise T1195) → TA0002 Execution → TA0040 Impact (Data Manipulation T1565)",
            "faisabilite": "difficile", "vraisemblance": 2, "maillon_limitant": "Contrôle d'intégrité des mises à jour", "niveau_risque": "eleve"}},
        {"id": "SO4", "type": "scenario_operationnel", "values": {
            "nom": "Fuite RH — accès abusif sous-traitant", "scenario_strategique": "SS4",
            "chemin": "Utilisation d'un compte du sous-traitant, extraction des bulletins, transmission externe.",
            "mitre": "TA0001 Initial Access (Trusted Relationship T1199) → TA0009 Collection → TA0010 Exfiltration",
            "faisabilite": "moyenne", "vraisemblance": 2, "maillon_limitant": "Journalisation et cloisonnement chez le sous-traitant", "niveau_risque": "moyen"}},
        {"id": "SO5", "type": "scenario_operationnel", "values": {
            "nom": "DDoS volumétrique", "scenario_strategique": "SS5",
            "chemin": "Botnet, saturation de la bande passante et des services applicatifs exposés.",
            "mitre": "TA0040 Impact (Network Denial of Service T1498)",
            "faisabilite": "elevee", "vraisemblance": 3, "maillon_limitant": "Service anti-DDoS de l'hébergeur", "niveau_risque": "moyen"}},
    ]
    # exigences du socle (hygiène ANSSI)
    d["objects"] += [
        {"id": "EX1", "type": "exigence_socle", "values": {"exigence": "Sauvegardes hors-ligne, testées et restaurables",
            "statut": "partiel", "reference": "Guide d'hygiène ANSSI — mesure 37 : Définir et appliquer une politique de sauvegarde des composants critiques", "ecart": "Sauvegardes en ligne exposées au chiffrement.",
            "remediation": "Mettre en place des sauvegardes immuables/hors-ligne et tester les restaurations."}},
        {"id": "EX2", "type": "exigence_socle", "values": {"exigence": "MFA sur les accès à privilèges et les accès distants",
            "statut": "partiel", "reference": "Guide d'hygiène ANSSI — mesure 13 : Privilégier lorsque c'est possible une authentification forte", "ecart": "MFA absente sur certains accès d'administration.",
            "remediation": "Généraliser le MFA et passer par un bastion d'administration."}},
        {"id": "EX3", "type": "exigence_socle", "values": {"exigence": "Cloisonnement et segmentation du réseau",
            "statut": "applique", "reference": "Guide d'hygiène ANSSI — mesure 19 : Segmenter le réseau et mettre en place un cloisonnement entre ces zones", "ecart": "",
            "remediation": ""}},
        {"id": "EX4", "type": "exigence_socle", "values": {"exigence": "Journalisation centralisée et supervision (SIEM)",
            "statut": "non_applique", "reference": "Guide d'hygiène ANSSI — mesure 36 : Activer et configurer les journaux des composants les plus importants", "ecart": "Pas de corrélation centralisée des journaux.",
            "remediation": "Déployer une collecte centralisée et des règles de détection."}},
        {"id": "EX5", "type": "exigence_socle", "values": {"exigence": "Gestion des vulnérabilités et des correctifs",
            "statut": "partiel", "reference": "Guide d'hygiène ANSSI — mesure 34 : Définir une politique de mise à jour des composants du système d'information", "ecart": "Délais de correctifs trop longs sur l'ERP.",
            "remediation": "Formaliser un cycle de patch et le suivi des vulnérabilités critiques."}},
    ]

    # ---- B.3 champs de risque (réfs scénarios + niveau source) + câblage
    for f in [
        {"code": "scenario_strat", "target": "risk", "type": "reference", "object_type": "scenario_strategique", "multiple": True, "label": L("Scénario stratégique"), "filterable": True},
        {"code": "scenario_op", "target": "risk", "type": "reference", "object_type": "scenario_operationnel", "multiple": True, "label": L("Scénario opérationnel"), "filterable": True},
        {"code": "niveau_source", "target": "risk", "type": "select", "label": L("Niveau de risque (source)"), "filterable": True, "items": items([
            ("faible", "Faible"), ("moyen", "Moyen"), ("eleve", "Élevé"), ("critique", "Critique")])},
    ]:
        add_field(d, f)
    WIRE = {  # risque -> (scenario_strat, scenario_op, niveau_source)
        "R8": (["SS1"], ["SO1"], "critique"), "R1": (["SS2"], ["SO2"], "eleve"),
        "R9": (["SS3"], ["SO3"], "eleve"), "R10": (["SS2", "SS3"], ["SO2"], "eleve"),
        "R4": (["SS4"], ["SO4"], "moyen"), "R11": (["SS5"], ["SO5"], "moyen"),
        "R12": (["SS2"], ["SO2"], "moyen")}   # erreur de config cloud → exposition base clients
    risk_by = {r["id"]: r for r in d["risks"]}
    for rid, (ss, so, niv) in WIRE.items():
        r = risk_by.get(rid)
        if r:
            r.setdefault("custom", {})
            r["custom"]["scenario_strat"] = ss; r["custom"]["scenario_op"] = so; r["custom"]["niveau_source"] = niv

    # ---- B.3 champs analyse (cadrage) — cotation.justification déjà présent
    for f in [
        {"code": "socle_securite", "target": "analysis", "type": "textarea", "label": L("Socle de sécurité de référence")},
        {"code": "recevabilite", "target": "analysis", "type": "textarea", "label": L("Recevabilité de l'étude")},
    ]:
        add_field(d, f)
    d.setdefault("custom", {})
    d["custom"]["socle_securite"] = ("Guide d'hygiène informatique de l'ANSSI et politique de sécurité interne (PSSI) ; "
                                     "conformité RGPD pour les données personnelles traitées par le SI de gestion.")
    d["custom"]["recevabilite"] = ("Étude recevable : périmètre du SI de gestion cadré, valeurs métier et biens supports "
                                   "identifiés, écosystème et sources de risque appréciés ; socle de sécurité évalué (voir exigences).")

    m = d["metadata"]
    m["title"] = "EBIOS RM enrichi — Système d'information de gestion"
    m["description"] = m["description"].replace(
        "illustrative et fictive.",
        "illustrative et fictive, générée par IA (Claude Opus 4.8).")
    m["revision"] = "2.0"
    m["updated_at"] = TODAY
    m["language"] = "fr"

    # ---- B.5 doublon source_risque (tag) ↔ sources_fiche (objets) : on supprime le tag. Les valeurs
    # sans objet (erreur/environnement/prestataire) ne sont pas des sources de risque EBIOS
    # (accidentelles, ou déjà modélisées en partie prenante) → pas d'enrichissement.
    for r in d["risks"]:
        r.get("custom", {}).pop("source_risque", None)
    d["custom_fields"] = [f for f in d["custom_fields"] if f.get("code") != "source_risque"]
    for f in d["custom_fields"]:
        if f.get("code") == "sources_fiche":
            f["label"] = L("Sources de risque")   # devient le seul : on retire le suffixe « (fiches) »

    # ---- B.6 réordonnancement des champs perso : regroupement par cible + ordre de lecture EBIOS.
    apply_field_order(d, {
        "analysis": ["referentiels", "perimetre", "socle_securite", "recevabilite"],
        "risk": ["vm_impactees", "biens_concernes", "evenements", "impacts", "sources_fiche",
                 "niveau_source", "parties_prenantes", "scenario_strat", "scenario_op"],
        "cotation": ["justification", "date_cotation"],
        "measure": ["fonction", "domaine", "avancement"],
        "link": ["effet"],
    })
    reorder_custom_fields(d, ("analysis", "risk", "cotation", "measure", "link"))

    # ---- B.6b types d'objets dans l'ordre des ateliers EBIOS RM (A1 cadrage/socle → A4 opérationnel).
    OT_ORDER = ["valeur_metier", "bien_support", "evenement_redoute", "exigence_socle",
                "source_risque", "partie_prenante", "scenario_strategique", "scenario_operationnel"]
    _otr = {c: i for i, c in enumerate(OT_ORDER)}
    d["object_types"].sort(key=lambda ot: _otr.get(ot["code"], len(OT_ORDER)))

    # ---- B.7 configuration du rapport : mêmes rubriques/ordre que l'AIPD, mais NON éclaté
    # (analyse complète, iteration.by="none" → les sections activées sont rendues dans l'ordre du
    # tableau ; les zones ne servent qu'en mode éclaté mais sont conservées par parité).
    d.setdefault("extensions", {}).setdefault("display", {})["report"] = {
        "scope": "all", "orientation": "portrait",
        "cover": {"on": True}, "toc": {"on": True},
        "iteration": {"by": "none", "sort": "alpha"},
        "sections": [
            # cadrage & fond de l'étude (ateliers 1-4)
            {"id": "metadata", "on": True, "zone": "header"},
            {"id": "presentation", "on": True, "zone": "header"},
            {"id": "objects", "on": True, "zone": "header", "view": "detail"},   # objets juste sous Présentation
            {"id": "matrix_ir", "on": False, "zone": "repeated"},
            {"id": "matrix_initial", "on": False, "zone": "repeated"},
            {"id": "matrix_residual", "on": False, "zone": "repeated"},
            # atelier 5 — la photo du risque (synthèse groupée)
            {"id": "summary_counts", "on": True, "zone": "appendix"},
            {"id": "summary_distribution", "on": True, "zone": "appendix"},
            {"id": "matrix_traj", "on": True, "zone": "repeated"},
            {"id": "radar", "on": True, "zone": "appendix", "dim": "vm_impactees", "metric": "max", "eval": "both-over"},
            # registre détaillé (colonnes EBIOS : scénario stratégique + niveau de source)
            {"id": "risks_table", "on": True, "zone": "repeated",
             "columns": ["id", "risk", "cat", "cf:scenario_strat", "cf:niveau_source", "initial", "residual", "measures"]},
            {"id": "risks_detail", "on": True, "zone": "repeated"},
            # traitement du risque (mesures + PACS groupés)
            {"id": "measures_table", "on": True, "zone": "repeated"},
            {"id": "measures_detail", "on": True, "zone": "repeated"},
            {"id": "links_table", "on": False, "zone": "repeated"},
            {"id": "links_detail", "on": True, "zone": "repeated"},
            {"id": "action_plan", "on": True, "zone": "appendix", "view": "due_date"},
            # annexes
            {"id": "grid_axes", "on": True, "zone": "appendix"},
            {"id": "grid_criticality", "on": True, "zone": "appendix"},
            {"id": "field_glossary", "on": True, "zone": "appendix"},
        ],
    }

    save(d, "demo-ebios-rm-systeme-d-information-objets-enrichi.rae.json")


if __name__ == "__main__":
    build_aipd_fr()
    build_ebios_fr()
