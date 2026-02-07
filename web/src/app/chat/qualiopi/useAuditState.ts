import { useCallback, useRef, useState } from "react";

import { startAudit } from "@/app/chat/qualiopi/qualiopiService";
import type {
  AuditProgressEvent,
  AuditReport,
  CriterionProgressStatus,
  IndicatorResult,
  QualiopiOnboardingData,
} from "@/app/chat/qualiopi/types";

interface CriterionProgress {
  status: CriterionProgressStatus;
  indicators: IndicatorResult[];
}

interface AuditState {
  onboardingData: QualiopiOnboardingData | null;
  isAuditing: boolean;
  auditProgress: Map<number, CriterionProgress>;
  auditReport: AuditReport | null;
  error: string | null;
}

interface AuditActions {
  setOnboardingData: (data: QualiopiOnboardingData) => void;
  runAudit: (chatSessionId: string) => Promise<void>;
  resetAudit: () => void;
}

export function useAuditState(): AuditState & AuditActions {
  const [onboardingData, setOnboardingData] =
    useState<QualiopiOnboardingData | null>(null);
  const [isAuditing, setIsAuditing] = useState(false);
  const [auditProgress, setAuditProgress] = useState<
    Map<number, CriterionProgress>
  >(new Map());
  const [auditReport, setAuditReport] = useState<AuditReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const abortRef = useRef(false);

  const handleProgressEvent = useCallback((event: AuditProgressEvent) => {
    if (event.event_type === "criterion_progress" && event.criterion_id) {
      setAuditProgress((prev) => {
        const next = new Map(prev);
        next.set(event.criterion_id!, {
          status: event.status ?? "pending",
          indicators: event.indicators_processed,
        });
        return next;
      });
    } else if (event.event_type === "audit_complete" && event.report) {
      setAuditReport(event.report);
    }
  }, []);

  const runAudit = useCallback(
    async (chatSessionId: string) => {
      if (!onboardingData) return;

      abortRef.current = false;
      setIsAuditing(true);
      setAuditReport(null);
      setAuditProgress(new Map());
      setError(null);

      const stream = startAudit(chatSessionId, onboardingData);

      for await (const event of stream) {
        if (abortRef.current) break;
        handleProgressEvent(event);
      }

      setIsAuditing(false);
    },
    [onboardingData, handleProgressEvent]
  );

  const resetAudit = useCallback(() => {
    abortRef.current = true;
    setIsAuditing(false);
    setAuditProgress(new Map());
    setAuditReport(null);
    setError(null);
  }, []);

  return {
    onboardingData,
    isAuditing,
    auditProgress,
    auditReport,
    error,
    setOnboardingData,
    runAudit,
    resetAudit,
  };
}
