import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import express from 'express';
import { ACCESS_TOKEN, APP_NAME, DATA_DIR, DIST_DIR, HOST, PORT, ROOT_DIR } from './config.js';
import { createApp } from './app.js';

async function main(): Promise<void> {
  const dev = process.env.NODE_ENV !== 'production';
  const app = createApp();
  const server = http.createServer(app);

  if (dev) {
    // Development: Vite middleware serves the React app with hot reload on the same port.
    const { createServer } = await import('vite');
    const vite = await createServer({
      root: ROOT_DIR,
      appType: 'custom',
      server: { middlewareMode: true, hmr: { server }, allowedHosts: true },
    });
    app.use(vite.middlewares);
    app.use(async (req, res, next) => {
      if (req.method !== 'GET' || req.path.startsWith('/api')) return next();
      try {
        const html = await fs.readFile(path.join(ROOT_DIR, 'index.html'), 'utf8');
        res.status(200).setHeader('Content-Type', 'text/html; charset=utf-8');
        res.end(await vite.transformIndexHtml(req.originalUrl, html));
      } catch (error) {
        vite.ssrFixStacktrace(error as Error);
        next(error);
      }
    });
  } else {
    try {
      await fs.access(path.join(DIST_DIR, 'index.html'));
    } catch {
      console.error('The web app is not built yet. Run: npm run build');
      process.exit(1);
    }
    app.use(express.static(DIST_DIR, { index: false, maxAge: '1h' }));
    app.use((req, res, next) => {
      if (req.method !== 'GET' || req.path.startsWith('/api')) return next();
      res.sendFile(path.join(DIST_DIR, 'index.html'));
    });
  }

  await fs.mkdir(DATA_DIR, { recursive: true });
  server.listen(PORT, HOST, () => {
    console.log(`${APP_NAME} is running at http://${HOST === '0.0.0.0' ? 'localhost' : HOST}:${PORT} (${dev ? 'development' : 'production'})`);
    if (ACCESS_TOKEN) console.log('Access token protection is enabled.');
  });
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
