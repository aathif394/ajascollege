// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

// Static site → Cloudflare Pages (no adapter needed for pure SSG).
// Images: built-in Sharp service optimizes files under src/assets/ (not public/).
// Sitemap: regenerated on every `astro build` from all routes.
// When custom domain is live, set site to https://ajascollege.ac.in
export default defineConfig({
  site: "https://ajascollege.pages.dev",
  trailingSlash: "always",
  build: {
    format: "directory",
    assets: "_astro",
  },
  integrations: [
    sitemap({
      // Skip CMS chrome and private-ish paths
      filter: (page) =>
        !page.includes("/admin") &&
        !page.includes("/pagefind"),
      changefreq: "weekly",
      priority: 0.7,
      lastmod: new Date(),
    }),
  ],
  image: {
    layout: "constrained",
    responsiveStyles: true,
    service: {
      entrypoint: "astro/assets/services/sharp",
      config: {
        limitInputPixels: false,
      },
    },
  },
  markdown: {
    syntaxHighlight: false,
  },
  vite: {
    server: {
      proxy: {},
    },
  },
});
