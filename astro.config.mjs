// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import sentry from '@sentry/astro';

// https://astro.build/config
export default defineConfig({
  site: 'https://workshop-ia-2026.686f6c61.dev',
  integrations: [
    sentry({
      dsn: process.env.PUBLIC_GLITCHTIP_DSN ?? '',
      release: 'workshop-ia-2026',
      environment: 'production',
      tracesSampleRate: 0.01,
      sourceMapsUploadOptions: { telemetry: false },
    }),
    sitemap(),
  ],
});
