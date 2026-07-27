#!/usr/bin/env python3
"""
Convert CMS content bodies from raw Edukin HTML wrappers → clean Markdown.

Editors then use Sveltia's visual markdown editor (WYSIWYG), never raw HTML.
Layout chrome (blog-single, chips, etc.) stays in Astro templates.
"""
from __future__ import annotations

import re
from pathlib import Path

from markdownify import markdownify as md

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

# Skip structured-only / special full-page layouts for now
SKIP = {
    CONTENT / "pages" / "home.md",  # custom home sections; use Homepage hero CMS instead
}


def extract_inner_html(body: str) -> str:
    """Pull editorial HTML out of Edukin chrome wrappers."""
    body = body.strip()
    if not body:
        return ""

    # Prefer migrate-content inner HTML
    m = re.search(
        r'class="[^"]*migrate-content[^"]*"[^>]*>(.*?)(?:</div>\s*){1,8}'
        r'(?:<div class="page-chips"|</article>|$)',
        body,
        re.S | re.I,
    )
    if m:
        return m.group(1).strip()

    m = re.search(
        r'class="[^"]*migrate-content[^"]*"[^>]*>(.*?)</div>',
        body,
        re.S | re.I,
    )
    if m:
        return m.group(1).strip()

    # Profile / listing pages without migrate-content: strip outer shells
    for pat in [
        r'class="profile-page"[^>]*>\s*<div class="container">(.*?)</div>\s*</div>\s*$',
        r'class="blog-single[^"]*"[^>]*>(.*?)$',
    ]:
        m = re.search(pat, body, re.S | re.I)
        if m:
            return m.group(1).strip()

    # Already looks like markdown / plain text
    if not re.search(r"<(div|section|article|p|h[1-6]|ul|table)\b", body, re.I):
        return body

    return body


def clean_html(html: str) -> str:
    # Drop empty gallery headings with no following media is fine
    html = re.sub(r"<br\s*/?>\s*</br>", "<br>", html, flags=re.I)
    html = re.sub(r"</?span[^>]*>", "", html, flags=re.I)
    # Remove empty class attributes noise later via markdownify
    return html


def to_markdown(html: str) -> str:
    html = clean_html(html)
    if not html.strip():
        return ""
    # If already mostly markdown (few tags), keep
    tag_count = len(re.findall(r"<[a-zA-Z][^>]*>", html))
    if tag_count <= 2 and not re.search(r"<div\b", html, re.I):
        # maybe just a leftover
        pass

    out = md(
        html,
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
        escape_asterisks=False,
        escape_underscores=False,
    )
    # tidy
    out = re.sub(r"\n{3,}", "\n\n", out)
    out = re.sub(r"[ \t]+\n", "\n", out)
    out = out.strip() + "\n"
    return out


def split_frontmatter(raw: str) -> tuple[str, str]:
    if not raw.startswith("---"):
        return "", raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return "", raw
    return parts[1], parts[2]


def process_file(path: Path) -> bool:
    if path in SKIP or path.resolve() in {p.resolve() for p in SKIP}:
        return False
    raw = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(raw)
    if not fm:
        return False

    # Skip pure JSON-ish / empty
    body_stripped = body.strip()
    if not body_stripped:
        return False

    # Detect if already markdown (no layout chrome)
    if "blog-single" not in body and "migrate-content" not in body and "profile-page" not in body:
        if not re.search(r"<div\s", body):
            # already clean enough
            return False

    inner = extract_inner_html(body)
    if not inner or len(inner) < 3:
        return False

    markdown = to_markdown(inner)
    if not markdown.strip():
        return False

    # Drop empty profile meta fields noise from CMS if present in fm
    fm_lines = []
    for line in fm.strip("\n").splitlines():
        if re.match(r"^(name|role|credentials):\s*['\"]?\s*['\"]?\s*$", line):
            continue
        if re.match(r"^(name|role|credentials):\s*''\s*$", line):
            continue
        fm_lines.append(line)
    fm_clean = "\n".join(fm_lines) + "\n"

    new = f"---\n{fm_clean}---\n\n{markdown}"
    if new == raw:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for p in sorted(CONTENT.rglob("*.md")):
        try:
            if process_file(p):
                changed += 1
                print("OK", p.relative_to(ROOT))
        except Exception as e:
            print("FAIL", p, e)
    print(f"Converted {changed} files to WYSIWYG markdown")


if __name__ == "__main__":
    main()
