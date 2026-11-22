import { ShieldAlert, ArrowLeft } from 'lucide-react';
import { Link, Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { hasRole, ROLE_META, type UserRole } from '../types/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { token, user } = useAuthStore();
  const location = useLocation();

  if (!token || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!hasRole(user.role, allowedRoles)) {
    const roleMeta = ROLE_META[user.role];
    return (
      <div className="min-h-[70vh] flex items-center justify-center p-6">
        <div className="max-w-md w-full rounded-2xl bg-factory-card border border-rose-500/30 p-7 text-center shadow-2xl">
          <div className="w-14 h-14 mx-auto mb-4 rounded-xl bg-rose-950/70 border border-rose-500/40 flex items-center justify-center text-rose-400">
            <ShieldAlert className="w-7 h-7" />
          </div>
          <p className="text-xs font-mono uppercase tracking-widest text-rose-400 font-semibold">
            HTTP 403 — Access Restricted
          </p>
          <h1 className="mt-2 text-xl font-bold text-white">Không có quyền truy cập</h1>
          <p className="mt-2 text-sm text-slate-400 leading-relaxed">
            Phiên làm việc hiện tại của bạn thuộc nhóm quyền{' '}
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-mono font-semibold ${roleMeta.badgeClass}`}
            >
              {roleMeta.label} ({user.role})
            </span>{' '}
            và không được phép truy cập phân hệ này.
          </p>
          <div className="mt-6">
            <Link
              to="/chat"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold transition-colors shadow-glow-blue"
            >
              <ArrowLeft className="w-4 h-4" />
              Quay lại Trợ lý RAG AI
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
