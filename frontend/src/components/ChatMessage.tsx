import React from 'react';
import { Message, Artifact } from '../types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { SourceCard } from './SourceCard';
import { Bot, User, Sparkles, FileText, Code, CheckCircle2, ArrowRight } from 'lucide-react';

interface ChatMessageProps {
  message: Message;
  onOpenArtifact: (artifact: Artifact) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, onOpenArtifact }) => {
  const isUser = message.role === 'user';

  const getRouteBadge = (route?: string) => {
    if (!route) return null;
    switch (route) {
      case 'SHIP30_ESSAY':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/10 border border-amber-500/30 text-amber-300 shadow-sm">
            <Sparkles className="w-3 h-3 text-amber-400 mr-0.5" />
            <span>Ship 30 Skill</span>
          </span>
        );
      case 'ARTIFACT_GEN':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/10 border border-purple-500/30 text-purple-300 shadow-sm">
            <Code className="w-3 h-3 text-purple-400 mr-0.5" />
            <span>Artifact Canvas</span>
          </span>
        );
      case 'KNOWLEDGE_QNA':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 border border-blue-500/30 text-blue-300 shadow-sm">
            <CheckCircle2 className="w-3 h-3 text-blue-400 mr-0.5" />
            <span>Grounded Q&A</span>
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className={`py-5 px-4 sm:px-8 flex space-x-4 border-b border-slate-900/60 transition-colors ${
      isUser ? 'bg-[#090d16]/40' : 'bg-[#0d1424]/40 backdrop-blur-sm'
    }`}>
      <div className="flex-shrink-0">
        {isUser ? (
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/20 border border-blue-400/30 font-bold">
            <User className="w-4 h-4" />
          </div>
        ) : (
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20 border border-indigo-400/30 font-bold">
            <Bot className="w-4.5 h-4.5" />
          </div>
        )}
      </div>

      <div className="flex-1 space-y-2.5 overflow-hidden">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <span className="text-xs font-bold text-slate-200 font-display">
              {isUser ? 'You' : 'Lenny Assistant'}
            </span>
            {!isUser && getRouteBadge(message.agent_route)}
          </div>
          <span className="text-[10px] text-slate-500 font-mono">
            {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        <div className="text-sm text-slate-200 leading-relaxed font-sans prose prose-invert max-w-none prose-p:leading-relaxed prose-headings:font-display prose-headings:text-slate-100 prose-code:font-mono prose-code:bg-slate-950 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-blue-300">
          {isUser ? (
            <p className="whitespace-pre-wrap font-medium">{message.content}</p>
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Source Citation Component */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <SourceCard sources={message.sources} />
        )}

        {/* Artifact Trigger Banner if message produced an artifact */}
        {!isUser && message.artifact && (
          <div className="mt-4 p-3.5 rounded-xl border border-purple-500/30 bg-gradient-to-r from-purple-950/40 via-indigo-950/20 to-slate-950/40 flex items-center justify-between backdrop-blur-md shadow-lg shadow-purple-950/30 group">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-lg bg-purple-500/20 border border-purple-400/30 text-purple-300">
                <FileText className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-100 font-display">{message.artifact.title}</h4>
                <p className="text-[10px] text-purple-300/80 uppercase tracking-wider font-mono font-semibold">
                  {message.artifact.artifact_type} Artifact Available
                </p>
              </div>
            </div>
            <button
              onClick={() => message.artifact && onOpenArtifact(message.artifact)}
              className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-semibold transition-all shadow-md shadow-purple-600/30 flex items-center space-x-1.5"
            >
              <span>View Canvas</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
