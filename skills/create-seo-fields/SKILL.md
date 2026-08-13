---
name: create-seo-fields
description: Create or refactor Sanity/CMS-backed SEO fields and frontend rendering for Meta, Open Graph, Twitter cards, and JSON-LD structured data. Use when adding SEO schema fields, naming metadata fields, wiring Astro/React/Next/etc. head output, validating BlogPosting or Article JSON-LD, adding character counters or constraints, using astro-seo-meta or astro-seo-schema, or replacing hardcoded SEO fallbacks with durable content-source data.
---

# Create SEO Fields

## Workflow

1. Inspect the project before designing fields.
   - Identify the CMS/schema system, frontend head component, JSON-LD helper, image URL builder, and existing SEO packages.
   - Reuse existing packages and helpers unless they block correct output.
   - In Astro projects, prefer installed `astro-seo-meta` for metadata and `astro-seo-schema` for JSON-LD. If the project already uses a custom head component, preserve it only when it emits equivalent tags correctly.
   - Verify current official docs when platform behavior matters: Google Search Central for search snippets and Article structured data, Open Graph protocol for `og:*`, and Schema.org for JSON-LD property names.

2. Group fields by emitted surface.
   - Use one `SEO` object or equivalent group.
   - Inside it, group `Metadata`, `Open Graph`, and `JSON-LD`.
   - Use real protocol/schema names for labels where useful: `metaTitle`, `metaDescription`, `og:title`, `og:description`, `og:image`, `og:image:alt`, `dateModified`, `articleSection`, `about`, `mentions`.
   - Avoid invented collaborative labels like "search title tag" or "title link" unless the user explicitly requests them.

3. Define fields with clear constraints.
   - `metaTitle`: string. HTML `<title>` source. Target 50-60 chars; max 70.
   - `metaDescription`: text. Search/social/schema description fallback. Target 150-160 chars; max 170.
   - `canonical`: URL. Absolute preferred URL override.
   - `robots`: enum. Prefer `index, follow`; include noindex options only when useful.
   - `snippetFocus`: string. Internal search intent note; do not emit.
   - `og:title`: string. Social title override. Max 95.
   - `og:description`: text. Social description override. Max 200.
   - `og:image`: image. Social image override. Prefer 1200x630 framing.
   - `og:image:alt`: string. Social image alt. Max 160 unless project policy differs.
   - `dateModified`: datetime. Emits JSON-LD `dateModified` and article modified meta.
   - `articleSection`: string. JSON-LD `articleSection`; fallback to primary category.
   - `keywords`: array of strings. JSON-LD keywords; merge with tags and dedupe.
   - `about`: array of `{name, url?}` Thing objects. Primary entities.
   - `mentions`: array of `{name, url?}` Thing objects. Referenced entities.
   - `author`: object with `name`, optional `url`, optional `sameAs[]`.

4. Build a single frontend normalization helper.
   - Input: CMS document plus canonical URL and locale.
   - Output: resolved title, description, robots, keywords, image, image alt, social overrides, article meta values, and JSON-LD.
   - Use fallback order from most-specific to generic: SEO override -> document field -> site default only for global defaults.
   - Keep Sanity/CMS as the content source. Do not reintroduce hardcoded per-post SEO maps, legacy markdown frontmatter fallbacks, local title/description/image constants, or route-specific SEO data.
   - Treat hardcoded values as allowed only for site-wide constants such as base URL, organization `@id`, default robots, locale, and package configuration.

5. Emit consistently.
   - Head: `<title>`, meta description, canonical, robots, keywords if project emits them.
   - Open Graph/Twitter: title, description, type, URL, image, image alt.
   - Article meta: published time, modified time, author URL when present, section, tags.
   - JSON-LD: `BlogPosting` or `Article` with `@id`, `mainEntityOfPage`, `headline`, `description`, `url`, image variants, dates, author, publisher, `articleSection`, `keywords`, `about`, `mentions`, and `inLanguage` when available.

6. Validate before finishing.
   - Run schema validation against real CMS content when credentials are available.
   - Build the frontend and Studio/CMS app.
   - Inspect generated HTML for at least one representative page: meta description, canonical, `og:*`, Twitter image alt, article meta, and JSON-LD.
   - If a full build fails for dependency or lockfile drift, isolate whether the SEO changes pass and report the separate blocker clearly.

## Implementation Notes

- Add live character counters for bounded text fields when the CMS supports custom inputs.
- Keep object fields as objects in both schema and content. If a field changed from string to object, migrate existing content or add a read-time compatibility projection.
- For image JSON-LD, emit multiple crop/aspect variants when the image helper can produce them.
- For unknown existing content shapes, prefer compatibility reads plus explicit content cleanup over fabricated defaults.
- For Sanity-backed projects, query every emitted per-entry SEO value from Sanity and verify the rendered HTML changes when Sanity content changes.
