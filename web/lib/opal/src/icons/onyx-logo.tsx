import type { IconProps } from "@opal/types";

const OnyxLogo = ({
  width = 24,
  height = 24,
  className,
  ...props
}: IconProps) => (
  <svg
    width={width}
    height={height}
    viewBox="0 0 100 100"
    xmlns="http://www.w3.org/2000/svg"
    className={className}
    {...props}
  >
    {/* LumiereAI Logo - 3x3 grid tilted */}
    <g transform="rotate(-15, 50, 50)">
      {/* Background layer (offset) */}
      <g transform="translate(4, 4)" opacity="0.3">
        <rect x="12" y="12" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
        <rect x="40" y="12" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
        <rect x="68" y="12" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
        <rect x="12" y="40" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
        <rect x="40" y="40" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
        <rect x="68" y="40" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
        <rect x="12" y="68" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
        <rect x="40" y="68" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
        <rect x="68" y="68" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
      </g>
      {/* Main grid */}
      <rect x="12" y="12" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
      <rect x="40" y="12" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
      <rect x="68" y="12" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
      <rect x="12" y="40" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
      <rect x="40" y="40" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
      <rect x="68" y="40" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
      <rect x="12" y="68" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
      <rect x="40" y="68" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
      <rect x="68" y="68" width="20" height="20" rx="4" fill="currentColor" stroke="currentColor" strokeWidth="2"/>
    </g>
  </svg>
);
export default OnyxLogo;
