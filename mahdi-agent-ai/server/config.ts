import path from 'node:path';
import { fileURLToPath } from 'node:url';
import './env.js';

const here = path.dirname(fileURLToPath(import.meta.url));

/** Root of the mahdi-agent-ai application (the folder containing package.json). */
export const ROOT_DIR = path.resolve(here, '..');
/** Where conversations, project files and version history are stored. */
export const DATA_DIR = path.resolve(process.env.MAHDI_DATA_DIR ?? path.join(ROOT_DIR, 'data'));
export const TEMPLATES_DIR = path.join(ROOT_DIR, 'templates');
export const DIST_DIR = path.join(ROOT_DIR, 'dist');

export const APP_NAME = 'MAHDI AGENT AI';
export const PORT = Number(process.env.PORT ?? 3000);
export const HOST = process.env.HOST ?? '0.0.0.0';
/** Maximum number of model/tool round-trips for a single user turn. */
export const MAX_STEPS = Math.max(1, Number(process.env.MAHDI_MAX_STEPS ?? 12));
/** If set, every /api request must present this token (header `x-mahdi-token` or `?token=`). */
export const ACCESS_TOKEN = (process.env.MAHDI_ACCESS_TOKEN ?? '').trim();

export const MAX_FILE_BYTES = 512 * 1024;
export const MAX_FILES_PER_PROJECT = 400;
export const MAX_VERSIONS_PER_PROJECT = 5000;
