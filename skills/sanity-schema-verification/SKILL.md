---
name: sanity-schema-verification
description: System-design and verification discipline for Sanity Studio schema work in any codebase — designing or restructuring document/object types, splitting or grouping fields, renaming or removing a type or field, writing or running a Sanity dataset migration script, or claiming a Sanity-related change is done, tested, safe to ship, or production-ready. Also applies before describing Sanity Studio's editorial UX (titles, grouping, document structure) as reviewed. Trigger even without the words "Sanity" or "schema" explicitly paired with "skill" — e.g. "clean up this schema," "add a new section type," "split this document type," "migrate this field," "is this safe to deploy," "review the CMS structure." Exists because mechanical checks (typecheck, lint, schema validate, a dry run that merely didn't throw) are routinely mistaken for proof of correctness in Sanity work and routinely aren't — the underlying document structure or a migration's actual output still needs a real look.
---

# Sanity schema verification

Sanity schema work fails in a specific, recurring shape across projects:
mechanical checks (`tsc`, lint, `sanity schema validate`, a dry run that
merely didn't throw) all pass, get reported as "done" or "production ready,"
and something real is still broken — a document type ships with wrong data,
a build breaks because a query still points at a document that moved, or an
editor opens Studio to find a giant unstructured form nobody actually
looked at. Each step below closes one specific gap in that pattern. Do the
step itself — don't substitute a broader mechanical check for the specific
thing it asks for, and don't guess at schema structure from generic Sanity
knowledge when the project already has an established, inspectable
convention of its own.

## 1. Structure content, sections, and config as a deliberate design — don't default to one flat document

A Sanity document type that accumulates many unrelated fields over time is
the single most common way this goes wrong: it's easy to add "just one more
field" to an existing document, and the result is a mega-document with no
internal structure that's unusable to edit. Treat schema layout as a design
decision, not a byproduct of wherever a field was easiest to add.

- **One document per independent concern, not one document holding many.**
  If a "concern" (a reusable page section, a config domain like SEO
  defaults or navigation) can be edited, published, or reasoned about
  independently of the others, it should be its own document type — not a
  field on a shared document. A helper factory that generates a document
  type from a name/title/content-type triplet is a good way to keep this
  cheap once there are several similar ones.
  *Example: a project's `Site Globals` document had ten unrelated
  sub-objects — brand, contact, header, footer, SEO defaults, indexing,
  forms, UI copy, app manifest, organization — crammed into one document
  with no internal grouping. The fix was ten separate singleton document
  types, one per concern, not one document with ten fields.*
- **Separate content from configuration at the structural level, not just by
  field naming.** If the project's desk/structure customization supports
  named groups or sections in its navigation, use that to keep editorial
  content (page sections, reusable blocks) visually and organizationally
  apart from site configuration (SEO, forms, navigation, branding). Decide
  the group by what a document actually is, not convenience.
- **Enforce singletons at the structural layer the project actually uses to
  enforce them, not only in the type registry.** Adding a document type to
  the schema's type list makes it exist; it does not make it a singleton.
  If the project has a mechanism for singleton enforcement (a filtered
  document-actions list, a filtered creation-template list, a custom desk
  structure entry with a fixed document ID), a new singleton type has to be
  registered wherever *that* mechanism reads its list — find that
  mechanism and register there, don't assume adding the type is sufficient.
- **Match the project's existing title-casing and naming convention,
  consistently — verify it, don't guess it.** Read several existing
  `title:` values (or your schema system's equivalent editor-facing label)
  before adding a new one, and match them exactly, including how they
  handle acronyms. Don't assume Title Case, sentence case, or any other
  convention without checking — but once the project's convention is
  established, follow it for every new type, not just the ones directly
  requested.
  *Example: a project's convention turned out to be Title Case
  (`"Global Button"`, `"SEO Defaults"`) with acronyms preserved uppercase
  (SEO, FAQ, CTA, UI). Two prior schema-review passes missed that ~90
  existing titles violated it, because nobody actually read the rendered
  title list — see step 5.*
- **Name things for what they are; only add a disambiguating suffix or
  wrapper on an actual, verified name collision.** Check whether the plain
  name is already taken by grepping/searching the schema before reaching
  for a prefix or suffix — most fields don't need one. Reserve
  disambiguation for the specific case where the same underlying object
  type is legitimately reused under two different roles.
- **Reuse existing object/field type definitions instead of duplicating
  their shape under a new name.** Before defining a new object type, search
  the project's shared/common schema definitions for one that already
  matches the shape needed (a social link, an image-with-alt-text, a button
  — these repeat across almost every schema). Duplicated shapes are exactly
  what makes a schema hard to maintain as it grows.
- **Group fields once a document or object holds more than a handful of
  unrelated ones.** Most schema systems support tabs/groups at the document
  level and sub-groupings (fieldsets) within a single field — use them. A
  flat, ungrouped field list past roughly five or six fields is what
  "unstructured mega-document" means in practice — group it as part of
  designing it, not after an editor complains.

If a structural question comes up with no existing precedent in the
project's own schema, say so and ask, or research the project's schema
system's own documented mechanism for it — don't default to generic
knowledge of the underlying platform, and don't invent a new pattern when
asking would settle it.

## 2. Find every consumer from the actual project root, not from the folder that "usually" has them

Before renaming, removing, splitting, or merging any document type or
field, find every place that reads it — queries by type/ID, interfaces or
types mirroring its shape, hardcoded references in build or deploy
scripts.

Run the search from the project root, across the whole tree (excluding
build output and dependency directories), not from whichever source
directory happens to hold most of the application code:

```bash
grep -rln "theFieldOrTypeName" . \
  --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=.git
```

The reason this is spelled out rather than left implicit: a consumer
search correctly run project-wide the first time can get silently narrowed
to just the main source directory the *next* time, by analogy to the first
search rather than by re-deriving the right scope each time. Build-time or
deploy-time scripts living outside the main application source directory
are an easy, costly miss — they don't show up in an editor's "find
references," they're not exercised by a dev server, and they can hardcode
a query against exactly the document being restructured.
*Example: a project's build pipeline had two scripts at the repository
root, outside its main source directory, each with a hardcoded query
against a document that was about to be split into several — a search
scoped to the source directory alone missed both. One broke the deploy
outright; the other would have failed silently.*

Also check whatever files register the schema's type list and any
custom desk/structure/singleton configuration — a restructure not
reflected there breaks the schema tool's own UI, not just downstream
consumers.

## 3. For any migration script, verify the dry-run output field-by-field against real data

A migration script should support a dry-run mode that prints the exact
operations it would perform without committing them — follow whatever
convention the project's existing migration scripts already use. Running
dry-run and confirming it exits without error is not verification — it
only proves the script doesn't crash, not that it does the right thing.
Print the full output and read it: check every changed document's ID,
type, and field values against what's actually expected, for at least one
representative document per kind of operation the script performs.

Three bug patterns are specific to Sanity's own query language and client
library, apply regardless of project, and have each caused real, silent
data corruption caught only by reading dry-run output against live data —
never by reasoning about the code:

- **GROQ `null` vs JS `undefined`.** GROQ returns `null` for an unset
  field, never `undefined`. A presence check written as
  `value !== undefined` always matches, even on fields that are actually
  empty. Use explicit `defined()` projections in the query itself, or
  check `!== null` in JS, not `!== undefined`.
- **The Sanity client patch builder's `.unset(paths)` replaces its
  internal path list on every call rather than merging across calls on
  the same patch.** A loop calling `.set()`/`.unset()` once per item, on a
  shared patch, keeps only the last item's unset paths and silently drops
  the rest. Accumulate every `set`/`unset` entry across the whole loop
  first, then call `.set()`/`.unset()` exactly once each on the
  fully-built patch.
- **Object spread order when constructing a new document from an old
  one.** `{...oldValue, _id: id, _type: type}` is not the same as
  `{_id: id, _type: type, ...oldValue}` — if `oldValue` already carries
  its own `_type` (Sanity annotates typed object fields with `_type` on
  write) and the spread comes *after* the explicit `_type:`, the old
  value silently wins and the new document gets the wrong type. Put the
  spread first, explicit `_id`/`_type` last, so stray keys already in the
  source data can't overwrite them.

Take a real data backup (the project's dataset export mechanism, or
equivalent) before running any migration for real, and confirm
idempotence by re-running dry-run after the real run and expecting a
no-op result.

## 4. Run the project's actual build/deploy command before calling anything deploy-safe

Identify the exact command the deploy platform runs (read it from the
project's own build/deploy configuration, don't assume) and run that
command directly before calling a schema or content change deploy-safe.
A dev-server spot-check hitting a few pages is not equivalent — build or
deploy scripts that run independently of the interactive dev server (data
export/transform steps, static generation post-processing) can hold their
own hardcoded queries against exactly the content that just changed, and
a dev server won't exercise them.
*Example: a project's real deploy command chained a pre-build data-fetch
script, the framework's own build step, and a post-build cleanup script —
the first and third both queried Sanity directly and independently of the
main build. A change that looked fine against the dev server broke the
live deploy because neither side script was ever run.*

Before telling anyone a Sanity-related change is deploy-safe, run the
real command end to end, from a clean state if there's any doubt, and
confirm it completes fully — not just that the main framework build step
succeeds.

## 5. Editorial/Studio-quality claims need a real look at the tool, not just schema source

"Is this schema clean / well-organized / good editorial UX" cannot be
answered by reading schema source files and confirming they typecheck or
pass schema validation. Source review catches structural facts (a field
exists, a type is registered) but not what an editor actually sees: how
titles render, whether groups/fieldsets actually produce usable tabs,
whether a document reads as one long undifferentiated scroll.

If real interactive verification of the schema tool's UI is possible, do
it — start it, open it, and look at the actual navigation and document
forms, not just the source that generates them. If that isn't possible in
the current session (an auth flow can't be completed non-interactively,
no display available), say so explicitly: state that the review was
source-only, name that as a limitation, and don't describe it as if it
were a full editorial review. Don't let a passing mechanical check quietly
stand in for the visual confirmation that was actually asked for.
*Example: two schema-review passes on the same project both read schema
source and reported it clean; both missed that nearly every document
title violated the project's own casing convention and that two documents
were completely unstructured mega-documents — found only when someone
actually opened the tool and looked.*

## Before reporting anything "done"

Don't say "done," "production ready," "verified," or similar for a Sanity
schema/content change unless the applicable steps above were actually
performed for that specific change — not merely available, not "should be
fine because the typecheck passed." If a step doesn't apply (no migration
script involved, for instance), say so rather than skipping it silently.
