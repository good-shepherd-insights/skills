---
name: serp-content-rank-audit
description: This skill decomposes a SERP's ranking pages into per-page content + structure, then synthesizes a gap analysis and prioritized playbook against the user's own competing page. Use it whenever the user wants to understand what content, E-E-A-T, or structural signals the SERP rewards, where their page is strong/weak/unique, and what to ship next. Triggers on phrases like "rank [query] for [project]", "competitive analysis of [query]", "why aren't we ranking for [query]", "gap analysis on the SERP", "match the SERP", "what does our page need to cover". Scale-agnostic — works on any commercial or informational query, any number of ranking URLs, any project type.
metadata:
  type: workflow
---

# SERP vs. project differences

3 inputs. 4 decoupled steps. Each step produces a useful artifact on its own. Subagents are optional and recommended only at scale (10+ URLs).

## Inputs (3, all from the user)

| # | Input | What it is |
|---|---|---|
| 1 | SERP query string | The exact query the user wants to rank for |
| 2 | Ranking URLs list | 1–15 URLs at their actual SERP positions; mark captcha-blocked as "skip" |
| 3 | Project source path(s) | Path(s) to the user's own page(s) that target the query |

Do not proceed without all 3.

## Output structure (always)

```
ranking/<query-slug>/
  <rank>/
    content.md
    structure.md
  analysis-<page-type>.md
  differences.md
  strategy.md
```

`<query-slug>` = lowercase, hyphens for spaces, no special chars.

## Dependency graph

```
INPUTS (3) → STEP 1 → STEP 2 → STEP 3 → STEP 4
```

Each step is decoupled — you can stop after any one and still have a useful artifact.

---

## Step 1 — Capture (per URL)

**Inputs:** input 1, input 2.
**Output:** for each URL, two files in `ranking/<query-slug>/<rank>/`:
- `content.md` — full extracted body. URL, content type, schema types, word count, OG, robots, canonical at the top. Then headings. Then full prose. **No summarizing.**
- `structure.md` — ASCII component tree of the page (header, nav, hero, every section, forms, footer).

**Guardrails:**
- Captcha-blocked URL → placeholder content.md + structure.md documenting the blocker. Do not skip the directory entry.
- "Full prose" = every paragraph, not a curated subset.
- Capture the meta block (title, description, OG, robots, canonical) at the top of content.md.
- If the page has heavy duplicated nav chrome, deduplicate inside the file but keep one reference copy.

---

## Step 2 — Analyze per page type (4 buckets)

**Inputs:** Step 1 outputs + input 3.
**Output:** 4 analysis files in `ranking/<query-slug>/`:
- `analysis-service-pages.md`
- `analysis-directories.md`
- `analysis-blogs.md`
- `analysis-ugc.md`

For each URL in a bucket, extract 9 dimensions:

1. URL, page type, schema types, word count, OG, robots, canonical
2. Heading structure (H1, H2, H3)
3. Service coverage (12 standard topics: GBP, citation, reviews, on-page, link building, content, technical SEO, analytics, AI/AEO/GEO, named tools, FAQ, case studies)
4. E-E-A-T sub-signals — Experience (years, named case studies with metrics, named team, testimonials) / Expertise (named tools, certifications, methodology, technical vocabulary) / Authoritativeness (schema count, reviews, awards, third-party mentions) / Trustworthiness (full NAP, pricing, refund/backup/migration policies, sources cited)
5. Local entity signals (cities, counties, neighborhoods, sub-pages, government/agency links)
6. Conversion elements (forms, free-audit offer, CTA count, named lead magnet)
7. FAQ count + topics
8. Internal-link density (approx count + external state resources)
9. Forward-looking content (AI / AEO / GEO / voice search / named AI tools)

End each analysis file with:
- Comparison table across the bucket on the 9 dimensions
- Per-page-type median pattern (1 paragraph)
- Per-page-type best-in-class competitor (1 paragraph)
- Bulleted list: "elements present in median but missing from the project" (cite the competitor)
- Bulleted list: "adopt vs ignore" with rationale

**Guardrails:**
- Exact numbers, exact schema types, exact city/county/practitioner names. Never "many", "some", "various".
- Cite the project source file path when describing a gap.
- Each bucket stays independent — no cross-bucket analysis in this step.
- Cap each analysis file at 3,000–5,000 words. Tables over prose where the data is tabular.

---

## Step 3 — Synthesize (`differences.md`)

**Inputs:** Step 1 outputs + Step 2 outputs + input 3.
**Output:** one file at `ranking/<query-slug>/differences.md`.

11 sections, in this order:

1. Executive summary (1 paragraph)
2. Method (1 paragraph naming the analysis files)
3. Competitor set table (all URLs: rank, domain, page type, word count, schema)
4. Master comparison table — project vs. all competitors, 22+ dimensions × 16 columns, grouped by Schema / E-E-A-T (4 pillars) / Conversion / Local entity / Forward-looking / Internal links / Aggregate quality
5. E-E-A-T sub-signal comparison (4 pillars × project vs. median vs. best-in-class)
6. Content coverage matrix (12 service topics × project coverage vs. competitor coverage)
7. Similarities (5–10 bullets: what the project already does that matches the median)
8. Differences — gaps (12 categorized gaps, each citing the competitor demonstrating the missing pattern)
9. Where the project beats the competitors (5–10 patterns no competitor can easily fake)
10. Five highest-leverage moves, ranked by impact (action, where, why, effort, tie-back to memory rules)
11. Strategic insight (1–2 paragraphs)

**Guardrails:**
- Every comparison cell uses exact numbers, exact schema types, exact names.
- Each gap must cite a specific competitor demonstrating the pattern.
- No "many" / "some" / "various" — name the number, the tool, the city, the practitioner.
- Strip all subagent-acknowledgement notes (the file is end-user facing).
- Total: 3,000–5,000 words.

---

## Step 4 — Strategize (`strategy.md`)

**Inputs:** Step 3 output + Step 2 outputs + input 3 + any project memory rules.
**Output:** one file at `ranking/<query-slug>/strategy.md`.

7 sections:

1. TL;DR (1 sentence)
2. What the page needs to cover — 2 matrices (service topics + structural layer)
3. What it's missing — categorized table of gaps
4. Where it's unique — table of advantages no competitor has
5. The best angle — one-sentence thesis + 4-bucket competitor analysis + non-negotiable rules
6. Prioritized action plan — single table with # / Action / Where / Impact / Effort / Priority
7. The 4 new page surfaces to create + the 2 non-negotiables

**Guardrails:**
- Action-ready, not analytical. Every "Action" names a file, a section, or a content block.
- "Impact" and "Effort" must be estimated (Low/Med/High or hours/days).
- Non-negotiable rules in §5 and §7 must be derived from project memory — never invent constraints the user did not surface.
- No vendor-marketing prose. Tables over paragraphs.
- Total: 2,000–4,000 words.

---

## Subagents — optional, recommended at 10+ URLs

| Subagent | Bucket | Reads | Writes |
|---|---|---|---|
| 1 | service-page competitors | their `content.md` + `structure.md` + project source | `analysis-service-pages.md` |
| 2 | directory competitors | their `content.md` + `structure.md` + project source | `analysis-directories.md` |
| 3 | blog-post competitors | their `content.md` + `structure.md` + project source | `analysis-blogs.md` |
| 4 | UGC + skipped | their `content.md` + `structure.md` + project source | `analysis-ugc.md` |
| 5 | synthesis | all 4 analysis files + project source | `differences.md` |

**Rules:**
- Subagents 1–4 run in parallel.
- Subagent 5 starts after all 4 finish.
- If a subagent cannot write files (some runtimes disable that), the parent agent writes the file from the subagent's handback text.
- Each subagent receives the same framework (the 9 dimensions + the file structure) and the same bucket of URLs.

For 5–9 URLs, do the analysis serially in one agent. For 1–4 URLs, do the analysis inline without subagents.

---

## Memory rules to capture

**Before the run** — add to `MEMORY.md` as one-line pointers:
- Project positioning facts (e.g. "is a GTM platform, not an agency")
- Hard constraints the user has surfaced (e.g. "no since-year-anchors in copy", "no agency-naming recommendations")

**During the run** — record any new feedback the user surfaces (use full project name, no abbreviation; no em-dashes; etc.) as a one-line pointer immediately, not at the end.

**After the run** — add:
- Any feedback rules that emerged
- New project facts learned

---

## Improvement hooks

After each run, check for:
- Steps that always take >2× expected time → add a guardrail or pre-flight check
- Output files the user never reads → drop them or merge them
- Dimensions in the analysis that are always "n/a" → remove them
- Sections in `differences.md` the user always skips → move to appendix or remove
- Sections in `strategy.md` the user always rewrites → add as boilerplate with project-specific blanks
