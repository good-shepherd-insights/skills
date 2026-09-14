---
name: figma-component-extraction
description: Build or repair a Payload/Astro/React component from Figma using verified content, measured responsive geometry, aligned Payload schema, and mandatory visual QA.
---

# Figma component extraction

Use after `figma-design-to-code` has retrieved the target node's design
context. Load `browser-screenshot-qa` with this skill. A Figma-derived
component is not complete without rebuilt-browser visual verification.

## 1. Establish ground truth

- Inspect the target node's real structure, reference-frame width, child
  geometry, fills, typography, and assets. Record the node IDs used.
- Inspect the containing page for a real mobile frame before inventing a mobile
  layout. If it exists, it is ground truth, not a suggestion.
- Verify apparent text. Outlined/vector text and layer names are not reliable
  content sources; render or inspect the actual asset.

## 2. Build from measured intent

- Use flex/grid with measured padding and gaps for normal layout. Use absolute
  positioning only for actual overlap.
- Express scalable dimensions from the reference-frame ratio. Preserve shapes
  with `aspect-ratio` and one controlled dimension; do not independently scale
  both dimensions.
- Measure each non-uniform gap. Do not normalize design-specific spacing into
  one generic value.
- Test intermediate widths as well as desktop and mobile. Clamp floors and
  grid tracks must not cause horizontal overflow between breakpoints.

## 3. Align the CMS contract

- Create one CMS field for every real editable content fact in the design, and
  no invented placeholder fields.
- Keep the TypeScript section shape, Payload block schema, guard, and renderer
  aligned. Use localized fields for editor-facing translatable copy.
- Before schema changes with nested arrays, check generated PostgreSQL
  identifier length and review the migration against the actual database
  schema.
- Use semantic HTML: lists are lists, icon-only controls have labels, and
  decorative graphics are hidden from assistive technology.

## 4. Mandatory QA

1. Rebuild the package and reload the consuming site.
2. Capture the live component at the Figma desktop reference width and at a
   mobile width. Capture the corresponding Figma node/frame.
3. Inventory every distinct element in the Figma component. Compare each built
   element and Figma element as an isolated crop.
4. Report a table: element, Figma node ID, pass/fail, and a specific note.
   Missing elements, wrong shape category, materially wrong proportions, and
   layout-changing spacing differences are failures.
5. Check mobile for overlap, clipping, invisible text, and horizontal
   overflow. Repeat the full comparison for a supplied mobile reference frame.
6. Have an independent reviewer repeat the element comparison and source audit
   before declaring the component complete. Fix every failure and rerun QA.

Use `browser-screenshot-qa` for actual rendered-browser captures; source or
CSS inspection alone is not visual verification.
