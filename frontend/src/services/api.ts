import { Session, SessionSummary, Message, Artifact, ProviderInfo } from '../types';

const API_BASE = '/api';

export const api = {
  // Health & Providers
  getHealth: async () => {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  getProviders: async (): Promise<ProviderInfo> => {
    const res = await fetch(`${API_BASE}/providers`);
    if (!res.ok) throw new Error('Failed to fetch providers');
    return res.json();
  },

  switchProvider: async (provider: string): Promise<{ active_provider: string }> => {
    const res = await fetch(`${API_BASE}/providers/switch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider }),
    });
    if (!res.ok) throw new Error('Failed to switch provider');
    return res.json();
  },

  // Sessions
  createSession: async (title?: string): Promise<Session> => {
    const res = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
  },

  listSessions: async (): Promise<SessionSummary[]> => {
    const res = await fetch(`${API_BASE}/sessions`);
    if (!res.ok) throw new Error('Failed to list sessions');
    return res.json();
  },

  getSession: async (id: string): Promise<Session> => {
    const res = await fetch(`${API_BASE}/sessions/${id}`);
    if (!res.ok) throw new Error('Failed to get session details');
    return res.json();
  },

  deleteSession: async (id: string): Promise<void> => {
    const res = await fetch(`${API_BASE}/sessions/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete session');
  },

  // Messages
  sendMessage: async (
    sessionId: string,
    content: string,
    providerOverride?: string
  ): Promise<Message> => {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, provider_override: providerOverride }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to send message' }));
      throw new Error(err.detail || 'Failed to send message');
    }
    return res.json();
  },

  // Artifacts
  getArtifact: async (id: string): Promise<Artifact> => {
    const res = await fetch(`${API_BASE}/artifacts/${id}`);
    if (!res.ok) throw new Error('Failed to fetch artifact');
    return res.json();
  },
};
