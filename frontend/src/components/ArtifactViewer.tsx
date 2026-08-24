import React, { useState } from 'react';
import { Artifact } from '../types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Code,
  FileText,
  Copy,
  Check,
  Download,
  X,
  Maximize2,
  Minimize2,
  RefreshCw,
  ShieldCheck,
  Eye,
  Sparkles
} from 'lucide-react';

interface ArtifactViewerProps {
  artifact: Artifact | null;
  onClose: () => void;
  isLoading?: boolean;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({
  artifact,
  onClose,
  isLoading = false
}) => {
  const [copied, setCopied] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');

  if (!artifact && !isLoading) {
    return (
      <div className="hidden lg:flex flex-col items-center justify-center h-full border-l border-slate-800/80 bg-[#070a11] p-8 text-center text-slate-500">
        <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-600 mb-4">
          <FileText className="w-7 h-7 stroke-[1.5]" />
        </div>
        <h3 className="text-sm font-bold text-slate-300 mb-1 font-display">Artifact Canvas Empty</h3>
        <p className="text-xs max-w-xs leading-relaxed text-slate-500">
          Ask the assistant to write a Ship 30 essay, design an HTML layout artifact, or create a PM framework doc to view it side-by-side here.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full border-l border-slate-800/80 bg-[#070a11] p-8 text-center">
        <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center mb-4">
          <RefreshCw className="w-6 h-6 text-blue-400 animate-spin" />
        </div>
        <h3 className="text-sm font-bold text-slate-200 font-display">Generating Artifact Canvas...</h3>
        <p className="text-xs text-slate-500 mt-1">Applying layout, CSS styles, and transcript grounding</p>
      </div>
    );
  }

  if (!artifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = artifact.artifact_type === 'html' ? 'html' : 'md';
    const blob = new Blob([artifact.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className={`flex flex-col h-full border-l border-slate-800/80 bg-[#070a11] transition-all duration-200 backdrop-blur-xl ${
        isFullscreen ? 'fixed inset-0 z-50 bg-[#070a11]' : 'w-full lg:w-1/2'
      }`}
    >
      {/* Top Controls Bar */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-slate-800/80 bg-[#090d16]/90 backdrop-blur-md">
        <div className="flex items-center space-x-3 overflow-hidden">
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-[10px] font-mono font-bold">
            {artifact.artifact_type === 'html' ? <Code className="w-3 h-3" /> : <FileText className="w-3 h-3" />}
            <span className="uppercase">{artifact.artifact_type}</span>
          </div>
          <h2 className="text-xs font-bold text-slate-200 truncate font-display">{artifact.title}</h2>
        </div>

        <div className="flex items-center space-x-2">
          {/* Toggle between Preview and Code view for HTML */}
          {artifact.artifact_type === 'html' && (
            <div className="flex rounded-lg bg-slate-900 p-0.5 border border-slate-800 mr-2">
              <button
                onClick={() => setActiveTab('preview')}
                className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                  activeTab === 'preview' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Eye className="w-3 h-3 inline mr-1" />
                Preview
              </button>
              <button
                onClick={() => setActiveTab('code')}
                className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                  activeTab === 'code' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Code className="w-3 h-3 inline mr-1" />
                Code
              </button>
            </div>
          )}

          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
            title="Copy Code"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>
          <button
            onClick={handleDownload}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
            title="Download Artifact"
          >
            <Download className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-red-400 transition-colors"
            title="Close Canvas"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Security Status Subhead for HTML */}
      {artifact.artifact_type === 'html' && (
        <div className="px-5 py-1.5 bg-emerald-950/30 border-b border-emerald-900/30 text-[10px] text-emerald-400 flex items-center justify-between font-mono font-medium">
          <span className="flex items-center space-x-1">
            <ShieldCheck className="w-3.5 h-3.5 mr-1 text-emerald-400" />
            Isolated Sandbox Active (CSP Enforced)
          </span>
          <span className="text-slate-500">iframe sandbox="allow-scripts"</span>
        </div>
      )}

      {/* Artifact Body Display */}
      <div className="flex-1 overflow-auto p-5 bg-[#070a11]">
        {artifact.artifact_type === 'html' ? (
          activeTab === 'preview' ? (
            <iframe
              title={artifact.title}
              srcDoc={artifact.content}
              sandbox="allow-scripts"
              className="w-full h-full min-h-[550px] border-0 rounded-xl bg-white shadow-2xl"
            />
          ) : (
            <pre className="p-4 bg-slate-950 rounded-xl text-slate-200 font-mono text-xs overflow-x-auto leading-relaxed border border-slate-800/80 shadow-inner">
              <code>{artifact.content}</code>
            </pre>
          )
        ) : (
          <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed font-sans prose-p:leading-relaxed prose-headings:font-display prose-headings:text-slate-100">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {artifact.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};
