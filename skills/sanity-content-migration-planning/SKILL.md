---
name: sanity-content-migration-planning
description: Plan tightly scoped Sanity/CMS content migrations before implementation. Use when migrating hardcoded or file-backed page/section content into Sanity, deciding which fields are eligible content versus app/global config, auditing reusable components such as CTAs, or preparing a no-regression migration plan for Astro/Sanity sites where scope discipline matters.
---

# Sanity Content Migration Planning

## Purpose

Create a migration plan that is explicit about what content moves into Sanity, what stays in code, and what validation proves the migration is complete. Keep scope narrow and evidence-based.

## Core Rules

- Treat the user-named route, collection, or component as the hard boundary.
- Do not include global header, footer, site config, i18n, routing, app settings, design tokens, analytics, or unrelated SEO systems unless the user explicitly includes them.
- Separate reusable content from route-owned content. For example, a CTA reused across the site belongs in a reusable component schema, not under a services-only schema.
- Move only editor-owned content or content configuration into Sanity. Keep rendering behavior, layout mechanics, component styling, fetch utilities, and computed metadata in code.
- Prefer adapting existing components to accept Sanity content props over creating duplicate components.
- Do not plan migration scripts or one-off data tooling unless needed for a repeatable or large migration.
- Keep the app build boundary clean. Do not make or preserve default build steps that install, build, or deploy unrelated subprojects such as Studio unless the scoped route requires them.

## Planning Workflow

1. Establish the boundary.
   - Quote the exact user scope, such as `services/` only.
   - List explicit exclusions.
   - Identify whether reusable components appear inside the scoped route but are used elsewhere.
   - Identify whether the default build/deploy path includes unrelated systems such as Studio, docs, dashboards, or workers; mark them required or out of scope.

2. Inventory current sources.
   - Find route files, section components, local markdown/content files, Sanity schemas, Sanity query helpers, existing Studio documents, package scripts, deploy config, and CI workflows.
   - Use repository evidence, not assumptions.
   - Mark each item as `migrate`, `adapt`, `delete`, `keep`, or `out of scope`.

3. Build the dependency map.
   - Create a dependency entry for each in-scope content source or rendered section.
   - Use stable IDs such as `D001`, `D002`, and `D003` so implementation and review can refer to exact dependencies.
   - Record current source, consuming routes/components, dependency type, current fields, migration target, frontend change required, and tracking checklist.
   - Required file artifact: for any migration that may be implemented, write the dependency map and plan to an actual repository file at `.context/<scope>-sanity-dependency-migration.md`. Do not rely on an inline chat-only map for implementation-track work.
   - Inline maps are only acceptable for read-only planning answers where no implementation is expected. If the user asks to plan work they intend to do next, create or update the `.context/...md` file before presenting the final plan.
   - Use the dependency map as the deletion guard: do not delete a local content file or fallback until every consumer has been moved, intentionally kept, or marked out of scope.

   Dependency entry template:

   ```markdown
   ### D001: Human-readable dependency name

   - Current source: `path/or/query/export`
   - Used by: `route-or-component`
   - Current dependency type: local markdown | hardcoded TypeScript | Sanity document | reusable component | disabled local section
   - Current fields:
     - `fieldName`
   - Migration target:
     - Sanity document/object/reusable schema, or keep/delete decision.
   - Frontend change required:
     - Query, route, component prop, or deletion work needed.
   - Tracking:
     - [ ] Add or reuse Sanity schema.
     - [ ] Create/populate Sanity data.
     - [ ] Add/update query and types.
     - [ ] Refactor consumers.
     - [ ] Verify rendered output uses Sanity data and no hidden legacy dependency remains.
   ```

4. Classify eligible Sanity data.
   - Page copy: titles, badges, excerpts, FAQs, process steps, stats text, buttons, image references, alt text.
   - Section config editors can reasonably control: enable flags, list limits, simple layout choices already supported by the component.
   - Reusable content: shared CTA text, button labels, CTA images, reusable social proof blocks.
   - Media: classify every visual/media dependency as a Sanity image asset, Sanity file asset, or external media reference managed by Sanity metadata.
   - Not eligible by default: header/footer nav, language config, global site settings, CSS classes, component implementation details, derived canonical URLs, generated schema IDs.

5. Design the schema.
   - Put route-owned sections in a route document, such as `serviceIndex`.
   - Put cross-site modules in reusable component schemas, such as `reusableComponents.ctaSection`.
   - Reuse shared object types where possible, such as button and image-with-alt objects.
   - Make required fields match frontend assumptions. Avoid optional fallbacks that hide missing Sanity data after migration.
   - Record which existing reusable schemas/components are reused and which tempting new abstractions are intentionally avoided.

6. Design frontend wiring.
   - Add Sanity query functions returning typed data for the scoped route.
   - Let existing components accept `content` props and only read legacy fallback content when no Sanity prop is provided.
   - Remove scoped route imports of local content once Sanity content exists.
   - For reusable components, make the component default to reusable Sanity data while still accepting explicit route-specific content props.
   - Search for hidden local content reads that still execute when Sanity props are present; treat those as migration leaks.

7. Data completion checklist.
   - Confirm each required Sanity singleton/document exists.
   - Confirm required arrays are populated.
   - Confirm image fields include asset references and alt text.
   - Confirm external media references include the provider/id/url fields the frontend renders, plus any Sanity-managed poster image.
   - Confirm object `_type` values match schemas for embedded reusable objects.
   - Confirm no deleted local content source remains wired in.
   - Run a concrete GROQ verification query and record the expected counts, required booleans, missing asset counts, and reusable component presence.

8. Regression plan.
   - Inspect `package.json`, deploy config, and CI workflows so checks match the real production/PR build path.
   - Run `npm ci --dry-run`, the project build, and the type/check command when available.
   - Run the Studio build only if Studio is part of the intended deliverable or the user explicitly asks for Studio verification.
   - Run type/check commands, but distinguish new migration errors from pre-existing unrelated diagnostics.
   - Search for deleted local content identifiers and old fallback keys.
   - Inspect generated output or browser output to prove migrated content is actually sourced from Sanity, especially image CDN URLs, external media embeds, and absolute-positioned CTA art.
   - If a build script performs unrelated work, simplify or flag it before claiming the migration is regression-safe.

## Dependency Map Usage

Use the dependency map to drive implementation and review:

- A migration plan intended for implementation is incomplete until the `.context/<scope>-sanity-dependency-migration.md` file exists and contains the current dependency map.
- Before implementation, every in-scope content dependency must have an entry.
- During implementation, update each tracking checklist as work lands.
- Before saying the migration is complete, every dependency entry must be closed with either verified migration, verified deletion, verified intentional keep, or explicit out-of-scope status.
- If a dependency is reused outside the scoped route, split it into route-owned and reusable-component work instead of burying it under the route schema.
- If a dependency is disabled local content, decide whether to delete it from the scoped route or model it as disabled Sanity content; do not leave an unused local import as a hidden dependency.

## Output Format

Use this structure for plans:

```markdown
**Scope**
- In: ...
- Out: ...

**Inventory**
- `path`: migrate/adapt/delete/keep/out of scope - reason

**Dependency Map**
- `D001`: current source, consumers, fields, target, frontend work, tracking checklist

**Sanity Model**
- Documents/objects to add or reuse
- Required fields
- Reusable component placement

**Frontend Wiring**
- Query/helper changes
- Route changes
- Component prop/default behavior

**Data Requirements**
- Required existing or new Sanity documents
- Required image assets, file assets, and external media references
- Required verification query/counts

**Verification**
- Build/check/search commands matched to the real PR/deploy path
- Rendered-output evidence that Sanity data is used
- Known acceptable pre-existing failures, if verified

**Completion Criteria**
- Conditions that must all be true before saying migration is complete
```

## Completion Criteria

Do not call the migration complete until all are true:

- Every in-scope hardcoded or file-backed content source has been replaced, adapted, or intentionally kept with a stated reason.
- Every eligible in-scope content value has a Sanity field and populated Sanity data.
- Every migrated image/file/external media dependency is classified, populated, and verified in rendered output.
- Reusable components discovered in scope are modeled under reusable schemas when used outside the route.
- The scoped route builds from Sanity data without legacy local content dependencies.
- The default PR/deploy build path only performs work required for the scoped app, or unrelated work is explicitly justified.
- Regression checks pass, or remaining failures are verified as unrelated and named precisely.
