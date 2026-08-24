import React from 'react';
import { Sparkles, BookOpen, Code, Layers, ArrowUpRight, Zap } from 'lucide-react';

interface QuickPromptsProps {
  onSelectPrompt: (promptText: string) => void;
}

export const QuickPrompts: React.FC<QuickPromptsProps> = ({ onSelectPrompt }) => {
  const starterPrompts = [
    {
      icon: BookOpen,
      label: 'LNO Framework',
      tag: 'Product Strategy',
      badgeColor: 'from-blue-500 to-indigo-500',
      text: 'What is Shreyas Doshi\'s LNO Framework for Product Managers and how do I apply it?'
    },
    {
      icon: Sparkles,
      label: 'Ship 30 PLG Essay',
      tag: 'Ship 30 Skill',
      badgeColor: 'from-amber-500 to-orange-500',
      text: 'Write a Ship 30 for 30 essay on Product-Led Growth and self-serve user onboarding.'
    },
    {
      icon: Code,
      label: 'Interactive Pricing HTML',
      tag: 'HTML Artifact',
      badgeColor: 'from-purple-500 to-pink-500',
      text: 'Create an interactive 3-tier SaaS pricing table HTML artifact with monthly/annual toggle.'
    },
    {
      icon: Layers,
      label: 'Founder Mode & Airbnb',
      tag: 'Leadership',
      badgeColor: 'from-emerald-500 to-teal-500',
      text: 'Explain Brian Chesky\'s advice on Founder Mode vs Manager Mode and product excellence.'
    }
  ];

  return (
    <div className="w-full max-w-3xl mx-auto my-6 px-2">
      <div className="flex items-center justify-between mb-3 px-1">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center">
          <Zap className="w-3.5 h-3.5 mr-1.5 text-amber-400 fill-amber-400" />
          Explore Grounded Transcript Capabilities
        </h3>
        <span className="text-[10px] text-slate-500 font-mono">Grounded RAG Engine Active</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {starterPrompts.map((p, i) => {
          const Icon = p.icon;
          return (
            <button
              key={i}
              onClick={() => onSelectPrompt(p.text)}
              className="p-3.5 rounded-xl border border-slate-800/80 bg-gradient-to-b from-[#0e1424] to-[#0a0e1a] hover:from-[#131b30] hover:to-[#0e1424] hover:border-slate-700/90 text-left transition-all duration-200 group shadow-lg shadow-black/30 relative overflow-hidden flex flex-col justify-between"
            >
              {/* Subtle top glow bar */}
              <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${p.badgeColor} opacity-70 group-hover:opacity-100 transition-opacity`} />
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div className={`w-7 h-7 rounded-lg bg-gradient-to-tr ${p.badgeColor} flex items-center justify-center text-white shadow-md`}>
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-xs font-bold text-slate-100 group-hover:text-blue-300 transition-colors font-display">
                      {p.label}
                    </span>
                  </div>
                  <ArrowUpRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-blue-400 transition-colors transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed font-sans group-hover:text-slate-300 transition-colors">
                  {p.text}
                </p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between">
                <span className="text-[9px] uppercase tracking-wider font-mono text-slate-500 font-semibold px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                  {p.tag}
                </span>
                <span className="text-[10px] text-blue-400/80 group-hover:text-blue-400 font-medium">Try Prompt →</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
