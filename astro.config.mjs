// @ts-check
import { defineConfig } from "astro/config";

// Static site → Cloudflare Pages (no adapter needed for pure SSG).
// Images: built-in Sharp service optimizes files under src/assets/ (not public/).
// https://docs.astro.build/en/guides/images/
export default defineConfig({
  site: "https://ajascollege.ac.in",
  trailingSlash: "always",
  build: {
    format: "directory",
    // Keep hashed assets cacheable forever
    assets: "_astro",
  },
  image: {
    // Global responsive defaults for <Image /> / Markdown local images
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
    // Preserve migrated Edukin HTML inside .md bodies
    syntaxHighlight: false,
  },
  vite: {
    server: {
      // Decap/Sveltia local_backend talks to port 8081
      proxy: {},
    },
  },
});
