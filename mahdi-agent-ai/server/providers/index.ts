import '../env.js';
import { createAnthropicAdapter } from './anthropic.js';
import { createOpenAICompatAdapter } from './openai-compat.js';
import { createDemoAdapter } from './offline.js';
import type { ModelAdapter, ModelInfo } from './types.js';

export type { ChatMessage, ModelAdapter, ModelInfo, ToolCall, ToolSpec } from './types.js';
export { ProviderError } from './types.js';

const env = (name: string): string => (process.env[name] ?? '').trim();

/** Builds the list of model adapters, enabling each provider only when its key/endpoint is configured. */
function buildAdapters(): ModelAdapter[] {
  const adapters: ModelAdapter[] = [createDemoAdapter()];

  if (env('OPENAI_API_KEY')) {
    adapters.push(
      createOpenAICompatAdapter({
        id: 'openai',
        label: 'OpenAI',
        provider: 'openai',
        model: env('OPENAI_MODEL') || 'gpt-4.1-mini',
        baseUrl: env('OPENAI_BASE_URL') || 'https://api.openai.com/v1',
        apiKey: env('OPENAI_API_KEY'),
        description: 'OpenAI Chat Completions with tool calling.',
      }),
    );
  }
  if (env('ANTHROPIC_API_KEY')) {
    adapters.push(
      createAnthropicAdapter({
        id: 'anthropic',
        label: 'Anthropic Claude',
        model: env('ANTHROPIC_MODEL') || 'claude-sonnet-4-5',
        apiKey: env('ANTHROPIC_API_KEY'),
        description: 'Anthropic Messages API with native tool use.',
      }),
    );
  }
  if (env('GEMINI_API_KEY')) {
    adapters.push(
      createOpenAICompatAdapter({
        id: 'gemini',
        label: 'Google Gemini',
        provider: 'google',
        model: env('GEMINI_MODEL') || 'gemini-2.5-flash',
        baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai',
        apiKey: env('GEMINI_API_KEY'),
        description: 'Gemini through its OpenAI-compatible endpoint.',
      }),
    );
  }
  if (env('OPENROUTER_API_KEY')) {
    adapters.push(
      createOpenAICompatAdapter({
        id: 'openrouter',
        label: 'OpenRouter',
        provider: 'openrouter',
        model: env('OPENROUTER_MODEL') || 'openrouter/auto',
        baseUrl: 'https://openrouter.ai/api/v1',
        apiKey: env('OPENROUTER_API_KEY'),
        description: 'One key for hundreds of models (routing included).',
        extraHeaders: { 'X-Title': 'MAHDI AGENT AI' },
      }),
    );
  }
  if (env('GROQ_API_KEY')) {
    adapters.push(
      createOpenAICompatAdapter({
        id: 'groq',
        label: 'Groq',
        provider: 'groq',
        model: env('GROQ_MODEL') || 'llama-3.3-70b-versatile',
        baseUrl: 'https://api.groq.com/openai/v1',
        apiKey: env('GROQ_API_KEY'),
        description: 'Very fast open-model inference.',
      }),
    );
  }
  if (env('OLLAMA_BASE_URL') || env('OLLAMA_MODEL')) {
    adapters.push(
      createOpenAICompatAdapter({
        id: 'ollama',
        label: 'Ollama (local)',
        provider: 'ollama',
        model: env('OLLAMA_MODEL') || 'llama3.1',
        baseUrl: env('OLLAMA_BASE_URL') || 'http://localhost:11434/v1',
        description: 'Run open models on your own machine.',
      }),
    );
  }
  return adapters;
}

const adapters = buildAdapters();

export function listModels(): ModelInfo[] {
  return adapters.map((a) => a.info);
}

export function resolveModel(id?: string): ModelAdapter {
  return adapters.find((a) => a.info.id === id) ?? adapters[0];
}

export const DEFAULT_MODEL_ID = adapters.length > 1 ? adapters[1].info.id : 'demo';
