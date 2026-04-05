// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://workshop-ia-2026.686f6c61.dev',
  integrations: [sitemap()],
});
