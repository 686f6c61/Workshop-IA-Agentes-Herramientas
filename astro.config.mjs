// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://workshop-ia-agentes-herramientas.onrender.com',
  integrations: [sitemap()],
});
