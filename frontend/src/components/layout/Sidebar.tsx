import {
  AlertTriangle,
  Bot,
  Cpu,
  FileText,
  LayoutDashboard,
  LogOut,
  Sliders,
  X,
  type LucideIcon,
} from 'lucide-react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { hasRole, ROLE_META, type UserRole } from '../../types/auth';

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  allowedRoles?: UserRole[];
}

export const NAV_ITEMS: NavItem[] = [
  {
    to: '/chat',
    label: 'Trợ lý RAG AI',
    icon: Bot,
  },
  {
    to: '/sops',
    label: 'Kho tài liệu SOP',
    icon: FileText,
  },
  {
    to: '/tickets',
    label: 'Phiếu báo sự cố',
    icon: AlertTriangle,
  },
  {
    to: '/dashboard',
    label: 'Dashboard KPI',
    icon: LayoutDashboard,
    allowedRoles: ['SHIFT_ENGINEER', 'FACTORY_MANAGER', 'ADMIN'],
  },
  {
    to: '/admin',
    label: 'Quản trị hệ thống',
    icon: Sliders,
    allowedRoles: ['ADMIN'],
  },
];

interface SidebarProps {
  mobileOpen: boolean;
  onCloseMobile: () => void;
}

function getInitials(fullName: string): string {
  const parts = fullName.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return 'U';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

export function Sidebar({ mobileOpen, onCloseMobile }: SidebarProps) {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const visibleItems = NAV_ITEMS.filter((item) => hasRole(user?.role, item.allowedRoles));
  const roleMeta = user ? ROLE_META[user.role] : null;

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <>
      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/70 backdrop-blur-sm lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-factory-panel border-r border-slate-800 flex flex-col transition-transform duration-200 lg:static lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Logo Header */}
        <div className="h-16 px-4 border-b border-slate-800 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-brand-600 to-cyan-400 p-[1px] shadow-glow-cyan">
              <div className="w-full h-full bg-factory-panel rounded-[7px] flex items-center justify-center">
                <Cpu className="w-5 h-5 text-brand-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold tracking-tight text-white text-base">
                  SmartSOP <span className="text-brand-400">AI</span>
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-sky-950/90 text-brand-400 border border-sky-500/30 font-semibold">
                  v2.4
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">SMT Factory RAG</p>
            </div>
          </div>

          <button
            type="button"
            onClick={onCloseMobile}
            className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
            aria-label="Đóng thanh điều hướng"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 p-3 space-y-1.5 overflow-y-auto">
          <div className="px-3 py-1.5 text-[10px] font-mono uppercase tracking-widest text-slate-500 font-semibold">
            Phân hệ vận hành
          </div>
          {visibleItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onCloseMobile}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all border ${
                    isActive
                      ? 'bg-brand-600/20 text-brand-400 border-brand-400/40 shadow-glow-cyan'
                      : 'text-slate-300 border-transparent hover:bg-slate-800/70 hover:text-white'
                  }`
                }
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* User Profile & Logout Footer */}
        {user && roleMeta && (
          <div className="p-3 border-t border-slate-800 bg-factory-darkest/50 flex-shrink-0">
            <div className="p-3 rounded-xl bg-factory-card/90 border border-slate-800 space-y-2.5">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-lg bg-sky-950 border border-sky-500/40 flex items-center justify-center text-xs font-mono font-bold text-brand-400 flex-shrink-0">
                  {getInitials(user.full_name)}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-semibold text-white truncate">{user.full_name}</p>
                  <p className="text-[11px] font-mono text-slate-400 truncate">@{user.username}</p>
                </div>
              </div>

              <div className="flex items-center justify-between gap-2">
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded border text-[10px] font-mono font-semibold truncate ${roleMeta.badgeClass}`}
                >
                  {roleMeta.label}
                </span>
              </div>

              <button
                type="button"
                onClick={handleLogout}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-slate-800/80 hover:bg-rose-950/70 text-slate-300 hover:text-rose-300 border border-slate-700 hover:border-rose-500/40 text-xs font-semibold transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Đăng xuất</span>
              </button>
            </div>
          </div>
        )}
      </aside>
    </>
  );
}
