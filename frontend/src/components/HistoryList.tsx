'use client';

import { ResearchJob } from '@/types';
import { Clock, CheckCircle, XCircle, Loader2, ChevronRight, Building2 } from 'lucide-react';

interface HistoryListProps {
  items: ResearchJob[];
  onSelect: (id: string) => void;
}

function StatusBadge({ status }: { status: ResearchJob['status'] }) {
  const config = {
    pending: { label: 'Pending', color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', icon: <Clock size={11} /> },
    extracting: { label: 'Extracting', color: '#6366f1', bg: 'rgba(99,102,241,0.1)', icon: <Loader2 size={11} className="animate-spin" /> },
    synthesizing: { label: 'Synthesizing', color: '#6366f1', bg: 'rgba(99,102,241,0.1)', icon: <Loader2 size={11} className="animate-spin" /> },
    complete: { label: 'Complete', color: '#10b981', bg: 'rgba(16,185,129,0.1)', icon: <CheckCircle size={11} /> },
    failed: { label: 'Failed', color: '#ef4444', bg: 'rgba(239,68,68,0.1)', icon: <XCircle size={11} /> },
  }[status] || { label: status, color: '#a1a1aa', bg: 'rgba(161,161,170,0.1)', icon: null };

  return (
    <span
      className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full"
      style={{ color: config.color, background: config.bg }}
    >
      {config.icon}
      {config.label}
    </span>
  );
}

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } catch {
    return dateStr;
  }
}

export default function HistoryList({ items, onSelect }: HistoryListProps) {
  if (items.length === 0) {
    return (
      <div className="text-center py-12">
        <div
          className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center"
          style={{ background: 'rgba(79,70,229,0.08)', border: '1px solid rgba(79,70,229,0.15)' }}
        >
          <Building2 size={24} className="text-[#4f46e5]" />
        </div>
        <p className="text-[#52525b] text-sm">No research yet.</p>
        <p className="text-[#3f3f46] text-xs mt-1">Search for a company above to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <button
          key={item.id}
          onClick={() => onSelect(item.id)}
          className="w-full text-left group"
        >
          <div
            className="flex items-center justify-between px-4 py-3.5 rounded-xl border border-[#1e1e1e] transition-all duration-200 group-hover:border-[#2a2a2a] group-hover:bg-[#141414]"
            style={{ background: '#0f0f0f' }}
          >
            <div className="flex items-center gap-3 min-w-0">
              {/* Company initial */}
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 text-sm font-bold"
                style={{
                  background: 'linear-gradient(135deg, rgba(79,70,229,0.2), rgba(99,102,241,0.1))',
                  border: '1px solid rgba(79,70,229,0.2)',
                  color: '#6366f1',
                }}
              >
                {item.company_name.charAt(0).toUpperCase()}
              </div>

              <div className="min-w-0">
                <p className="text-sm font-medium text-white truncate group-hover:text-[#a5b4fc] transition-colors">
                  {item.company_name}
                </p>
                <p className="text-xs text-[#52525b] mt-0.5">
                  {formatDate(item.created_at)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 ml-3 flex-shrink-0">
              <StatusBadge status={item.status} />
              <ChevronRight
                size={14}
                className="text-[#3f3f46] group-hover:text-[#6366f1] transition-colors"
              />
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}
