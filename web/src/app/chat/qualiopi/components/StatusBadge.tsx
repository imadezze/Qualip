import { cn } from "@/lib/utils";
import Text from "@/refresh-components/texts/Text";

import type { IndicatorStatus } from "@/app/chat/qualiopi/types";

const STATUS_STYLES: Record<IndicatorStatus, string> = {
  valid: "bg-status-success-01 text-status-success-05",
  nc_mineure: "bg-status-warning-01 text-status-warning-05",
  nc_majeure: "bg-status-error-01 text-status-error-05",
  non_applicable: "bg-background-neutral-02 text-text-03",
};

const STATUS_LABELS: Record<IndicatorStatus, string> = {
  valid: "Conforme",
  nc_mineure: "NC Mineure",
  nc_majeure: "NC Majeure",
  non_applicable: "N/A",
};

interface StatusBadgeProps {
  status: IndicatorStatus;
  className?: string;
}

function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5",
        STATUS_STYLES[status],
        className
      )}
    >
      <Text secondaryBody>{STATUS_LABELS[status]}</Text>
    </span>
  );
}

export default StatusBadge;
