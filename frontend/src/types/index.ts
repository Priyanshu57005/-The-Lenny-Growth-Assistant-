export interface SourceCitation {
  chunk_id: string;
  guest: string;
  title: string;
  url?: string;
  date?: string;
  snippet: string;
  score: number;
}

export interface Artifact {
  id: string;
  session_id: string;
  message_id?: string;
  artifact_type: 'markdown' | 'html';
  title: string;
  content: string;
  created_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: SourceCitation[];
  agent_route?: string;
  created_at: string;
  artifact?: Artifact;
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface SessionSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ProviderInfo {
  active_provider: string;
  available_providers: string[];
  ollama_model: string;
  anthropic_model: string;
  openai_model: string;
  status: Record<string, boolean>;
}
