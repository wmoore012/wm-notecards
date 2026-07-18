# Release contract

Before calling a notecard notebook complete:

## Evidence

- Recompute visible values from the source objects.
- Verify units, denominator, sign, aggregation, split, baseline, and metric direction.
- State what is descriptive, in-sample, holdout, predictive, or causal.
- Treat surprising random/model winners as implementation-audit triggers.

## Visuals

- Reject category-label collisions; use top-N, horizontal bars, or facets.
- Keep semantic color stable and add labels, shapes, or line styles.
- Never let chips or callouts overlap prose.
- Give long tables two-axis scrolling and sticky headers.
- Keep neutral table zebra bands visible and below semantic fills in the attention
  hierarchy.
- Keep label columns left-aligned and numeric/date columns right-aligned.
- Verify that title, evidence, annotation, and metadata form an intentional
  preattentive reading order.
- Test typography, spacing, contrast, keyboard scrolling, and reduced motion.

## Proof

- Restart/run all.
- Observe desktop and narrow widths.
- Observe empty/error/long-content states.
- Verify SVG and 3× PNG when sharing is supported.
- Add a regression test for fixed bugs.
- Scan notebooks, exports, metadata, and embedded files for secrets and private paths.

Use the repository's `docs/OPEN_SOURCE_GRAPH_CHECKLIST.md` as the authoritative full
gate when it is available.
