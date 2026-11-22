export type UserRole = 'ADMIN' | 'FACTORY_MANAGER' | 'SHIFT_ENGINEER' | 'OPERATOR';

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface HealthStatus {
  status: string;
  app?: string;
  version?: string;
  environment?: string;
}

export interface RoleMetadata {
  label: string;
  shortLabel: string;
  badgeClass: string;
}

export const ROLE_META: Record<UserRole, RoleMetadata> = {
  ADMIN: {
    label: 'Quản trị hệ thống',
    shortLabel: 'ADMIN',
    badgeClass: 'bg-purple-950/80 text-purple-300 border-purple-500/40',
  },
  FACTORY_MANAGER: {
    label: 'Quản đốc nhà máy',
    shortLabel: 'MANAGER',
    badgeClass: 'bg-amber-950/80 text-amber-300 border-amber-500/40',
  },
  SHIFT_ENGINEER: {
    label: 'Kỹ sư trưởng ca',
    shortLabel: 'ENGINEER',
    badgeClass: 'bg-sky-950/80 text-sky-300 border-sky-500/40',
  },
  OPERATOR: {
    label: 'Công nhân đứng máy',
    shortLabel: 'OPERATOR',
    badgeClass: 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40',
  },
};

export function hasRole(role: UserRole | undefined, allowed?: UserRole[]): boolean {
  if (!allowed || allowed.length === 0) {
    return true;
  }
  if (!role) {
    return false;
  }
  return allowed.includes(role);
}
