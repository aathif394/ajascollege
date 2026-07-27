#!/usr/bin/env bash
# Rewrite hard-coded owner URLs after moving GitHub / Cloudflare / Worker to college accounts.
# Usage:
#   export NEW_GH_REPO='college-org/ajascollege'
#   export NEW_SITE_URL='https://ajascollege.pages.dev'
#   export NEW_AUTH_BASE='https://ajas-cms-auth.xxx.workers.dev'
#   ./scripts/retarget-ownership.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

: "${NEW_GH_REPO:?Set NEW_GH_REPO e.g. aljamia-college/ajascollege}"
: "${NEW_SITE_URL:?Set NEW_SITE_URL e.g. https://ajascollege.pages.dev}"
: "${NEW_AUTH_BASE:?Set NEW_AUTH_BASE e.g. https://ajas-cms-auth.subdomain.workers.dev}"

# strip trailing slash from base URLs
NEW_SITE_URL="${NEW_SITE_URL%/}"
NEW_AUTH_BASE="${NEW_AUTH_BASE%/}"

CFG="public/admin/config.yml"
if [[ ! -f "$CFG" ]]; then
  echo "Missing $CFG" >&2
  exit 1
fi

# portable sed
tmp="$(mktemp)"
python3 - "$CFG" "$NEW_GH_REPO" "$NEW_SITE_URL" "$NEW_AUTH_BASE" <<'PY'
import re, sys
path, repo, site, auth = sys.argv[1:5]
text = open(path, encoding="utf-8").read()
text = re.sub(r"(?m)^(\s*repo:\s*).*$", rf"\1{repo}", text, count=1)
text = re.sub(r"(?m)^(\s*base_url:\s*).*$", rf"\1{auth}", text, count=1)
text = re.sub(r"(?m)^(\s*site_url:\s*).*$", rf"\1{site}", text, count=1)
text = re.sub(r"(?m)^(\s*display_url:\s*).*$", rf"\1{site}", text, count=1)
open(path, "w", encoding="utf-8").write(text)
print("Updated", path)
print("  repo:", repo)
print("  site_url/display_url:", site)
print("  base_url:", auth)
PY

# README common URL replacements (best-effort)
if [[ -f README.md ]]; then
  python3 - <<PY
from pathlib import Path
p = Path("README.md")
t = p.read_text(encoding="utf-8")
# do not invent old→new map beyond known patterns
for old in [
    "https://ajascollege.pages.dev",
    "https://github.com/aathif394/ajascollege",
    "aathif394/ajascollege",
    "https://ajas-cms-auth.aathif394.workers.dev",
]:
    pass
t2 = t.replace("aathif394/ajascollege", "$NEW_GH_REPO")
t2 = t2.replace("https://github.com/aathif394/ajascollege", f"https://github.com/$NEW_GH_REPO")
t2 = t2.replace("https://ajascollege.pages.dev", "$NEW_SITE_URL")
t2 = t2.replace("https://ajas-cms-auth.aathif394.workers.dev", "$NEW_AUTH_BASE")
if t2 != t:
    p.write_text(t2, encoding="utf-8")
    print("Updated README.md URLs (best-effort)")
else:
    print("README.md: no known developer URLs found (or already updated)")
PY
fi

echo ""
echo "Next:"
echo "  1. git diff public/admin/config.yml"
echo "  2. Commit & push to the COLLEGE repo"
echo "  3. Ensure Worker secrets CMS_PASSWORD, GITHUB_TOKEN, ALLOWED_DOMAINS are set"
echo "  4. Ensure GitHub Actions secrets CLOUDFLARE_API_TOKEN + CLOUDFLARE_ACCOUNT_ID are set"
echo "  5. Test /admin login and a publish"
