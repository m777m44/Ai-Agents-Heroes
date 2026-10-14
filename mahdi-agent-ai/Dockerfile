FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --omit=dev
EXPOSE 3000
ENV HOST=0.0.0.0 PORT=3000 MAHDI_DATA_DIR=/app/data
VOLUME ["/app/data"]
CMD ["npx", "tsx", "server/index.ts"]
