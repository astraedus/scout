'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Crosshair } from 'lucide-react';
import SearchBar from '@/components/SearchBar';
import ProgressTracker from '@/components/ProgressTracker';
import HistoryList from '@/components/HistoryList';
import { startResearch, streamResearch, getHistory, searchBriefings } from '@/lib/api';
import { ResearchJob, ProgressEvent, SearchResult } from '@/types';

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [currentCompany, setCurrentCompany] = useState('');
  const [progressStage, setProgressStage] = useState('');
  const [progressPct, setProgressPct] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [history, setHistory] = useState<ResearchJob[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);

  const loadHistory = useCallback(async () => {
    try {
      const data = await getHistory();
      const items = Array.isArray(data) ? data : data?.results || [];
      setHistory(items);
    } catch {
      // Backend not running — silently fail, show empty state
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleSearch = async (companyName: string, websiteUrl?: string) => {
    setIsLoading(true);
    setCurrentCompany(companyName);
    setProgressStage('website');
    setProgressPct(5);
    setProgressMessage('Starting research...');

    try {
      const job = await startResearch(companyName, websiteUrl);
      const jobId = job.id || job.research_id;

      if (!jobId) {
        throw new Error('No job ID returned from API');
      }

      // Connect SSE stream
      const source = streamResearch(jobId);

      source.onmessage = (event) => {
        try {
          const data: ProgressEvent = JSON.parse(event.data);
          setProgressStage(data.stage || data.status || '');
          setProgressPct(data.progress || 0);
          if (data.message) setProgressMessage(data.message);

          // On completion, navigate to briefing
          if (data.status === 'complete' || data.progress >= 100) {
            source.close();
            setTimeout(() => {
              router.push(`/research/${jobId}`);
            }, 800);
          }

          if (data.status === 'failed') {
            source.close();
            setIsLoading(false);
            setProgressMessage('Research failed. Please try again.');
          }
        } catch {
          // Ignore parse errors
        }
      };

      source.onerror = () => {
        // SSE connection dropped — poll for completion
        source.close();
        const poll = setInterval(async () => {
          try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/research/${jobId}`);
            const data = await res.json();
            if (data.status === 'complete') {
              clearInterval(poll);
              router.push(`/research/${jobId}`);
            } else if (data.status === 'failed') {
              clearInterval(poll);
              setIsLoading(false);
              setProgressMessage('Research failed. Please try again.');
            }
          } catch {
            clearInterval(poll);
            setIsLoading(false);
          }
        }, 2000);
      };
    } catch {
      setIsLoading(false);
      setProgressMessage('Failed to connect to backend. Is it running?');
    }
  };

  const handleSelectHistory = (id: string) => {
    router.push(`/research/${id}`);
  };

  const handleSemanticSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    setSearchResults([]);
    try {
      const data = await searchBriefings(searchQuery.trim());
      setSearchResults(data.results || []);
    } catch {
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  return (
    <div className="min-h-screen" style={{ background: '#0a0a0a' }}>
      {/* Background radial glow */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(79,70,229,0.08) 0%, transparent 70%)',
        }}
      />

      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Header */}
        <div className="text-center mb-14">
          {/* Logo */}
          <div className="flex items-center justify-center gap-3 mb-6">
            <div
              className="w-12 h-12 rounded-2xl flex items-center justify-center"
              style={{
                background: 'linear-gradient(135deg, #4f46e5, #6366f1)',
                boxShadow: '0 0 30px rgba(79,70,229,0.4)',
              }}
            >
              <Crosshair size={24} className="text-white" strokeWidth={1.5} />
            </div>
            <span
              className="text-4xl font-bold tracking-tight"
              style={{
                background: 'linear-gradient(135deg, #fff 30%, #a5b4fc 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              Scout
            </span>
          </div>

          <p className="text-lg text-[#71717a] font-light tracking-wide">
            AI-Powered Company Research in Seconds
          </p>
        </div>

        {/* Search card */}
        <div
          className="rounded-2xl border border-[#222] p-8 mb-6"
          style={{
            background: 'linear-gradient(135deg, #141414 0%, #111111 100%)',
            boxShadow: '0 4px 40px rgba(0,0,0,0.4)',
          }}
        >
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {/* Progress tracker */}
        {isLoading && (
          <div className="mb-6">
            <ProgressTracker
              stage={progressStage}
              progress={progressPct}
              message={progressMessage}
              companyName={currentCompany}
            />
          </div>
        )}

        {/* Error / info message when not loading */}
        {!isLoading && progressMessage && progressMessage.includes('fail') && (
          <div
            className="mb-6 px-4 py-3 rounded-xl text-sm text-[#fca5a5] border"
            style={{ background: 'rgba(239,68,68,0.08)', borderColor: 'rgba(239,68,68,0.2)' }}
          >
            {progressMessage}
          </div>
        )}

        {/* Semantic Search section */}
        <div
          className="rounded-2xl border border-[#222] p-6 mb-6"
          style={{
            background: 'linear-gradient(135deg, #141414 0%, #111111 100%)',
            boxShadow: '0 4px 40px rgba(0,0,0,0.4)',
          }}
        >
          <h2 className="text-sm font-semibold text-[#71717a] uppercase tracking-widest mb-4">
            Semantic Search
          </h2>
          <form onSubmit={handleSemanticSearch} className="flex gap-3">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search briefings..."
              className="flex-1 rounded-xl px-4 py-2 text-sm text-white bg-[#1a1a1a] border border-[#2a2a2a] outline-none focus:border-[#4f46e5] transition-colors"
            />
            <button
              type="submit"
              disabled={searchLoading || !searchQuery.trim()}
              className="px-5 py-2 rounded-xl text-sm font-medium text-white transition-opacity disabled:opacity-40"
              style={{ background: 'linear-gradient(135deg, #4f46e5, #6366f1)' }}
            >
              {searchLoading ? 'Searching...' : 'Search'}
            </button>
          </form>

          {searchResults.length > 0 && (
            <div className="mt-4 space-y-2">
              {searchResults.map((result) => (
                <button
                  key={result.research_id}
                  onClick={() => router.push(`/research/${result.research_id}`)}
                  className="w-full text-left rounded-xl border border-[#222] p-4 hover:border-[#4f46e5] transition-colors"
                  style={{ background: '#0f0f0f' }}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-semibold text-white">{result.company_name}</span>
                    <span className="text-xs text-[#4f46e5] font-mono">
                      {(result.similarity * 100).toFixed(1)}% match
                    </span>
                  </div>
                  <p className="text-xs text-[#71717a] line-clamp-2">{result.snippet}</p>
                </button>
              ))}
            </div>
          )}

          {!searchLoading && searchQuery && searchResults.length === 0 && (
            <p className="mt-4 text-xs text-[#3f3f46]">
              No results found. Research some companies first to enable semantic search.
            </p>
          )}
        </div>

        {/* History section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-[#71717a] uppercase tracking-widest">
              Recent Research
            </h2>
            {history.length > 0 && (
              <span className="text-xs text-[#3f3f46]">
                {history.length} {history.length === 1 ? 'report' : 'reports'}
              </span>
            )}
          </div>

          {historyLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-14 rounded-xl shimmer"
                  style={{ opacity: 1 - i * 0.2 }}
                />
              ))}
            </div>
          ) : (
            <HistoryList items={history} onSelect={handleSelectHistory} />
          )}
        </div>
      </div>
    </div>
  );
}
