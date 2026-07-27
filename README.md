# Al Jamia Arts & Science College — website

**Stack:** Astro (SSG) · **Sveltia CMS** · Cloudflare Pages · Pagefind  

**Live (Cloudflare):** https://ajascollege.pages.dev  

Day-to-day edits happen at **`/admin/`** (Sveltia). Content is Git-backed Markdown/JSON under `content/`.

---

## What staff edit (WordPress-like day-to-day)

| CMS section | What it is | Public URL |
|---|---|---|
| **1 · News** | Campus news posts | `/college-news/…` |
| **2 · Events** | Events | `/event/…` |
| **3 · Notices & downloads** | Circulars, NIRF, RTI, IQAC PDFs | `/notices/` |
| **4 · Fees & prospectus** | Fee / prospectus PDFs | `/fees/` |
| **5 · Site settings** | Phone, email, admission open, default fee PDF | site-wide |
| **6 · Homepage hero** | Hero text, CTAs, stats, principal blurb | `/` (settings layer) |
| **7 · Programmes** | UG/PG course list | `/programmes/` |
| **8 · Faculty** | Faculty bios | `/faculties/…` |
| **9 · Other pages** | About, IQAC, labs, clubs, static pages | various |

Also: admission strip (top of site) reads from **Site settings**.

---

## Commands

```bash
cd ajascollege-new
pnpm install   # or npm install
pnpm dev       # http://localhost:4321

# Local CMS (no GitHub needed):
# terminal 1:
pnpm dev
# terminal 2:
pnpm run cms   # starts decap-server — LOCAL FILE BRIDGE only
# open http://localhost:4321/admin/
```

### Why the terminal says “Decap”

`pnpm run cms` runs **`decap-server`**, a small local proxy so Sveltia can write files on disk without OAuth.  
**The admin UI is Sveltia**, not Decap. Production does not use Decap Identity.

| Piece | Role |
|---|---|
| Sveltia CMS (`/admin`) | Editor UI in the browser |
| `decap-server` | Local-only file API (`pnpm run cms`) |
| GitHub OAuth | Production login + commits |

---

## Deploy (Cloudflare Pages)

Already deployed once via:

```bash
pnpm run build
npx wrangler pages deploy dist --project-name ajascollege --branch main
```

Or: `pnpm run deploy`

| Setting | Value |
|---|---|
| Project | `ajascollege` |
| URL | https://ajascollege.pages.dev |
| Build output | `dist` |
| Account | linked Wrangler OAuth |

Custom domain later: Cloudflare dashboard → Pages → `ajascollege` → Custom domains → `ajascollege.ac.in`.

---

## Production CMS login (honest constraints)

Sveltia is **Git-based**. There is **no WordPress-style username/password** built into Sveltia.

### What works in production

1. **GitHub OAuth (recommended)**  
   - Set `backend.repo` in `public/admin/config.yml` to your real `org/repo`.  
   - Deploy [sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth) as a Cloudflare Worker and set `base_url`.  
   - Staff get a **shared editor GitHub account** (they only open `/admin`, never the repo).  
   - Saves = git commits → rebuild/redeploy (connect Git integration or run `wrangler pages deploy` in CI).

2. **Local only**  
   - `local_backend: true` + `pnpm run cms` — good for IT staff on a laptop, not for remote college staff on the public URL.

3. **True email/password without GitHub**  
   - Not available with pure Sveltia on Cloudflare Pages.  
   - Would need Netlify Identity + Git Gateway, or a different CMS (Payload/Directus/Strapi) with its own users.

Until the GitHub repo + OAuth worker are connected, **use local CMS** for edits, then redeploy.

---

## Project layout

```
content/
  news/ events/ notices/ fees/ programmes/ faculty/
  pages/          # static pages
  settings/site.json
  home/homepage.json
public/admin/     # Sveltia
public/assets/    # media + Edukin CSS/JS
src/              # layouts, components, routes
```

Agents/developers edit files in the repo. Staff use `/admin` once OAuth is wired.

---

## Search

Pagefind indexes every build (`pnpm run build`). Floating search button / ⌘K on the site.
