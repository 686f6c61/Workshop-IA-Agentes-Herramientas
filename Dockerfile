FROM node:22-alpine AS build
WORKDIR /app

# Build-time public identifier de GlitchTip. Se recibe desde Coolify.
ARG PUBLIC_GLITCHTIP_DSN
ARG PUBLIC_SITE_URL=https://workshop-ia-2026.686f6c61.dev
ENV PUBLIC_GLITCHTIP_DSN=$PUBLIC_GLITCHTIP_DSN
ENV PUBLIC_SITE_URL=$PUBLIC_SITE_URL

COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
