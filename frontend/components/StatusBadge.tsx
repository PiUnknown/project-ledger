import type { ReactNode } from "react";
import { statusLabels } from "@/lib/presentation";
import type { ChatStatus } from "@/lib/types";
import {
  CheckIcon,
  MinusCircleIcon,
  QuestionIcon,
  ShieldXIcon,
  WarningIcon,
} from "./icons";

const statusIcons: Record<ChatStatus, ReactNode> = {
  answered: <CheckIcon size={14} />,
  refused: <ShieldXIcon size={14} />,
  no_data: <MinusCircleIcon size={14} />,
  needs_clarification: <QuestionIcon size={14} />,
  error: <WarningIcon size={14} />,
};

export function StatusBadge({ status }: { status: ChatStatus }) {
  return (
    <span className={`status-badge status-${status}`}>
      {statusIcons[status]}
      {statusLabels[status]}
    </span>
  );
}
