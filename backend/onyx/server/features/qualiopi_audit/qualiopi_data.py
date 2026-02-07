from dataclasses import dataclass
from dataclasses import field
from typing import Final

from onyx.server.features.qualiopi_audit.models import ActionCategory


@dataclass(frozen=True)
class IndicatorDef:
    id: int
    name: str
    applicable_to: frozenset[ActionCategory]
    certifications_only: bool = False
    cfa_only: bool = False
    nouveau_entrant_adapted: bool = False


@dataclass(frozen=True)
class CriterionDef:
    id: int
    name: str
    indicator_ids: tuple[int, ...]


CRITERIA: Final[dict[int, CriterionDef]] = {
    1: CriterionDef(
        id=1,
        name="Conditions d'information du public",
        indicator_ids=(1, 2, 3),
    ),
    2: CriterionDef(
        id=2,
        name="Identification precise des objectifs",
        indicator_ids=(4, 5, 6, 7),
    ),
    3: CriterionDef(
        id=3,
        name="Adaptation aux publics beneficiaires",
        indicator_ids=(8, 9, 10, 11),
    ),
    4: CriterionDef(
        id=4,
        name="Adequation des moyens pedagogiques",
        indicator_ids=(12, 13, 14, 15, 16),
    ),
    5: CriterionDef(
        id=5,
        name="Qualification et developpement des competences",
        indicator_ids=(17, 18, 19, 20, 21),
    ),
    6: CriterionDef(
        id=6,
        name="Inscription dans l'environnement professionnel",
        indicator_ids=(22, 23, 24, 25, 26, 27),
    ),
    7: CriterionDef(
        id=7,
        name="Recueil et prise en compte des appreciations",
        indicator_ids=(28, 29, 30, 31, 32),
    ),
}

_ALL: Final[frozenset[ActionCategory]] = frozenset({"OF", "CFA", "CBC", "VAE"})
_CFA_ONLY: Final[frozenset[ActionCategory]] = frozenset({"CFA"})

INDICATORS: Final[dict[int, IndicatorDef]] = {
    1: IndicatorDef(1, "Information accessible au public", _ALL),
    2: IndicatorDef(2, "Indicateurs de resultats", _ALL, nouveau_entrant_adapted=True),
    3: IndicatorDef(
        3,
        "Taux d'obtention des certifications",
        _ALL,
        certifications_only=True,
        nouveau_entrant_adapted=True,
    ),
    4: IndicatorDef(4, "Analyse des besoins du beneficiaire", _ALL),
    5: IndicatorDef(5, "Objectifs de la prestation et leur adequation", _ALL),
    6: IndicatorDef(6, "Contenus et modalites de mise en oeuvre", _ALL),
    7: IndicatorDef(
        7,
        "Adequation des contenus aux exigences de la certification",
        _CFA_ONLY,
        certifications_only=True,
    ),
    8: IndicatorDef(
        8, "Procedures de positionnement et d'evaluation des acquis", _ALL
    ),
    9: IndicatorDef(9, "Conditions de deroulement de la prestation", _ALL),
    10: IndicatorDef(10, "Adaptation de la prestation aux beneficiaires", _ALL),
    11: IndicatorDef(
        11,
        "Evaluation de l'atteinte des objectifs",
        _ALL,
        nouveau_entrant_adapted=True,
    ),
    12: IndicatorDef(12, "Moyens humains et techniques adaptes", _ALL),
    13: IndicatorDef(
        13,
        "Coordination des intervenants",
        _ALL,
        nouveau_entrant_adapted=True,
    ),
    14: IndicatorDef(
        14,
        "Ressources pedagogiques a disposition",
        _ALL,
        nouveau_entrant_adapted=True,
    ),
    15: IndicatorDef(
        15, "Parcours de formation des apprentis", _CFA_ONLY, cfa_only=True
    ),
    16: IndicatorDef(
        16,
        "Missions tuteur/maitre d'apprentissage",
        _CFA_ONLY,
        cfa_only=True,
    ),
    17: IndicatorDef(17, "Competences des intervenants", _ALL),
    18: IndicatorDef(18, "Mobilisation des intervenants internes/externes", _ALL),
    19: IndicatorDef(
        19,
        "Developpement des competences des salaries",
        _ALL,
        nouveau_entrant_adapted=True,
    ),
    20: IndicatorDef(20, "Formateurs occasionnels (respect reglementation)", _ALL),
    21: IndicatorDef(21, "Competences et habilitations requises", _ALL),
    22: IndicatorDef(
        22,
        "Veille legale et reglementaire",
        _ALL,
        nouveau_entrant_adapted=True,
    ),
    23: IndicatorDef(23, "Veille emplois, metiers, competences", _ALL),
    24: IndicatorDef(
        24,
        "Veille innovations pedagogiques et technologiques",
        _ALL,
        nouveau_entrant_adapted=True,
    ),
    25: IndicatorDef(
        25,
        "Veille handicap",
        _CFA_ONLY,
        cfa_only=True,
        nouveau_entrant_adapted=True,
    ),
    26: IndicatorDef(
        26,
        "Referent handicap et accessibilite",
        _CFA_ONLY,
        cfa_only=True,
        nouveau_entrant_adapted=True,
    ),
    27: IndicatorDef(27, "Partenariats et reseaux", _ALL),
    28: IndicatorDef(
        28, "Recueil des appreciations des parties prenantes", _ALL
    ),
    29: IndicatorDef(29, "Traitement des difficultes rencontrees", _ALL),
    30: IndicatorDef(30, "Traitement des reclamations", _ALL),
    31: IndicatorDef(
        31, "Prise en compte des appreciations pour l'amelioration", _ALL
    ),
    32: IndicatorDef(
        32,
        "Mesures d'amelioration continue",
        _ALL,
        nouveau_entrant_adapted=True,
    ),
}

NOUVEAU_ENTRANT_INDICATOR_IDS: Final[frozenset[int]] = frozenset(
    {2, 3, 11, 13, 14, 19, 22, 24, 25, 26, 32}
)


def get_applicable_indicators(
    categories: list[ActionCategory],
    nouveau_entrant: bool,
    certifications_formations: bool,
) -> list[IndicatorDef]:
    cat_set = frozenset(categories)
    result: list[IndicatorDef] = []

    for ind in INDICATORS.values():
        if not ind.applicable_to.intersection(cat_set):
            if not ind.certifications_only:
                continue
        if ind.certifications_only and not certifications_formations:
            if "CFA" not in cat_set:
                continue
        if ind.cfa_only and "CFA" not in cat_set:
            continue
        result.append(ind)

    return result


INDICATOR_INSTRUCTIONS: Final[dict[int, str]] = {
    1: """INDICATEUR 1 : Information accessible au public
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier que le site web est accessible (code 200)
- Rechercher une page "formations" ou "catalogue" ou equivalent
- Pour CHAQUE formation listee, verifier la presence de :
  - Intitule de la formation
  - Objectifs pedagogiques (ce que le stagiaire saura faire)
  - Duree (en heures ou jours)
  - Prerequis (ou mention "aucun prerequis")
  - Tarif (ou mention "sur devis" ou "nous contacter")
  - Modalites d'evaluation (comment on evalue les acquis)
  - Methodes pedagogiques mobilisees
- Verifier presence d'un contact (email OU telephone OU formulaire)
- Verifier presence des delais d'acces (ex: "inscription jusqu'a 14 jours avant")
- Verifier presence d'informations sur l'accessibilite handicap
- Verifier que les CGV sont accessibles (lien ou document)

Controles NICE-TO-HAVE :
- Verifier que les informations sont a jour (date de mise a jour visible)
- Verifier la coherence des tarifs entre les pages
- Verifier presence du NDA sur le site
- Verifier presence de la certification Qualiopi (logo + n certificat)
- Verifier que le reglement interieur est accessible
- Verifier presence des modalites de paiement

Si NC, localiser :
- Page concernee : /formations, /catalogue, ou page d'accueil
- Section manquante : preciser quel element est absent
- Exemple de correction : fournir un texte type""",
    2: """INDICATEUR 2 : Indicateurs de resultats
Applicable a : OF, CFA, CBC, VAE
Nouveau entrant : Modalites adaptees (process formalise suffit)

Controles OBLIGATOIRES :
- Verifier la presence d'indicateurs de resultats publies
- Les indicateurs doivent etre ADAPTES a la nature des prestations :
  - Pour OF : taux de satisfaction, taux de completion
  - Pour CFA : taux d'obtention diplome, taux d'insertion, taux de rupture
  - Pour CBC : taux de satisfaction, taux de realisation du plan d'action
  - Pour VAE : taux de validation totale/partielle
- Verifier que les indicateurs portent sur une periode identifiee (annee N-1, etc.)
- Verifier que les indicateurs sont diffuses au public (site web, plaquette)

Si NOUVEAU ENTRANT :
- Verifier que le process de collecte des indicateurs est formalise
- Accepter l'absence de donnees chiffrees si < 1 an d'activite
- Verifier qu'un outil de collecte est prevu (questionnaire, etc.)""",
    3: """INDICATEUR 3 : Taux d'obtention des certifications
Applicable a : Formations certifiantes uniquement (RNCP, RS, CQP, diplomes)
Nouveau entrant : Modalites adaptees

Controles OBLIGATOIRES :
- Identifier si l'organisme propose des formations certifiantes
- Si OUI, verifier pour chaque certification :
  - Taux d'obtention de la certification (ou des blocs de competences)
  - Possibilites de valider un ou des blocs de competences
  - Equivalences possibles
  - Passerelles vers d'autres certifications
  - Suites de parcours possibles
  - Debouches (metiers vises, secteurs)
- Verifier que ces informations sont accessibles au public

Si NON APPLICABLE :
- Si aucune formation certifiante : indicateur non audite
- Documenter : "Pas de formation certifiante au catalogue" """,
    4: """INDICATEUR 4 : Analyse des besoins du beneficiaire
Applicable a : OF, CFA, CBC, VAE (avec specificites)

Controles OBLIGATOIRES :
- Verifier l'existence d'un processus d'analyse des besoins
- Verifier que l'analyse prend en compte :
  - Le besoin du beneficiaire (stagiaire)
  - Le contexte professionnel (entreprise si concernee)
  - Le financeur (si applicable)
- Verifier la tracabilite de l'analyse (document, compte-rendu, questionnaire)

SPECIFICITES PAR CATEGORIE :
- Pour CBC : verifier l'analyse de la demande et de la situation professionnelle
- Pour VAE : verifier l'analyse de la faisabilite du projet VAE
- Pour CFA : verifier la prise en compte du projet professionnel de l'apprenti

Documents a rechercher :
- Questionnaire de recueil des besoins
- Compte-rendu d'entretien prealable
- Fiche de positionnement
- Analyse de la demande (pour CBC/VAE)""",
    5: """INDICATEUR 5 : Objectifs de la prestation et leur adequation
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier que les objectifs sont definis pour chaque prestation
- Verifier que les objectifs sont :
  - Mesurables (on peut verifier s'ils sont atteints)
  - Realistes (atteignables dans la duree prevue)
  - En lien avec le besoin identifie (indicateur 4)
- Verifier la communication des objectifs au beneficiaire AVANT la formation
- Verifier la presence des objectifs dans les documents contractuels

Formulation attendue :
- BONNE formulation : "A l'issue de la formation, le stagiaire sera capable de..."
- MAUVAISE formulation : "Decouvrir les bases de..." """,
    6: """INDICATEUR 6 : Contenus et modalites de mise en oeuvre
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier la presence d'un programme detaille pour chaque formation
- Le programme doit contenir :
  - Les contenus (themes, modules, sequences)
  - La duree de chaque module/sequence
  - Les modalites (presentiel, distanciel, mixte)
  - Les methodes pedagogiques
  - Les moyens pedagogiques (supports, outils)
- Verifier la coherence entre le programme et les objectifs (indicateur 5)

SPECIFICITES :
- Pour CFA : verifier l'articulation avec le referentiel du diplome
- Pour VAE : verifier les etapes de l'accompagnement
- Pour CBC : verifier les phases du bilan (preliminaire, investigation, conclusion)""",
    7: """INDICATEUR 7 : Adequation des contenus aux exigences de la certification
Applicable a : CFA et formations certifiantes uniquement

Controles OBLIGATOIRES :
- Verifier que le programme couvre le referentiel de la certification
- Verifier la correspondance entre :
  - Blocs de competences du referentiel
  - Modules de formation proposes
- Verifier que les modalites d'evaluation correspondent aux exigences
- Verifier la mise a jour en cas d'evolution du referentiel

Si NON APPLICABLE :
- Si pas de formation certifiante : indicateur non audite""",
    8: """INDICATEUR 8 : Procedures de positionnement et d'evaluation des acquis
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier l'existence d'une procedure de positionnement a l'entree
- La procedure doit permettre d'evaluer :
  - Les acquis du beneficiaire (connaissances, competences)
  - L'adequation avec les prerequis
- Verifier la tracabilite du positionnement (test, entretien, questionnaire)
- Verifier que le positionnement est realise AVANT ou AU DEBUT de la formation

SPECIFICITES :
- Pour CBC : positionnement = analyse de la demande (phase preliminaire)
- Pour VAE : positionnement = etude de faisabilite""",
    9: """INDICATEUR 9 : Conditions de deroulement de la prestation
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier l'information du beneficiaire sur les conditions de deroulement
- Informations a communiquer :
  - Lieu(x) de formation
  - Horaires
  - Modalites d'acces (presentiel/distanciel)
  - Reglement interieur
  - Contacts en cas de difficulte
- Verifier la communication de ces informations AVANT le demarrage
- Verifier l'existence d'un livret d'accueil ou equivalent""",
    10: """INDICATEUR 10 : Adaptation de la prestation aux beneficiaires
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier que la prestation peut etre adaptee au beneficiaire
- Formes d'adaptation possibles :
  - Adaptation du rythme
  - Adaptation des supports
  - Adaptation des modalites pedagogiques
  - Amenagements specifiques (handicap, contraintes pro)
- Verifier la tracabilite des adaptations realisees
- Verifier la prise en compte des situations particulieres""",
    11: """INDICATEUR 11 : Evaluation de l'atteinte des objectifs
Applicable a : OF, CFA, CBC, VAE
Nouveau entrant : Modalites adaptees

Controles OBLIGATOIRES :
- Verifier l'existence de modalites d'evaluation des acquis
- L'evaluation doit porter sur l'atteinte des objectifs definis (indicateur 5)
- Verifier la tracabilite des evaluations :
  - Supports d'evaluation (QCM, exercices, mises en situation)
  - Resultats des evaluations
  - Attestation de fin de formation mentionnant les acquis
- Verifier que l'evaluation est realisee EN COURS ou EN FIN de formation""",
    12: """INDICATEUR 12 : Moyens humains et techniques adaptes
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier la description des moyens humains :
  - Qualification des formateurs/intervenants
  - Experience dans le domaine
- Verifier la description des moyens techniques :
  - Locaux (si presentiel)
  - Equipements pedagogiques
  - Outils numeriques (si distanciel)
- Verifier l'adequation des moyens avec les prestations proposees
- Verifier la mise a disposition effective des moyens annonces""",
    13: """INDICATEUR 13 : Coordination des intervenants
Applicable a : OF, CFA, CBC, VAE
Nouveau entrant : Modalites adaptees

Controles OBLIGATOIRES :
- Verifier l'existence d'une coordination entre intervenants (si plusieurs)
- Formes de coordination :
  - Reunions pedagogiques
  - Outils de suivi partages
  - Fiches de liaison
- Verifier la designation d'un responsable pedagogique ou coordinateur
- Verifier la tracabilite de la coordination (comptes-rendus, etc.)

SI FORMATEUR UNIQUE :
- Verifier la coordination avec les fonctions support (admin, commercial)""",
    14: """INDICATEUR 14 : Ressources pedagogiques a disposition
Applicable a : OF, CFA, CBC, VAE
Nouveau entrant : Modalites adaptees

Controles OBLIGATOIRES :
- Verifier la mise a disposition de ressources pedagogiques
- Types de ressources :
  - Supports de cours (papier ou numerique)
  - Exercices, cas pratiques
  - Documentation complementaire
  - Acces a des plateformes/outils
- Verifier que les ressources sont accessibles aux beneficiaires
- Verifier la mise a jour des ressources""",
    15: """INDICATEUR 15 : Parcours de formation des apprentis (CFA)
Applicable a : CFA uniquement

Controles OBLIGATOIRES :
- Verifier l'existence de parcours de formation formalises
- Le parcours doit integrer :
  - Alternance centre de formation / entreprise
  - Progression pedagogique
  - Evaluations en cours de formation (CCF si applicable)
- Verifier la coordination avec l'entreprise d'accueil
- Verifier le suivi du parcours de chaque apprenti""",
    16: """INDICATEUR 16 : Missions tuteur/maitre d'apprentissage (CFA)
Applicable a : CFA uniquement

Controles OBLIGATOIRES :
- Verifier l'information de l'employeur sur les missions du maitre d'apprentissage
- Missions a communiquer :
  - Accompagnement de l'apprenti
  - Transmission des savoir-faire
  - Liaison avec le CFA
  - Participation aux evaluations
- Verifier la tracabilite de cette information (courrier, convention, etc.)
- Verifier l'accompagnement propose au maitre d'apprentissage""",
    17: """INDICATEUR 17 : Competences des intervenants
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier la detention des competences par les intervenants
- Pour chaque intervenant, verifier :
  - Qualification (diplomes, certifications)
  - Experience professionnelle dans le domaine
  - Experience pedagogique
- Verifier l'adequation entre les competences et les prestations assurees
- Verifier la conservation des justificatifs (CV, diplomes)""",
    18: """INDICATEUR 18 : Mobilisation des intervenants internes/externes
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Identifier les intervenants internes et externes
- Pour les intervenants EXTERNES, verifier :
  - Contrat de prestation ou convention
  - Transmission des informations necessaires
  - Respect des exigences qualite de l'organisme
- Pour les intervenants INTERNES, verifier :
  - Fiche de poste ou missions definies
  - Integration dans l'equipe pedagogique
- Verifier la procedure de selection des intervenants""",
    19: """INDICATEUR 19 : Developpement des competences des salaries
Applicable a : OF, CFA, CBC, VAE
Nouveau entrant : Modalites adaptees

Controles OBLIGATOIRES :
- Verifier l'existence d'un plan de developpement des competences
- Le plan doit concerner :
  - Les formateurs (competences pedagogiques, techniques)
  - Le personnel administratif (si concerne par la qualite)
- Verifier la tracabilite des formations suivies par les salaries
- Verifier l'adequation avec les besoins identifies""",
    20: """INDICATEUR 20 : Formateurs occasionnels (respect reglementation)
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Identifier si l'organisme fait appel a des formateurs occasionnels
- Si OUI, verifier le respect de la reglementation :
  - Statut juridique conforme (salarie, auto-entrepreneur, societe)
  - Contrat ou convention en place
  - Respect des obligations sociales et fiscales
- Verifier l'absence de salariat deguise""",
    21: """INDICATEUR 21 : Competences et habilitations requises
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Identifier les formations necessitant des competences specifiques
- Pour ces formations, verifier :
  - Habilitations requises (ex: habilitation electrique, CACES)
  - Certifications professionnelles
  - Agrements (si reglementes)
- Verifier la validite des habilitations (dates d'expiration)
- Verifier la conservation des justificatifs""",
    22: """INDICATEUR 22 : Veille legale et reglementaire
Applicable a : OF, CFA, CBC, VAE
Nouveau entrant : Modalites adaptees

Controles OBLIGATOIRES :
- Verifier l'existence d'un dispositif de veille legale et reglementaire
- Domaines de veille :
  - Reglementation de la formation professionnelle
  - Obligations des organismes de formation
  - Evolutions du cadre Qualiopi
- Verifier la tracabilite de la veille (sources, frequence, actions)
- Verifier l'impact de la veille sur les pratiques""",
    23: """INDICATEUR 23 : Veille emplois, metiers, competences
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier l'existence d'une veille sur les evolutions :
  - Des competences recherchees
  - Des metiers (emergents, en transformation)
  - Du marche de l'emploi dans les secteurs concernes
- Verifier l'utilisation de cette veille pour :
  - Faire evoluer l'offre de formation
  - Adapter les contenus
- Verifier la tracabilite (sources, analyses, decisions)""",
    24: """INDICATEUR 24 : Veille innovations pedagogiques et technologiques
Applicable a : OF, CFA, CBC, VAE
Nouveau entrant : Modalites adaptees

Controles OBLIGATOIRES :
- Verifier l'existence d'une veille sur les innovations :
  - Pedagogiques (methodes, approches)
  - Technologiques (outils, plateformes)
- Verifier l'experimentation ou l'integration d'innovations
- Verifier la tracabilite (sources, tests, deploiements)""",
    25: """INDICATEUR 25 : Veille handicap (CFA obligatoire)
Applicable a : CFA (obligatoire), autres (facultatif)
Nouveau entrant : Modalites adaptees

Controles OBLIGATOIRES :
- Pour CFA : verifier l'existence d'une veille specifique handicap
- Domaines de veille :
  - Reglementation accessibilite
  - Aides et financements disponibles
  - Bonnes pratiques d'accueil
  - Evolutions des accompagnements possibles
- Verifier le lien avec le referent handicap (indicateur 26)
- Verifier la diffusion des informations en interne""",
    26: """INDICATEUR 26 : Referent handicap et accessibilite
Applicable a : CFA (obligatoire), autres (recommande)
Nouveau entrant : Modalites adaptees

Controles OBLIGATOIRES :
- Pour CFA : verifier la designation d'un referent handicap
- Verifier les missions du referent :
  - Accueil et accompagnement des personnes handicapees
  - Mobilisation des aides et adaptations
  - Lien avec les partenaires specialises
- Verifier les conditions d'accessibilite de l'organisme :
  - Locaux (si presentiel)
  - Supports pedagogiques
  - Outils numeriques
- Verifier l'information sur l'accessibilite (site web, documents)""",
    27: """INDICATEUR 27 : Partenariats et reseaux
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier l'existence de partenariats ou l'inscription dans des reseaux
- Types de partenariats :
  - Avec des entreprises (stages, alternance)
  - Avec d'autres organismes de formation
  - Avec des acteurs de l'emploi (France Travail, missions locales)
  - Avec des branches professionnelles
- Verifier la formalisation des partenariats (conventions, accords)
- Verifier l'utilite des partenariats pour les beneficiaires""",
    28: """INDICATEUR 28 : Recueil des appreciations des parties prenantes
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier l'existence d'un dispositif de recueil des appreciations
- Parties prenantes a interroger :
  - Beneficiaires (stagiaires, apprentis)
  - Financeurs (OPCO, entreprises, particuliers)
  - Equipes pedagogiques
  - Entreprises d'accueil (pour CFA)
- Verifier les outils de recueil (questionnaires, entretiens)
- Verifier la regularite du recueil (a chaud, a froid)
- Verifier la conservation des retours""",
    29: """INDICATEUR 29 : Traitement des difficultes rencontrees
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier l'existence d'un processus de traitement des difficultes
- Types de difficultes :
  - Difficultes pedagogiques des beneficiaires
  - Difficultes organisationnelles
  - Situations particulieres (abandon, conflit)
- Verifier la reactivite de traitement
- Verifier la tracabilite (signalement, analyse, actions, suivi)
- Verifier l'information des beneficiaires sur ce processus""",
    30: """INDICATEUR 30 : Traitement des reclamations
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier l'existence d'une procedure de traitement des reclamations
- La procedure doit prevoir :
  - Modalites de depot d'une reclamation
  - Delai de traitement
  - Reponse au reclamant
  - Actions correctives si necessaire
- Verifier l'information des beneficiaires sur cette procedure
- Verifier la tracabilite des reclamations (registre, suivi)
- Verifier le traitement effectif des reclamations recues""",
    31: """INDICATEUR 31 : Prise en compte des appreciations pour l'amelioration
Applicable a : OF, CFA, CBC, VAE

Controles OBLIGATOIRES :
- Verifier que les appreciations (indicateur 28) sont analysees
- Verifier que l'analyse conduit a des actions d'amelioration :
  - Identification des points forts et axes d'amelioration
  - Priorisation des actions
  - Mise en oeuvre des ameliorations
- Verifier la tracabilite (comptes-rendus, plans d'action)
- Verifier le lien entre les retours et les evolutions constatees""",
    32: """INDICATEUR 32 : Mesures d'amelioration continue
Applicable a : OF, CFA, CBC, VAE
Nouveau entrant : Modalites adaptees

Controles OBLIGATOIRES :
- Verifier l'existence d'une demarche d'amelioration continue
- La demarche doit s'appuyer sur :
  - Analyse des appreciations (indicateur 31)
  - Analyse des reclamations (indicateur 30)
  - Analyse des indicateurs de resultats (indicateur 2)
- Verifier la mise en oeuvre effective de mesures d'amelioration
- Verifier le suivi et l'evaluation des mesures prises
- Verifier la formalisation (revue de direction, bilan qualite)""",
}


def get_indicator_instructions(indicator_id: int) -> str:
    return INDICATOR_INSTRUCTIONS[indicator_id]
