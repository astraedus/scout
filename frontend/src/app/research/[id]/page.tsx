'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import {
  ArrowLeft,
  Building2,
  Users,
  Newspaper,
  Code2,
  TrendingUp,
  Swords,
  MessageSquare,
  DollarSign,
  ShieldCheck,
  ExternalLink,
  MapPin,
  Calendar,
  Layers,
  Globe,
  AlertCircle,
  Loader2,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import BriefingCard from '@/components/BriefingCard';
import { getResearch } from '@/lib/api';
import { ResearchJob, Briefing } from '@/types';

interface PageProps {
  params: Promise<{ id: string }>;
}

function ConfidenceBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const level = pct >= 70 ? 'High' : pct >= 40 ? 'Medium' : 'Low';
  const color = pct >= 70 ? '#10b981' : pct >= 40 ? '#f59e0b' : '#ef4444';
  const bg = pct >= 70 ? 'rgba(16,185,129,0.1)' : pct >= 40 ? 'rgba(245,158,11,0.1)' : 'rgba(239,68,68,0.1)';

  return (
    <div className="flex items-center gap-3">
      <span
        className="text-xs font-semibold px-3 py-1 rounded-full"
        style={{ color, background: bg, border: `1px solid ${color}30` }}
      >
        {level} Confidence
      </span>
      <div className="flex items-center gap-2">
        <div className="w-24 h-1.5 bg-[#1e1e1e] rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{ width: `${pct}%`, background: color }}
          />
        </div>
        <span className="text-xs text-[#52525b] font-mono">{pct}%</span>
      </div>
    </div>
  );
}

function MetaGrid({ briefing }: { briefing: Briefing }) {
  const items = [
    { label: 'Industry', value: briefing.industry, icon: <Layers size={14} /> },
    { label: 'Stage', value: briefing.stage, icon: <TrendingUp size={14} /> },
    { label: 'Founded', value: briefing.founded, icon: <Calendar size={14} /> },
    { label: 'HQ', value: briefing.headquarters, icon: <MapPin size={14} /> },
    { label: 'Size', value: briefing.size, icon: <Users size={14} /> },
    { label: 'Website', value: briefing.website, icon: <Globe size={14} />, isLink: true },
  ].filter(i => i.value);

  if (items.length === 0) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-4">
      {items.map(({ label, value, icon, isLink }) => (
        <div
          key={label}
          className="px-3 py-2.5 rounded-lg"
          style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid #1e1e1e' }}
        >
          <div className="flex items-center gap-1.5 mb-1">
            <span className="text-[#52525b]">{icon}</span>
            <span className="text-xs text-[#52525b] font-medium">{label}</span>
          </div>
          {isLink && value ? (
            <a
              href={value.startsWith('http') ? value : `https://${value}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-[#6366f1] hover:text-[#a5b4fc] transition-colors flex items-center gap-1 truncate"
            >
              <span className="truncate">{value}</span>
              <ExternalLink size={11} className="flex-shrink-0" />
            </a>
          ) : (
            <p className="text-sm text-white font-medium truncate">{value}</p>
          )}
        </div>
      ))}
    </div>
  );
}

export default function BriefingPage({ params }: PageProps) {
  const { id } = use(params);
  const router = useRouter();
  const [job, setJob] = useState<ResearchJob | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getResearch(id);
        setJob(data);
      } catch {
        setError('Failed to load research. Is the backend running?');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0a0a0a' }}>
        <div className="text-center">
          <Loader2 size={32} className="text-[#4f46e5] animate-spin mx-auto mb-3" />
          <p className="text-[#52525b] text-sm">Loading briefing...</p>
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#0a0a0a' }}>
        <div className="text-center max-w-sm">
          <AlertCircle size={32} className="text-[#ef4444] mx-auto mb-3" />
          <p className="text-white font-medium mb-1">Could not load briefing</p>
          <p className="text-[#52525b] text-sm mb-6">{error || 'Job not found'}</p>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 text-sm text-[#6366f1] hover:text-white border border-[#2a2a2a] hover:border-[#4f46e5] rounded-lg transition-all"
          >
            Back to dashboard
          </button>
        </div>
      </div>
    );
  }

  const briefing = job.briefing;
  const companyName = briefing?.company_name || job.company_name;

  return (
    <div className="min-h-screen" style={{ background: '#0a0a0a' }}>
      {/* Background glow */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 80% 40% at 50% -5%, rgba(79,70,229,0.06) 0%, transparent 70%)',
        }}
      />

      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Back button */}
        <button
          onClick={() => router.push('/')}
          className="flex items-center gap-2 text-sm text-[#52525b] hover:text-white transition-colors mb-8 group"
        >
          <ArrowLeft size={16} className="group-hover:-translate-x-0.5 transition-transform" />
          Back to dashboard
        </button>

        {/* Page header */}
        <div className="mb-8">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="flex items-center gap-4">
              <div
                className="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-bold flex-shrink-0"
                style={{
                  background: 'linear-gradient(135deg, rgba(79,70,229,0.2), rgba(99,102,241,0.1))',
                  border: '1px solid rgba(79,70,229,0.3)',
                  color: '#a5b4fc',
                }}
              >
                {companyName.charAt(0).toUpperCase()}
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white tracking-tight">{companyName}</h1>
                {briefing?.industry && (
                  <p className="text-[#71717a] text-sm mt-0.5">{briefing.industry}</p>
                )}
              </div>
            </div>

            {briefing && (
              <div className="flex flex-col items-end gap-2">
                <ConfidenceBadge score={briefing.confidence} />
              </div>
            )}
          </div>
        </div>

        {/* Failed state */}
        {job.status === 'failed' && (
          <div
            className="mb-6 p-4 rounded-xl border flex items-start gap-3"
            style={{ background: 'rgba(239,68,68,0.08)', borderColor: 'rgba(239,68,68,0.2)' }}
          >
            <AlertCircle size={18} className="text-[#ef4444] flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-[#fca5a5]">Research failed</p>
              {job.error && <p className="text-xs text-[#71717a] mt-0.5">{job.error}</p>}
            </div>
          </div>
        )}

        {!briefing && job.status !== 'failed' && (
          <div className="flex items-center gap-3 p-4 rounded-xl border border-[#2a2a2a] mb-6"
            style={{ background: '#141414' }}>
            <Loader2 size={16} className="text-[#4f46e5] animate-spin" />
            <p className="text-sm text-[#71717a]">Research in progress...</p>
          </div>
        )}

        {briefing && (
          <div className="space-y-4">
            {/* Overview */}
            <BriefingCard title="Overview" icon={<Building2 size={16} />} defaultOpen={true}>
              <p className="text-sm text-[#a1a1aa] leading-relaxed mt-3">
                {briefing.summary}
              </p>

              <MetaGrid briefing={briefing} />

              {briefing.business_model && (
                <div className="mt-4 pt-4 border-t border-[#1e1e1e]">
                  <p className="text-xs text-[#52525b] font-medium uppercase tracking-wider mb-2">Business Model</p>
                  <p className="text-sm text-[#a1a1aa] leading-relaxed">{briefing.business_model}</p>
                </div>
              )}

              {briefing.products_services?.length > 0 && (
                <div className="mt-4 pt-4 border-t border-[#1e1e1e]">
                  <p className="text-xs text-[#52525b] font-medium uppercase tracking-wider mb-2">Products & Services</p>
                  <div className="flex flex-wrap gap-2">
                    {briefing.products_services.map((item, i) => (
                      <span
                        key={i}
                        className="text-xs px-2.5 py-1 rounded-lg text-[#a1a1aa]"
                        style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid #222' }}
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </BriefingCard>

            {/* Key People */}
            {briefing.key_people?.length > 0 && (
              <BriefingCard title="Key People" icon={<Users size={16} />} accentColor="#6366f1">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3">
                  {briefing.key_people.map((person, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-3 p-3 rounded-lg"
                      style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid #1e1e1e' }}
                    >
                      <div
                        className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                        style={{
                          background: `hsl(${(i * 47 + 220) % 360}, 60%, 20%)`,
                          color: `hsl(${(i * 47 + 220) % 360}, 80%, 70%)`,
                        }}
                      >
                        {person.name.charAt(0)}
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-white truncate">{person.name}</p>
                        <p className="text-xs text-[#71717a] truncate">{person.title}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </BriefingCard>
            )}

            {/* Recent News */}
            {briefing.recent_news?.length > 0 && (
              <BriefingCard title="Recent News" icon={<Newspaper size={16} />} accentColor="#f59e0b">
                <div className="space-y-3 mt-3">
                  {briefing.recent_news.map((item, i) => (
                    <div
                      key={i}
                      className="flex gap-4 pb-3"
                      style={{ borderBottom: i < briefing.recent_news.length - 1 ? '1px solid #1a1a1a' : 'none' }}
                    >
                      {/* Timeline dot */}
                      <div className="flex flex-col items-center">
                        <div
                          className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0"
                          style={{ background: '#f59e0b' }}
                        />
                        {i < briefing.recent_news.length - 1 && (
                          <div className="w-px flex-1 mt-1" style={{ background: '#1e1e1e' }} />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white leading-snug">{item.headline}</p>
                        {item.date && (
                          <p className="text-xs text-[#52525b] mt-0.5">{item.date}</p>
                        )}
                        {item.summary && (
                          <p className="text-xs text-[#71717a] mt-1 leading-relaxed">{item.summary}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </BriefingCard>
            )}

            {/* Tech Stack */}
            {(briefing.tech_stack?.confirmed?.length > 0 || briefing.tech_stack?.inferred?.length > 0) && (
              <BriefingCard title="Tech Stack" icon={<Code2 size={16} />} accentColor="#10b981">
                <div className="mt-3 space-y-4">
                  {briefing.tech_stack.confirmed?.length > 0 && (
                    <div>
                      <p className="text-xs text-[#52525b] font-medium uppercase tracking-wider mb-2">Confirmed</p>
                      <div className="flex flex-wrap gap-2">
                        {briefing.tech_stack.confirmed.map((tech, i) => (
                          <span
                            key={i}
                            className="text-xs px-2.5 py-1 rounded-lg font-medium"
                            style={{
                              background: 'rgba(16,185,129,0.1)',
                              color: '#6ee7b7',
                              border: '1px solid rgba(16,185,129,0.2)',
                            }}
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {briefing.tech_stack.inferred?.length > 0 && (
                    <div>
                      <p className="text-xs text-[#52525b] font-medium uppercase tracking-wider mb-2">Inferred</p>
                      <div className="flex flex-wrap gap-2">
                        {briefing.tech_stack.inferred.map((tech, i) => (
                          <span
                            key={i}
                            className="text-xs px-2.5 py-1 rounded-lg font-medium"
                            style={{
                              background: 'rgba(255,255,255,0.04)',
                              color: '#71717a',
                              border: '1px solid #222',
                            }}
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </BriefingCard>
            )}

            {/* Growth Signals */}
            {briefing.growth_signals?.length > 0 && (
              <BriefingCard title="Growth Signals" icon={<TrendingUp size={16} />} accentColor="#10b981">
                <ul className="mt-3 space-y-2">
                  {briefing.growth_signals.map((signal, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <div
                        className="w-5 h-5 rounded flex items-center justify-center flex-shrink-0 mt-0.5"
                        style={{ background: 'rgba(16,185,129,0.1)' }}
                      >
                        <TrendingUp size={11} className="text-[#10b981]" />
                      </div>
                      <span className="text-sm text-[#a1a1aa] leading-relaxed">{signal}</span>
                    </li>
                  ))}
                </ul>
              </BriefingCard>
            )}

            {/* Competitive Landscape */}
            {briefing.competitive_landscape?.length > 0 && (
              <BriefingCard title="Competitive Landscape" icon={<Swords size={16} />} accentColor="#f59e0b">
                <div className="mt-3 flex flex-wrap gap-2">
                  {briefing.competitive_landscape.map((comp, i) => (
                    <span
                      key={i}
                      className="text-sm px-3 py-1.5 rounded-lg font-medium"
                      style={{
                        background: 'rgba(245,158,11,0.08)',
                        color: '#fbbf24',
                        border: '1px solid rgba(245,158,11,0.2)',
                      }}
                    >
                      {comp}
                    </span>
                  ))}
                </div>
              </BriefingCard>
            )}

            {/* Talking Points — most important, highlighted */}
            {briefing.talking_points?.length > 0 && (
              <BriefingCard
                title="Talking Points"
                icon={<MessageSquare size={16} />}
                accentColor="#6366f1"
                defaultOpen={true}
              >
                <div className="mt-3 space-y-3">
                  {briefing.talking_points.map((point, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-4 p-4 rounded-xl"
                      style={{
                        background: 'linear-gradient(135deg, rgba(79,70,229,0.08), rgba(99,102,241,0.04))',
                        border: '1px solid rgba(79,70,229,0.15)',
                      }}
                    >
                      <div
                        className="w-7 h-7 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0"
                        style={{
                          background: 'linear-gradient(135deg, #4f46e5, #6366f1)',
                          color: 'white',
                          fontSize: '12px',
                        }}
                      >
                        {i + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm text-[#c7d2fe] leading-relaxed">{point}</p>
                      </div>
                      <MessageSquare size={14} className="text-[#4f46e5] flex-shrink-0 mt-0.5" />
                    </div>
                  ))}
                </div>
              </BriefingCard>
            )}

            {/* Funding */}
            {briefing.funding && (
              <BriefingCard title="Funding" icon={<DollarSign size={16} />} accentColor="#10b981">
                <div className="mt-3 space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    {briefing.funding.total_raised && (
                      <div
                        className="p-3 rounded-lg text-center"
                        style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.15)' }}
                      >
                        <p className="text-xs text-[#52525b] mb-1">Total Raised</p>
                        <p className="text-lg font-bold text-[#10b981]">{briefing.funding.total_raised}</p>
                      </div>
                    )}
                    {briefing.funding.last_round && (
                      <div
                        className="p-3 rounded-lg text-center"
                        style={{ background: 'rgba(16,185,129,0.05)', border: '1px solid #1e1e1e' }}
                      >
                        <p className="text-xs text-[#52525b] mb-1">Last Round</p>
                        <p className="text-lg font-bold text-white">{briefing.funding.last_round}</p>
                      </div>
                    )}
                  </div>
                  {briefing.funding.investors?.length > 0 && (
                    <div>
                      <p className="text-xs text-[#52525b] font-medium uppercase tracking-wider mb-2">Investors</p>
                      <div className="flex flex-wrap gap-2">
                        {briefing.funding.investors.map((investor, i) => (
                          <span
                            key={i}
                            className="text-xs px-2.5 py-1 rounded-lg text-[#a1a1aa]"
                            style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid #1e1e1e' }}
                          >
                            {investor}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </BriefingCard>
            )}

            {/* Data Quality Footer */}
            <div
              className="rounded-2xl border border-[#1e1e1e] p-5"
              style={{ background: '#0f0f0f' }}
            >
              <div className="flex items-center gap-2 mb-4">
                <ShieldCheck size={16} className="text-[#52525b]" />
                <span className="text-xs font-semibold text-[#52525b] uppercase tracking-wider">Data Quality</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {[
                  { name: 'Website', ok: true },
                  { name: 'News', ok: briefing.recent_news?.length > 0 },
                  { name: 'LinkedIn', ok: briefing.key_people?.length > 0 },
                  { name: 'Crunchbase', ok: !!briefing.funding },
                  { name: 'Careers', ok: briefing.growth_signals?.length > 0 },
                ].map(({ name, ok }) => (
                  <span
                    key={name}
                    className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg font-medium"
                    style={{
                      background: ok ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)',
                      color: ok ? '#6ee7b7' : '#fca5a5',
                      border: `1px solid ${ok ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}`,
                    }}
                  >
                    {ok
                      ? <CheckCircle size={11} />
                      : <XCircle size={11} />
                    }
                    {name}
                  </span>
                ))}
              </div>
              <div className="mt-4 pt-3 border-t border-[#1a1a1a]">
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="text-[#52525b]">Overall confidence</span>
                  <span className="text-[#71717a] font-mono">{Math.round(briefing.confidence * 100)}%</span>
                </div>
                <div className="w-full h-2 bg-[#1a1a1a] rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: `${briefing.confidence * 100}%`,
                      background: briefing.confidence >= 0.7
                        ? 'linear-gradient(90deg, #059669, #10b981)'
                        : briefing.confidence >= 0.4
                        ? 'linear-gradient(90deg, #d97706, #f59e0b)'
                        : 'linear-gradient(90deg, #dc2626, #ef4444)',
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
