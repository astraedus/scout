'use client';

import { useState, ReactNode } from 'react';
import { ChevronDown } from 'lucide-react';

interface BriefingCardProps {
  title: string;
  icon: ReactNode;
  children: ReactNode;
  defaultOpen?: boolean;
  accentColor?: string;
}

export default function BriefingCard({
  title,
  icon,
  children,
  defaultOpen = true,
  accentColor = '#4f46e5',
}: BriefingCardProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div
      className="scout-card overflow-hidden transition-all duration-200 hover:border-[#333]"
      style={{
        background: 'linear-gradient(135deg, #141414 0%, #111111 100%)',
      }}
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-6 py-4 text-left group"
      >
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ background: `${accentColor}20`, color: accentColor }}
          >
            {icon}
          </div>
          <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
            {title}
          </h3>
        </div>
        <ChevronDown
          size={16}
          className="text-[#52525b] group-hover:text-[#a1a1aa] transition-all duration-200"
          style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)' }}
        />
      </button>

      <div
        className="overflow-hidden transition-all duration-300"
        style={{ maxHeight: isOpen ? '2000px' : '0px', opacity: isOpen ? 1 : 0 }}
      >
        <div className="px-6 pb-6 pt-1 border-t border-[#1e1e1e]">
          {children}
        </div>
      </div>
    </div>
  );
}
