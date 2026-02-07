import IconButton from "@/refresh-components/buttons/IconButton";
import { SvgShield } from "@opal/icons";

interface AuditToggleButtonProps {
  onClick: () => void;
  active: boolean;
}

function AuditToggleButton({ onClick, active }: AuditToggleButtonProps) {
  return (
    <IconButton
      icon={SvgShield}
      onClick={onClick}
      aria-label="Toggle audit panel"
      className={active ? "text-theme-primary-05" : undefined}
    />
  );
}

export default AuditToggleButton;
