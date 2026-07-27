# Al Jamia Arts & Science College

**Live:** https://ajascollege.pages.dev  
**CMS:** https://ajascollege.pages.dev/admin/  
**Repo:** https://github.com/aathif394/ajascollege  

Stack: **Astro** · **Sveltia CMS** · **Cloudflare Pages** · **Pagefind**

---

## Day-to-day editing (like WordPress sections)

Open **https://ajascollege.pages.dev/admin/** → Login with **GitHub** (`aathif394` or any collaborator with write access).

| # | Section | What staff change |
|---|---------|-------------------|
| 1 | News | Campus news |
| 2 | Events | Events |
| 3 | Notices & downloads | Circulars / PDFs |
| 4 | Fees & prospectus | Fee PDFs |
| 5 | Site settings | Phone, email, admission open |
| 6 | Homepage hero | Hero text / CTAs |
| 7 | Programmes | UG/PG list |
| 8 | Faculty | Faculty bios |
| 9 | Other pages | About, IQAC, labs, … |

After publish, GitHub Action rebuilds and deploys to Cloudflare Pages automatically.

---

## URLs

| What | URL |
|------|-----|
| Site | https://ajascollege.pages.dev |
| Admin | https://ajascollege.pages.dev/admin/ |
| Notices | https://ajascollege.pages.dev/notices/ |
| Fees | https://ajascollege.pages.dev/fees/ |
| Programmes | https://ajascollege.pages.dev/programmes/ |
| Auth worker (optional OAuth proxy) | https://ajas-cms-auth.aathif394.workers.dev |

---

## Local development

```bash
git clone https://github.com/aathif394/ajascollege.git
cd ajascollege
npm install
npm run dev          # http://localhost:4321

# Local CMS (no GitHub OAuth):
npm run cms          # starts decap-server — local file bridge only
# then http://localhost:4321/admin/
```

`npm run cms` may print “Decap” — that is only the local proxy. The UI is **Sveltia**.

---

## Deploy

- **Automatic:** push to `main` → GitHub Action → Cloudflare Pages  
- **Manual:** `npm run deploy`

Secrets (already set on the repo):

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

> If CI deploys fail after months, re-run `wrangler login` and refresh the `CLOUDFLARE_API_TOKEN` secret (token is from Wrangler OAuth).

---

## Production CMS login notes

Sveltia uses **GitHub** (not username/password like WordPress).

1. Open `/admin/`
2. **Login with GitHub**
3. Authorize access to `aathif394/ajascollege`
4. Edit → Publish → wait for the deploy Action

Invite staff: GitHub → repo **Settings → Collaborators** → write access. They only need GitHub for the CMS login, not to use git.

Optional custom OAuth proxy Worker is deployed as `ajas-cms-auth`. To use it instead of the default Netlify OAuth client:

1. Create a GitHub OAuth App: https://github.com/settings/applications/new  
   - Callback: `https://ajas-cms-auth.aathif394.workers.dev/callback`
2. Set Worker secrets: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
3. Uncomment `base_url` in `public/admin/config.yml`

---

## Project layout

```
content/     # CMS-editable Markdown + JSON
public/      # assets + /admin
src/         # Astro layouts & routes
.github/workflows/deploy.yml
```
