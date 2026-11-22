import { useEffect, useState, type FormEvent } from 'react';
import {
  Activity,
  AlertCircle,
  BadgeCheck,
  Clock,
  Cpu,
  Eye,
  EyeOff,
  Loader2,
  Lock,
  ShieldCheck,
  User as UserIcon,
} from 'lucide-react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { checkHealthApi } from '../api/auth';
import { useAuthStore } from '../store/authStore';

interface DemoAccount {
  roleLabel: string;
  username: string;
  password: string;
  accentClass: string;
}

const DEMO_ACCOUNTS: DemoAccount[] = [
  {
    roleLabel: 'Admin',
    username: 'admin',
    password: 'Admin@2026',
    accentClass: 'hover:border-purple-400/60 hover:bg-purple-950/40 text-purple-300',
  },
  {
    roleLabel: 'Manager',
    username: 'manager',
    password: 'Manager@2026',
    accentClass: 'hover:border-amber-400/60 hover:bg-amber-950/40 text-amber-300',
  },
  {
    roleLabel: 'Engineer',
    username: 'engineer',
    password: 'Engineer@2026',
    accentClass: 'hover:border-sky-400/60 hover:bg-sky-950/40 text-sky-300',
  },
  {
    roleLabel: 'Operator',
    username: 'operator',
    password: 'Operator@2026',
    accentClass: 'hover:border-emerald-400/60 hover:bg-emerald-950/40 text-emerald-300',
  },
];

export function LoginPage() {
  const { token, user, isLoading, error, login, clearError } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const [username, setUsername] = useState('engineer');
  const [password, setPassword] = useState('Engineer@2026');
  const [showPassword, setShowPassword] = useState(false);
  const [gatewayOnline, setGatewayOnline] = useState<boolean | null>(null);

  const fromPath = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname || '/chat';

  useEffect(() => {
    let mounted = true;
    checkHealthApi()
      .then((res) => {
        if (mounted) setGatewayOnline(res.status === 'ok');
      })
      .catch(() => {
        if (mounted) setGatewayOnline(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  if (token && user) {
    return <Navigate to={fromPath} replace />;
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const ok = await login(username, password);
    if (ok) {
      navigate(fromPath, { replace: true });
    }
  };

  const applyDemoAccount = (account: DemoAccount) => {
    clearError();
    setUsername(account.username);
    setPassword(account.password);
  };

  return (
    <main className="min-h-screen w-full flex flex-col lg:flex-row bg-factory-dark text-slate-100">
      {/* Left 60% Industrial Hero */}
      <section className="relative w-full lg:w-[60%] min-h-[460px] lg:min-h-screen flex flex-col justify-between p-6 sm:p-10 lg:p-14 overflow-hidden border-b lg:border-b-0 lg:border-r border-slate-800/80 bg-gradient-to-br from-factory-darkest via-factory-dark to-factory-card">
        <div className="absolute inset-0 bg-grid-tech opacity-80 pointer-events-none" />
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-brand-600/15 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute -bottom-24 right-10 w-80 h-80 bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none" />

        {/* Brand Bar */}
        <header className="relative z-10 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-xl bg-slate-900/90 border border-brand-400/40 shadow-glow-cyan flex items-center justify-center">
              <Cpu className="w-6 h-6 text-brand-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-white">
                  SmartSOP <span className="text-brand-400 font-extrabold">AI</span>
                </span>
                <span className="text-[10px] uppercase font-mono tracking-widest px-1.5 py-0.5 rounded bg-sky-950/80 border border-sky-500/30 text-sky-300 font-semibold">
                  v2.4
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                Industrial SOP Management &amp; Operations Assistant
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5 px-3.5 py-1.5 rounded-full industrial-glass border border-emerald-500/30">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="text-[11px] font-mono font-semibold tracking-wider text-emerald-300 uppercase">
              SMT Production Knowledge Engine
            </span>
          </div>
        </header>

        {/* Hero Copy */}
        <div className="relative z-10 my-auto py-8 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 mb-5 rounded-md bg-sky-950/70 border border-sky-400/30 text-sky-300 text-xs font-mono font-semibold uppercase tracking-wider">
            <Activity className="w-3.5 h-3.5 text-sky-400" />
            <span>SMART FACTORY • ANTI-HALLUCINATION RAG</span>
          </div>

          <h1 className="text-3xl sm:text-4xl xl:text-5xl font-extrabold text-white tracking-tight leading-[1.18] mb-5">
            Hệ thống Quản lý SOP &amp; Trợ lý Vận hành —{' '}
            <span className="bg-gradient-to-r from-sky-400 via-cyan-300 to-blue-500 bg-clip-text text-transparent">
              SmartSOP AI
            </span>
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed mb-7 max-w-xl">
            Tra cứu quy trình vận hành chuẩn theo mã lỗi thiết bị, đối chiếu trực tiếp trang tài liệu
            PDF gốc với độ trễ thấp (<span className="text-sky-300 font-mono font-semibold">SSE Streaming</span>)
            và quản trị phiếu sự cố gắn kết MTTR toàn xưởng.
          </p>

          <div className="flex flex-wrap items-center gap-2.5 text-xs text-slate-300 font-mono">
            <div className="flex items-center gap-2 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-700/60">
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
              <span>Fuji NXT III: Pick &amp; Place</span>
            </div>
            <div className="flex items-center gap-2 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-700/60">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span>Heller 1809 MK5: Reflow</span>
            </div>
            <div className="flex items-center gap-2 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-700/60">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span>Koh Young 3D AOI / Parmi SPI</span>
            </div>
          </div>
        </div>

        {/* Footer Metric Cards */}
        <footer className="relative z-10 pt-2">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 mb-5">
            <div className="industrial-glass rounded-xl p-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                  Xác thực nguồn
                </span>
                <BadgeCheck className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-extrabold text-emerald-400 font-mono">100% Cited</div>
              <div className="text-xs text-slate-300 mt-1">Trích dẫn đúng tệp &amp; số trang</div>
            </div>

            <div className="industrial-glass rounded-xl p-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                  Tốc độ phản hồi
                </span>
                <Clock className="w-4 h-4 text-brand-400" />
              </div>
              <div className="text-2xl font-extrabold text-brand-400 font-mono">SSE Live</div>
              <div className="text-xs text-slate-300 mt-1">Dual-Retrieval Vector + Regex</div>
            </div>

            <div className="industrial-glass rounded-xl p-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                  Phân quyền RBAC
                </span>
                <ShieldCheck className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-2xl font-extrabold text-white font-mono">4 Roles</div>
              <div className="text-xs text-slate-300 mt-1">Admin • Manager • Engineer • Op</div>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400 font-mono border-t border-slate-800/80 pt-3">
            <span>IPC-A-610 • ANSI/ESD S20.20 • J-STD-033D</span>
            <span>Table-Aware PDF Chunking + ChromaDB</span>
          </div>
        </footer>
      </section>

      {/* Right 40% Auth Panel */}
      <section className="w-full lg:w-[40%] bg-factory-panel flex flex-col justify-center px-6 sm:px-10 lg:px-12 py-10 relative overflow-y-auto">
        <div className="absolute -top-32 -right-32 w-80 h-80 bg-brand-600/15 rounded-full blur-[100px] pointer-events-none" />
        <div className="w-full max-w-md mx-auto space-y-6 relative z-10">
          {/* Form Header */}
          <div className="space-y-2 border-b border-slate-800 pb-5">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-mono tracking-wider uppercase text-brand-400 font-semibold flex items-center gap-1.5">
                <span className="w-2 h-2 rounded bg-brand-400" />
                Cổng Xác Thực Vận Hành
              </span>

              <span
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium border ${
                  gatewayOnline === false
                    ? 'bg-rose-950/70 border-rose-500/40 text-rose-300'
                    : 'bg-emerald-950/70 border-emerald-500/40 text-emerald-400'
                }`}
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    gatewayOnline === false
                      ? 'bg-rose-400'
                      : gatewayOnline === true
                        ? 'bg-emerald-400 animate-pulse'
                        : 'bg-amber-400 animate-pulse'
                  }`}
                />
                {gatewayOnline === false
                  ? 'Gateway API: Offline'
                  : gatewayOnline === true
                    ? 'Gateway API: Online'
                    : 'Gateway API: Checking'}
              </span>
            </div>

            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Đăng Nhập Hệ Thống
            </h2>
            <p className="text-sm text-slate-400">
              Nhập tài khoản nhân sự ca làm việc để nhận JWT Access Token (hiệu lực 8 giờ).
            </p>
          </div>

          {/* Error Banner */}
          {error && (
            <div
              role="alert"
              className="flex items-start gap-2.5 p-3.5 rounded-xl bg-rose-950/70 border border-rose-500/40 text-rose-200 text-xs"
            >
              <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="username"
                className="block text-xs font-mono uppercase tracking-wider text-slate-300 mb-1.5"
              >
                Tên đăng nhập (Username)
              </label>
              <div className="relative">
                <UserIcon className="w-4 h-4 text-brand-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  value={username}
                  onChange={(e) => {
                    if (error) clearError();
                    setUsername(e.target.value);
                  }}
                  placeholder="VD: engineer, admin, operator"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-900/90 border border-slate-700/80 rounded-lg text-white font-mono text-sm placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-xs font-mono uppercase tracking-wider text-slate-300 mb-1.5"
              >
                Mật khẩu truy cập
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-brand-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => {
                    if (error) clearError();
                    setPassword(e.target.value);
                  }}
                  placeholder="••••••••••••"
                  className="w-full pl-10 pr-11 py-2.5 bg-slate-900/90 border border-slate-700/80 rounded-lg text-white font-mono text-sm placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-brand-400 p-1"
                  aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiện mật khẩu'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || !username.trim() || !password}
              className="w-full py-2.5 px-4 rounded-lg bg-brand-600 hover:bg-brand-500 disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold text-sm flex items-center justify-center gap-2 transition-all shadow-glow-blue"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Đang xác thực...</span>
                </>
              ) : (
                <span>Đăng Nhập Ca Làm Việc</span>
              )}
            </button>
          </form>

          {/* Quick-Fill Demo Role Switcher */}
          <div className="pt-2 border-t border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span>Tài khoản mẫu (Seed Data RBAC):</span>
              <span className="text-slate-500">Bấm để điền nhanh</span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              {DEMO_ACCOUNTS.map((acc) => {
                const isSelected = username === acc.username;
                return (
                  <button
                    key={acc.username}
                    type="button"
                    onClick={() => applyDemoAccount(acc)}
                    className={`px-3 py-2 rounded-lg border text-left transition-all bg-slate-900/70 ${
                      isSelected
                        ? 'border-brand-400 bg-brand-600/15 text-white shadow-glow-cyan'
                        : `border-slate-800 text-slate-300 ${acc.accentClass}`
                    }`}
                  >
                    <div className="text-xs font-bold">{acc.roleLabel}</div>
                    <div className="text-[11px] font-mono text-slate-400 truncate">
                      {acc.username} / {acc.password}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
