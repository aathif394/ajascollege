# Handoff: move AJAS website stack to the college team

This document is the full transfer plan for **Al Jamia Arts & Science College** site stack currently owned by a personal developer account.

Use it when the college has:

- A **GitHub** org or user (e.g. `aljamia-college` or `ajascollege`)
- A **Cloudflare** account (email they control, ideally with billing access)
- People who will edit content (CMS) and who will maintain the site (IT)

---

## What you are moving

| Piece | Current (developer) | After transfer (college) |
|---|---|---|
| GitHub repo | `aathif394/ajascollege` | `COLLEGE_ORG/ajascollege` (or new name) |
| Cloudflare account | `aathif394@gmail.com` · ID `885696ed5faef85a5de48ee3fda26f4f` | College CF account |
| Pages site | project `ajascollege` → `ajascollege.pages.dev` | New project (same or new name) → `*.pages.dev` |
| Auth Worker | `ajas-cms-auth` → `ajas-cms-auth.aathif394.workers.dev` | Redeploy under college account → `ajas-cms-auth.<subdomain>.workers.dev` |
| CMS config | `backend.repo` + `base_url` point at developer resources | Updated to college repo + worker |
| GitHub Actions secrets | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` | Recreated on college repo |
| CMS password + GitHub token | Worker secrets on developer account | Recreated on college Worker |
| Custom domain (later) | — | `ajascollege.ac.in` DNS on college Cloudflare |

**Important:** Cloudflare does **not** transfer Pages/Workers between accounts. You **recreate and redeploy**. GitHub **can** transfer a repository.

---

## Inventory (do not skip)

### Accounts to create / receive access

| Role | Account | Who |
|---|---|---|
| A | GitHub owner (org recommended) | College IT / web lead |
| B | Cloudflare owner | College IT (same person or team) |
| C | CMS editors | Staff with GitHub write **or** people who use CMS password (current design uses Worker password + site owner GitHub token) |
| D | Optional: keep developer as collaborator for 2–4 weeks | Temporary |

### Secrets you will re-create (never email these in plain text long-term)

| Secret | Where it lives | Purpose |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | GitHub Actions | Deploy Pages on push |
| `CLOUDFLARE_ACCOUNT_ID` | GitHub Actions | Target CF account |
| `CMS_PASSWORD` | Worker secret | Staff login popup for `/admin` |
| `GITHUB_TOKEN` | Worker secret | Lets CMS write commits as a GitHub identity |
| `.cms-password.local` | Dev machine only (gitignored) | Local copy of CMS password |

### Files that hard-code the current owner

After transfer, update these (or run `scripts/retarget-ownership.sh`):

| File | Fields |
|---|---|
| `public/admin/config.yml` | `backend.repo`, `base_url`, `site_url`, `display_url` |
| `cms-auth/wrangler.toml` | Worker `name` (optional rename) |
| `wrangler.jsonc` / Pages project name | Project name if changed |
| `.github/workflows/deploy.yml` | `--project-name` if changed |
| `README.md` | URLs |

---

## Recommended target shape

```text
GitHub org:     e.g. aljamia-college  (or a college-owned user)
Repo:           aljamia-college/ajascollege
Cloudflare:     college@ajascollege.ac.in (or IT email)
Pages:          project ajascollege → https://ajascollege.pages.dev
                later: https://ajascollege.ac.in
Worker:         ajas-cms-auth → https://ajas-cms-auth.<workers-subdomain>.workers.dev
CMS:            https://ajascollege.pages.dev/admin/
```

Use a **GitHub Organization** so the site isn’t tied to one staff member’s personal account.

---

## Phase 0 — Prepare (1 day)

1. College creates **GitHub org** (free is fine).
2. College creates **Cloudflare** account; verify email; note **Account ID**  
   (Dashboard → Workers & Pages → right sidebar / Overview → Account ID).
3. Install tools on an IT machine:
   - Node 22+
   - `git`
   - GitHub CLI (`gh`) or GitHub web UI
   - Cloudflare Wrangler: `npm i -g wrangler` then `wrangler login`
4. Create a **GitHub Machine / bot user** *or* a dedicated user `ajas-web-bot` with write access to the repo (used only as `GITHUB_TOKEN` for CMS commits).  
   Prefer a fine-grained PAT on that user: Contents **Read and write**, Metadata **Read**.
5. Agree CMS password policy (shared password today; rotate quarterly).

---

## Phase 1 — GitHub transfer (30–60 min)

### Option A — Transfer existing repo (keeps history, issues, Actions history)

1. On `aathif394/ajascollege` → **Settings → General → Danger Zone → Transfer**.
2. Transfer to college org/user (they must accept if required).
3. Update local remotes:

```bash
git remote set-url origin https://github.com/COLLEGE_ORG/ajascollege.git
git fetch origin
```

4. Invite developers temporarily as collaborators if needed.

### Option B — Fresh fork / push (clean break)

```bash
# On a machine with the code:
cd ajascollege-new
gh repo create COLLEGE_ORG/ajascollege --public --source=. --remote=college --push
# or create empty repo in UI, then:
git remote add college https://github.com/COLLEGE_ORG/ajascollege.git
git push -u college main
```

After transfer, **repo string** becomes e.g. `aljamia-college/ajascollege`.

---

## Phase 2 — Cloudflare Pages (college account)

On a machine logged into the **college** Cloudflare account:

```bash
cd ajascollege-new
npm ci
npm run build

# Create project (once)
npx wrangler pages project create ajascollege --production-branch main

# First deploy
npx wrangler pages deploy dist --project-name ajascollege --branch main
```

Note the new URL: `https://ajascollege.pages.dev` (or `https://ajascollege-<hash>.pages.dev` if name taken — pick a free project name).

### GitHub Actions deploy secrets (college repo)

1. College Cloudflare → **My Profile → API Tokens → Create Token**  
   Template: **Edit Cloudflare Workers** (or custom with Account → Cloudflare Pages → Edit, Account → Account Settings → Read).
2. In college GitHub repo → **Settings → Secrets and variables → Actions**:
   - `CLOUDFLARE_API_TOKEN` = token from step 1  
   - `CLOUDFLARE_ACCOUNT_ID` = college Account ID  
3. Confirm `.github/workflows/deploy.yml` still has:

```yaml
command: pages deploy dist --project-name ajascollege --branch main
```

4. Test: push a small commit to `main` → **Actions** tab should go green → site updates.

---

## Phase 3 — CMS Auth Worker (college account)

Still on college Wrangler login:

```bash
cd cms-auth

# Deploy worker under college account
npx wrangler deploy --config wrangler.toml

# Note the printed URL, e.g.:
# https://ajas-cms-auth.<college-subdomain>.workers.dev
```

Set secrets (do **not** commit these):

```bash
# CMS staff password (choose a strong one)
printf '%s' 'COLLEGE_CMS_PASSWORD_HERE' | npx wrangler secret put CMS_PASSWORD --config wrangler.toml

# GitHub token that can write to COLLEGE_ORG/ajascollege
printf '%s' 'ghp_xxxxxxxx' | npx wrangler secret put GITHUB_TOKEN --config wrangler.toml

# Allowed site hostnames for the login popup
printf '%s' 'ajascollege.pages.dev,*.ajascollege.pages.dev,localhost,127.0.0.1,ajascollege.ac.in,www.ajascollege.ac.in' \
  | npx wrangler secret put ALLOWED_DOMAINS --config wrangler.toml
```

Optional: store password only in a password manager + college IT vault (not in git).  
Local copy pattern: `.cms-password.local` (already gitignored).

---

## Phase 4 — Point Sveltia at college resources

Edit `public/admin/config.yml` (or run the retarget script):

```yaml
backend:
  name: github
  repo: COLLEGE_ORG/ajascollege   # ← new
  branch: main
  base_url: https://ajas-cms-auth.<college-subdomain>.workers.dev  # ← new
  auth_endpoint: auth

site_url: https://ajascollege.pages.dev   # or final domain
display_url: https://ajascollege.pages.dev
```

Commit and push to college `main` → Actions redeploys.

### CMS login test

1. Open `https://<college-pages>/admin/`
2. **Sign In with GitHub** → password popup (Worker) → CMS loads  
3. Edit a draft field on a non-critical page → Publish  
4. Confirm a commit appears on the **college** repo  
5. Confirm Actions deploys and public page updates in ~1–2 minutes  

---

## Phase 5 — Custom domain (ajascollege.ac.in)

On **college** Cloudflare (DNS must be on that account or point correctly):

1. Pages → `ajascollege` → **Custom domains** → add `ajascollege.ac.in` and `www`.  
2. Follow DNS instructions (CNAME/flattening).  
3. Update:

```yaml
# public/admin/config.yml
site_url: https://ajascollege.ac.in
display_url: https://ajascollege.ac.in
```

4. Update Worker `ALLOWED_DOMAINS` to include the apex + www.  
5. Optional: redirect `www` → apex (or reverse) in Pages / Bulk Redirects.

---

## Phase 6 — Cutover & decommission (developer account)

### Soft cutover (1–2 weeks)

| Keep on developer | College uses |
|---|---|
| Old `ajascollege.pages.dev` as fallback | New Pages URL as primary |
| Temporary collaborator on college repo | Full ownership |

Share only:

- College site URL  
- College `/admin/`  
- CMS password (via password manager)  
- Who owns GitHub org + Cloudflare  

### Hard cutover

1. DNS live on college domain.  
2. Remove developer Cloudflare Pages project `ajascollege` (optional, after backups).  
3. Delete or disable developer Worker `ajas-cms-auth` (so logins can’t hit the old password).  
4. Revoke old GitHub tokens / Cloudflare API tokens on developer account.  
5. Remove developer from org if contract ends (or leave as outside collaborator).  
6. Archive or leave personal GitHub repo as mirror (read-only) if history was transferred.

### Data that does **not** need separate migration

- Site **content** and **media** live in the Git repo (`content/`, `public/assets/`). Transferring/pushing the repo moves them.  
- No database.  
- No Netlify.

---

## Phase 7 — Roles after handoff

| Person | Access |
|---|---|
| Content editors | CMS only (`/admin` + CMS password). Prefer not giving raw GitHub unless they need it. |
| Web lead / IT | GitHub **admin**, Cloudflare **admin**, Worker secrets, Actions secrets |
| External developer | Temporary GitHub write; no long-lived production tokens |

### Rotate on staff change

1. Change `CMS_PASSWORD` on Worker.  
2. Rotate `GITHUB_TOKEN` PAT.  
3. Rotate `CLOUDFLARE_API_TOKEN` if the person who created it leaves.

---

## Quick command: retarget config

After you know the new names, from repo root:

```bash
# Example values — replace all of these
export NEW_GH_REPO='aljamia-college/ajascollege'
export NEW_SITE_URL='https://ajascollege.pages.dev'
export NEW_AUTH_BASE='https://ajas-cms-auth.YOUR_SUBDOMAIN.workers.dev'

./scripts/retarget-ownership.sh
git add public/admin/config.yml README.md
git commit -m "Retarget CMS and site URLs to college ownership"
git push origin main
```

---

## Acceptance checklist (sign-off)

- [ ] College GitHub org owns the repo  
- [ ] College Cloudflare owns Pages project; `npm` Actions deploy works on push  
- [ ] College Worker serves CMS login; `ALLOWED_DOMAINS` includes production host  
- [ ] `config.yml` `repo` + `base_url` match college resources  
- [ ] Test publish creates commit on **college** repo and updates live site  
- [ ] CMS password stored in college password manager  
- [ ] Developer tokens revoked / old Worker deleted  
- [ ] (Optional) `ajascollege.ac.in` on Pages + HTTPS green  
- [ ] Editors trained: visual content only, wait ~1–2 min after Publish  

---

## What the college needs from the current developer

Provide this package (securely):

1. This document  
2. Repo access (transfer or push)  
3. Current live URL and `/admin`  
4. Current CMS password (then **rotate** after they take Worker ownership)  
5. List of special pages (homepage hero = structured JSON; listings auto-generated)  
6. Optional: 2-week support window  

Do **not** send long-lived Cloudflare Global API Keys in chat. Create new tokens under the college account.

---

## Current production snapshot (before transfer)

| Item | Value |
|---|---|
| GitHub | https://github.com/aathif394/ajascollege |
| Site | https://ajascollege.pages.dev |
| CMS | https://ajascollege.pages.dev/admin/ |
| Auth Worker | https://ajas-cms-auth.aathif394.workers.dev |
| CF Account | `885696ed5faef85a5de48ee3fda26f4f` (personal) |
| Deploy | GitHub Action → Wrangler Pages on push to `main` |

When transfer is complete, rewrite this table with college values and commit it to the college repo README.
