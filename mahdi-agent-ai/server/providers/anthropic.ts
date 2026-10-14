import type { ChatMessage, ModelAdapter, ModelResponse, ToolSpec } from './types.js';
import { ProviderError } from './types.js';

interface AnthropicOptions {
  id: string;
  label: string;
  model: string;
  apiKey: string;
  baseUrl?: string;
  description: string;
}

type AnthropicBlock =
  | { type: 'text'; text: string }
  | { type: 'tool_use'; id: string; name: string; input: Record<string, unknown> }
  | { type: 'tool_result'; tool_use_id: string; content: string };

interface AnthropicMessage {
  role: 'user' | 'assistant';
  content: string | AnthropicBlock[];
}

function toAnthropicMessages(messages: ChatMessage[]): { system: string; messages: AnthropicMessage[] } {
  const system = messages
    .filter((m) => m.role === 'system')
    .map((m) => m.content)
    .join('\n\n');
  const out: AnthropicMessage[] = [];
  for (const m of messages) {
    if (m.role === 'system') continue;
    if (m.role === 'tool') {
      const block: AnthropicBlock = { type: 'tool_result', tool_use_id: m.toolCallId ?? '', content: m.content || '(empty)' };
      const prev = out[out.length - 1];
      if (prev && prev.role === 'user' && Array.isArray(prev.content) && prev.content.every((b) => b.type === 'tool_result')) {
        prev.content.push(block);
      } else {
        out.push({ role: 'user', content: [block] });
      }
      continue;
    }
    if (m.role === 'assistant') {
      const blocks: AnthropicBlock[] = [];
      if (m.content) blocks.push({ type: 'text', text: m.content });
      for (const c of m.toolCalls ?? []) blocks.push({ type: 'tool_use', id: c.id, name: c.name, input: c.args ?? {} });
      if (!blocks.length) blocks.push({ type: 'text', text: '...' });
      out.push({ role: 'assistant', content: blocks });
      continue;
    }
    out.push({ role: 'user', content: m.content || '...' });
  }
  return { system, messages: out };
}

export function createAnthropicAdapter(opts: AnthropicOptions): ModelAdapter {
  return {
    info: {
      id: opts.id,
      label: opts.label,
      provider: 'anthropic',
      model: opts.model,
      available: true,
      description: opts.description,
    },
    async complete(messages: ChatMessage[], tools: ToolSpec[], signal?: AbortSignal): Promise<ModelResponse> {
      const converted = toAnthropicMessages(messages);
      const body = {
        model: opts.model,
        max_tokens: 4096,
        system: converted.system,
        messages: converted.messages,
        ...(tools.length
          ? { tools: tools.map((t) => ({ name: t.name, description: t.description, input_schema: t.parameters })) }
          : {}),
      };
      const res = await fetch(`${(opts.baseUrl ?? 'https://api.anthropic.com').replace(/\/$/, '')}/v1/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': opts.apiKey,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify(body),
        signal,
      });
      if (!res.ok) {
        const detail = (await res.text()).slice(0, 400);
        throw new ProviderError(`${opts.label} returned HTTP ${res.status}: ${detail}`);
      }
      const json = (await res.json()) as { content?: AnthropicBlock[] };
      const blocks = json.content ?? [];
      const text = blocks
        .filter((b): b is { type: 'text'; text: string } => b.type === 'text')
        .map((b) => b.text)
        .join('\n');
      const toolCalls = blocks
        .filter((b): b is Extract<AnthropicBlock, { type: 'tool_use' }> => b.type === 'tool_use')
        .map((b) => ({ id: b.id, name: b.name, args: b.input ?? {} }));
      return { text, toolCalls };
    },
  };
}
