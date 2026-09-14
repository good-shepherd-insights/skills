---
name: figma-design-to-code
description: Implement a Figma node as production code. Use before retrieving Figma design context or building a Figma-derived UI.
---

# Figma design to code

Use this skill for the read-from-Figma direction: inspect a supplied Figma node,
then adapt it to the real project. It does not authorize writing to Figma.

## Required sequence

1. Require a node-specific Figma URL. Do not guess a node ID from a file URL.
2. Call `get_design_context` for that node before writing implementation code.
3. Treat returned code as reference material, not code to paste unchanged.
4. Inspect the target repository for existing components, tokens, styles, CMS
   contracts, and framework conventions before creating equivalents.
5. Apply Code Connect mappings, component documentation, design annotations,
   existing tokens, and then raw geometry in that order of authority.

## Assets and content

- Use Figma-exported image/icon assets or a real CMS media field. Do not redraw
  an icon, invent an SVG, or substitute a placeholder.
- Do not trust layer names as user-facing copy. A layer can be outlined text or
  stale metadata; inspect the asset or text node itself.
- Preserve a dynamic-content boundary: editable copy, images, links, and
  accessibility labels belong in the CMS contract, not hardcoded in a renderer.

## Handoff to the component workflow

For a Good Shepherd Insights Payload/Astro/React component, immediately follow
this skill with `figma-component-extraction`. It owns measured responsive
implementation, component schema alignment, semantic HTML, and visual QA.
