import Button from "@/refresh-components/buttons/Button";
import SimpleCollapsible from "@/refresh-components/SimpleCollapsible";
import Text from "@/refresh-components/texts/Text";
import { SvgCheckCircle, SvgAlertCircle, SvgAlertTriangle } from "@opal/icons";

import StatusBadge from "@/app/chat/qualiopi/components/StatusBadge";
import type { AuditReport, IndicatorResult } from "@/app/chat/qualiopi/types";
import { INDICATOR_DEFINITIONS } from "@/app/chat/qualiopi/types";

interface AuditReportSummaryProps {
  report: AuditReport;
  onRelaunch: () => void;
}

function AuditReportSummary({ report, onRelaunch }: AuditReportSummaryProps) {
  const { vue_ensemble } = report;
  const ncMajeures = report.indicateurs.filter(
    (i) => i.status === "nc_majeure"
  );
  const ncMineures = report.indicateurs.filter(
    (i) => i.status === "nc_mineure"
  );

  const isPret = report.status === "pret_pour_audit";

  return (
    <div className="flex flex-col gap-4 p-4">
      <div
        className={
          isPret
            ? "rounded-lg p-4 bg-status-success-01 border border-status-success-03"
            : "rounded-lg p-4 bg-status-error-01 border border-status-error-03"
        }
      >
        <div className="flex items-center gap-2">
          {isPret ? (
            <SvgCheckCircle className="w-5 h-5 text-status-success-05" />
          ) : (
            <SvgAlertCircle className="w-5 h-5 text-status-error-05" />
          )}
          <Text headingH3>
            {isPret ? "PRET POUR L'AUDIT" : "NON PRET POUR L'AUDIT"}
          </Text>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <ScoreCard
          label="Total"
          value={vue_ensemble.total_indicators}
          variant="neutral"
        />
        <ScoreCard
          label="Conformes"
          value={vue_ensemble.valid}
          variant="success"
        />
        <ScoreCard
          label="NC Mineures"
          value={vue_ensemble.nc_mineure}
          variant="warning"
        />
        <ScoreCard
          label="NC Majeures"
          value={vue_ensemble.nc_majeure}
          variant="error"
        />
      </div>

      {ncMajeures.length > 0 && (
        <NCSection
          title="Non-conformites majeures"
          items={ncMajeures}
          variant="error"
        />
      )}

      {ncMineures.length > 0 && (
        <NCSection
          title="Non-conformites mineures"
          items={ncMineures}
          variant="warning"
        />
      )}

      <div className="flex gap-2 pt-2">
        <Button action secondary onClick={onRelaunch}>
          Relancer l'audit
        </Button>
        <Button action secondary disabled>
          Telecharger PDF
        </Button>
      </div>
    </div>
  );
}

interface ScoreCardProps {
  label: string;
  value: number;
  variant: "neutral" | "success" | "warning" | "error";
}

const VARIANT_STYLES: Record<string, string> = {
  neutral:
    "bg-background-neutral-02 border-border-02",
  success:
    "bg-status-success-01 border-status-success-03",
  warning:
    "bg-status-warning-01 border-status-warning-03",
  error:
    "bg-status-error-01 border-status-error-03",
};

function ScoreCard({ label, value, variant }: ScoreCardProps) {
  return (
    <div className={`rounded-lg border p-3 text-center ${VARIANT_STYLES[variant]}`}>
      <Text headingH2 as="p">
        {value}
      </Text>
      <Text secondaryBody text03 as="p">
        {label}
      </Text>
    </div>
  );
}

interface NCSectionProps {
  title: string;
  items: IndicatorResult[];
  variant: "warning" | "error";
}

function NCSection({ title, items, variant }: NCSectionProps) {
  const bgClass =
    variant === "error" ? "bg-status-error-01" : "bg-status-warning-01";
  const icon =
    variant === "error" ? (
      <SvgAlertCircle className="w-4 h-4 text-status-error-05" />
    ) : (
      <SvgAlertTriangle className="w-4 h-4 text-status-warning-05" />
    );

  return (
    <SimpleCollapsible
      trigger={
        <div className="flex items-center gap-2">
          {icon}
          <SimpleCollapsible.Header
            title={`${title} (${items.length})`}
          />
        </div>
      }
      defaultOpen
    >
      <div className="flex flex-col gap-2 pb-2">
        {items.map((item) => {
          const def = INDICATOR_DEFINITIONS[item.id];
          return (
            <div
              key={item.id}
              className={`rounded-lg p-3 ${bgClass}`}
            >
              <div className="flex items-center justify-between">
                <Text mainUiBody>
                  Ind. {item.id} - {def?.name}
                </Text>
                <StatusBadge
                  status={item.status}
                />
              </div>
              {item.issues.length > 0 && (
                <ul className="pl-4 list-disc pt-1">
                  {item.issues.map((issue, idx) => (
                    <li key={idx}>
                      <Text secondaryBody>{issue}</Text>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </SimpleCollapsible>
  );
}

export default AuditReportSummary;
