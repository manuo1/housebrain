interface RadiatorIconProps {
  className?: string;
}

export default function RadiatorIcon({ className }: RadiatorIconProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect x="4" y="4" width="16" height="16" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
      <line x1="8" y1="4" x2="8" y2="20" stroke="currentColor" strokeWidth="1.6" />
      <line x1="12" y1="4" x2="12" y2="20" stroke="currentColor" strokeWidth="1.6" />
      <line x1="16" y1="4" x2="16" y2="20" stroke="currentColor" strokeWidth="1.6" />
      <line x1="4" y1="9" x2="2" y2="9" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <line x1="4" y1="14" x2="2" y2="14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <line x1="20" y1="9" x2="22" y2="9" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <line x1="20" y1="14" x2="22" y2="14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}
