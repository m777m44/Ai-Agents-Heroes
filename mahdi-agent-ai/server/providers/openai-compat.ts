import type { ChatMessage, ModelAdapter, ModelInfo, ModelResponse, ToolSpec } from './types.js';
import { ProviderError, parseArgs } from './types.js';

interface OpenAICompatOptions {
  id: string;
  label: string;
  provider: string;
  model: string;
  baseUrl: string;
  apiKey?: string;
  description: string;
  extraHeaders?: Record<string, string>;
}

function toOpenAIMessage(m: ChatMessage): Record<string, unknown> {
  if (m.role === 'tool') return { role: 'tool', tool_call_id: m.toolCallId, content: m.content };
  if (m.role === 'assistant' && m.toolCalls?.length) {
    return {
      role: 'assistant',
      content: m.content || null,
      tool_calls: m.toolCalls.map((c) => ({
        id: c.id,
        type: 'function',
        function: { name: c.name, arguments: JSON.stringify(c.args ?? {}) },
      })),
    };
  }
  return { role: m.role, content: m.content };
}

/**
 * Adapter for any OpenAI-compatible Chat Completions endpoint
 * (OpenAI, OpenRouter, Groq, Google Gemini's OpenAI endpoint, Ollama, ...).
 */
export function createOpenAICompatAdapter(opts: OpenAICompatOptions): ModelAdapter {
  const info: ModelInfo = {
    id: opts.id,
    label: opts.label,
    provider: opts.provider,
    model: opts.model,
    available: true,
    description: opts.description,
  };
  return {
    info,
    async complete(messages: ChatMessage[], tools: ToolSpec[], signal?: AbortSignal): Promise<ModelResponse> {
      const headers: Record<string, string> = { 'Content-Type': 'application/json', ...opts.extraHeaders };
      if (opts.apiKey) headers.Authorization = `Bearer ${opts.apiKey}`;
      const body = {
        model: opts.model,
        messages: messages.map(toOpenAIMessage),
        ...(tools.length
          ? {
              tools: tools.map((t) => ({
                type: 'function',
                function: { name: t.name, description: t.description, parameters: t.parameters },
              })),
              tool_choice: 'auto',
            }
          : {}),
      };
      const res = await fetch(`${opts.baseUrl.replace(/\/$/, '')}/chat/completions`, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
        signal,
      });
      if (!res.ok) {
        const detail = (await res.text()).slice(0, 400);
        throw new ProviderError(`${opts.label} returned HTTP ${res.status}: ${detail}`);
      }
      const json = (await res.json()) as {
        choices?: { message?: { content?: string | null; tool_calls?: { id?: string; function?: { name?: string; arguments?: unknown } }[] } }[];
      };
      const msg = json.choices?.[0]?.message ?? {};
      const toolCalls = (msg.tool_calls ?? [])
        .filter((c) => c.function?.name)
        .map((c, i) => ({
          id: c.id || `call_${Date.now()}_${i}`,
          name: c.function!.name!,
          args: parseArgs(c.function!.arguments),
        }));
      return { text: msg.content ?? '', toolCalls };
    },
  };
}
