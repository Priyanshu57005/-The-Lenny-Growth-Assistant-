import React, { useState } from 'react';
import { SourceCitation } from '../types';
import { BookOpen, ExternalLink, ChevronDown, ChevronUp, Sparkles, UserCheck, ShieldCheck } from 'lucide-react';

interface SourceCardProps {
  sources: SourceCitation[];
}

export const SourceCard: React.FC<SourceCardProps> = ({ sources }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3.5 rounded-xl border border-blue-500/20 bg-gradient-to-r from-blue-950/40 via-indigo-950/20 to-slate-950/40 text-xs overflow-hidden backdrop-blur-md shadow-lg shadow-blue-950/20">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3.5 py-2.5 flex items-center justify-between text-blue-300 hover:bg-blue-900/30 transition-all duration-200"
      >
        <div className="flex items-center space-x-2.5">
          <div className="w-5 h-5 rounded-md bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-blue-400">
            <BookOpen className="w-3 h-3" />
          </div>
          <span className="font-semibold text-slate-200 tracking-tight">
            Grounded in {sources.length} Lenny Podcast {sources.length === 1 ? 'Source' : 'Sources'}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-semibold flex items-center space-x-1">
            <ShieldCheck className="w-2.5 h-2.5 inline mr-0.5 text-emerald-400" />
            {Math.round(sources[0].score * 100)}% match
          </span>
          {isOpen ? <ChevronUp className="w-4 h-4 text-blue-400" /> : <ChevronDown className="w-4 h-4 text-blue-400" />}
        </div>
      </button>

      {isOpen && (
        <div className="p-3 border-t border-blue-500/15 space-y-2.5 bg-slate-950/60 backdrop-blur-xl">
          {sources.map((src, i) => (
            <div
              key={src.chunk_id || i}
              className="p-3 rounded-lg border border-slate-800/80 bg-[#0d1424]/90 space-y-2 hover:border-slate-700/80 transition-all shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-amber-500 to-orange-500 flex items-center justify-center text-white text-[10px] font-bold shadow-sm">
                    {src.guest.charAt(0)}
                  </div>
                  <div>
                    <span className="font-bold text-slate-100 text-xs flex items-center">
                      {src.guest}
                      <Sparkles className="w-3 h-3 text-amber-400 ml-1 inline" />
                    </span>
                  </div>
                </div>
                {src.url && (
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[11px] text-blue-400 hover:text-blue-300 font-medium flex items-center space-x-1 bg-blue-950/60 px-2 py-0.5 rounded border border-blue-800/50 hover:bg-blue-900/50 transition-colors"
                  >
                    <span>Episode</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
              <p className="text-slate-300 text-[11px] font-medium leading-snug">{src.title}</p>
              <p className="text-slate-300 text-[11px] italic bg-[#070b14] p-2.5 rounded-md border border-slate-800/80 leading-relaxed font-sans">
                "{src.snippet}"
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
