# Visual evidence router

Choose evidence from the reader's comparison, not from a favorite chart type. A
notebook is a sequential reasoning surface and a slide is a self-contained reading
surface. Neither is a dashboard grid.

## Evidence families

| Reader's question | Default evidence | Required boundary |
|---|---|---|
| What is the exact value? | table or scorecard | preserve units and denominator |
| What shape does one numeric field have? | micro-profile; histogram or ECDF when bins or tails matter | show sample size and missingness |
| Which categories are most common? | sorted horizontal bars | show count and share; use top-N + Other when crowded |
| How does a numeric value differ by group? | box or violin plus sample size | do not imply significance from overlap alone |
| Do two numeric fields move together? | scatter; density or hexbin when crowded | state grain and do not imply causation |
| What changed over time? | line with explicit comparison window | mark splits and preserve time order |
| Where is data incomplete? | ranked missingness evidence | offer candidate actions before logging a decision |
| Which fields repeat the same signal? | ranked association pairs | use a heatmap only when the matrix is the question |
| How rare is the target? | prevalence/base-rate evidence | print numerator and denominator |
| How does a binary classifier trade precision for recall? | PR curve plus prevalence baseline | add threshold/confusion evidence before recommending action |
| Are probabilities usable for decisions? | calibration evidence | separate ranking quality from probability accuracy |
| What does a projection preserve? | explained variance and loadings before a 2D projection | call the projection lossy |
| What influenced a prediction? | signed coefficients, permutation importance, or SHAP | distinguish global/local evidence and reject causal language |
| Where does a geographic difference occur? | map only after a denominator-safe table | require accessible and offline fallbacks |

## Reference comparison recipe

Use this recipe when the same measure is compared with both a prior period and a
target.

1. Define the prior period precisely: previous month, comparable season, previous year,
   or previous experiment window.
2. Match the target's population, unit, aggregation, and period to the displayed marks.
3. Use position and length for magnitude. Keep context marks neutral and give the focal
   period one primary accent.
4. Draw the target as a labeled reference line. Use a small secondary marker or a compact
   signed delta for the prior-period comparison.
5. Prefer direct labels when they remove a legend lookup. Keep exact values and the
   denominator visible.
6. If the encoding becomes crowded, switch to a slope chart, dot plot, bullet chart, or
   small multiples instead of adding more colors.

Below prior, below target, statistically meaningful, and operationally meaningful are
four different statements. Never let a red dot silently mean all four. Color reinforces
meaning; line style, marker shape, position, and labels must preserve it without color.

## Surface contract

- **Notebook:** question -> direct answer -> evidence -> boundary -> takeaway.
- **Slide/static export:** include every label needed to understand the evidence without
  hover or surrounding notebook cells.
- **Published HTML:** restrained interaction may reveal detail, but the conclusion must
  remain visible without it.
- **Dashboard:** out of scope. Do not import filters, KPI walls, dense tiles, or monitoring
  navigation into the notecard grammar.

Simple means low decoding effort, not generic styling or shallow analysis. For every
shipped visual, record the question, takeaway, grain, denominator, evidence family,
non-color channel, fallback, export footprint, and final QA surface.

## Evidence order and table pairing

- Show complete missingness evidence before selected numeric or categorical profiles.
  A profile rail is a focused view, not proof that every incomplete field was reviewed.
- When a table makes a visual claim about rank, shape, comparison, or tradeoff, pair it
  with a chart. The table keeps exact values; the chart carries the pattern.
- Do not duplicate a tiny receipt with a decorative chart. Pair evidence only when the
  visual reduces decoding work.
- Keep the full audit dataframe available in code, but render a decision-sized public
  view. Prefer three or four concise columns to a horizontally scrolling ledger.
- Put the evidence first, then record the decision. Never show an imputation receipt
  before an imputation has occurred.

## Statistical guardrails

- Split before fitting learned imputation, scaling, encoding, thresholds, or feature
  selection.
- For rare outcomes, do not use accuracy or ROC alone. Show prevalence, PR, a selected
  threshold, and confusion counts. Add calibration when probabilities drive action.
- Do not call unusual values fraud, errors, or failures without supporting labels.
- Correlation, feature importance, SHAP, and PCA do not establish causality.
- A PCA scatter is not the setup. Show explained variance and loadings first.
- A feature-decision ledger should record: field, observed evidence, allowed role,
  candidate transformation, validation test, leakage/privacy/fairness boundary, and
  final decision.

## Supervised-classification story spine

A public teaching notebook should make the analytical order visible. Use this spine as
a coverage check, not as permission to dump every possible chart:

1. State the outcome, observation grain, prediction window, and data provenance.
2. Check shape, duplicates, identifiers, target values, types, and dates.
3. Show complete missingness evidence before selected field profiles; propose actions
   before changing values.
4. Establish target prevalence with counts and shares.
5. Inspect numeric shape, categorical composition, and a small set of target
   relationships chosen from the question.
6. Record feature decisions and leakage, privacy, and fairness boundaries.
7. Show the split visually; preserve time order when later observations are meant to
   represent the future.
8. Fit preprocessing on training rows only and display the resulting receipt.
9. Define challengers, fit them in a separate cell, and evaluate them on untouched rows.
10. Pair ranking metrics with curves, threshold tables with tradeoff visuals, confusion
    counts with a confusion matrix, and coefficient tables with signed direction plots.
11. End with a bounded recommendation and the human decision that remains open.

Do not hard-code a winning model assertion merely to keep a synthetic story stable.
Seed synthetic generation, derive every visible claim from the resulting data, and let
tests protect the process contract rather than force a preferred conclusion.

## Visual anti-patterns

- Do not draw one equal-length bar per unique decision. The labels are the evidence; a
  decision ledger is clearer than four bars that all say `1`.
- Do not invent a business target, review line, or operational threshold for a synthetic
  dataset. A reference line needs a documented source or a clearly labeled teaching
  assumption with sensitivity analysis.
- Do not compress schema review, split, preprocessing, fitting, and scoring into one
  giant cell. Separate the concepts so the notebook can teach and failures can be found.
- Do not use a selected profile rail as the missingness audit. Incomplete text and
  categorical fields must be visible before numeric cards receive attention.
