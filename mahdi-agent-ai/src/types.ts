export type Lang = 'ar' | 'en';

export interface ModelInfo {
  id: string;
  label: string;
  provider: string;
  model: string;
  available: boolean;
  description: string;
}

export interface TemplateInfo {
  id: string;
  icon: string;
  name: { ar: string; en: string };
  description: { ar: string; en: string };
}

export interface ToolCall {
  id: string;
  name: string;
  args: Record<string, unknown>;
}

export interface Turn {
  role: 'user' | 'assistant' | 'tool';
  content: string;
  toolCalls?: ToolCall[];
  toolCallId?: string;
  toolName?: string;
  createdAt?: string;
}

export interface Conversation {
  id: string;
  title: string;
  projectId: string;
  model: string;
  pinned: boolean;
  createdAt: string;
  updatedAt: string;
  turns: Turn[];
}

export interface ConversationSummary {
  id: string;
  title: string;
  projectId: string;
  model: string;
  pinned: boolean;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  preview: string;
}

export interface FileInfo {
  path: string;
  size: number;
}

export interface Version {
  id: string;
  path: string;
  action: 'create' | 'update' | 'delete' | 'restore' | 'template' | 'import';
  actor: 'user' | 'agent' | 'system';
  message: string;
  size: number;
  hash: string | null;
  createdAt: string;
}

export interface DiffLine {
  type: 'equal' | 'add' | 'del';
  text: string;
}

export interface DiffResult {
  version: Version & { content: string | null };
  lines: DiffLine[];
  added: number;
  removed: number;
}

export interface StreamEvent {
  event: string;
  data: Record<string, any>;
}
