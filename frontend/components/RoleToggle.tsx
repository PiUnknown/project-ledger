"use client";

import { roleInitials } from "@/lib/presentation";
import type { RoleId, RoleSummary } from "@/lib/types";

export function RoleToggle({
  roles,
  activeRoleId,
  onSelect,
}: {
  roles: RoleSummary[];
  activeRoleId: RoleId;
  onSelect: (roleId: RoleId) => void;
}) {
  return (
    <div className="role-switcher" role="group" aria-label="Demo role">
      {roles.map((role) => (
        <button
          aria-pressed={role.id === activeRoleId}
          className={role.id === activeRoleId ? "active" : ""}
          key={role.id}
          onClick={() => onSelect(role.id)}
          title={role.label}
          type="button"
        >
          <span className="role-short">{roleInitials(role.label)}</span>
          <span className="role-full">{role.label}</span>
        </button>
      ))}
    </div>
  );
}
