# Canonical foundation

The foundation is deliberately small. A card is canonical only when it owns a durable
reasoning job, works in Jupyter and Colab, survives saved HTML and static export, and can
be tested without asking an AI to improvise its layout.

## Canonical roles

| Role | Durable job |
|---|---|
| Question | Name the uncertainty or human choice |
| Preview | Establish reading order or a guardrail |
| Formula | Keep the minimum necessary math visible |
| Evidence table | Preserve exact values and denominators |
| Evidence visual | Reveal shape, order, change, or relative gaps |
| Pictogram / big number | Make one earned proportion or scale memorable |
| Counterintuitive | Explain the smart-beginner misread |
| Takeaway | Answer the section question without adding evidence |
| Verdict / check | State a bounded pass, check, or fail gate |
| Next-think | Return the consequential choice to the human |

Question pairs, before/after tables, split summaries, formula pairs, and EDA boards are
compositions of these roles. They are not new prose-card families.

## The canonical EDA conversation

`wm_eda_overview(...)` is the replacement for “print everything and hope the learner
notices the problem.” It renders:

1. an optional, caller-supplied analytical question—never an invented UI-instruction card;
2. for wide schemas, dtype chips that let the reader scan one family at a time;
3. data chips grouped in stable analytical-role order; headings and color do the
   orientation work without UI-instruction prose;
4. compact numeric and categorical profiles selected for the current question;
5. a field-by-field decision contract.

Numeric profiles include distribution shape, missing count, mean, median, minimum,
maximum, and a visible skew threshold. Categorical bars show count and share. The
inspection helper never parses, imputes, drops, scales, or changes the caller's frame.

Targeted helpers add only the follow-up the question earns:

- `display_cols_by_dtype(...)` compresses a wide raw schema and can glow when an
  explicitly expected field landed in the wrong dtype family.
- `display_dtype_change_chips(...)` keeps raw and reviewed dtype groups side by side and
  highlights only the fields whose dtype changed.
- `wm_build_category_share_table(...)` groups values by field and orders each field by
  share of all rows.
- `wm_build_correlation_clues(...)` ranks pairs, prints the chosen threshold, and calls
  association a clue rather than causation or an automatic drop rule.
- `wm_build_eda_contract(...)` records the field role, completeness, uniqueness, skew,
  status, and the human decision still required.

If preprocessing changes data later, the notebook must show a before/after contract.
Inspection and mutation are intentionally separate.

Missingness must leave an audit trail after an action. Before action, show bounded
candidate methods and the tradeoff the learner must decide. When values are filled, show
the affected fields, method or fill value, training-only fit scope, missing-value counts
before and after, and whether the pipeline kept a missingness indicator. A no-op does not
need its own decision card, and “handled missing values” is never documentation.

Do not make a reader decode three axes, a 3D projection, or a dense multivariate glyph as
their first contact with the data. Walk up through the variables, encodings, and question
first. If the simpler views already answer the question, stop there.

## Text and NLP foundation

Use this reading order:

> corpus coverage → raw examples → shared room language → distinctive TF-IDF edges →
> representation/model → error slices → plain-English decision boundary

Word clouds are not primary evidence because they hide order, denominator, and exact
comparison. A ranked table or bar chart must carry the claim.

## Optional evidence recipes

Maps, globes, network diagrams, Sankey diagrams, animations, and scrollytelling can be
excellent evidence. They are recipes, not canonical card roles. A recipe graduates only
after it has:

- a claim-specific denominator and legend;
- accessible text alternative;
- offline or no-JavaScript final state;
- SVG/PNG/PDF proof where relevant;
- desktop, narrow, dark-host, and static-HTML visual QA.

The orthographic globe remains optional. Geography deserves a canonical contract before
the globe deserves a canonical component.

## Anti-bloat rule

Do not add a component because one notebook used it once. Add it when at least three
different stories need the same reasoning job and the shared implementation removes a
known failure mode. Otherwise keep it as an example recipe.

## Scratch is not a failed share notebook

Scratch and share notebooks are separate product surfaces. The scratch notebook is a
fast, traceable workbench; the share notebook is the reviewed learning sequence. The
exact tagging, naming, and generation contract lives in
[SCRATCH_AND_SHARE_NOTEBOOKS.md](SCRATCH_AND_SHARE_NOTEBOOKS.md).
