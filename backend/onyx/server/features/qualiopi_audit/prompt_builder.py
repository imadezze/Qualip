import json
from typing import Final

from onyx.server.features.qualiopi_audit.models import QualiopiOnboardingData
from onyx.server.features.qualiopi_audit.qualiopi_data import CRITERIA
from onyx.server.features.qualiopi_audit.qualiopi_data import get_indicator_instructions
from onyx.server.features.qualiopi_audit.qualiopi_data import IndicatorDef


INDICATOR_RESULT_SCHEMA: Final[str] = json.dumps(
    {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "Indicator number (1-32)"},
                "status": {
                    "type": "string",
                    "enum": ["valid", "nc_mineure", "nc_majeure", "non_applicable"],
                },
                "issues": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of specific issues found. Empty if valid.",
                },
                "corrective_plan": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Suggested corrective actions. Empty if valid.",
                },
            },
            "required": ["id", "status", "issues", "corrective_plan"],
        },
    },
    indent=2,
)


def build_criterion_audit_prompt(
    criterion_id: int,
    applicable_indicators: list[IndicatorDef],
    onboarding_data: QualiopiOnboardingData,
) -> str:
    criterion = CRITERIA[criterion_id]

    indicator_instructions_text = ""
    for ind in applicable_indicators:
        instructions = get_indicator_instructions(ind.id)
        indicator_instructions_text += f"\n---\n{instructions}\n"

    indicator_ids_str = ", ".join(str(ind.id) for ind in applicable_indicators)

    nouveau_entrant_note = ""
    if onboarding_data.nouveau_entrant:
        nouveau_entrant_note = (
            "\nIMPORTANT: Cet organisme est un NOUVEAU ENTRANT. "
            "Pour les indicateurs adaptes, verifier la formalisation "
            "du processus plutot que la mise en oeuvre effective.\n"
        )

    return f"""Tu es un auditeur Qualiopi expert du RNQ V9. Tu audites le CRITERE {criterion_id} : {criterion.name}.

CONTEXTE DE L'ORGANISME :
- NDA : {onboarding_data.nda}
- Categories d'actions : {', '.join(onboarding_data.categorie_actions)}
- Mode d'audit : {onboarding_data.mode_audit}
- Nouveau entrant : {'Oui' if onboarding_data.nouveau_entrant else 'Non'}
- Site web : {onboarding_data.site_web or 'Non renseigne'}
- Formations certifiantes : {'Oui' if onboarding_data.certifications_formations else 'Non'}
{nouveau_entrant_note}
INDICATEURS A AUDITER pour ce critere : {indicator_ids_str}

Pour chaque indicateur, analyse les documents du dossier et determine le statut de conformite.

INSTRUCTIONS PAR INDICATEUR :
{indicator_instructions_text}

REGLE DE STATUT :
- "valid" : tous les controles obligatoires sont satisfaits
- "nc_mineure" : un ou deux elements mineurs manquent mais le processus existe
- "nc_majeure" : le processus n'existe pas ou des elements essentiels manquent
- "non_applicable" : l'indicateur ne s'applique pas a cet organisme

REPONDS UNIQUEMENT avec un tableau JSON conforme a ce schema :
{INDICATOR_RESULT_SCHEMA}

Analyse chaque indicateur ({indicator_ids_str}) et retourne le JSON. Pas de texte avant ou apres le JSON."""
