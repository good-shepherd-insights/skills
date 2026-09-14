---
name: browser-screenshot-qa
description: Visually verify a running local or tunneled website with real browser screenshots before reporting UI, layout, or CSS correctness.
---

# Browser screenshot QA

Use this whenever a visual/UI change is about to be called correct and the page
is reachable by URL. HTTP responses, DOM inspection, and CSS values do not
prove that the browser rendered the intended layout.

## Workflow

1. Use a connected browser if one is available; otherwise use a local
   Playwright/Chromium screenshot tool against the actual local or tunneled
   URL.
2. Capture the smallest useful target: a component selector when reviewing a
   component, a full viewport for layout interaction, and full-page capture
   only when needed.
3. Capture desktop and mobile widths. Also check intermediate desktop/tablet
   widths whenever a grid, clamp, or breakpoint is involved.
4. Open and inspect the resulting images. A successful screenshot command is
   not a visual pass.
5. Record actual findings: overlap, clipping, overflow, missing assets,
   contrast/invisible text, incorrect shape, wrong spacing/proportion, and
   font fallback.
6. After every fix, rebuild/reload and capture again. Do not validate a stale
   bundle or cached screenshot.

## Figma-specific checks

- Verify Figma text from real text nodes or rendered vector assets, never from
  layer names alone.
- Confirm referenced fonts actually load in the rendered page; CSS font-family
  declarations alone do not prove font availability.
- Compare the live component against the relevant Figma node at equivalent
  dimensions. For component extraction, use the per-element verdict table
  required by `figma-component-extraction`.

## Completion standard

Report only what was actually rendered and inspected. If the page was not
reachable, the build was not refreshed, or the screenshot was not viewed, say
that visual QA was not completed.
