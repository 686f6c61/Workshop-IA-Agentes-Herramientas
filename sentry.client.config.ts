import * as Sentry from '@sentry/astro';

const dsn = import.meta.env.PUBLIC_GLITCHTIP_DSN;

if (dsn) {
  Sentry.init({
    dsn,
    release: import.meta.env.PUBLIC_SENTRY_RELEASE ?? 'workshop-ia-2026',
    environment: import.meta.env.PUBLIC_SENTRY_ENVIRONMENT ?? import.meta.env.MODE ?? 'production',
    tracesSampleRate: 0.01,
  });
}
