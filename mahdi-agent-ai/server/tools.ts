import { evaluateExpression } from './calc.js';
import { AppError } from './errors.js';
import { loadTemplateFiles, isTemplateId, TEMPLATE_META } from './templates.js';
import type { ToolSpec } from './providers/types.js';
import type { Workspace } from './workspace.js';

export interface ToolContext {
  ws: Workspace;
  language: string;
}

export interface ToolResult {
  ok: boolean;
  text: string;
  changed?: string[];
  versionIds?: string[];
}

interface ToolDef {
  spec: ToolSpec;
  run(args: Record<string, unknown>, ctx: ToolContext): Promise<ToolResult>;
}

const MAX_READ_CHARS = 24_000;

function str(args: Record<string, unknown>, key: string, { optional = false } = {}): string {
  const value = args[key];
  if (value === undefined || value === null || value === '') {
    if (optional) return '';
    throw new AppError(400, `Missing argument "${key}"`);
  }
  if (typeof value !== 'string') throw new AppError(400, `Argument "${key}" must be a string`);
  return value;
}

const obj = (properties: Record<string, unknown>, required: string[] = []) => ({
  type: 'object',
  properties,
  required,
  additionalProperties: false,
});

const TOOLS: ToolDef[] = [
  {
    spec: {
      name: 'list_files',
      description: 'List every file in the current project workspace with its size in bytes.',
      parameters: obj({}),
    },
    async run(_args, ctx) {
      const files = await ctx.ws.listFiles();
      if (!files.length) return { ok: true, text: 'The workspace is empty.' };
      return { ok: true, text: files.map((f) => `${f.path} (${f.size} bytes)`).join('\n') };
    },
  },
  {
    spec: {
      name: 'read_file',
      description: 'Read the full text content of a file in the project workspace.',
      parameters: obj({ path: { type: 'string', description: 'Relative path, e.g. "index.html"' } }, ['path']),
    },
    async run(args, ctx) {
      const text = await ctx.ws.readFile(str(args, 'path'));
      const clipped = text.length > MAX_READ_CHARS ? `${text.slice(0, MAX_READ_CHARS)}\n…[truncated]` : text;
      return { ok: true, text: clipped };
    },
  },
  {
    spec: {
      name: 'write_file',
      description:
        'Create or overwrite a file with the given content. Every write is saved as a new version in the history.',
      parameters: obj(
        {
          path: { type: 'string' },
          content: { type: 'string', description: 'Full new content of the file' },
          summary: { type: 'string', description: 'Short description of the change for the history' },
        },
        ['path', 'content'],
      ),
    },
    async run(args, ctx) {
      const path = str(args, 'path');
      const content = str(args, 'content', { optional: true });
      const { version, changed } = await ctx.ws.writeFile(path, content, {
        actor: 'agent',
        message: str(args, 'summary', { optional: true }) || 'Agent wrote file',
      });
      if (!changed || !version) return { ok: true, text: `No change: ${path} already has this content.` };
      return { ok: true, text: `Saved ${path} (${version.size} bytes, version ${version.id.slice(0, 8)}).`, changed: [path], versionIds: [version.id] };
    },
  },
  {
    spec: {
      name: 'edit_file',
      description:
        'Replace one exact occurrence of old_text with new_text inside a file. Prefer this over rewriting a whole file. old_text must be unique in the file.',
      parameters: obj(
        {
          path: { type: 'string' },
          old_text: { type: 'string' },
          new_text: { type: 'string' },
        },
        ['path', 'old_text', 'new_text'],
      ),
    },
    async run(args, ctx) {
      const path = str(args, 'path');
      const { version } = await ctx.ws.editFile(path, str(args, 'old_text'), str(args, 'new_text', { optional: true }), {
        actor: 'agent',
        message: 'Agent edited file',
      });
      if (!version) return { ok: true, text: `No change in ${path}.` };
      return { ok: true, text: `Edited ${path} (version ${version.id.slice(0, 8)}).`, changed: [path], versionIds: [version.id] };
    },
  },
  {
    spec: {
      name: 'delete_file',
      description: 'Delete a file from the project workspace. The deletion is recorded and can be undone from history.',
      parameters: obj({ path: { type: 'string' } }, ['path']),
    },
    async run(args, ctx) {
      const path = str(args, 'path');
      const version = await ctx.ws.deleteFile(path, { actor: 'agent', message: 'Agent deleted file' });
      return { ok: true, text: `Deleted ${path}.`, changed: [path], versionIds: [version.id] };
    },
  },
  {
    spec: {
      name: 'search_files',
      description: 'Search for a case-insensitive text in all project files and return matching lines.',
      parameters: obj({ query: { type: 'string' } }, ['query']),
    },
    async run(args, ctx) {
      const hits = await ctx.ws.search(str(args, 'query'));
      if (!hits.length) return { ok: true, text: 'No matches.' };
      return { ok: true, text: hits.map((h) => `${h.path}:${h.line}: ${h.text}`).join('\n') };
    },
  },
  {
    spec: {
      name: 'create_app',
      description:
        'Scaffold a complete, working starter application into the workspace from a built-in template. Existing files with the same names are replaced (versioned).',
      parameters: obj(
        {
          template: { type: 'string', enum: TEMPLATE_META.map((t) => t.id) },
        },
        ['template'],
      ),
    },
    async run(args, ctx) {
      const template = str(args, 'template');
      if (!isTemplateId(template)) throw new AppError(400, `Unknown template "${template}"`);
      const files = await loadTemplateFiles(template);
      const changed: string[] = [];
      const versionIds: string[] = [];
      for (const [path, content] of Object.entries(files)) {
        const { version, changed: didChange } = await ctx.ws.writeFile(path, content, {
          actor: 'agent',
          message: `Created from template "${template}"`,
          action: 'template',
        });
        if (didChange && version) {
          changed.push(path);
          versionIds.push(version.id);
        }
      }
      const listing = Object.keys(files).join(', ');
      return {
        ok: true,
        text: `Created the "${template}" app with ${Object.keys(files).length} files: ${listing}. Open the Preview panel to run it.`,
        changed,
        versionIds,
      };
    },
  },
  {
    spec: {
      name: 'calculate',
      description: 'Evaluate an arithmetic expression exactly (supports + - * / % ^, parentheses, sqrt(), abs()).',
      parameters: obj({ expression: { type: 'string' } }, ['expression']),
    },
    async run(args) {
      const value = evaluateExpression(str(args, 'expression'));
      return { ok: true, text: String(Math.round(value * 1e12) / 1e12) };
    },
  },
  {
    spec: {
      name: 'current_time',
      description: 'Get the current date and time in UTC (ISO 8601).',
      parameters: obj({}),
    },
    async run() {
      return { ok: true, text: new Date().toISOString() };
    },
  },
];

export const TOOL_SPECS: ToolSpec[] = TOOLS.map((t) => t.spec);

/** Runs one tool call. Errors are returned to the model as results so it can self-correct. */
export async function executeTool(name: string, args: Record<string, unknown>, ctx: ToolContext): Promise<ToolResult> {
  const tool = TOOLS.find((t) => t.spec.name === name);
  if (!tool) return { ok: false, text: `Error: unknown tool "${name}"` };
  try {
    return await tool.run(args, ctx);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { ok: false, text: `Error: ${message}` };
  }
}
