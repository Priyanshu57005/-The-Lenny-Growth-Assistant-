import React, { useState, useEffect, useRef } from 'react';
import { api } from './services/api';
import { Session, SessionSummary, Message, Artifact, ProviderInfo } from './types';
import { Sidebar } from './components/Sidebar';
import { ChatMessage } from './components/ChatMessage';
import { ArtifactViewer } from './components/ArtifactViewer';
import { QuickPrompts } from './components/QuickPrompts';
import {
  Send,
  Sparkles,
  Bot,
  RefreshCw,
  AlertCircle,
  Menu,
  FileText,
  Cpu,
  Zap,
  BookOpen
} from 'lucide-react';

export const App: React.FC = () => {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Artifact Viewer state
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [isArtifactLoading, setIsArtifactLoading] = useState(false);

  // Provider state
  const [providerInfo, setProviderInfo] = useState<ProviderInfo | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  // Load initial data
  useEffect(() => {
    loadProviders();
    loadSessions();
  }, []);

  const loadProviders = async () => {
    try {
      const data = await api.getProviders();
      setProviderInfo(data);
    } catch (err) {
      console.warn('Failed to load providers:', err);
    }
  };

  const loadSessions = async () => {
    try {
      const list = await api.listSessions();
      setSessions(list);
      if (list.length > 0) {
        selectSession(list[0].id);
      } else {
        handleNewSession();
      }
    } catch (err) {
      setError('Could not connect to backend service. Ensure FastAPI server is running.');
    }
  };

  const selectSession = async (sessionId: string) => {
    setCurrentSessionId(sessionId);
    setError(null);
    try {
      const sess = await api.getSession(sessionId);
      setCurrentSession(sess);
      setMessages(sess.messages || []);
      const lastWithArtifact = [...(sess.messages || [])].reverse().find(m => m.artifact);
      if (lastWithArtifact && lastWithArtifact.artifact) {
        setActiveArtifact(lastWithArtifact.artifact);
      } else {
        setActiveArtifact(null);
      }
    } catch (err) {
      setError('Failed to load conversation history.');
    }
  };

  const handleNewSession = async () => {
    setError(null);
    try {
      const newSess = await api.createSession('New Conversation');
      setSessions(prev => [
        { id: newSess.id, title: newSess.title, created_at: newSess.created_at, updated_at: newSess.updated_at, message_count: 0 },
        ...prev
      ]);
      setCurrentSessionId(newSess.id);
      setCurrentSession(newSess);
      setMessages([]);
      setActiveArtifact(null);
    } catch (err) {
      setError('Failed to create new session.');
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await api.deleteSession(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (currentSessionId === sessionId) {
        const remaining = sessions.filter(s => s.id !== sessionId);
        if (remaining.length > 0) {
          selectSession(remaining[0].id);
        } else {
          handleNewSession();
        }
      }
    } catch (err) {
      setError('Failed to delete session.');
    }
  };

  const handleSwitchProvider = async (provider: string) => {
    try {
      await api.switchProvider(provider);
      await loadProviders();
    } catch (err) {
      setError(`Failed to switch provider to ${provider}`);
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || !currentSessionId || isSending) return;

    const userMessageText = query.trim();
    setInput('');
    setIsSending(true);
    setError(null);

    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      session_id: currentSessionId,
      role: 'user',
      content: userMessageText,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    if (userMessageText.toLowerCase().includes('html') || userMessageText.toLowerCase().includes('artifact') || userMessageText.toLowerCase().includes('ship 30')) {
      setIsArtifactLoading(true);
    }

    try {
      const assistantMsg = await api.sendMessage(currentSessionId, userMessageText);
      setMessages(prev => [...prev, assistantMsg]);
      
      if (assistantMsg.artifact) {
        setActiveArtifact(assistantMsg.artifact);
      }

      loadSessions();
    } catch (err: any) {
      setError(err.message || 'Error communicating with Lenny Assistant.');
    } finally {
      setIsSending(false);
      setIsArtifactLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#070a11] text-slate-100 font-sans">
      {/* Sidebar */}
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={selectSession}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
        providerInfo={providerInfo}
        onSwitchProvider={handleSwitchProvider}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />

      {/* Main Workspace Layout */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Top Glassmorphic Header */}
        <header className="h-15 border-b border-slate-800/80 bg-[#090d16]/80 backdrop-blur-xl px-5 flex items-center justify-between flex-shrink-0 z-10 shadow-sm">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white lg:hidden transition-colors"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center space-x-2.5">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow-md shadow-blue-500/20 font-display">
                L
              </div>
              <h2 className="text-sm font-bold text-slate-100 tracking-tight font-display truncate">
                {currentSession?.title || 'Lenny Growth Assistant'}
              </h2>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {providerInfo && (
              <div className="hidden sm:flex items-center space-x-2 text-xs bg-slate-900/90 px-3.5 py-1.5 rounded-full border border-slate-800/90 shadow-sm backdrop-blur-md">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-slate-400 font-medium">Engine:</span>
                <span className="font-bold text-slate-200 uppercase font-mono">{providerInfo.active_provider}</span>
                <span className="text-slate-500 text-[11px] font-mono">
                  ({providerInfo.active_provider === 'ollama' ? providerInfo.ollama_model : providerInfo.active_provider === 'anthropic' ? providerInfo.anthropic_model : providerInfo.active_provider === 'openai' ? providerInfo.openai_model : 'grounded-demo'})
                </span>
              </div>
            )}
            
            {activeArtifact && (
              <button
                onClick={() => setActiveArtifact(activeArtifact ? null : activeArtifact)}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-purple-950/80 border border-purple-700/60 text-purple-200 text-xs font-semibold hover:bg-purple-900 transition-colors shadow-md shadow-purple-950/40"
              >
                <FileText className="w-3.5 h-3.5 text-purple-400" />
                <span>Toggle Canvas</span>
              </button>
            )}
          </div>
        </header>

        {/* Global Error Banner */}
        {error && (
          <div className="bg-red-950/90 border-b border-red-800/80 px-5 py-2.5 text-xs text-red-200 flex items-center justify-between backdrop-blur-md">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-white font-bold text-xs">
              Dismiss
            </button>
          </div>
        )}

        {/* Workspace Body: Chat Panel + Artifact Panel */}
        <div className="flex-1 flex overflow-hidden">
          {/* Chat Panel */}
          <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#070a11]">
            {/* Messages Scroll Area */}
            <div className="flex-1 overflow-y-auto">
              {messages.length === 0 ? (
                <div className="max-w-3xl mx-auto px-4 py-10 text-center">
                  {/* Hero Header */}
                  <div className="relative inline-block mb-4">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-xl shadow-blue-500/25 mx-auto border border-blue-400/30">
                      <Sparkles className="w-8 h-8 fill-white/20" />
                    </div>
                  </div>
                  <h2 className="text-2xl font-extrabold text-slate-100 mb-2 font-display tracking-tight">
                    Ground Your Growth in Expert Knowledge
                  </h2>
                  <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed mb-6 font-sans">
                    Ask questions grounded in Lenny's Podcast transcripts, generate Ship 30 for 30 essays, or request interactive HTML artifacts.
                  </p>
                  <QuickPrompts onSelectPrompt={(p) => handleSendMessage(p)} />
                </div>
              ) : (
                messages.map((msg) => (
                  <ChatMessage
                    key={msg.id}
                    message={msg}
                    onOpenArtifact={(art) => setActiveArtifact(art)}
                  />
                ))
              )}

              {isSending && (
                <div className="py-4 px-6 bg-[#0d1424]/60 flex items-center space-x-3 border-t border-slate-900/80 backdrop-blur-md">
                  <div className="w-8 h-8 rounded-lg bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                    <Bot className="w-4 h-4 animate-spin" />
                  </div>
                  <div className="flex items-center space-x-2 text-xs text-slate-300 font-medium">
                    <span>Synthesizing transcript vector chunks...</span>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-blue-400" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Form Bar */}
            <div className="p-4 border-t border-slate-800/80 bg-[#080c14] backdrop-blur-xl">
              <div className="max-w-4xl mx-auto relative">
                <div className="relative rounded-2xl border border-slate-800/90 bg-[#0d1322] focus-within:border-blue-500/80 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:shadow-[0_0_30px_rgba(59,130,246,0.15)] transition-all duration-200 p-2">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    placeholder="Ask a growth question, request a Ship 30 essay, or ask for an HTML artifact..."
                    rows={2}
                    className="w-full bg-transparent text-xs text-slate-100 placeholder-slate-500 focus:outline-none resize-none px-3 py-1 font-sans leading-relaxed"
                  />
                  <div className="flex items-center justify-between pt-2 px-3 border-t border-slate-800/50">
                    <div className="flex items-center space-x-2 text-[10px] text-slate-400 font-mono">
                      <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-blue-400 font-semibold flex items-center">
                        <BookOpen className="w-3 h-3 mr-1 text-blue-400" />
                        RAG Grounded
                      </span>
                      <span className="hidden sm:inline">Press Enter to send, Shift + Enter for newline</span>
                    </div>
                    <button
                      onClick={() => handleSendMessage()}
                      disabled={!input.trim() || isSending}
                      className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 disabled:hover:from-blue-600 font-bold text-white text-xs transition-all shadow-md shadow-blue-600/20 flex items-center space-x-1.5"
                    >
                      <span>Send</span>
                      <Send className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Artifact Side-by-Side Canvas */}
          {activeArtifact && (
            <ArtifactViewer
              artifact={activeArtifact}
              onClose={() => setActiveArtifact(null)}
              isLoading={isArtifactLoading}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
