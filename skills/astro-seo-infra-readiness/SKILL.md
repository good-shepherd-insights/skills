---
name: astro-seo-infra-readiness
description: Audit and repair Astro frontend SEO infrastructure for production readiness with astro-seo metadata rendering, schema-dts typed JSON-LD builders, centralized JSON-LD serialization, @astrojs/sitemap, and rendered-output tests. Use when Codex is asked to make an Astro site SEO-ready, validate metadata/JSON-LD/sitemap/canonical/robots emission, build CMS-backed schema builders, distinguish frontend infra gaps from copywriter/CMS content gaps, or confirm 100% SEO infrastructure readiness across generated pages.
---

# Astro SEO Infra Readiness

## Purpose

Use this skill to make an Astro site's SEO infrastructure complete and verifiable without overfitting to one codebase. Treat the built HTML as the source of truth. Prefer descriptive, adaptable patterns over fixed file names or a single page taxonomy.

The goal is not to judge copy quality. It is to ensure that if content exists in the site or CMS, the frontend can normalize it, render it, relate it, and prove the result in generated output.

## Scope Boundary

Count as frontend infrastructure:

- Metadata rendering paths for title, description, canonical, robots, Open Graph, Twitter, alternates, and article meta.
- JSON-LD rendering paths using typed `schema-dts` objects and a centralized serializer.
- Normalization helpers that convert page/CMS data into metadata and schema objects.
- Sitemap and robots consistency for built pages.
- Canonical URL resolution and stable schema `@id` generation.
- Page-template wiring when data exists but is not passed into the SEO layer.
- Schema graph relationships such as `isPartOf`, `mainEntity`, `mainEntityOfPage`, `publisher`, `provider`, and `BreadcrumbList`.
- Rendered-output tests that prove generated HTML, sitemap, robots, and JSON-LD match the project's business route contract.

Do not count as frontend infrastructure:

- Long titles, weak titles, thin descriptions, or poor keyword choices.
- Missing CMS values when the frontend already supports emitting them.
- Editorial image alt quality when the template passes available alt text.
- Business decisions about whether placeholder, draft, legal, taxonomy, or paginated pages should be indexable.

Still report out-of-scope findings separately when they could block real SEO performance or cause crawl risk.

## Decision Model

Classify each finding before fixing or reporting it:

- `Infrastructure gap`: the generated page is missing or emitting invalid SEO output even though the frontend has, or should have, enough page data to render it.
- `Package gap`: required local stack pieces are absent, installed but unused, or bypassed in a way that prevents consistent output. For the preferred Astro stack, that means `astro-seo`, `schema-dts`, `@astrojs/sitemap`, and rendered-output test tooling such as Vitest plus Cheerio.
- `Content/data gap`: the frontend can emit the field correctly, but the CMS or page data lacks the value or contains weak editorial copy.
- `Policy gap`: the correct behavior depends on a product decision, such as whether a generated placeholder, draft, legal, taxonomy, or paginated page should be indexable.

Only infrastructure and authorized package gaps count against frontend SEO infrastructure readiness. Content/data and policy gaps must be named separately and must not be hidden inside the readiness score.

## Readiness Definition

An Astro site is at 100% frontend SEO infrastructure readiness when all active indexable generated pages satisfy these checks:

- The production build completes.
- Every active indexable page has a title, meta description, canonical URL, robots directive, Open Graph core tags, Twitter core tags, and parseable JSON-LD.
- Canonical URLs are absolute and match `og:url` unless the project deliberately uses a different canonical strategy.
- Active indexable pages are included in the sitemap.
- Noindex pages are excluded from the sitemap.
- The global graph emits one stable `WebSite` and one stable business or publisher entity, such as `Organization`, `LocalBusiness`, `Bakery`, or another project-appropriate subtype.
- Non-home active pages emit breadcrumbs; the home page does not need a breadcrumb.
- Page-specific JSON-LD exists for the page's actual role, such as `WebPage`, `CollectionPage`, `ItemList`, `BlogPosting`, `Article`, `Service`, `ContactPage`, or `FAQPage`.
- Collection pages that list entities emit an `ItemList` and connect it through `CollectionPage.mainEntity`.
- Detail pages connect the page and primary entity with a coherent relationship, such as `WebPage.mainEntity -> Product @id` or `Product.mainEntityOfPage -> WebPage @id`.
- Articles and blog posts emit article metadata and JSON-LD fields from CMS data when available.
- Generated JSON-LD objects use stable absolute `@id` values and cross-reference those IDs instead of duplicating unrelated entities.

If placeholder or intentionally unused pages are built, exclude them from the readiness score only when the user or repository evidence explicitly marks them out of scope. Otherwise, audit them as crawlable pages.

## Workflow

1. Establish the page universe from generated output.
   - Run or inspect the production build.
   - Enumerate generated `dist/**/*.html`.
   - Parse the sitemap index and concrete sitemap files.
   - Classify pages as active indexable, noindex, placeholder/draft/unused, and special files such as 404.
   - Do not rely only on navigation or source routes; generated HTML is what crawlers see.

2. Inventory existing SEO infrastructure.
   - Identify Astro layout/head components.
   - Identify whether `astro-seo`, `schema-dts`, `@astrojs/sitemap`, Vitest, and Cheerio or equivalent generated-output test tooling are installed.
   - Use `astro-seo` for metadata rendering when adding package-backed metadata in Astro. Do not refer to or install `astro-seo-meta`.
   - Use `schema-dts` for Schema.org typing. Do not handroll loose untyped JSON-LD objects when typed builders are practical.
   - Do not require `astro-seo-schema`. If it is present, verify raw built JSON-LD before keeping it; known failure mode is entity-escaped values such as `Cups &amp; Cakes` inside the JSON-LD script.
   - Find CMS fetch helpers, image URL builders, locale helpers, canonical helpers, sitemap scripts, and robots generation.
   - Find all JSON-LD script emitters, `<Schema>` calls, serializer helpers, and inline `@type` objects.

3. Audit generated HTML.
   - Parse metadata tags rather than eyeballing source.
   - Parse every `application/ld+json` script with `JSON.parse`.
   - Compare canonical, `og:url`, robots, sitemap membership, schema types, and schema relationships.
   - Separate infrastructure failures from content quality findings.

4. Repair infrastructure gaps in the smallest surface that can generalize.
   - Prefer a shared normalization or schema-builder layer over page-by-page ad hoc objects.
   - Keep CMS as the source of page facts.
   - Use page templates only to pass already-fetched data into the shared SEO layer.
   - Preserve existing metadata packages unless they block correct output.
   - Replace package JSON-LD rendering with a small centralized serializer when generated output proves the package mutates JSON values or emits invalid/dirty JSON-LD. Keep Schema.org typing in `schema-dts`.

5. Validate from generated output again.
   - Re-run type checks/builds.
   - Re-run the dist audit.
   - Report exact counts: built pages, active pages, sitemap URLs, noindex pages, placeholders excluded, infra failures, and out-of-scope content findings.

## Preferred Package Architecture

For Astro sites that need durable SEO and JSON-LD infrastructure, prefer this stack unless the repository has a stronger existing equivalent:

- `astro-seo`: render metadata tags from normalized SEO props.
- `schema-dts`: type Schema.org nodes and graphs.
- `@astrojs/sitemap`: generate sitemap files and filter noindex routes.
- Central JSON-LD serializer: serialize final `schema-dts` objects into `<script type="application/ld+json">` without HTML entity-encoding JSON string values.
- Vitest plus Cheerio: parse production `dist` HTML and assert metadata, robots, canonical, sitemap, and JSON-LD behavior.

Do not default to `astro-seo-schema`. It can be useful only if verified against built output. If raw JSON-LD contains entity strings like `&amp;`, `&lt;`, `&gt;`, `&quot;`, or `&apos;` inside parsed values, remove or bypass that renderer and use the centralized serializer.

Keep the boundary clean:

- Package-backed metadata: `astro-seo`.
- Package-backed schema vocabulary/types: `schema-dts`.
- Project data mapping: local normalizer and schema builders.
- Script emission: centralized serializer.
- Route/search policy: local route policy and sitemap/robots integration.

Use a small module split instead of a God component. For CMS-backed Astro sites, a clean target shape is:

- route policy: indexability, sitemap eligibility, noindex behavior.
- SEO resolver: CMS/page/product facts into `astro-seo` props and schema node inputs.
- schema builders: CMS facts into typed `schema-dts` nodes and graphs.
- image helpers: absolute CMS image URLs and canonical social images.
- JSON-LD serializer: one safe script serialization path.
- sitemap/robots helpers: build-time sitemap filtering and robots generation.
- head component: render `<SEO />` plus JSON-LD scripts from resolved data.

## Implementation Patterns

Build or refactor toward these concepts, adapting names and shapes to the codebase.

### Metadata Normalization

Create one normalizer per broad document family when needed. It should resolve:

- `title`, `description`, `robots`, `canonical`, `keywords`
- `image`, `imageAlt`
- `og:title`, `og:description`, `og:type`, `og:url`, `og:image`, `og:image:alt`
- `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`, `twitter:image:alt`
- article fields such as published time, modified time, author, section, and tags

Use fallback order from most specific to most generic:

1. SEO override fields
2. document/page fields
3. section or media fields already fetched for the page
4. global site defaults

Do not fabricate content-specific facts in code. If a fact is absent from CMS and no fallback exists, leave it absent and report it as a content/data gap.

### Schema Builder Layer

Prefer small composable builders:

- ID helpers: base URL, canonical URL, `#website`, `#organization` or `#business`, `#webpage`, `#breadcrumb`, `#itemlist`, primary entity IDs.
- Graph helper: remove empty values and emit `{ "@context": "https://schema.org", "@graph": [...] }`.
- Base builders: `WebSite`, `Organization`, `BreadcrumbList`.
- Page builders: `WebPage`, `CollectionPage`, `ContactPage`, `FAQPage`.
- Entity builders: `ItemList`, `BlogPosting` or `Article`, `Service`, and other domain entities.

The builders should be descriptive and data-driven. They should accept already-normalized data, IDs, current URL, locale, and site globals. They should not import page components or hard-code route-specific copy.

The builders may be local project code, but the returned objects should be typed with `schema-dts` wherever practical. Avoid anonymous `Record<string, unknown>` schema blobs except at generic graph boundaries where a typed union is not feasible.

### JSON-LD Relationships

Use relationships to make the graph coherent:

- `WebPage.isPartOf -> WebSite`
- `WebPage.mainEntity -> primary entity @id` when the page owns a product, service, article, or other primary entity.
- `BreadcrumbList.itemListElement[].item -> absolute URL`
- `CollectionPage.mainEntity -> ItemList @id`
- `ItemList.itemListElement[].item -> listed entity`
- `Service.mainEntityOfPage -> WebPage @id`
- `Service.provider -> Organization @id`
- `BlogPosting.mainEntityOfPage -> WebPage @id`
- `BlogPosting.publisher -> Organization @id`
- `ContactPage.mainEntity -> Organization @id`

Prefer stable `@id` links over copying the full organization or website object into each schema.

### Astro Wiring

Use Astro layouts and page templates based on the existing architecture:

- Put global metadata and base schema in the common head/layout path.
- Keep page-specific schema close to the page or route family only when that page has unique fetched data.
- For collection pages, ensure the template or layout has access to the actual list being rendered.
- For detail pages, ensure the primary entity schema receives the resolved canonical URL and the page `@id`.
- Pass existing `imageAlt` values into the SEO component wherever an image is already passed.

Do not add or replace SEO packages without authorization. When the repo already uses a package, verify its generated output before preserving it. A package is not acceptable merely because it exists in `package.json`; it must emit clean, parseable, project-correct output.

## Audit Checklist

For every built HTML page:

- exactly one canonical link or project-approved equivalent
- title present
- meta description present
- robots present
- `og:title`, `og:description`, `og:type`, `og:url`, `og:image` present where the site has an image fallback
- `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image` present where the site has an image fallback
- JSON-LD scripts parse
- parsed JSON-LD values do not contain HTML entity escapes caused by the renderer

For active indexable pages:

- canonical appears in sitemap
- `WebSite` and the project-appropriate publisher/business entity are present
- non-home pages have `BreadcrumbList`
- collection pages with lists have `CollectionPage` plus `ItemList`
- detail pages relate `WebPage` and the primary entity through `WebPage.mainEntity` or `mainEntityOfPage`
- blog/article pages have `BlogPosting` or `Article` plus article meta tags where values exist
- contact pages have `ContactPage`
- FAQ pages have `FAQPage` only when real questions/answers exist

For noindex pages:

- not present in sitemap
- no contradiction between meta robots and sitemap inclusion

For placeholder or unused pages:

- classify from repository evidence or user instruction
- report if built as `index, follow`
- exclude from readiness score only when explicitly out of scope

## Validation Commands

Adapt to the repository:

- Install dependencies only with user authorization.
- Prefer the lockfile command: `npm ci`, `pnpm install --frozen-lockfile`, or equivalent.
- Run the project's Astro type check if available, such as `npm run astro-check`.
- Run the production build.
- Run the CMS/Studio build when SEO fields or CMS schemas are touched.
- Run or add focused rendered-output tests with the repository's test runner. For Astro/Vite projects with no runner, use Vitest; parse static HTML with Cheerio.
- Run format or diff whitespace checks for changed files.

Always validate generated `dist` HTML after build. Source-code inspection alone is not enough.

## Reporting Format

Report infrastructure readiness separately from content quality:

- `Frontend infra readiness`: pass/fail and percentage only for scoped pages.
- `Evidence`: build results, page counts, sitemap counts, JSON-LD parse results, schema relationship counts.
- `Infra failures`: actionable frontend gaps with page groups and source files.
- `Out-of-scope content/data findings`: long titles, thin descriptions, missing CMS values, weak alt text.
- `Policy findings`: placeholder/draft/noindex/sitemap decisions that need product direction.

Do not claim 100% readiness if any active indexable page has a frontend infra failure. If only content or policy findings remain, say infra is ready and name the remaining non-infra work.
