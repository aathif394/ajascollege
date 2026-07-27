#!/usr/bin/env python3
"""
One-shot extractor: static Edukin HTML (ajascollege-new/*/) → Astro content collections.

Run from repo root or ajascollege-new:
  python3 scripts/extract-content.py

Idempotent: overwrites content/*.md from current HTML sources.
"""
from __future__ import annotations

import re
import html as html_lib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content"
PARTIALS = ROOT / "src" / "partials"
# Prefer live HTML at project root; fall back to archived migration dump
HTML_ROOT = ROOT / "_archive" / "html" if (ROOT / "_archive" / "html").is_dir() else ROOT

SKIP_DIRS = {
    "node_modules", "dist", "public", "content", "src", "scripts",
    ".astro", ".git", ".vscode", "assets", "stylesheet", "javascript",
    "images", "fonts", "icon", "_archive", "admin",
}

# Paths that are pure asset trees (never contain pages)
ASSET_TOP = {"assets", "stylesheet", "javascript", "images", "fonts", "icon"}


def absify(fragment: str) -> str:
    """Rewrite relative Edukin asset/page links to site-root absolute paths."""
    h = fragment
    # multi-depth asset paths (../assets, ../../assets)
    h = re.sub(
        r'(href|src|data-src|poster)="(?:\.\./)+(assets|stylesheet|javascript|images|fonts|icon)/',
        r'\1="/\2/',
        h,
    )
    # root-relative already-correct: skip
    # bare relative assets from home: assets/..., stylesheet/...
    h = re.sub(
        r'(href|src|data-src|poster)="(?!/|https?:|mailto:|tel:|#)(assets|stylesheet|javascript|images|fonts|icon)/',
        r'\1="/\2/',
        h,
    )
    h = re.sub(
        r"url\((['\"]?)(?:\.\./)+(assets|stylesheet|javascript|images|fonts|icon)/",
        r"url(\1/\2/",
        h,
    )
    h = re.sub(
        r"url\((['\"]?)(?!/|https?:)(assets|stylesheet|javascript|images|fonts|icon)/",
        r"url(\1/\2/",
        h,
    )
    # page links: ../foo/ or ../../foo/bar/
    h = re.sub(r'href="(?:\.\./)+index\.html"', 'href="/"', h)
    h = re.sub(r'href="index\.html"', 'href="/"', h)
    h = re.sub(r'href="(?:\.\./)+([^"#?]+?)(?:/index\.html)?/?(#[^"]*)?"', _page_href, h)
    # home-style relative page links: admission/ overview/ etc (not assets)
    h = re.sub(
        r'href="(?!/|https?:|mailto:|tel:|#|\.\./)([a-zA-Z0-9][^"#?]*/?)(#[^"]*)?"',
        _home_page_href,
        h,
    )
    # bare ./ 
    h = re.sub(r'href="\./"', 'href="/"', h)
    return h


def _home_page_href(m: re.Match) -> str:
    path = m.group(1)
    frag = m.group(2) or ""
    if path.startswith(("assets/", "stylesheet/", "javascript/", "images/", "fonts/", "icon/", "admin/")):
        return m.group(0)
    if path.endswith((".pdf", ".jpg", ".jpeg", ".png", ".webp", ".svg", ".gif", ".css", ".js", ".html")):
        if path.endswith("index.html"):
            return f'href="/{frag}"' if not path.startswith("http") else m.group(0)
        return f'href="/{path.lstrip("/")}{frag}"'
    path = path.rstrip("/")
    return f'href="/{path}/{frag}"'


def _page_href(m: re.Match) -> str:
    path = m.group(1).rstrip("/")
    frag = m.group(2) or ""
    if path.startswith(("http:", "https:", "mailto:", "tel:", "assets/", "javascript:", "#")):
        return m.group(0)
    if path.endswith((".pdf", ".jpg", ".jpeg", ".png", ".webp", ".svg", ".gif", ".css", ".js")):
        return f'href="/{path}{frag}"'
    return f'href="/{path}/{frag}"' if not frag else f'href="/{path}/{frag}"'


def yaml_escape(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    if any(c in s for c in ':#{}[]&*?|>!%@`\'"\n') or s.strip() != s:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    return s


def extract_title(html: str, fallback: str) -> str:
    m = re.search(r"<title>([^<]+)</title>", html, re.I)
    if not m:
        return fallback
    t = html_lib.unescape(m.group(1))
    t = re.sub(r"\s*\|\s*Al Jamia.*$", "", t).strip()
    return t or fallback


def extract_description(html: str) -> str:
    m = re.search(r'name=["\']description["\']\s+content=["\']([^"\']*)["\']', html, re.I)
    if not m:
        m = re.search(r'content=["\']([^"\']*)["\']\s+name=["\']description["\']', html, re.I)
    if not m:
        return "Al Jamia Arts & Science College, Perinthalmanna — affiliated to the University of Calicut."
    return html_lib.unescape(m.group(1))


def extract_main(html: str, is_home: bool) -> str:
    if is_home:
        m = re.search(
            r"(?:</div><!-- wrap-header -->|<!-- wrap-header -->)(.*?)(?=<footer\b)",
            html,
            re.S | re.I,
        )
        if m:
            return m.group(1).strip()
        # fallback: after first </header>
        m = re.search(r"</header>\s*</div>\s*</div>(.*?)(?=<footer\b)", html, re.S | re.I)
        if m:
            return m.group(1).strip()

    m = re.search(r"<!--\s*bg-header\s*-->(.*?)(?=<footer\b)", html, re.S | re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r"</div><!--\s*bg-header\s*-->(.*?)(?=<footer\b)", html, re.S | re.I)
    if m:
        return m.group(1).strip()
    # last resort: between last </header> block end and footer
    m = re.search(r"</header>(.*?)(?=<footer\b)", html, re.S | re.I)
    if m:
        chunk = m.group(1)
        # drop breadcrumbs shell if still inside bg-header
        return chunk.strip()
    return ""


def extract_profile_fields(body: str) -> dict:
    fields: dict = {}
    m = re.search(
        r'class="profile-photo"[^>]*>\s*<img[^>]+src="([^"]+)"[^>]*(?:alt="([^"]*)")?',
        body,
        re.S,
    )
    if m:
        fields["image"] = m.group(1)
    m = re.search(r'class="profile-name"[^>]*>([^<]+)', body)
    if m:
        fields["name"] = html_lib.unescape(m.group(1).strip())
    metas = re.findall(r'class="profile-meta"[^>]*>\s*(?:<li>([^<]+)</li>\s*)+', body)
    li = re.findall(r"<li>([^<]+)</li>", body)
    if li and "profile-meta" in body:
        # take first two lis near profile
        block = re.search(r'class="profile-meta">(.*?)</ul>', body, re.S)
        if block:
            items = [html_lib.unescape(x.strip()) for x in re.findall(r"<li>([^<]+)</li>", block.group(1))]
            if items:
                fields["credentials"] = items[0]
            if len(items) > 1:
                fields["role"] = items[1]
    role = re.search(r'class="profile-role"[^>]*>([^<]+)', body)
    if role:
        fields["role"] = html_lib.unescape(role.group(1).strip())
    return fields


def classify(rel: str) -> tuple[str, str]:
    """Return (collection, content_relative_path without extension)."""
    if rel in ("", ".", "index.html"):
        return "pages", "home"
    # normalize
    path = rel.replace("\\", "/").removesuffix("/index.html").removesuffix("index.html").strip("/")
    if path.startswith("college-news/") and path != "college-news":
        slug = path[len("college-news/") :]
        return "news", slug
    if path.startswith("event/") and path != "event":
        slug = path[len("event/") :]
        return "events", slug
    if path.startswith("faculties/") and path != "faculties":
        slug = path[len("faculties/") :]
        return "faculty", slug
    return "pages", path


def write_md(collection: str, slug: str, meta: dict, body: str) -> None:
    dest_dir = OUT / collection / Path(slug).parent
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = OUT / collection / f"{slug}.md"
    lines = ["---"]
    for k, v in meta.items():
        if v is None or v is False:
            continue
        if isinstance(v, bool):
            lines.append(f"{k}: true")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        else:
            lines.append(f"{k}: {yaml_escape(str(v))}")
    lines.append("---")
    lines.append("")
    lines.append(body.rstrip())
    lines.append("")
    dest.write_text("\n".join(lines), encoding="utf-8")


def extract_partials(sample_html: str) -> None:
    PARTIALS.mkdir(parents=True, exist_ok=True)
    m = re.search(r'(<div class="top-bar clearfix">.*?</header>)', sample_html, re.S)
    if m:
        (PARTIALS / "header.html").write_text(absify(m.group(1)), encoding="utf-8")
    m = re.search(r'(<footer id="footer".*?</footer>)', sample_html, re.S)
    if m:
        (PARTIALS / "footer.html").write_text(absify(m.group(1)), encoding="utf-8")
    # mobile + reveal scripts (shared)
    m = re.search(r"(<script>\s*\(function\(\)\{\s*var reduce[\s\S]*?</script>)", sample_html)
    if m:
        (PARTIALS / "site-scripts.html").write_text(m.group(1), encoding="utf-8")
    else:
        # try broader
        scripts = re.findall(r"<script(?![^>]*src=)[^>]*>[\s\S]*?</script>", sample_html)
        inline = "\n".join(scripts)
        if inline:
            (PARTIALS / "site-scripts.html").write_text(inline, encoding="utf-8")


def page_type_for(collection: str, slug: str, body: str) -> str:
    if slug == "home":
        return "home"
    if "profile-page" in body or "profile-card" in body:
        return "profile"
    if "listing-intro" in body or "flat-team" in body or "courses-grid-page" in body:
        return "listing"
    if collection in ("news", "events"):
        return "article"
    return "page"


def main() -> None:
    # clear previous extracted md (keep dirs)
    for coll in ("pages", "news", "events", "faculty"):
        d = OUT / coll
        d.mkdir(parents=True, exist_ok=True)
        for p in d.rglob("*.md"):
            p.unlink()

    print(f"HTML source: {HTML_ROOT}")
    html_files = sorted(HTML_ROOT.rglob("index.html"))
    count = {k: 0 for k in ("pages", "news", "events", "faculty")}
    partials_done = False

    for fp in html_files:
        rel_parts = fp.relative_to(HTML_ROOT).parts
        if any(p in SKIP_DIRS or p.startswith(".") for p in rel_parts[:-1]):
            continue
        if rel_parts and rel_parts[0] in ASSET_TOP:
            continue
        # skip nested node/dist etc.
        if "node_modules" in rel_parts or "dist" in rel_parts:
            continue

        rel = str(fp.relative_to(HTML_ROOT))
        html = fp.read_text(encoding="utf-8", errors="ignore")
        if not partials_done and "top-bar" in html and "main-nav" in html:
            extract_partials(html)
            partials_done = True

        collection, slug = classify(rel)
        is_home = slug == "home"
        title = extract_title(html, slug.replace("-", " ").title())
        description = extract_description(html)
        body = absify(extract_main(html, is_home=is_home))
        if not body:
            print(f"WARN empty body: {rel}")
            continue

        # permalink for routing
        if is_home:
            permalink = "/"
        elif collection == "news":
            permalink = f"/college-news/{slug}/"
        elif collection == "events":
            permalink = f"/event/{slug}/"
        elif collection == "faculty":
            permalink = f"/faculties/{slug}/"
        else:
            permalink = f"/{slug}/"

        ptype = page_type_for(collection, slug, body)
        meta: dict = {
            "title": title,
            "description": description,
            "permalink": permalink,
            "type": ptype,
            "draft": False,
        }

        if collection == "faculty" or ptype == "profile":
            meta.update({k: v for k, v in extract_profile_fields(body).items() if v})

        # crude date from path year in uploads inside body — skip if none
        write_md(collection, slug, meta, body)
        count[collection] += 1

    print("Extracted:", count, "total", sum(count.values()))
    print("Partials:", PARTIALS, "exists" if PARTIALS.exists() else "MISSING")
    for name in ("header.html", "footer.html", "site-scripts.html"):
        p = PARTIALS / name
        print(f"  {name}: {p.stat().st_size if p.exists() else 'missing'} bytes")


if __name__ == "__main__":
    main()
