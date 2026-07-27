// @ts-check
import { defineConfig } from "astro/config";

// Static site → Cloudflare Pages (no adapter needed for pure SSG).
// https://docs.astro.build/en/guides/deploy/cloudflare/
export default defineConfig({
  site: "https://ajascollege.ac.in",
  trailingSlash: "always",
  build: {
    format: "directory",
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
