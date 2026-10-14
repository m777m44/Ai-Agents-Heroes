import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

/** Loads KEY=VALUE pairs from the project's .env file without overriding real environment variables. */
const here = path.dirname(fileURLToPath(import.meta.url));
const envFile = path.resolve(here, '..', '.env');

if (fs.existsSync(envFile)) {
  for (const raw of fs.readFileSync(envFile, 'utf8').split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const eq = line.indexOf('=');
    if (eq === -1) continue;
    const key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (key && process.env[key] === undefined) process.env[key] = value;
  }
}
