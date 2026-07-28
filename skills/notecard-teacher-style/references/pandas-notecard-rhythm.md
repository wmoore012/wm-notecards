# Pandas and notecard reading rhythm

Pandas and wm-notecards are partners. Pandas is the audit trail. Notecards keep the
question, reading order, interpretation, and decision visible when the notebook grows.

## Human reading order

Use this order for each new evidence family:

1. Ask the real question before revealing unfamiliar evidence.
2. Show the smallest ordinary Pandas audit that earns trust when it is useful:
   `head()` for recognizable rows, numeric `describe()` for exact summaries, and
   categorical `describe(include="all")` for raw category coverage.
3. Render the purpose-built notecard visual or table immediately after that audit.
4. Add a short reading guide when a capable beginner could misread an axis, denominator,
   whisker, baseline, threshold, coefficient, or color.
5. State the bounded answer and the next decision.

Do not make the learner scroll past another topic and then return to interpret the
evidence. A section must work as one local conversation.

## Arrival and missingness sequence

Start EDA with evidence in this order:

1. `df.head()` so the row grain is concrete.
2. Source-contract checks for row count, duplicates, identifiers, target domain, and
   parseable dates. Prefer a visual check/verdict composition over a decorative table.
3. Raw dtypes and explicit conversion candidates.
4. Complete missingness evidence across every field before selected profiles.
5. A memory bridge that names incomplete fields by semantic type. Within each type,
   sort by missing count descending, then missing share, then stable field name.
6. Numeric and categorical Pandas summaries followed by matching wm micro-profiles.

The memory bridge and profile rail must use the same order. A numeric rail cannot make
text or categorical missingness disappear from the story.

## Pairing invariant

When a table and visual answer the same question, render them in the same cell or in
immediately adjacent cells with no unrelated output between them. Required pairs include:

- exact group counts + a rate/share comparison;
- validation metrics + PR/ROC evidence;
- threshold counts + the precision/recall tradeoff;
- confusion counts + a confusion-matrix visual;
- coefficient values + a signed direction plot.

The table holds exact values. The visual makes the pattern preattentive. Remove either
one when it merely duplicates the other.

## Public output boundary

Raw Pandas is appropriate for recognizable source rows and unmodified audit summaries.
Feature ledgers, preprocessing receipts, model comparisons, threshold receipts,
confusion counts, and final decisions use the canonical wm table renderer so text wraps,
evidence stays labeled, and the output can travel to slides.

Do not announce interface mechanics to the reader. Write the data question, evidence,
and consequence. Avoid em dashes in visible public copy; use a sentence, colon, comma,
or short hyphen when punctuation is actually needed.
