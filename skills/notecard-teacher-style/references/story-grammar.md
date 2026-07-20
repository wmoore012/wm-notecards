# Story grammar

## Lead-first card roles

| Role | Use it for | Avoid |
|---|---|---|
| Question | A real uncertainty or choice | “Distribution check” topic labels |
| Preview | Reading order and guardrails | Repeating the title |
| Formula | The minimum math needed to read evidence | A derivation wall |
| Evidence table | Exact values and auditability | Dozens of unbounded rows |
| Evidence chart | Shape, order, change, or relative gaps | Decorative duplication |
| Pictogram | One memorable proportion | Tiny differences or precision |
| Counterintuitive | A likely novice overread | Generic caveats |
| Takeaway | The direct section answer | New evidence |
| Verdict | A bounded pass/check/fail gate | Unqualified certainty |
| Next-think | A consequential human choice | Fake multiple choice |

## Writing pattern

Use this compact sequence:

- Question: “Does the seasonal model learn the annual wave or only its average level?”
- Answer: “It learns the month pattern, but misses the rising level.”
- Evidence: holdout overlay plus exact RMSE/MAE table.
- Boundary: decomposition is descriptive; holdout error decides model usefulness.
- Takeaway: “Seasonality helps, but trend + seasonality is the credible baseline.”
- Choice: “Do you want to test a changing seasonal amplitude or keep the simpler model?”

## EDA chips

Group chips by data role or dtype, then use a stable reading order: identifiers/time,
targets, numeric measures, categorical context, missingness/quality flags. Within a
category, order by a meaningful percentage or coverage metric when one exists. Do not
change grouping on each generation.

## Human ownership

Let AI discover, compute, teach, and suggest. Let the human choose model complexity,
intervention, publication, or deployment when tradeoffs remain.
