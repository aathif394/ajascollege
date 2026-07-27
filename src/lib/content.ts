import { getCollection, type CollectionEntry } from "astro:content";

export type AnyEntry =
  | CollectionEntry<"pages">
  | CollectionEntry<"news">
  | CollectionEntry<"events">
  | CollectionEntry<"faculty">;

export async function getAllEntries(): Promise<AnyEntry[]> {
  const [pages, news, events, faculty] = await Promise.all([
    getCollection("pages", ({ data }) => !data.draft),
    getCollection("news", ({ data }) => !data.draft),
    getCollection("events", ({ data }) => !data.draft),
    getCollection("faculty", ({ data }) => !data.draft),
  ]);
  return [...pages, ...news, ...events, ...faculty];
}

export async function getEntryByPermalink(
  permalink: string,
): Promise<AnyEntry | undefined> {
  const normalized = normalizePermalink(permalink);
  const all = await getAllEntries();
  return all.find((e) => normalizePermalink(e.data.permalink) === normalized);
}

export function normalizePermalink(p: string): string {
  if (!p || p === "/") return "/";
  let s = p.startsWith("/") ? p : `/${p}`;
  if (!s.endsWith("/")) s += "/";
  return s;
}

/** Astro route path without trailing slash (except home). */
export function routeFromPermalink(permalink: string): string {
  const n = normalizePermalink(permalink);
  if (n === "/") return "/";
  return n.replace(/\/$/, "") || "/";
}
