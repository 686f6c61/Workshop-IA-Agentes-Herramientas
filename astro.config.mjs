// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import sentry from '@sentry/astro';

const hasSentryDsn = Boolean(process.env.PUBLIC_GLITCHTIP_DSN);
const hasSentryAuthToken = Boolean(process.env.SENTRY_AUTH_TOKEN);
const siteUrl =
  process.env.PUBLIC_SITE_URL ?? process.env.ASTRO_SITE ?? 'https://workshop-ia-2026.686f6c61.dev';

// https://astro.build/config
export default defineConfig({
  site: siteUrl,
  integrations: [
    ...(hasSentryDsn
      ? [
          sentry({
            enabled: { client: true, server: false },
            clientInitPath: './sentry.client.config.ts',
            sourcemaps: { disable: !hasSentryAuthToken },
            telemetry: false,
            ...(hasSentryAuthToken
              ? {
                  authToken: process.env.SENTRY_AUTH_TOKEN,
                  org: process.env.SENTRY_ORG,
                  project: process.env.SENTRY_PROJECT,
                }
              : {}),
          }),
        ]
      : []),
    sitemap(),
  ],
});
