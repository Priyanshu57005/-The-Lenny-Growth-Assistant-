import React from 'react';
import { SessionSummary, ProviderInfo } from '../types';
import {
  Plus,
  MessageSquare,
  Trash2,
  Cpu,
  CheckCircle,
  XCircle,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  Zap
} from 'lucide-react';

interface SidebarProps {
  sessions: SessionSummary[];
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
  providerInfo: ProviderInfo | null;
  onSwitchProvider: (provider: string) => void;
  isOpen: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  currentSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  providerInfo,
  onSwitchProvider,
  isOpen,
  onToggle
}) => {
  return (
    <aside
      className={`fixed lg:static inset-y-0 left-0 z-40 flex flex-col bg-[#070a11] border-r border-slate-800/80 transition-all duration-300 backdrop-blur-xl ${
        isOpen ? 'w-72' : 'w-0 lg:w-16 overflow-hidden'
      }`}
    >
      {/* Sidebar Header */}
      <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
        {isOpen ? (
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/25 border border-blue-400/30">
              <Sparkles className="w-4 h-4 fill-white/20" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-slate-100 tracking-tight font-display">Lenny Assistant</h1>
              <p className="text-[10px] font-mono text-slate-400 font-medium">Product & Growth Copilot</p>
            </div>
          </div>
        ) : (
          <div className="w-full flex justify-center">
            <Sparkles className="w-5 h-5 text-blue-500" />
          </div>
        )}

        <button
          onClick={onToggle}
          className="p-1.5 rounded-lg hover:bg-slate-800/80 text-slate-400 hover:text-slate-200 transition-colors"
        >
          {isOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {/* New Chat Action */}
      <div className="p-3.5">
        <button
          onClick={onNewSession}
          className={`w-full py-2.5 px-3.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 hover:brightness-110 text-white font-bold text-xs flex items-center justify-center space-x-2 transition-all shadow-lg shadow-blue-600/25 border border-blue-400/30 active:scale-[0.98] ${
            !isOpen && 'lg:px-0'
          }`}
        >
          <Plus className="w-4 h-4 stroke-[2.5]" />
          {isOpen && <span className="font-display">New Conversation</span>}
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto px-3 py-1 space-y-1.5">
        {isOpen && (
          <div className="flex items-center justify-between px-2 py-1 text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">
            <span>Conversations</span>
            <span>{sessions.length}</span>
          </div>
        )}
        {sessions.map((s) => {
          const isActive = s.id === currentSessionId;
          return (
            <div
              key={s.id}
              onClick={() => onSelectSession(s.id)}
              className={`group relative flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-150 text-xs ${
                isActive
                  ? 'bg-gradient-to-r from-blue-950/80 to-indigo-950/60 text-slate-100 font-semibold border border-blue-500/40 shadow-md shadow-blue-950/30'
                  : 'text-slate-400 hover:bg-slate-900/80 hover:text-slate-200'
              }`}
            >
              {isActive && (
                <div className="absolute left-0 top-2 bottom-2 w-1 bg-blue-500 rounded-r-full shadow-[0_0_8px_#3b82f6]" />
              )}
              <div className="flex items-center space-x-2.5 truncate pl-1">
                <MessageSquare className={`w-3.5 h-3.5 flex-shrink-0 ${isActive ? 'text-blue-400' : 'text-slate-500'}`} />
                {isOpen && <span className="truncate font-sans">{s.title}</span>}
              </div>
              {isOpen && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(s.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 text-slate-500 transition-opacity"
                  title="Delete Session"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Provider & System Control Footer */}
      {isOpen && providerInfo && (
        <div className="p-3.5 border-t border-slate-800/80 bg-[#090d16] text-xs space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-300 flex items-center font-display">
              <Cpu className="w-3.5 h-3.5 mr-1.5 text-blue-400" />
              Active LLM Engine
            </span>
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 font-semibold">
              {providerInfo.active_provider}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-1.5 pt-0.5">
            {providerInfo.available_providers.map((p) => {
              const isSelected = p === providerInfo.active_provider;
              const isHealthy = providerInfo.status[p];
              return (
                <button
                  key={p}
                  onClick={() => onSwitchProvider(p)}
                  className={`py-1.5 px-2 rounded-lg text-[10px] font-mono flex items-center justify-between border transition-all ${
                    isSelected
                      ? 'bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border-blue-500/50 text-blue-200 font-bold shadow-sm'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                  }`}
                >
                  <span className="capitalize">{p}</span>
                  {isHealthy ? (
                    <CheckCircle className="w-3 h-3 text-emerald-400" />
                  ) : (
                    <XCircle className="w-3 h-3 text-slate-600" />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </aside>
  );
};
