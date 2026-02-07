from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


ActionCategory = Literal["OF", "CFA", "CBC", "VAE"]
AuditMode = Literal["initial", "surveillance", "renouvellement"]
IndicatorStatus = Literal["valid", "nc_mineure", "nc_majeure", "non_applicable"]
AuditStatus = Literal["pret_pour_audit", "non_pret_pour_audit"]
CriterionProgressStatus = Literal["pending", "in_progress", "completed", "error"]


class QualiopiOnboardingData(BaseModel):
    nda: str = Field(min_length=11, max_length=11)
    categorie_actions: list[ActionCategory]
    mode_audit: AuditMode
    nouveau_entrant: bool
    site_web: str | None = None
    sous_traitance: dict[str, bool] = Field(default_factory=dict)
    certifications_formations: bool = False


class IndicatorResult(BaseModel):
    id: int
    status: IndicatorStatus
    issues: list[str] = Field(default_factory=list)
    corrective_plan: list[str] = Field(default_factory=list)


class AuditOverview(BaseModel):
    total_indicators: int
    valid: int
    nc_mineure: int
    nc_majeure: int
    non_applicable: int


class AuditReport(BaseModel):
    vue_ensemble: AuditOverview
    status: AuditStatus
    indicateurs: list[IndicatorResult]


class StartAuditRequest(BaseModel):
    chat_session_id: UUID
    onboarding_data: QualiopiOnboardingData
    criteria_to_audit: list[int] | None = None


class AuditProgressEvent(BaseModel):
    event_type: Literal["criterion_progress", "audit_complete"] = "criterion_progress"
    criterion_id: int | None = None
    criterion_name: str | None = None
    status: CriterionProgressStatus | None = None
    indicators_processed: list[IndicatorResult] = Field(default_factory=list)
    report: AuditReport | None = None
