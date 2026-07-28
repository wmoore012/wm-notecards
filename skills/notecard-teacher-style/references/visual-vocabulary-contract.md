# Visual vocabulary contract

The notebook is a teaching surface, so the model must know the visual vocabulary
before it decides what to show. The rule is not “use every chart blindly.” The rule is
“never let an AI omission masquerade as judgment.”

## Inventory first

For each analytical question, write a short inventory before authoring the cell:

| Evidence job | Visuals to consider | What the reader should learn |
|---|---|---|
| One numeric field | micro-profile, histogram, ECDF, box, violin | shape, spread, tails, missingness |
| Categories | sorted bars, dot plot, lollipop, pictogram | order, share, denominator |
| Numeric by group | box, violin, strip or beeswarm | typical value, spread, outliers, sample size |
| Two numeric fields | scatter, hexbin or density | direction, concentration, exceptions |
| Time | line, annotated timeline, small multiples | sequence, change, season, split |
| Composition | stacked bars, 100% bars, treemap or waterfall | parts, total, contribution |
| Association/redundancy | ranked pairs, heatmap, clustered matrix | repeated signal and its limits |
| Classification | prevalence pictogram, PR, ROC, calibration, confusion matrix, threshold tradeoff | base rate, ranking, probability, action cost |
| Model explanation | signed coefficients, permutation importance, SHAP, partial dependence | direction or contribution, never causality |
| High dimensional structure | explained-variance bars, loadings, PCA scatter | what is retained, then where rows sit |
| Geography | denominator-safe table, map, small multiples | where a difference occurs and who is represented |

The inventory is a coverage check. Use the relevant families that answer different
parts of the question. If a family is not used, write one plain-language reason in the
planning cell: “No time field, so a line chart would invent an order,” or “The matrix is
not the question, so a heatmap would add decoding work.” Never write “not needed” with
no evidence.

## Canonical notebook rhythm

The mature notebooks use a repeatable sequence:

1. orient the file with real rows (`head`), shape, types, dates, and the target;
2. ask the first human question;
3. show exact Pandas evidence and the matching notecard visual together;
4. move from distributions to comparisons, relationships, time, and missingness;
5. make feature, leakage, and fairness decisions visible;
6. show the split and preprocessing receipt;
7. fit challengers in separate cells;
8. compare metrics with curves and confusion counts with a confusion matrix;
9. choose a threshold only after showing the precision/recall tradeoff;
10. close with a bounded takeaway and a human decision.

Do not make the reader scroll away from a table to find the chart that explains it.
Keep the table and visual in one output cell or adjacent cells, with a short reading
guide between them. Each group must stand alone for a screenshot or slide export.

## Human examples are executable canon

Before inventing a new card, inspect the closest mature notebook pattern. The strongest
examples are not generic prose: they are real cells that pair a question, a direct
answer, a visual, a table, and a boundary. Preserve their cadence and replace only the
nouns and computed evidence.

- `notebooks/source/Wilton MooreMLproj2_scratch.ipynb`: date trust, friction tails,
  feature scorecards, ranked queues, and anomaly boundaries.
- `notebooks/source/Wilton MooreMLproj2_takeover.ipynb`: signal scans, model-risk maps,
  and human review decisions.
- `examples/logistic_regression_thinking_interface.ipynb`: target contract, missingness,
  categorical rates, leakage ledger, chronological split, PR/ROC, threshold tradeoff,
  and confusion evidence.
- `examples/simple_seasonal_forecasting_lab.ipynb`: full-series EDA, decomposition,
  forecast overlays, residuals, model comparison, and a bounded final choice.

If a referenced notebook is unavailable, say so in the planning cell and use the nearest
available example. Do not replace an absent example with invented “AI best practice.”

## Visual discipline

- Use position and length for magnitude before color.
- Reserve the primary accent for the focal mark; keep context neutral or use a restrained
  sequential family. A youthful accent is not a universal palette.
- Put target lines, split boundaries, prior-period markers, and denominators directly on
  the figure. Never make a reader decode an unexplained legend.
- Use accessible shape, line style, labels, or annotations alongside color.
- A chart can be simple and still be analytically rich. “Simple” means low decoding
  effort, not generic styling or shallow evidence.
- Static export must retain every label, value, boundary, and caveat without hover.
