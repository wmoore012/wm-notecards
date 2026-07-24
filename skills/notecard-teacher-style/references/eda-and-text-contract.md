# EDA and text evidence contract

EDA is a conversation about field decisions, not a prettier `df.describe()`.

## Canonical EDA sequence

Use the smallest sequence that answers the source question:

1. Ask the real analytical question. Never explain the interface to the reader.
2. For a wide source, group the raw columns by dtype so the learner can scan one family
   at a time. If a date or number arrived as text, make that wrong-lane field glow.
3. After any explicit conversion, show the raw and reviewed dtype groups side by side.
   Highlight only fields that moved. Never imply the display helper converted them.
4. Show stable data chips by analytical role: identifier, time, target, numeric,
   categorical, boolean/flag, then text/high-cardinality.
5. Show micro-profiles for the fields that matter to the current question. Do not dump a
   profile for every field merely because the dataframe is wide.
6. Show suggestions as suggestions. A decision log exists only after a human-approved
   transformation has actually run.
7. Add one targeted follow-up only when the evidence earns it: category shares,
   missingness, skew, correlation, time coverage, or split integrity.
8. Close with the decision the human still owns.

Do not emit every diagnostic for every dataset.

## Data chips

- Keep the role order stable across notebooks.
- Omit completeness at 100%. Print it only when a field is incomplete.
- Within a role, show incomplete fields first, then use stable field order.
- Alternate the two candidate-chip surfaces by rendered role row. Missing role rows do
  not reset or consume the alternation.
- Chips are borderless, flat, and free of text shadow. The notecard shell keeps its border.
- Make missingness glow only when values are actually missing.
- Use category tables, not chip color, to communicate category prevalence.
- Never let an inferred role silently coerce the source dtype.

## Numeric micro-profiles

- Use a compact distribution shape plus visible minimum, mean, median, maximum,
  missing count, and skew.
- Print the chosen skew review threshold on the card.
- Treat skew as a clue to inspect scale, unusual values, and modeling assumptions.
  It is not an automatic transform order.
- If a transform is chosen, fit it on training data only and record the choice.

## Missingness and type decisions

- Never impute, drop, parse, or coerce inside an inspection helper.
- Preserve the raw field before parsing dates or recoding labels.
- Say whether missingness may carry meaning before filling it. Present plausible methods
  and their tradeoffs before the human approves one; do not create a decorative
  “no imputation” card merely to fill the sequence.
- Never write only “handled missing values.” After imputation runs, render a decision
  table naming every
  affected field, the method or fill value, training-only fit scope, missing-value counts
  before and after, and whether a missingness indicator was preserved.
- Dates may legitimately arrive as strings; numeric-looking values may legitimately
  be identifiers. Ask what the field represents before changing it.
- When a notebook changes data, render a visible before/after contract with the
  affected fields, rule, row count, and validation check.
- Keep suspected blank/sentinel tokens separate from actual null counts. Inspection
  must not normalize them silently.

## Evidence gate

- A card role is not a quota. If evidence is unresolved, use a question, check, or
  next-think card. Do not manufacture a takeaway or verdict.
- Human-facing copy must answer the analytical question. Ban interface narration such
  as “Color names the role,” “This lab shows,” or “No automatic changes.”
- Every canonical EDA recipe returns exact tabular evidence and a purpose-specific
  visual. This rule does not intercept arbitrary pandas DataFrames.
- Learned imputers, encoders, scalers, and thresholds fit on training rows only.
- Every AI-chosen parsing, skew, category, or correlation threshold is visible and
  challengeable.

## Categories and correlation

- For categories, group by field and order values by share of all rows. Print both
  count and percentage so the denominator is auditable.
- Use a correlation heatmap only when the matrix itself is the question.
- Otherwise rank field pairs by absolute association, print the review threshold,
  and state that correlation is a clue rather than causation or an automatic drop.
- Echo any AI-chosen threshold in the final takeaway so the learner can challenge it.

## Text and NLP reading order

Text evidence should move from room to edges to decision:

1. Show corpus/source coverage and a few representative raw examples.
2. Show the shared room language: common terms and document frequency.
3. Show distinctive edges: TF-IDF or another explicitly defined weighting.
4. Show the representation or model only after the reader understands the inputs.
5. Show error slices or nearest examples with exact text evidence.
6. State the reason-code or decision boundary in plain English.

Avoid word clouds as primary evidence. They obscure denominator, ordering, and exact
comparison. A word cloud may be decorative only when a ranked table or chart carries
the claim.

Do not lead with a 3D or multi-axis view. Walk the learner through the variables, axes,
and encodings first, then use the complex view only if it answers a question the simpler
views could not.

## Foundation boundary

The canonical foundation is intentionally small: question, preview/formula,
evidence table/visual, pictogram/big number when earned, counterintuitive boundary,
takeaway, verdict/check, and next-think. EDA is a workflow built from those roles, not
a new family of prose cards.

Maps and globes are optional evidence recipes. Do not make them canonical until the
specific map has an offline fallback, readable legend, accessible alternative,
static export, and geographic denominator that supports the claim.
