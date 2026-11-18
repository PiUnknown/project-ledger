import type { ReactNode, SVGProps } from "react";

interface IconProps extends Omit<SVGProps<SVGSVGElement>, "children"> {
  size?: number;
  children: ReactNode;
}

export function Icon({ size = 18, children, ...rest }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      focusable="false"
      height={size}
      viewBox="0 0 24 24"
      width={size}
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.8"
      {...rest}
    >
      {children}
    </svg>
  );
}

export function CheckIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <path d="m5 12 4 4L19 6" />
    </Icon>
  );
}

export function ShieldXIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" />
      <path d="m9.5 9.5 5 5m0-5-5 5" />
    </Icon>
  );
}

export function MinusCircleIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <circle cx="12" cy="12" r="9" />
      <path d="M8 12h8" />
    </Icon>
  );
}

export function QuestionIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <circle cx="12" cy="12" r="9" />
      <path d="M9.7 9a2.5 2.5 0 1 1 3.8 2.1c-.9.5-1.5 1-1.5 2.2M12 17h.01" />
    </Icon>
  );
}

export function WarningIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <path d="M10.3 3.8 2.2 18a2 2 0 0 0 1.7 3h16.2a2 2 0 0 0 1.7-3L13.7 3.8a2 2 0 0 0-3.4 0Z" />
      <path d="M12 9v4m0 4h.01" />
    </Icon>
  );
}

export function SendIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <path d="m5 12 14-7-5 14-2-5-7-2Z" />
    </Icon>
  );
}

export function PlusIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <path d="M12 5v14M5 12h14" />
    </Icon>
  );
}

export function MenuIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <path d="M4 7h16M4 12h16M4 17h16" />
    </Icon>
  );
}

export function CloseIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <path d="m6 6 12 12M18 6 6 18" />
    </Icon>
  );
}

export function AgentIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <rect x="5" y="7" width="14" height="11" rx="3" />
      <path d="M9 12h.01M15 12h.01M9 15h6M12 7V4" />
    </Icon>
  );
}

export function ChatIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <path d="M4 19V9a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v7a3 3 0 0 1-3 3H9l-5 3v-3Z" />
    </Icon>
  );
}

export function RetryIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <path d="M20 11a8 8 0 1 0-2.3 5.7M20 4v7h-7" />
    </Icon>
  );
}

export function InfoIcon({ size }: { size?: number }) {
  return (
    <Icon size={size}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5m0-8h.01" />
    </Icon>
  );
}
