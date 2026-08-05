import { marked } from "marked";

export type FactRow = { label: string; value: string };
export type ContentSection = {
  id: string;
  title: string;
  level: 2 | 3;
  bodyMd: string;
  bodyHtml: string;
  facts: FactRow[];
  images: string[];
  empty: boolean;
};

export type ProgrammeBlock = {
  title: string;
  duration?: string;
  fee?: string;
  intake?: string;
  complementary?: string;
  eligibility?: string;
  extraHtml: string;
};

function slugify(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 60);
}

function parseMarkdownTable(md: string): FactRow[] {
  const lines = md
    .trim()
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);
  if (lines.length < 2 || !lines[0].includes("|")) return [];
  const rows: FactRow[] = [];
  for (const line of lines) {
    if (/^\|?\s*:?-{3,}/.test(line)) continue;
    const cells = line
      .replace(/^\|/, "")
      .replace(/\|$/, "")
      .split("|")
      .map((c) => c.trim());
    if (cells.length < 2) continue;
    // skip empty header rows
    if (!cells[0] && !cells[1]) continue;
    if (cells[0] === "" && cells.every((c, i) => i === 0 || !c || c === "---")) continue;
    rows.push({ label: cells[0] || cells[1], value: cells[1] || cells.slice(1).join(" · ") });
  }
  // drop header-like first row if both are empty-ish or generic
  if (rows.length && (!rows[0].label || rows[0].label === rows[0].value)) {
    // keep
  }
  return rows.filter((r) => r.label || r.value);
}

function extractImages(md: string): string[] {
  const out: string[] = [];
  const re = /!\[[^\]]*\]\(([^)]+)\)/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(md))) out.push(m[1]);
  return out;
}

function stripImages(md: string): string {
  return md.replace(/!\[[^\]]*\]\(([^)]+)\)\s*/g, "").trim();
}

function mdToHtml(md: string): string {
  if (!md.trim()) return "";
  return marked.parse(md, { async: false }) as string;
}

/** Split page body into H2 sections (+ leading intro). */
export function splitSections(body: string): {
  introMd: string;
  introHtml: string;
  introImages: string[];
  introFacts: FactRow[];
  sections: ContentSection[];
} {
  const text = body.replace(/\r\n/g, "\n").trim();
  const parts = text.split(/(?=^## )/m);
  let introMd = "";
  const sections: ContentSection[] = [];

  for (const part of parts) {
    if (!part.trim()) continue;
    if (part.startsWith("## ")) {
      const nl = part.indexOf("\n");
      const title = part.slice(3, nl === -1 ? undefined : nl).trim();
      const bodyMd = (nl === -1 ? "" : part.slice(nl + 1)).trim();
      // Collect tables in section
      const facts: FactRow[] = [];
      let rest = bodyMd;
      const tableBlocks = bodyMd.match(/(?:^\|.+\|$\n?)+/gm);
      if (tableBlocks) {
        for (const tb of tableBlocks) {
          facts.push(...parseMarkdownTable(tb));
          rest = rest.replace(tb, "").trim();
        }
      }
      const images = extractImages(bodyMd);
      const textOnly = stripImages(rest).replace(/(?:^\|.+\|$\n?)+/gm, "").trim();
      const empty = !textOnly && facts.length === 0 && images.length === 0;
      sections.push({
        id: slugify(title),
        title,
        level: 2,
        bodyMd: rest,
        bodyHtml: mdToHtml(rest),
        facts,
        images,
        empty,
      });
    } else {
      introMd += (introMd ? "\n\n" : "") + part.trim();
    }
  }

  // Tables in intro
  const introFacts: FactRow[] = [];
  let introRest = introMd;
  const introTables = introMd.match(/(?:^\|.+\|$\n?)+/gm);
  if (introTables) {
    for (const tb of introTables) {
      introFacts.push(...parseMarkdownTable(tb));
      introRest = introRest.replace(tb, "").trim();
    }
  }
  const introImages = extractImages(introMd);
  const introHtml = mdToHtml(stripImages(introRest).replace(/(?:^\|.+\|$\n?)+/gm, "").trim());

  return {
    introMd: introRest,
    introHtml,
    introImages,
    introFacts,
    sections: sections.filter((s) => !s.empty),
  };
}

/** Parse admission-style ### programme blocks. */
export function parseProgrammes(body: string): {
  leadHtml: string;
  programmes: ProgrammeBlock[];
  tailHtml: string;
} {
  const text = body.replace(/\r\n/g, "\n");
  // Drop a top ## Programme Offered wrapper title for cleaner UI
  const cleaned = text.replace(/^## Programme Offered\s*\n+/i, "");
  const chunks = cleaned.split(/(?=^### )/m);
  let lead = "";
  const programmes: ProgrammeBlock[] = [];
  let tail = "";

  for (const chunk of chunks) {
    if (!chunk.trim()) continue;
    if (!chunk.startsWith("### ")) {
      if (programmes.length === 0) lead += chunk;
      else tail += chunk;
      continue;
    }
    const nl = chunk.indexOf("\n");
    const title = chunk.slice(4, nl === -1 ? undefined : nl).trim();
    const bodyMd = (nl === -1 ? "" : chunk.slice(nl + 1)).trim();

    const pick = (label: string) => {
      const re = new RegExp(
        `(?:^|\\n)[-*]\\s*${label}\\s*[:\\s]*([^\\n]+)`,
        "i",
      );
      const m = bodyMd.match(re);
      return m ? m[1].replace(/^[:\\s]+/, "").trim() : undefined;
    };

    // Duration06 sem / Fee19500 patterns without space after label
    const duration =
      pick("Duration") ||
      bodyMd.match(/Duration\s*([^\n]+)/i)?.[1]?.trim();
    const fee =
      pick("Fee") || bodyMd.match(/Fee\s*([^\n]+)/i)?.[1]?.trim();
    const intake =
      pick("Intake") || bodyMd.match(/Intake\s*([^\n]+)/i)?.[1]?.trim();

    let eligibility: string | undefined;
    const elig = bodyMd.match(
      /\*\*Eligibility\*\*\s*([\s\S]*?)(?=\n### |\n\*\*|$)/i,
    );
    if (elig) eligibility = elig[1].trim();

    let complementary: string | undefined;
    const comp = bodyMd.match(
      /\*\*Complementary\*\*\s*([\s\S]*?)(?=\n### |\n\*\*|$)/i,
    );
    if (comp) complementary = comp[1].replace(/^Complementary:\s*/i, "").trim();

    // remaining narrative
    let extra = bodyMd
      .replace(/(?:^|\n)[-*]\s*Duration[^\n]*/gi, "")
      .replace(/(?:^|\n)[-*]\s*Fee[^\n]*/gi, "")
      .replace(/(?:^|\n)[-*]\s*Intake[^\n]*/gi, "")
      .replace(/Duration[^\n]*/gi, "")
      .replace(/Fee[^\n]*/gi, "")
      .replace(/Intake[^\n]*/gi, "")
      .replace(/\*\*Eligibility\*\*[\s\S]*?(?=\n### |\n\*\*|$)/i, "")
      .replace(/\*\*Complementary\*\*[\s\S]*?(?=\n### |\n\*\*|$)/i, "")
      .trim();

    programmes.push({
      title,
      duration,
      fee,
      intake,
      complementary,
      eligibility,
      extraHtml: mdToHtml(extra),
    });
  }

  return {
    leadHtml: mdToHtml(lead.trim()),
    programmes,
    tailHtml: mdToHtml(tail.trim()),
  };
}

export function looksLikeAdmission(body: string, permalink: string): boolean {
  return (
    permalink.includes("admission") ||
    (/### /.test(body) && /Fee|Intake|Duration/i.test(body))
  );
}

/**
 * Only the dedicated Vision & Mission page should get the 2-panel layout.
 * Matching on "has a Vision heading and a Mission heading" false-positives on
 * every department/club/cell page (they almost all have their own Vision +
 * Mission subsections among several other sections) and wrecks them — see
 * incident where placement-cell/department pages rendered as two giant
 * cartoon panels with every other section (tables, galleries) silently
 * dropped. Scope this to pages that are ONLY Vision + Mission.
 */
export function looksLikeVision(body: string, title: string, permalink?: string): boolean {
  if (permalink && normalizeForVisionCheck(permalink) === "/vision-mission/") return true;
  if (!/vision/i.test(title)) return false;
  const headings = (body.match(/^##\s+(.+)$/gm) || []).map((h) =>
    h.replace(/^##\s+/, "").trim().toLowerCase(),
  );
  return (
    headings.length > 0 &&
    headings.length <= 2 &&
    headings.every((h) => h === "vision" || h === "mission")
  );
}

function normalizeForVisionCheck(p: string): string {
  const s = p.startsWith("/") ? p : `/${p}`;
  return s.endsWith("/") ? s : `${s}/`;
}
