---
name: price-update
description: Update a product catalog price and every dependent package or quantity modifier atomically, with source-of-truth and storefront verification. Use when changing cupcake or other Sanity-backed product pricing so base prices, checkout totals, and displayed prices are updated correctly in one pass.
---

# Price Update

Perform a complete price update in one controlled pass. Never change a base price and stop before recalculating dependent modifiers.

## Workflow

1. **Resolve the authoritative record.** Inspect the repository schema and query layer first. For this project, product base prices live in Sanity `product.price`; the Cupcakes record is `product-chocolate-cupcake` with slug `cupcakes`. Do not edit UI literals when the UI already reads from Sanity.

2. **Read before writing.** Fetch the complete target document and record its `_id`, `_rev`, current base price, every customization group, and every price-bearing option. Abort if the record, price, quantity group, or expected labels are missing or ambiguous.

3. **Derive dependent values before mutating.** For the Cupcakes quantity group, the Snipcart contract is `selected total = base price + priceModifier`. Quantity options represent per-cupcake pricing, so calculate:

   `package total = new base price × cupcake count`

   `priceModifier = package total − new base price`

   Interpret `1/2 Dozen` as 6, `1 Dozen` as 12, and `N Dozen` as `N × 12`. For a new base of `$3.75`, the modifiers are `18.75`, `41.25`, `86.25`, `131.25`, and `176.25` for 1/2, 1, 2, 3, and 4 dozen. Do not reuse old modifiers after changing the base price. For any other product, determine the modifier contract from the schema and existing checkout code; never guess whether a stored value is a total or an increment.

4. **Validate the complete update in memory.** Assert the requested base price is finite and has at most two decimals. Assert every dependent package total and modifier is exact to cents. Preserve names, slugs, images, options, and unrelated products. Abort on any unexpected current value rather than overwriting blindly.

5. **Write the CMS record once.** Use the authenticated Sanity workflow available in the repository (`npx sanity documents get` → create a complete edited document → `npx sanity documents create ... --replace`) or an authenticated transaction. Never use the public project ID alone as write authorization. Keep the original document as a recovery copy and verify the target `_id` before replacing it.

6. **Read back and verify the remote record.** Fetch the document again and assert the new base price, every modifier, and every computed package total. Print the final values. If any assertion fails, stop and report the partial-state risk; do not claim completion.

7. **Audit all consumers.** Confirm the existing code paths still derive prices from Sanity: homepage cards, `/products`, product detail/variant routes, `/api/product-options`, and `/snipcart-products.json` where applicable. Search for duplicate hardcoded prices and inspect the Snipcart builder and cart recalculation formula. The expected formula is base plus the selected modifier, then line total multiplied by cart quantity.

8. **Verify the repository change separately.** If a repository verification guide contains current expected prices, update only those expectations and run `git diff --check`. Do not add fallback price literals or unrelated refactors. If a PR is requested, report the CMS mutation separately from the committed repository diff.

## Failure guards

- Never change only `product.price` when the product has price-bearing quantity/package options.
- Never infer package totals from labels without checking the product's established pricing contract.
- Never replace a Sanity document unless the fetched `_id` and all expected preconditions match.
- Never claim checkout correctness from a source edit alone; verify the generated/API paths and computed totals.
- If the requested price is ambiguous (per item vs package total), stop and ask before writing.
