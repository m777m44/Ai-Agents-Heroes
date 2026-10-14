export type Role = 'system' | 'user' | 'assistant' | 'tool';

export interface ToolCall {
  id: string;
  name: string;
  args: Record<string, unknown>;
}

/** Provider-neutral chat message. */
export interface ChatMessage {
  role: Role;
  content: string;
  toolCalls?: ToolCall[];
  toolCallId?: string;
  toolName?: string;
  createdAt?: string;
}

export interface ToolSpec {
  name: string;
  description: string;
  parameters: Record<string, unknown>;
}

export interface ModelResponse {
  text: string;
  toolCalls: ToolCall[];
}

export interface ModelInfo {
  id: string;
  label: string;
  provider: string;
  model: string;
  available: boolean;
  description: string;
}

export interface ModelAdapter {
  info: ModelInfo;
  complete(messages: ChatMessage[], tools: ToolSpec[], signal?: AbortSignal): Promise<ModelResponse>;
}

export class ProviderError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ProviderError';
  }
}

export function parseArgs(raw: unknown): Record<string, unknown> {
  if (raw && typeof raw === 'object') return raw as Record<string, unknown>;
  if (typeof raw !== 'string' || !raw.trim()) return {};
  try {
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' ? (parsed as Record<string, unknown>) : {};
  } catch {
    return { _raw: raw };
  }
}
