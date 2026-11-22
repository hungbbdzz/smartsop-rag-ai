import { useEffect, useState } from 'react';
import { Menu } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { checkHealthApi } from '../../api/auth';
import { useAuthStore } from '../../store/authStore';
import { ROLE_META } from '../../types/auth';

interface RouteHeaderMeta {
  title: string;
  subtitle: string;
}

const ROUTE_HEADERS: Record<string, RouteHeaderMeta> = {
  '/chat': {
    title: 'Trợ lý Kỹ thuật RAG AI',
    subtitle: 'Tra cứu SOP theo thời gian thực với trích dẫn nguồn PDF xác thực',
  },
  '/sops': {
    title: 'Kho Tài liệu SOP & Kỹ thuật',
    subtitle: 'Quản lý quy trình chuẩn SMT, tài liệu hãng & trạng thái Vector ChromaDB',
  },
  '/tickets': {
    title: 'Quản lý Phiếu Báo Sự cố',
    subtitle: 'Theo dõi sự cố dây chuyền và nhận gợi ý quy trình xử lý tự động từ AI',
  },
  '/dashboard': {
    title: 'Dashboard KPI Vận hành',
    subtitle: 'Phân tích MTTR, phân bố sự cố theo dây chuyền & top SOP tra cứu',
  },
  '/admin': {
    title: 'Quản trị Hệ thống & RBAC',
    subtitle: 'Quản lý người dùng, nhật ký kiểm toán AI & trạng thái dịch vụ',
  },
};

interface HeaderProps {
  onOpenMobileMenu: () => void;
}

export function Header({ onOpenMobileMenu }: HeaderProps) {
  const { pathname } = useLocation();
  const { user } = useAuthStore();
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  const meta = ROUTE_HEADERS[pathname] || {
    title: 'SmartSOP AI',
    subtitle: 'Hệ thống Quản lý SOP & Trợ lý Vận hành Nhà máy Thông minh',
  };

  useEffect(() => {
    let mounted = true;
    const pollHealth = async () => {
      try {
        const res = await checkHealthApi();
        if (mounted) {
          setApiOnline(res.status === 'ok');
        }
      } catch {
        if (mounted) {
          setApiOnline(false);
        }
      }
    };

    void pollHealth();
    const timer = window.setInterval(pollHealth, 30000);
    return () => {
      mounted = false;
      window.clearInterval(timer);
    };
  }, []);

  const roleMeta = user ? ROLE_META[user.role] : null;

  return (
    <header className="h-16 px-4 sm:px-6 bg-factory-panel/95 border-b border-slate-800 flex items-center justify-between gap-4 flex-shrink-0">
      <div className="flex items-center gap-3 min-w-0">
        <button
          type="button"
          onClick={onOpenMobileMenu}
          className="lg:hidden p-2 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white"
          aria-label="Mở menu điều hướng"
        >
          <Menu className="w-4 h-4" />
        </button>

        <div className="min-w-0">
          <h1 className="text-sm sm:text-base font-bold text-white truncate">{meta.title}</h1>
          <p className="text-xs text-slate-400 truncate hidden sm:block">{meta.subtitle}</p>
        </div>
      </div>

      <div className="flex items-center gap-2.5 flex-shrink-0">
        {roleMeta && (
          <span
            className={`hidden md:inline-flex items-center px-2.5 py-1 rounded-full border text-[11px] font-mono font-semibold ${roleMeta.badgeClass}`}
          >
            {roleMeta.shortLabel}
          </span>
        )}

        <div
          className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-mono font-semibold ${
            apiOnline === false
              ? 'bg-rose-950/70 border-rose-500/40 text-rose-300'
              : 'bg-emerald-950/70 border-emerald-500/40 text-emerald-300'
          }`}
          title="Trạng thái kết nối FastAPI Gateway (/health)"
        >
          <span
            className={`w-2 h-2 rounded-full ${
              apiOnline === false
                ? 'bg-rose-400'
                : apiOnline === true
                  ? 'bg-emerald-400 animate-pulse'
                  : 'bg-amber-400 animate-pulse'
            }`}
          />
          <span>
            {apiOnline === false
              ? 'API Offline'
              : apiOnline === true
                ? 'API Online'
                : 'Checking API...'}
          </span>
        </div>
      </div>
    </header>
  );
}
