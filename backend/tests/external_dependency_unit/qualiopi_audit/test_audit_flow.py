from onyx.server.features.qualiopi_audit.models import AuditOverview
from onyx.server.features.qualiopi_audit.models import IndicatorResult
from onyx.server.features.qualiopi_audit.prompt_builder import (
    build_criterion_audit_prompt,
)
from onyx.server.features.qualiopi_audit.models import QualiopiOnboardingData
from onyx.server.features.qualiopi_audit.qualiopi_data import get_applicable_indicators
from onyx.server.features.qualiopi_audit.api import _compute_audit_status


def _make_onboarding(**overrides: object) -> QualiopiOnboardingData:
    defaults: dict[str, object] = {
        "nda": "12345678901",
        "categorie_actions": ["OF"],
        "mode_audit": "initial",
        "nouveau_entrant": False,
        "site_web": "https://example.fr",
        "sous_traitance": {},
        "certifications_formations": False,
    }
    defaults.update(overrides)
    return QualiopiOnboardingData(**defaults)  # type: ignore[arg-type]


def test_get_applicable_indicators_of() -> None:
    indicators = get_applicable_indicators(
        categories=["OF"],
        nouveau_entrant=False,
        certifications_formations=False,
    )
    ids = {ind.id for ind in indicators}
    assert 1 in ids
    assert 2 in ids
    assert 3 not in ids  # certifications only, no certifications_formations
    assert 7 not in ids  # CFA only
    assert 15 not in ids  # CFA only
    assert 16 not in ids  # CFA only
    assert 25 not in ids  # CFA only
    assert 26 not in ids  # CFA only
    assert 4 in ids
    assert 32 in ids


def test_get_applicable_indicators_of_with_certifications() -> None:
    indicators = get_applicable_indicators(
        categories=["OF"],
        nouveau_entrant=False,
        certifications_formations=True,
    )
    ids = {ind.id for ind in indicators}
    assert 3 in ids  # certifications_only=True but certifications_formations=True


def test_get_applicable_indicators_cfa() -> None:
    indicators = get_applicable_indicators(
        categories=["CFA"],
        nouveau_entrant=False,
        certifications_formations=False,
    )
    ids = {ind.id for ind in indicators}
    assert 7 in ids
    assert 15 in ids
    assert 16 in ids
    assert 25 in ids
    assert 26 in ids
    assert 1 in ids
    assert 32 in ids


def test_get_applicable_indicators_nouveau_entrant() -> None:
    indicators = get_applicable_indicators(
        categories=["OF"],
        nouveau_entrant=True,
        certifications_formations=False,
    )
    ids = {ind.id for ind in indicators}
    adapted = [ind for ind in indicators if ind.nouveau_entrant_adapted]
    adapted_ids = {ind.id for ind in adapted}
    assert 2 in adapted_ids
    assert 11 in adapted_ids
    assert 32 in adapted_ids


def test_build_criterion_audit_prompt() -> None:
    onboarding = _make_onboarding(categorie_actions=["OF", "CFA"])
    indicators = get_applicable_indicators(
        categories=["OF", "CFA"],
        nouveau_entrant=False,
        certifications_formations=False,
    )
    crit1_indicators = [ind for ind in indicators if ind.id in (1, 2, 3)]

    prompt = build_criterion_audit_prompt(
        criterion_id=1,
        applicable_indicators=crit1_indicators,
        onboarding_data=onboarding,
    )

    assert "CRITERE 1" in prompt
    assert "12345678901" in prompt
    assert "OF" in prompt
    assert "INDICATEUR 1" in prompt or "Indicateur 1" in prompt.lower()
    assert '"status"' in prompt
    assert '"nc_majeure"' in prompt


def test_audit_report_aggregation_pret() -> None:
    results = [
        IndicatorResult(id=i, status="valid", issues=[], corrective_plan=[])
        for i in range(1, 23)
    ]
    overview, status = _compute_audit_status(results)

    assert overview.total_indicators == 22
    assert overview.valid == 22
    assert overview.nc_mineure == 0
    assert overview.nc_majeure == 0
    assert status == "pret_pour_audit"


def test_audit_report_non_pret_majeure() -> None:
    results = [
        IndicatorResult(id=1, status="nc_majeure", issues=["Missing info"], corrective_plan=["Add info"]),
    ] + [
        IndicatorResult(id=i, status="valid", issues=[], corrective_plan=[])
        for i in range(2, 23)
    ]
    overview, status = _compute_audit_status(results)

    assert overview.nc_majeure == 1
    assert status == "non_pret_pour_audit"


def test_audit_report_non_pret_5_mineures() -> None:
    results = [
        IndicatorResult(id=i, status="nc_mineure", issues=[f"Issue {i}"], corrective_plan=[])
        for i in range(1, 6)
    ] + [
        IndicatorResult(id=i, status="valid", issues=[], corrective_plan=[])
        for i in range(6, 23)
    ]
    overview, status = _compute_audit_status(results)

    assert overview.nc_mineure == 5
    assert status == "non_pret_pour_audit"


def test_audit_report_pret_with_4_mineures() -> None:
    results = [
        IndicatorResult(id=i, status="nc_mineure", issues=[f"Issue {i}"], corrective_plan=[])
        for i in range(1, 5)
    ] + [
        IndicatorResult(id=i, status="valid", issues=[], corrective_plan=[])
        for i in range(5, 23)
    ]
    overview, status = _compute_audit_status(results)

    assert overview.nc_mineure == 4
    assert status == "pret_pour_audit"
