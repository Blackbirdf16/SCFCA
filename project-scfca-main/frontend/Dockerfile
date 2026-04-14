# Frontend Dockerfile for React + Vite app
# This Dockerfile supports both a dev-friendly image and a small production build.

# Stage 1 - deps & build
FROM node:25-alpine AS build
WORKDIR /app
# Copy package files first for better layer caching
COPY frontend/package*.json ./
# If a package-lock.json exists, copy it to allow `npm ci` to work reproducibly
COPY frontend/package-lock.json* ./
RUN apk add --no-cache bash git
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

# Stage 2 - serve production using a lightweight server
FROM nginx:stable-alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
# Default nginx serves on port 80; map host port 5173 -> container 80 in docker-compose
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Note: For local development you may prefer to run `npm run dev` on host or
# run `docker-compose run --service-ports frontend npm run dev` which binds host ports.
