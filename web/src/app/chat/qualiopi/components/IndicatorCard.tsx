import { cn } from "@/lib/utils";
import Text from "@/refresh-components/texts/Text";
import { SvgLoader } from "@opal/icons";

import StatusBadge from "@/app/chat/qualiopi/components/StatusBadge";
import type { IndicatorResult } from "@/app/chat/qualiopi/types";
import { INDICATOR_DEFINITIONS } from "@/app/chat/qualiopi/types";

interface IndicatorCardProps {
  indicatorId: number;
  result: IndicatorResult | null;
  isProcessing: boolean;
}

function IndicatorCard({
  indicatorId,
  result,
  isProcessing,
}: IndicatorCardProps) {
  const definition = INDICATOR_DEFINITIONS[indicatorId];

  return (
    <div
      className={cn(
        "rounded-lg border border-border-02 p-3",
        "bg-background-neutral-01"
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <Text secondaryBody text03>
            Ind. {indicatorId}
          </Text>
          <Text mainUiBody as="p">
            {definition?.name ?? `Indicateur ${indicatorId}`}
          </Text>
        </div>
        <div className="flex-shrink-0">
          {isProcessing && (
            <SvgLoader className="w-4 h-4 animate-spin text-text-03" />
          )}
          {result && <StatusBadge status={result.status} />}
          {!isProcessing && !result && (
            <span className="inline-flex items-center rounded-full px-2 py-0.5 bg-background-neutral-02">
              <Text secondaryBody text03>
                A traiter
              </Text>
            </span>
          )}
        </div>
      </div>

      {result && result.issues.length > 0 && (
        <div className="pt-2">
          <Text secondaryBody text03 as="p">
            Problemes :
          </Text>
          <ul className="pl-4 list-disc">
            {result.issues.map((issue, idx) => (
              <li key={idx}>
                <Text secondaryBody as="span">
                  {issue}
                </Text>
              </li>
            ))}
          </ul>
        </div>
      )}

      {result && result.corrective_plan.length > 0 && (
        <div className="pt-1">
          <Text secondaryBody text03 as="p">
            Plan correctif :
          </Text>
          <ul className="pl-4 list-disc">
            {result.corrective_plan.map((action, idx) => (
              <li key={idx}>
                <Text secondaryBody as="span">
                  {action}
                </Text>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default IndicatorCard;
