import { useCallback, useState } from "react";

import Button from "@/refresh-components/buttons/Button";
import Checkbox from "@/refresh-components/inputs/Checkbox";
import InputSelect from "@/refresh-components/inputs/InputSelect";
import InputTypeIn from "@/refresh-components/inputs/InputTypeIn";
import Switch from "@/refresh-components/inputs/Switch";
import Text from "@/refresh-components/texts/Text";

import type {
  ActionCategory,
  AuditMode,
  QualiopiOnboardingData,
} from "@/app/chat/qualiopi/types";

const CATEGORY_OPTIONS: { value: ActionCategory; label: string }[] = [
  { value: "OF", label: "Organisme de Formation (OF)" },
  { value: "CFA", label: "Centre de Formation d'Apprentis (CFA)" },
  { value: "CBC", label: "Bilan de Competences (CBC)" },
  { value: "VAE", label: "Validation des Acquis (VAE)" },
];

interface OnboardingFormProps {
  onSubmit: (data: QualiopiOnboardingData) => void;
}

function OnboardingForm({ onSubmit }: OnboardingFormProps) {
  const [nda, setNda] = useState("");
  const [categories, setCategories] = useState<ActionCategory[]>([]);
  const [modeAudit, setModeAudit] = useState<AuditMode>("initial");
  const [nouveauEntrant, setNouveauEntrant] = useState(false);
  const [siteWeb, setSiteWeb] = useState("");
  const [certifications, setCertifications] = useState(false);

  const toggleCategory = useCallback((cat: ActionCategory, checked: boolean) => {
    setCategories((prev) =>
      checked ? [...prev, cat] : prev.filter((c) => c !== cat)
    );
  }, []);

  const handleSubmit = useCallback(() => {
    if (nda.length !== 11 || categories.length === 0) return;

    onSubmit({
      nda,
      categorie_actions: categories,
      mode_audit: modeAudit,
      nouveau_entrant: nouveauEntrant,
      site_web: siteWeb || null,
      sous_traitance: {},
      certifications_formations: certifications,
    });
  }, [nda, categories, modeAudit, nouveauEntrant, siteWeb, certifications, onSubmit]);

  const isValid = nda.length === 11 && categories.length > 0;

  return (
    <div className="flex flex-col gap-4 p-4">
      <Text headingH3 as="p">
        Informations de l'organisme
      </Text>

      <div className="flex flex-col gap-1">
        <Text mainUiBody text03 as="p">
          NDA (11 chiffres)
        </Text>
        <InputTypeIn
          value={nda}
          onChange={(e) => setNda(e.target.value)}
          placeholder="12345678901"
          maxLength={11}
        />
      </div>

      <div className="flex flex-col gap-1">
        <Text mainUiBody text03 as="p">
          Categories d'actions
        </Text>
        <div className="flex flex-col gap-2">
          {CATEGORY_OPTIONS.map((opt) => (
            <label key={opt.value} className="flex items-center gap-2">
              <Checkbox
                checked={categories.includes(opt.value)}
                onCheckedChange={(checked) =>
                  toggleCategory(opt.value, checked)
                }
              />
              <Text mainUiBody>{opt.label}</Text>
            </label>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <Text mainUiBody text03 as="p">
          Mode d'audit
        </Text>
        <InputSelect
          value={modeAudit}
          onValueChange={(val) => setModeAudit(val as AuditMode)}
        >
          <InputSelect.Trigger placeholder="Selectionner..." />
          <InputSelect.Content>
            <InputSelect.Item value="initial">Audit initial</InputSelect.Item>
            <InputSelect.Item value="surveillance">
              Audit de surveillance
            </InputSelect.Item>
            <InputSelect.Item value="renouvellement">
              Audit de renouvellement
            </InputSelect.Item>
          </InputSelect.Content>
        </InputSelect>
      </div>

      <div className="flex items-center justify-between">
        <Text mainUiBody>Nouveau entrant</Text>
        <Switch
          checked={nouveauEntrant}
          onCheckedChange={setNouveauEntrant}
        />
      </div>

      <div className="flex items-center justify-between">
        <Text mainUiBody>Formations certifiantes</Text>
        <Switch
          checked={certifications}
          onCheckedChange={setCertifications}
        />
      </div>

      <div className="flex flex-col gap-1">
        <Text mainUiBody text03 as="p">
          Site web (optionnel)
        </Text>
        <InputTypeIn
          value={siteWeb}
          onChange={(e) => setSiteWeb(e.target.value)}
          placeholder="https://www.exemple.fr"
        />
      </div>

      <Button
        main
        primary
        onClick={handleSubmit}
        disabled={!isValid}
      >
        Valider les informations
      </Button>
    </div>
  );
}

export default OnboardingForm;
