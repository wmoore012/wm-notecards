---
name: notecard-teacher-style
description: Create, revise, repair, or review data-science notebooks as lead-first, visually deliberate notecard conversations. Use for .ipynb teaching flows, wm_notecards helpers, card grammar, notebook scaffolding, evidence/claim review, Colab-ready lessons, and visual QA of tables, charts, formulas, pictograms, takeaways, or human decision points.
---

# Notecard Teacher Style

Build a guided conversation with the learner, not a decorated analysis dump.

## Required references

Read all three before creating or revising a notebook:

- `references/story-grammar.md`
- `references/eda-and-text-contract.md`
- `references/release-contract.md`

Read `references/scratch-and-share-contract.md` when a repo has scratch, takeover,
Colab, final, or public-example notebooks, or when naming a shared notebook.

Read `references/portable-and-host-contract.md` when building for Colab, saved HTML,
dark mode, collapsing noisy cells, or a published story.

## Core sequence

Structure each analytical section as:

1. Ask a decision-relevant question.
2. Give the direct answer early.
3. Teach the evidence and its reading order.
4. State uncertainty and what the result does not prove.
5. Close with a takeaway.
6. Return the consequential next choice to the human.

Use energetic, down-to-earth language. Define technical terms on first use. Keep
internal variable names technical when the code needs them; translate them in visible
labels.

## Workflow

### 1. Inspect before authoring

- Read repository instructions and the canonical notebook/runtime helpers.
- Reuse existing `wm_*` cards, kickers, chart styling, and table renderers.
- Identify the source, unit of observation, split logic, and decision the notebook
  supports.
- If the section is EDA or text/NLP, follow `references/eda-and-text-contract.md` and
  keep every suggested conversion or threshold visible to the learner.
- Run the notebook or inspect computed outputs before writing a claim.

### 2. Build the narrative skeleton

Write the question and tentative answer before choosing a visual. Choose the smallest
card sequence that teaches the result. Do not use every card type merely because it
exists.

Use a table for exact values and a chart for shape/order. Pair them only when those jobs
differ. Use a formula card before evidence when the learner needs the math to interpret
the result. Use a counterintuitive card when a smart beginner could overread the result.

### 3. Build evidence safely

- Compute visible numbers from the same objects used by the chart/table.
- Fit preprocessing and thresholds on training data only.
- Label descriptive decomposition, in-sample fit, baselines, and holdout evidence
  accurately.
- Avoid fraud/anomaly certainty unless labels and evidence support it.
- Tie model-quality language to the displayed metric, split, and uncertainty.

### 4. Enforce visual behavior

- Let dense named bar charts become horizontal.
- Reduce or facet charts above the category limit; do not force an unreadable override.
- Use semantic color roles consistently and add a non-color channel.
- Design a preattentive reading order: answer-first title, evidence, then quiet
  methodology; use salience sparingly instead of highlighting everything.
- Keep alternating row shades visible on neutral tables, with semantic fills reserved
  for defined states.
- Allow long tables to scroll in both directions while keeping headers visible.
- Keep chips, annotations, legends, and prose in separate layout regions.
- Use shared font, spacing, radius, and color tokens.
- Respect reduced motion.

### 5. Inspect with eyes

Restart and run the notebook from the declared environment. Observe the actual rendered
end states at desktop and narrow widths. Check long labels, long tables, empty states,
chips, legends, scrollbars, alignment, dark mode, and static exports. Treat blank cards,
clipping, and out-of-shell charts as failures even when execution succeeds.

### 6. Close the loop

State the answer, evidence, boundary, and human choice. Add a regression test for a fixed
visual or calculation bug when practical. Record unverified environments honestly.

## Colab and public distribution

Use the repository's Colab builder instead of manually duplicating notebooks. Clear
execution state and inspect the embedded source. Remove credentials, local paths,
proprietary comments, private product names, and non-public data from release artifacts.

Declare cell presentation intent with metadata. Use `wm-essential` for evidence and
decisions, `wm-hide-source` for implementation code that is not the lesson,
`wm-collapse-output` for long raw audit output, and `wm-noise` for bootstrap/setup. Do
not infer collapse behavior from prose or function names.

## Prohibited shortcuts

- Do not replace the teaching flow with raw `df.describe()` output.
- Do not silently impute, coerce, parse, drop, or transform inside an EDA display helper.
- Do not make every optional visual recipe into a canonical card type.
- Do not write a conclusion before checking the computed evidence.
- Do not invent a takeaway because the card grammar has a takeaway slot. Unresolved
  evidence ends with a question, check, or next-think card.
- Do not narrate the interface in public copy. Show the data decision itself.
- Do not let an LLM choose arbitrary fonts, colors, card variants, or overflow behavior.
- Do not call a notebook visually verified because tests passed.
- Do not hide a math, data-quality, accessibility, or environment limitation.
