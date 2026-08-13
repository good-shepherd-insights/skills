---
name: seo-output-test-contracts
description: Create or audit clean, project-specific automated tests that verify rendered SEO and JSON-LD output from a web app build. Use when Codex is asked to add SEO/JSON-LD tests, split infrastructure readiness from content readiness, verify generated HTML/sitemap/robots/schema output, avoid generic SEO-audit slop, or build regression gates based on a codebase's actual business route rules, CMS fields, and SEO rendering architecture.
---

# SEO Output Test Contracts

## Purpose

Create regression tests that prove a project emits the SEO and structured-data surface it is designed to emit. These tests are not external SEO audits, copy scoring, Rich Results replacement, or generic checklists. They are codebase-specific gates derived from the app's actual route policy, CMS model, rendering layer, and business rules.

## Core Rule

Discover first. Do not hardcode another project's routes, schema types, CMS field names, or indexability policy. Treat the generated production output as the source of truth, then encode the target project's own contract in small test helpers.

## Technology Selection

Use this local test stack:

- Test runner: use the repository's existing test runner. For Vite/Astro projects with no runner, add Vitest.
- Output source: run the production build and read the generated files from the framework's build output directory.
- HTML parser: use `cheerio` for generated static HTML. If the project does not already have `cheerio`, add it.
- Sitemap and robots: read generated files directly. Extract sitemap `<loc>` values with a small local helper and read robots directives as text.
- JSON-LD: parse scripts with `JSON.parse`, then use small graph helpers for `@graph`, `@id`, references, required `@type`, and entity relationships.
- Reports: write simple JSON reports from the test run. Keep infra readiness and content readiness separate.

Do not use browser automation, alternate HTML parsers, crawler suites, Lighthouse, Rich Results Test, schema validator packages, Semrush, Ahrefs, or broad SEO audit packages for this local regression gate.

## Workflow

1. Inventory the project.
   - Read `package.json`, build scripts, lockfile, framework config, route files, layouts/head components, sitemap/robots config, CMS schemas, SEO helpers, and JSON-LD builders.
   - Identify existing test runner and HTML parser dependencies before adding anything.
   - Apply the technology-selection hierarchy above before adding dependencies.

2. Establish the page universe from build output.
   - Run the production build unless the user explicitly asks for research-only work.
   - Enumerate generated HTML files and parse all sitemap files.
   - Classify only routes that belong to the project's SEO contract: active indexable content pages, duplicate canonical entries, noindex flows, admin, API, feed/JSON, preview/draft, utility, or deliberately ignored static output.
   - Do not fail infrastructure just because an unclassified generated file exists. Report unclassified output as "classification review needed" unless the project explicitly treats unclassified pages as blockers.

3. Derive the project contract.
   - Use repository evidence and user-stated policy to define expected route behavior.
   - Examples of contract facts to derive, not copy:
     - Which routes are active indexable pages.
     - Which generated routes are duplicate entry points with canonical targets.
     - Which cart, checkout, account, admin, preview, API, JSON, or utility routes are noindex or robots-disallowed.
     - Which page roles require `WebPage`, `CollectionPage`, `ItemList`, `Product`, `Offer`, `Article`, `FAQPage`, `LocalBusiness`, or other schema types.
     - Which CMS fields are the source of SEO facts.

4. Split tests by responsibility.
   - `infra` test: hard-fail only frontend/CMS plumbing regressions.
   - `content` report/test: show currently emitted data and missing CMS values without failing infra for copywriter-owned gaps.
   - Keep reports separate. Do not mix `infraBlockers: 0` with content warnings in one ambiguous score.

## Recommended Test Architecture

Use a small directory like:

```text
tests/seo/
  lib/
    contracts.ts
    distReader.ts
    extractSeo.ts
    schemaGraph.ts
    contentReport.ts
    infraReport.ts
  seo-infra.test.ts
  seo-content-report.test.ts
```

Adapt names to the codebase. Keep each file single-purpose:

- `contracts.ts`: project route classes, expected schema by page kind, known noindex/duplicate/excluded paths, required source files, required CMS field paths.
- `distReader.ts`: read build output, sitemap files, robots.txt, and generated HTML.
- `extractSeo.ts`: parse one HTML document into normalized SEO data. No assertions.
- `schemaGraph.ts`: small JSON-LD graph lookup and relationship helpers.
- `infraReport.ts`: write explicit infra blocker counts for the current run.
- `contentReport.ts`: write emitted data and CMS-owned gaps with exact page, field, source, owner, and note.
- `seo-infra.test.ts`: hard project contract assertions.
- `seo-content-report.test.ts`: generated data report, not copy quality scoring.

Avoid God files. If a helper starts knowing both route policy and HTML selectors, split it.

## Infra Test Contract

The infra test should fail for:

- Production build output missing or stale relative to the test command.
- Sitemap URL has no generated page.
- Active indexable generated page is absent from sitemap.
- Noindex/utility/admin/API/feed routes are in sitemap.
- A route classified as SEO-relevant lacks the required metadata, sitemap, canonical, robots, or JSON-LD behavior for its class.
- Canonical is missing, duplicated, relative when absolute is required, or mismatched with sitemap/canonical policy.
- Robots tag is missing, duplicated, or contradictory.
- JSON-LD is missing where the project requires it or cannot be parsed with `JSON.parse`.
- Required schema type is missing for the route's project role.
- JSON-LD relationships are broken, e.g. `CollectionPage.mainEntity` does not reference `ItemList`, or detail page `WebPage.mainEntity` does not reference the primary entity.
- SEO rendering bypasses the centralized resolver/layout/package path.
- Page templates stop passing fetched CMS/page facts into the SEO resolver.
- Required CMS fields are not attached at the expected schema paths.

The infra test should not fail for:

- Title or description length.
- Weak copy.
- Missing CMS content when the field exists and the frontend can emit it.
- Missing address, phone, hours, ratings, reviews, SKU, or availability when the business has not provided real data.
- Rich Results eligibility that requires external validation.

## Content Report Contract

The content report should answer: "What SEO/JSON-LD data is emitted now, and which CMS fields need content?"

For each audited page, report:

- URL and project page kind.
- title, meta description, canonical, robots.
- Open Graph and Twitter fields.
- JSON-LD schema types.
- Current gaps as objects:

```ts
{
  field: string;
  source: string;
  owner: 'copywriter' | 'business' | 'engineering' | string;
  note: string;
}
```

Use exact CMS field paths from the target project where possible, e.g. `page.seo.metaImage`, `globalSettings.organization`, or `catalogItem.seo.metaDescription`, not vague labels like "social missing".

## Anti-False-Positive Requirements

Before finishing, audit the tests themselves:

- Confirm the test command runs the production build before reading output.
- Confirm tests read `dist` or the framework's actual production output, not route source only.
- Confirm every SEO-relevant route is classified by project business logic before assertions are applied.
- Confirm unclassified generated output is reported separately and does not masquerade as either ready or broken.
- Confirm reports are reset or overwritten per run so stale sections cannot survive.
- Confirm CMS schema assertions inspect real schema objects or exact file paths, not broad source substrings.
- Confirm source-plumbing assertions are backed by rendered-output assertions or behavior tests, not comments/dead code.
- Confirm intentionally content-owned gaps are not counted as infra failures.
- Confirm failure messages include exact URL/file and failed condition.

## Behavior Fixtures

When source-string checks are unavoidable, add behavior tests instead:

- Call the SEO resolver or metadata builder with synthetic complete CMS data.
- Assert optional CMS-backed fields appear in normalized metadata and JSON-LD.
- Call it again with empty optional fields.
- Assert absent facts are omitted rather than fabricated.

This is better than checking whether a field name appears somewhere in source.

## External Tools

Do not add external SEO tools in this skill. This skill creates local regression gates only. Google Rich Results Test, Search Console, schema validators, Lighthouse, Semrush, Ahrefs, and deployed crawlers are separate validation work.

## Reporting

Report results in separate sections:

- `Infra readiness`: pass/fail and explicit `infraBlockers` count.
- `Evidence`: build status, sitemap URL count, built HTML count, noindex count, JSON-LD parse count.
- `Infra blockers`: exact URL/file/condition list.
- `Content/data gaps`: exact CMS field paths and owners.
- `Known limits`: external validators not run, content not populated, project-wide unrelated type/test issues.

Do not claim readiness if any active page has an infra blocker. If only content gaps remain, say infra is ready and content is pending.
