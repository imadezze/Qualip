import SimpleCollapsible from "@/refresh-components/SimpleCollapsible";
import Text from "@/refresh-components/texts/Text";
import { SvgCheckCircle, SvgLoader } from "@opal/icons";

import IndicatorCard from "@/app/chat/qualiopi/components/IndicatorCard";
import type {
  CriterionDefinition,
  CriterionProgressStatus,
  IndicatorResult,
} from "@/app/chat/qualiopi/types";

interface CriterionSectionProps {
  criterion: CriterionDefinition;
  status: CriterionProgressStatus;
  indicatorResults: Map<number, IndicatorResult>;
}

function CriterionSection({
  criterion,
  status,
  indicatorResults,
}: CriterionSectionProps) {
  const completedCount = criterion.indicatorIds.filter((id) =>
    indicatorResults.has(id)
  ).length;
  const totalCount = criterion.indicatorIds.length;

  const statusIcon =
    status === "in_progress" ? (
      <SvgLoader className="w-4 h-4 animate-spin text-text-03" />
    ) : status === "completed" ? (
      <SvgCheckCircle className="w-4 h-4 text-status-success-05" />
    ) : null;

  const trigger = (
    <SimpleCollapsible.Header
      title={`Critere ${criterion.id} : ${criterion.name}`}
      description={`${completedCount}/${totalCount} indicateurs`}
    />
  );

  return (
    <SimpleCollapsible
      trigger={
        <div className="flex items-center gap-2 w-full">
          <div className="flex-1">{trigger}</div>
          {statusIcon}
        </div>
      }
      defaultOpen={status === "in_progress" || status === "completed"}
    >
      <div className="flex flex-col gap-2 pb-2">
        {criterion.indicatorIds.map((indId) => (
          <IndicatorCard
            key={indId}
            indicatorId={indId}
            result={indicatorResults.get(indId) ?? null}
            isProcessing={
              status === "in_progress" && !indicatorResults.has(indId)
            }
          />
        ))}
      </div>
    </SimpleCollapsible>
  );
}

export default CriterionSection;
