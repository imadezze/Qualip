export type ActionCategory = "OF" | "CFA" | "CBC" | "VAE";
export type AuditMode = "initial" | "surveillance" | "renouvellement";
export type IndicatorStatus =
  | "valid"
  | "nc_mineure"
  | "nc_majeure"
  | "non_applicable";
export type AuditStatus = "pret_pour_audit" | "non_pret_pour_audit";
export type CriterionProgressStatus =
  | "pending"
  | "in_progress"
  | "completed"
  | "error";

export interface QualiopiOnboardingData {
  nda: string;
  categorie_actions: ActionCategory[];
  mode_audit: AuditMode;
  nouveau_entrant: boolean;
  site_web: string | null;
  sous_traitance: Record<string, boolean>;
  certifications_formations: boolean;
}

export interface IndicatorResult {
  id: number;
  status: IndicatorStatus;
  issues: string[];
  corrective_plan: string[];
}

export interface AuditOverview {
  total_indicators: number;
  valid: number;
  nc_mineure: number;
  nc_majeure: number;
  non_applicable: number;
}

export interface AuditReport {
  vue_ensemble: AuditOverview;
  status: AuditStatus;
  indicateurs: IndicatorResult[];
}

export interface AuditProgressEvent {
  event_type: "criterion_progress" | "audit_complete";
  criterion_id: number | null;
  criterion_name: string | null;
  status: CriterionProgressStatus | null;
  indicators_processed: IndicatorResult[];
  report: AuditReport | null;
}

export interface CriterionDefinition {
  id: number;
  name: string;
  indicatorIds: number[];
}

export interface IndicatorDefinition {
  id: number;
  name: string;
}

export const CRITERIA_DEFINITIONS: CriterionDefinition[] = [
  {
    id: 1,
    name: "Conditions d'information du public",
    indicatorIds: [1, 2, 3],
  },
  {
    id: 2,
    name: "Identification precise des objectifs",
    indicatorIds: [4, 5, 6, 7],
  },
  {
    id: 3,
    name: "Adaptation aux publics beneficiaires",
    indicatorIds: [8, 9, 10, 11],
  },
  {
    id: 4,
    name: "Adequation des moyens pedagogiques",
    indicatorIds: [12, 13, 14, 15, 16],
  },
  {
    id: 5,
    name: "Qualification et developpement des competences",
    indicatorIds: [17, 18, 19, 20, 21],
  },
  {
    id: 6,
    name: "Inscription dans l'environnement professionnel",
    indicatorIds: [22, 23, 24, 25, 26, 27],
  },
  {
    id: 7,
    name: "Recueil et prise en compte des appreciations",
    indicatorIds: [28, 29, 30, 31, 32],
  },
];

export const INDICATOR_DEFINITIONS: Record<number, IndicatorDefinition> = {
  1: { id: 1, name: "Information accessible au public" },
  2: { id: 2, name: "Indicateurs de resultats" },
  3: { id: 3, name: "Taux d'obtention des certifications" },
  4: { id: 4, name: "Analyse des besoins du beneficiaire" },
  5: { id: 5, name: "Objectifs de la prestation et leur adequation" },
  6: { id: 6, name: "Contenus et modalites de mise en oeuvre" },
  7: {
    id: 7,
    name: "Adequation des contenus aux exigences de la certification",
  },
  8: {
    id: 8,
    name: "Procedures de positionnement et d'evaluation des acquis",
  },
  9: { id: 9, name: "Conditions de deroulement de la prestation" },
  10: { id: 10, name: "Adaptation de la prestation aux beneficiaires" },
  11: { id: 11, name: "Evaluation de l'atteinte des objectifs" },
  12: { id: 12, name: "Moyens humains et techniques adaptes" },
  13: { id: 13, name: "Coordination des intervenants" },
  14: { id: 14, name: "Ressources pedagogiques a disposition" },
  15: { id: 15, name: "Parcours de formation des apprentis" },
  16: { id: 16, name: "Missions tuteur/maitre d'apprentissage" },
  17: { id: 17, name: "Competences des intervenants" },
  18: { id: 18, name: "Mobilisation des intervenants internes/externes" },
  19: { id: 19, name: "Developpement des competences des salaries" },
  20: { id: 20, name: "Formateurs occasionnels" },
  21: { id: 21, name: "Competences et habilitations requises" },
  22: { id: 22, name: "Veille legale et reglementaire" },
  23: { id: 23, name: "Veille emplois, metiers, competences" },
  24: { id: 24, name: "Veille innovations pedagogiques et technologiques" },
  25: { id: 25, name: "Veille handicap" },
  26: { id: 26, name: "Referent handicap et accessibilite" },
  27: { id: 27, name: "Partenariats et reseaux" },
  28: { id: 28, name: "Recueil des appreciations des parties prenantes" },
  29: { id: 29, name: "Traitement des difficultes rencontrees" },
  30: { id: 30, name: "Traitement des reclamations" },
  31: {
    id: 31,
    name: "Prise en compte des appreciations pour l'amelioration",
  },
  32: { id: 32, name: "Mesures d'amelioration continue" },
};
