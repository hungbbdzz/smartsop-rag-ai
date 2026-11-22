import { CheckCircle2, Wrench, type LucideIcon } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { ROLE_META } from '../types/auth';

interface PlaceholderPageProps {
  title: string;
  milestone: string;
  description: string;
  icon: LucideIcon;
  highlights: string[];
}

export function PlaceholderPage({
  title,
  milestone,
  description,
  icon: Icon,
  highlights,
}: PlaceholderPageProps) {
  const { user } = useAuthStore();
  const roleMeta = user ? ROLE_META[user.role] : null;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="rounded-2xl bg-factory-card/90 border border-slate-800 p-6 sm:p-8 shadow-xl space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-800 pb-5">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-sky-950/80 border border-brand-400/40 flex items-center justify-center text-brand-400 shadow-glow-cyan">
              <Icon className="w-6 h-6" />
            </div>
            <div>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-amber-950/70 border border-amber-500/40 text-amber-300 text-[10px] font-mono font-semibold uppercase tracking-wider">
                <Wrench className="w-3 h-3" />
                {milestone}
              </span>
              <h2 className="mt-1.5 text-xl font-bold text-white">{title}</h2>
            </div>
          </div>

          {user && roleMeta && (
            <div className="text-right">
              <div className="text-[11px] font-mono text-slate-400 mb-1">Phiên hiện tại</div>
              <span
                className={`inline-flex items-center px-2.5 py-1 rounded-full border text-xs font-mono font-semibold ${roleMeta.badgeClass}`}
              >
                {user.username} • {roleMeta.label}
              </span>
            </div>
          )}
        </div>

        <p className="text-sm text-slate-300 leading-relaxed">{description}</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {highlights.map((item) => (
            <div
              key={item}
              className="flex items-start gap-2.5 p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 text-xs text-slate-300"
            >
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
