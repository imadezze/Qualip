import json
import re
from collections.abc import Generator

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from onyx.auth.users import current_user
from onyx.chat.chat_state import ChatStateContainer
from onyx.chat.process_message import gather_stream
from onyx.chat.process_message import handle_stream_message_objects
from onyx.db.engine.sql_engine import get_session_with_current_tenant
from onyx.db.models import User
from onyx.server.features.qualiopi_audit.models import AuditOverview
from onyx.server.features.qualiopi_audit.models import AuditProgressEvent
from onyx.server.features.qualiopi_audit.models import AuditReport
from onyx.server.features.qualiopi_audit.models import IndicatorResult
from onyx.server.features.qualiopi_audit.models import StartAuditRequest
from onyx.server.features.qualiopi_audit.prompt_builder import (
    build_criterion_audit_prompt,
)
from onyx.server.features.qualiopi_audit.qualiopi_data import CRITERIA
from onyx.server.features.qualiopi_audit.qualiopi_data import get_applicable_indicators
from onyx.server.features.qualiopi_audit.qualiopi_data import IndicatorDef
from onyx.server.query_and_chat.models import SendMessageRequest
from onyx.utils.logger import setup_logger

logger = setup_logger()

router = APIRouter(prefix="/qualiopi-audit", tags=["qualiopi-audit"])


def _parse_indicator_results_from_answer(answer: str) -> list[IndicatorResult]:
    json_match = re.search(r"\[.*\]", answer, re.DOTALL)
    if not json_match:
        raise ValueError(f"No JSON array found in LLM answer: {answer[:200]}")
    raw = json.loads(json_match.group())
    return [IndicatorResult(**item) for item in raw]


def _run_criterion_audit(
    criterion_id: int,
    applicable_indicators: list[IndicatorDef],
    request: StartAuditRequest,
    user: User | None,
    db_session: Session,
) -> list[IndicatorResult]:
    prompt = build_criterion_audit_prompt(
        criterion_id=criterion_id,
        applicable_indicators=applicable_indicators,
        onboarding_data=request.onboarding_data,
    )

    msg_req = SendMessageRequest(
        message=prompt,
        chat_session_id=request.chat_session_id,
        stream=False,
    )

    state_container = ChatStateContainer()
    packets = handle_stream_message_objects(
        new_msg_req=msg_req,
        user=user,
        db_session=db_session,
        external_state_container=state_container,
    )
    result = gather_stream(packets)
    return _parse_indicator_results_from_answer(result.answer)


def _compute_audit_status(
    all_results: list[IndicatorResult],
) -> tuple[AuditOverview, str]:
    valid = sum(1 for r in all_results if r.status == "valid")
    nc_min = sum(1 for r in all_results if r.status == "nc_mineure")
    nc_maj = sum(1 for r in all_results if r.status == "nc_majeure")
    na = sum(1 for r in all_results if r.status == "non_applicable")

    overview = AuditOverview(
        total_indicators=len(all_results),
        valid=valid,
        nc_mineure=nc_min,
        nc_majeure=nc_maj,
        non_applicable=na,
    )

    if nc_maj > 0 or nc_min >= 5:
        status = "non_pret_pour_audit"
    else:
        status = "pret_pour_audit"

    return overview, status


@router.post("/start")
def start_audit(
    audit_request: StartAuditRequest,
    user: User | None = Depends(current_user),
) -> StreamingResponse:
    criteria_to_audit = audit_request.criteria_to_audit or list(range(1, 8))

    all_applicable = get_applicable_indicators(
        categories=audit_request.onboarding_data.categorie_actions,
        nouveau_entrant=audit_request.onboarding_data.nouveau_entrant,
        certifications_formations=audit_request.onboarding_data.certifications_formations,
    )
    applicable_by_id = {ind.id: ind for ind in all_applicable}

    def stream_generator() -> Generator[str, None, None]:
        all_results: list[IndicatorResult] = []

        with get_session_with_current_tenant() as db_session:
            for crit_id in criteria_to_audit:
                criterion = CRITERIA.get(crit_id)
                if not criterion:
                    continue

                crit_indicators = [
                    applicable_by_id[ind_id]
                    for ind_id in criterion.indicator_ids
                    if ind_id in applicable_by_id
                ]

                if not crit_indicators:
                    continue

                progress = AuditProgressEvent(
                    event_type="criterion_progress",
                    criterion_id=crit_id,
                    criterion_name=criterion.name,
                    status="in_progress",
                )
                yield f"data: {progress.model_dump_json()}\n\n"

                indicator_results = _run_criterion_audit(
                    criterion_id=crit_id,
                    applicable_indicators=crit_indicators,
                    request=audit_request,
                    user=user,
                    db_session=db_session,
                )

                all_results.extend(indicator_results)

                progress = AuditProgressEvent(
                    event_type="criterion_progress",
                    criterion_id=crit_id,
                    criterion_name=criterion.name,
                    status="completed",
                    indicators_processed=indicator_results,
                )
                yield f"data: {progress.model_dump_json()}\n\n"

            overview, status = _compute_audit_status(all_results)
            report = AuditReport(
                vue_ensemble=overview,
                status=status,
                indicateurs=all_results,
            )

            final_event = AuditProgressEvent(
                event_type="audit_complete",
                report=report,
            )
            yield f"data: {final_event.model_dump_json()}\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")
