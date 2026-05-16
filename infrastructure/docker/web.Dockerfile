# Veyra Multi-stage Build for Development
# Optimized for fast iteration and local CPU usage

# Stage 1: Base setup with dependencies
FROM node:22-alpine AS base

WORKDIR /app

# Install system dependencies including Python
RUN apk add --no-cache python3 py3-pip build-base

# Install pnpm globally
RUN npm install -g pnpm@10.0.0

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

# Stage 2: Dependencies only (cached layer)
FROM base AS dependencies

# Copy all dependency definition files
COPY package.json ./
COPY pnpm-lock.yaml* ./
COPY pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/package.json

# Install dependencies
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile 2>/dev/null || pnpm install

# Stage 3: Development environment
FROM dependencies AS development

WORKDIR /app

# Copy source code
COPY . .

EXPOSE 3000 3001 3002 3003 3004 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) process.exit(1)})" 2>/dev/null

CMD ["pnpm", "--filter", "@veyra/web", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

# Stage 4: Static production build for low-CPU local containers
FROM dependencies AS build

WORKDIR /app
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY . .
RUN pnpm --filter @veyra/web build

FROM nginx:1.27-alpine AS production

COPY infrastructure/docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/apps/web/dist /usr/share/nginx/html

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1:3000 >/dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]
