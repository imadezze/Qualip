import type {
  AuditProgressEvent,
  QualiopiOnboardingData,
} from "@/app/chat/qualiopi/types";

export async function* startAudit(
  chatSessionId: string,
  onboardingData: QualiopiOnboardingData,
  criteriaToAudit?: number[]
): AsyncGenerator<AuditProgressEvent> {
  const response = await fetch("/api/qualiopi-audit/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_session_id: chatSessionId,
      onboarding_data: onboardingData,
      criteria_to_audit: criteriaToAudit ?? null,
    }),
  });

  if (!response.ok) {
    throw new Error(`Audit request failed: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith("data: ")) {
        const jsonStr = trimmed.slice(6);
        if (jsonStr) {
          const event: AuditProgressEvent = JSON.parse(jsonStr);
          yield event;
        }
      }
    }
  }
}
