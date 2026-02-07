import { useCallback, useMemo } from "react";

import Button from "@/refresh-components/buttons/Button";
import IconButton from "@/refresh-components/buttons/IconButton";
import Text from "@/refresh-components/texts/Text";
import { SvgX, SvgShield } from "@opal/icons";

import AuditReportSummary from "@/app/chat/qualiopi/components/AuditReportSummary";
import CriterionSection from "@/app/chat/qualiopi/components/CriterionSection";
import OnboardingForm from "@/app/chat/qualiopi/components/OnboardingForm";
import type {
  AuditReport,
  CriterionProgressStatus,
  IndicatorResult,
  QualiopiOnboardingData,
} from "@/app/chat/qualiopi/types";
import { CRITERIA_DEFINITIONS } from "@/app/chat/qualiopi/types";

interface CriterionProgress {
  status: CriterionProgressStatus;
  indicators: IndicatorResult[];
}

interface AuditPanelProps {
  onClose: () => void;
  chatSessionId: string | null;
  onboardingData: QualiopiOnboardingData | null;
  isAuditing: boolean;
  auditProgress: Map<number, CriterionProgress>;
  auditReport: AuditReport | null;
  setOnboardingData: (data: QualiopiOnboardingData) => void;
  runAudit: (chatSessionId: string) => Promise<void>;
  resetAudit: () => void;
}

function AuditPanel({
  onClose,
  chatSessionId,
  onboardingData,
  isAuditing,
  auditProgress,
  auditReport,
  setOnboardingData,
  runAudit,
  resetAudit,
}: AuditPanelProps) {
  const handleStartAudit = useCallback(() => {
    if (!chatSessionId) return;
    runAudit(chatSessionId);
  }, [chatSessionId, runAudit]);

  const handleRelaunch = useCallback(() => {
    resetAudit();
    if (chatSessionId) {
      runAudit(chatSessionId);
    }
  }, [chatSessionId, resetAudit, runAudit]);

  const indicatorResultsMap = useMemo(() => {
    const map = new Map<number, IndicatorResult>();
    Array.from(auditProgress.values()).forEach((progress) => {
      progress.indicators.forEach((ind) => {
        map.set(ind.id, ind);
      });
    });
    return map;
  }, [auditProgress]);

  const completedCriteria = Array.from(auditProgress.values()).filter(
    (p) => p.status === "completed"
  ).length;
  const totalCriteria = 7;
  const progressPercent = Math.round((completedCriteria / totalCriteria) * 100);

  return (
    <div className="h-full flex flex-col bg-background-tint-01 border-l border-border-01">
      <div className="sticky top-0 z-sticky bg-background-tint-01">
        <div className="flex items-center justify-between gap-2 p-3 border-b border-border-01">
          <div className="flex items-center gap-2">
            <SvgShield className="w-5 h-5 text-text-02" />
            <Text headingH3>Audit Qualiopi</Text>
          </div>
          <IconButton icon={SvgX} onClick={onClose} aria-label="Fermer" />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {!onboardingData && (
          <OnboardingForm onSubmit={setOnboardingData} />
        )}

        {onboardingData && !isAuditing && !auditReport && (
          <div className="p-4 flex flex-col gap-4">
            <div className="rounded-lg border border-border-02 p-3 bg-background-neutral-01">
              <Text mainUiBody text03 as="p">
                Organisme configure
              </Text>
              <Text mainUiBody as="p">
                NDA : {onboardingData.nda}
              </Text>
              <Text mainUiBody as="p">
                Categories : {onboardingData.categorie_actions.join(", ")}
              </Text>
              <Text mainUiBody as="p">
                Mode : {onboardingData.mode_audit}
              </Text>
            </div>

            <Button
              main
              primary
              onClick={handleStartAudit}
              disabled={!chatSessionId}
              leftIcon={SvgShield}
            >
              Lancer l'audit complet
            </Button>

            {!chatSessionId && (
              <Text secondaryBody text03 as="p">
                Envoyez un message dans le chat pour demarrer une session avant
                de lancer l'audit.
              </Text>
            )}
          </div>
        )}

        {isAuditing && (
          <div className="p-4 flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <Text mainUiBody text03>
                  Progression
                </Text>
                <Text mainUiBody text03>
                  {progressPercent}%
                </Text>
              </div>
              <div className="h-2 rounded-full bg-background-neutral-03 overflow-hidden">
                <div
                  className="h-full rounded-full bg-theme-primary-05 transition-all duration-500"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>

            {CRITERIA_DEFINITIONS.map((criterion) => {
              const progress = auditProgress.get(criterion.id);
              return (
                <CriterionSection
                  key={criterion.id}
                  criterion={criterion}
                  status={progress?.status ?? "pending"}
                  indicatorResults={indicatorResultsMap}
                />
              );
            })}
          </div>
        )}

        {auditReport && (
          <AuditReportSummary
            report={auditReport}
            onRelaunch={handleRelaunch}
          />
        )}
      </div>
    </div>
  );
}

export default AuditPanel;
