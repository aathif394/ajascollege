# Transfer checklist (print / tick)

**From:** aathif394 (personal)  
**To:** _________________ (college GitHub) + _________________ (college Cloudflare)  
**Date started:** __________ **Date complete:** __________

## Accounts

- [ ] College GitHub org/user created  
- [ ] College Cloudflare account created; Account ID: ____________________  
- [ ] IT machine has Node 22, git, gh, wrangler login (college)  

## GitHub

- [ ] Repo transferred **or** pushed to college  
- [ ] New URL: https://github.com/____________________/____________________  
- [ ] Web lead has Admin; editors as needed  
- [ ] Bot/user PAT created for CMS (`GITHUB_TOKEN`)  

## Cloudflare Pages

- [ ] `wrangler pages project create` (or dashboard) under **college** account  
- [ ] First `wrangler pages deploy dist` succeeds  
- [ ] Pages URL: https://____________________.pages.dev  
- [ ] Actions secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`  
- [ ] Push to `main` runs green deploy  

## Auth Worker

- [ ] `cd cms-auth && wrangler deploy` under college account  
- [ ] Worker URL: https://____________________.workers.dev  
- [ ] Secrets: `CMS_PASSWORD`, `GITHUB_TOKEN`, `ALLOWED_DOMAINS`  
- [ ] Password stored in college password manager  

## Config

- [ ] Ran `scripts/retarget-ownership.sh` **or** hand-edited `public/admin/config.yml`  
- [ ] `repo` = college  
- [ ] `base_url` = college Worker  
- [ ] `site_url` / `display_url` = college site  

## Tests

- [ ] `/admin` login with CMS password works  
- [ ] Publish creates commit on **college** repo  
- [ ] Site updates within ~2 minutes  
- [ ] News / Faculty / Events visual edit (no HTML)  

## Domain (optional later)

- [ ] `ajascollege.ac.in` on college CF Pages  
- [ ] HTTPS OK  
- [ ] `ALLOWED_DOMAINS` + `site_url` updated  

## Decommission personal

- [ ] Old Worker deleted/disabled  
- [ ] Old Pages project removed (after cutover)  
- [ ] Personal API tokens revoked  
- [ ] Developer access reduced/removed  

**Signed (IT):** _________________ **Date:** __________  
**Signed (developer):** _________________ **Date:** __________
