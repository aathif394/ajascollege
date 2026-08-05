import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const entrySchema = z.object({
  title: z.string(),
  description: z.string().optional(),
  permalink: z.string(),
  type: z
    .enum(["home", "page", "listing", "profile", "article"])
    .default("page"),
  draft: z.boolean().default(false),
  date: z.coerce.date().optional(),
  image: z.string().optional(),
  name: z.string().optional(),
  role: z.string().optional(),
  credentials: z.string().optional(),
  attachments: z
    .array(z.object({ label: z.string(), file: z.string() }))
    .optional(),
  gallery: z.array(z.string()).optional(),
  people: z
    .array(
      z.object({
        photo: z.string().optional(),
        name: z.string(),
        role: z.string().optional(),
        phone: z.string().optional(),
      }),
    )
    .optional(),
  menu_items: z
    .array(
      z.object({
        title: z.string(),
        href: z.string().optional(),
        description: z.string().optional(),
      }),
    )
    .optional(),
});

const pages = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./content/pages" }),
  schema: entrySchema,
});

const news = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./content/news" }),
  schema: entrySchema,
});

const events = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./content/events" }),
  schema: entrySchema,
});

const faculty = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./content/faculty" }),
  schema: entrySchema,
});

/** Day-to-day: programmes (UG/PG) */
const programmes = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./content/programmes" }),
  schema: z.object({
    title: z.string(),
    level: z.enum(["ug", "pg", "certificate", "other"]).default("ug"),
    order: z.number().default(0),
    permalink: z.string(),
    draft: z.boolean().default(false),
    description: z.string().optional(),
    duration: z.string().optional(),
    seats: z.string().optional(),
    department: z.string().optional(),
  }),
});

/** Day-to-day: circulars / mandatory docs / downloads */
const notices = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./content/notices" }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date().optional(),
    category: z
      .enum(["general", "academic", "compliance", "iqac", "mandatory", "admin", "admission"])
      .default("general"),
    file: z.string(),
    permalink: z.string(),
    draft: z.boolean().default(false),
    description: z.string().optional(),
  }),
});

/** Day-to-day: fee structure PDFs */
const fees = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./content/fees" }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date().optional(),
    file: z.string(),
    permalink: z.string(),
    draft: z.boolean().default(false),
    description: z.string().optional(),
  }),
});

/** Site-wide settings (contact, admission banner, key PDFs) */
const settings = defineCollection({
  loader: glob({ pattern: "site.json", base: "./content/settings" }),
  schema: z.object({
    college_name: z.string(),
    short_name: z.string().optional(),
    tagline: z.string().optional(),
    phone: z.string(),
    phone_display: z.string().optional(),
    email: z.string(),
    address: z.string(),
    logo: z.string().optional(),
    admission_open: z.boolean().default(true),
    admission_label: z.string().optional(),
    admission_url: z.string().optional(),
    admission_note: z.string().optional(),
    fee_pdf: z.string().optional(),
    prospectus_pdf: z.string().optional(),
  }),
});

/** Homepage hero + principal blurb (structured, WordPress-like) */
const home = defineCollection({
  loader: glob({ pattern: "**/*.{json,yml,yaml}", base: "./content/home" }),
  schema: z.object({
    hero_kicker: z.string(),
    hero_title: z.string(),
    hero_text: z.string(),
    hero_cta_primary_label: z.string(),
    hero_cta_primary_url: z.string(),
    hero_cta_secondary_label: z.string(),
    hero_cta_secondary_url: z.string(),
    hero_images: z.array(z.string()).default([]),
    stat_departments: z.string().optional(),
    stat_ug: z.string().optional(),
    stat_pg: z.string().optional(),
    stat_established: z.string().optional(),
    principal_name: z.string().optional(),
    principal_photo: z.string().optional(),
    principal_excerpt: z.string().optional(),
  }),
});

export const collections = {
  pages,
  news,
  events,
  faculty,
  programmes,
  notices,
  fees,
  settings,
  home,
};
