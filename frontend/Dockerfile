# Production image for the Next.js frontend (Phase 12 — DEPLOYMENT_SPEC.md).
# Build context is frontend/ (see docker-compose.yml) -- the frontend has
# no dependency on backend/ or ml/ source.
#
# NEXT_PUBLIC_API_BASE_URL is inlined into the client bundle at build time
# by Next.js, so it must be supplied as a build ARG, not just a runtime
# env var (DEPLOYMENT_SPEC.md: "Configure an environment variable ...
# Do not hard-code production API URLs").

FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ARG NEXT_PUBLIC_API_BASE_URL
ARG NEXT_PUBLIC_MAX_UPLOAD_MB=5
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL} \
    NEXT_PUBLIC_MAX_UPLOAD_MB=${NEXT_PUBLIC_MAX_UPLOAD_MB}

RUN npm run build

FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', r => process.exit(r.statusCode < 500 ? 0 : 1)).on('error', () => process.exit(1))"

CMD ["node", "server.js"]
