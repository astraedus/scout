'use client';

import { Check, X, Loader2, Globe, Newspaper, Users, TrendingUp, Briefcase, Sparkles } from 'lucide-react';

interface ProgressStep {
  id: string;
  label: string;
  icon: React.ReactNode;
  status: 'pending' | 'active' | 'done' | 'failed';
}

interface ProgressTrackerProps {
  stage: string;
  progress: number;
  message?: string;
  companyName: string;
}

const STAGES = [
  { id: 'website', label: 'Visiting website', icon: <Globe size={16} />, keywords: ['website', 'scraping', 'extracting', 'visiting'] },
  { id: 'news', label: 'Searching news', icon: <Newspaper size={16} />, keywords: ['news', 'searching', 'articles'] },
  { id: 'linkedin', label: 'Checking LinkedIn', icon: <Users size={16} />, keywords: ['linkedin', 'people', 'team'] },
  { id: 'crunchbase', label: 'Analyzing Crunchbase', icon: <TrendingUp size={16} />, keywords: ['crunchbase', 'funding', 'investors'] },
  { id: 'careers', label: 'Reviewing careers', icon: <Briefcase size={16} />, keywords: ['careers', 'jobs', 'hiring'] },
  { id: 'synthesis', label: 'Synthesizing briefing', icon: <Sparkles size={16} />, keywords: ['synth', 'briefing', 'compiling', 'analyzing', 'complete'] },
];

function getStepStatus(stageId: string, currentStage: string, progress: number): 'pending' | 'active' | 'done' | 'failed' {
  const stageIndex = STAGES.findIndex(s => s.id === stageId);
  const currentIndex = STAGES.findIndex(s =>
    s.keywords.some(k => currentStage.toLowerCase().includes(k))
  );

  if (currentStage.toLowerCase().includes('complete') || progress >= 100) {
    return 'done';
  }

  if (currentIndex === -1) {
    return stageIndex === 0 ? 'active' : 'pending';
  }

  if (stageIndex < currentIndex) return 'done';
  if (stageIndex === currentIndex) return 'active';
  return 'pending';
}

export default function ProgressTracker({ stage, progress, message, companyName }: ProgressTrackerProps) {
  const steps: ProgressStep[] = STAGES.map(s => ({
    id: s.id,
    label: s.label,
    icon: s.icon,
    status: getStepStatus(s.id, stage, progress),
  }));

  const clampedProgress = Math.min(100, Math.max(0, progress));

  return (
    <div
      className="w-full rounded-2xl border border-[#2a2a2a] overflow-hidden animate-slide-in"
      style={{
        background: 'linear-gradient(135deg, #141414 0%, #0f0f1a 100%)',
        boxShadow: '0 0 40px rgba(79,70,229,0.1)',
      }}
    >
      {/* Header */}
      <div className="px-6 py-4 border-b border-[#1e1e2e] flex items-center gap-3">
        <div
          className="w-2 h-2 rounded-full bg-[#4f46e5] animate-pulse-glow"
          style={{ flexShrink: 0 }}
        />
        <div>
          <p className="text-sm font-semibold text-white">
            Researching <span className="text-[#6366f1]">{companyName}</span>
          </p>
          {message && (
            <p className="text-xs text-[#52525b] mt-0.5">{message}</p>
          )}
        </div>
        <div className="ml-auto text-xs font-mono text-[#4f46e5] font-semibold">
          {clampedProgress}%
        </div>
      </div>

      {/* Steps grid */}
      <div className="p-6 grid grid-cols-2 md:grid-cols-3 gap-3">
        {steps.map((step) => (
          <div
            key={step.id}
            className="flex items-center gap-3 p-3 rounded-lg transition-all"
            style={{
              background: step.status === 'active'
                ? 'rgba(79,70,229,0.1)'
                : step.status === 'done'
                ? 'rgba(16,185,129,0.05)'
                : 'rgba(255,255,255,0.02)',
              border: step.status === 'active'
                ? '1px solid rgba(79,70,229,0.3)'
                : step.status === 'done'
                ? '1px solid rgba(16,185,129,0.2)'
                : '1px solid rgba(255,255,255,0.04)',
            }}
          >
            {/* Status icon */}
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0"
              style={{
                background: step.status === 'active'
                  ? 'rgba(79,70,229,0.2)'
                  : step.status === 'done'
                  ? 'rgba(16,185,129,0.15)'
                  : step.status === 'failed'
                  ? 'rgba(239,68,68,0.15)'
                  : 'rgba(255,255,255,0.05)',
              }}
            >
              {step.status === 'active' && (
                <Loader2 size={14} className="text-[#4f46e5] animate-spin" />
              )}
              {step.status === 'done' && (
                <Check size={14} className="text-[#10b981]" strokeWidth={2.5} />
              )}
              {step.status === 'failed' && (
                <X size={14} className="text-[#ef4444]" />
              )}
              {step.status === 'pending' && (
                <div className="text-[#3f3f46]">{step.icon}</div>
              )}
            </div>

            {/* Label */}
            <span
              className="text-xs font-medium truncate"
              style={{
                color: step.status === 'active'
                  ? '#a5b4fc'
                  : step.status === 'done'
                  ? '#6ee7b7'
                  : step.status === 'failed'
                  ? '#fca5a5'
                  : '#52525b',
              }}
            >
              {step.label}
            </span>
          </div>
        ))}
      </div>

      {/* Progress bar */}
      <div className="px-6 pb-5">
        <div className="w-full h-1.5 bg-[#1e1e1e] rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700 ease-out"
            style={{
              width: `${clampedProgress}%`,
              background: 'linear-gradient(90deg, #4f46e5, #6366f1)',
              boxShadow: '0 0 8px rgba(99,102,241,0.6)',
            }}
          />
        </div>
      </div>
    </div>
  );
}
