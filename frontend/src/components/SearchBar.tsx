'use client';

import { useState } from 'react';
import { Search, Globe, Loader2 } from 'lucide-react';

interface SearchBarProps {
  onSearch: (companyName: string, websiteUrl?: string) => void;
  isLoading: boolean;
}

export default function SearchBar({ onSearch, isLoading }: SearchBarProps) {
  const [companyName, setCompanyName] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [showUrlField, setShowUrlField] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName.trim() || isLoading) return;
    onSearch(companyName.trim(), websiteUrl.trim() || undefined);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-3">
      {/* Main search row */}
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-[#a1a1aa] pointer-events-none">
            <Search size={18} />
          </div>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="Enter company name..."
            disabled={isLoading}
            className="w-full bg-[#141414] border border-[#2a2a2a] rounded-xl pl-11 pr-4 py-4 text-white placeholder-[#52525b] text-base focus:outline-none focus:border-[#4f46e5] focus:ring-2 focus:ring-[#4f46e5]/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>
        <button
          type="submit"
          disabled={!companyName.trim() || isLoading}
          className="px-6 py-4 bg-[#4f46e5] hover:bg-[#4338ca] disabled:bg-[#2a2a3a] disabled:text-[#52525b] disabled:cursor-not-allowed text-white rounded-xl font-semibold text-base transition-all flex items-center gap-2 whitespace-nowrap min-w-[130px] justify-center"
          style={{ boxShadow: companyName.trim() && !isLoading ? '0 0 20px rgba(79,70,229,0.3)' : 'none' }}
        >
          {isLoading ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              Researching
            </>
          ) : (
            <>
              <Search size={18} />
              Research
            </>
          )}
        </button>
      </div>

      {/* URL toggle + input */}
      <div>
        {!showUrlField ? (
          <button
            type="button"
            onClick={() => setShowUrlField(true)}
            className="text-sm text-[#52525b] hover:text-[#a1a1aa] transition-colors flex items-center gap-1.5 pl-1"
          >
            <Globe size={14} />
            Add company website URL (optional)
          </button>
        ) : (
          <div className="relative animate-slide-in">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-[#a1a1aa] pointer-events-none">
              <Globe size={16} />
            </div>
            <input
              type="url"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              placeholder="https://company.com (optional)"
              disabled={isLoading}
              className="w-full bg-[#0f0f0f] border border-[#222] rounded-xl pl-10 pr-4 py-3 text-white placeholder-[#3f3f46] text-sm focus:outline-none focus:border-[#4f46e5]/50 transition-all disabled:opacity-50"
            />
          </div>
        )}
      </div>
    </form>
  );
}
