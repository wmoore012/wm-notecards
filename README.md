# wm-notecards

> I’m new here. Thank you for having me—I mean that. I’m learning in public,
> and this is the tool I needed while I was learning.

We are data scientists. We make visualizations for a living.

**Why are we still doing machine learning in MS-DOS?**

I almost failed Machine Learning—not because the math was impossible, but because I
kept forgetting what I had already learned while staring at walls of notebook output.

![Before-and-after demonstration of a raw notebook becoming a notecard thinking interface](assets/wm-notecards-demo.gif)

Jupyter gave me `df.describe()`.

I wanted `df.explain()`.

## Data Science CAN look as good as Stripe or Notion.

## `df.describe()` should be better.

```text
Age   Income   BMI    Visits  Claims  Premium  Score   Balance  State   Segment   Churn
45    NaN      31.2   12      2       1430.52  0.91    4432.10  NC      Gold      False
38    82250    NaN    4       0       982.33   0.42    1210.55  SC      Silver    False
NaN   61500    28.7   8       1       1142.01  NaN     2988.41  NC      Gold      True
```

The goal is insights.

What do you want to know every time you look at a **numerical** variable?

Answer that.

What do you want to know every time you look at a **categorical** variable?

Answer just that.

You have count but no missingness? Add it.

The quartiles are written for computers. Put the box plot beside them.

Forty columns should not require forty thoughts at once.

The questions are predictable.

**The notebook should be too.**

`wm-notecards` turns notebook output into a thinking interface:

> question → direct answer → evidence → takeaway → your decision

## Two notebooks. Two jobs.

### Simple Seasonal Forecasting Lab

[Open the polished forecasting notebook](examples/simple_seasonal_forecasting_lab.ipynb).

It keeps the argument still: question, formula, exact evidence, visual structure,
bounded takeaway, and the learner's next choice. Its data is deterministic and fully
synthetic.

### 40-Column EDA Scratchbook

[Open the EDA scratch notebook](examples/40_column_eda_scratchbook.ipynb).

This one remembers the messy thinking: raw pandas output, dtype suspicions,
missingness, skew, imputation candidates, the approved train-only fill, its audit
trail, field roles, feature exclusions, and the questions still unanswered.

No private CSV. No equal placeholder categories. No silent transformation.

## Install

```bash
uv add "wm-notecards @ git+https://github.com/wmoore012/wm-notecards.git"
```

Then:

```python
from wm_notecards import WMTheme, init_notebook

theme = WMTheme.light()
init_notebook()
```

The shorter `uv add wm-notecards` command will be documented after the first PyPI
release. It is intentionally not claimed before that release exists.

## What the library protects

- **Readable categories:** Dense named bars become horizontal; charts above the
  reviewed category limit stop instead of stacking labels into soup.
- **Tables you can scan:** Alternating row shades, sticky headers, and two-directional
  overflow are standard.
- **Preattentive EDA:** Complete fields stay quiet. Incomplete fields carry one global
  amber signal. High skew carries one blue evidence border.
- **Crisp chips:** Borderless, shadowless type and role chips alternate by visible role
  row instead of becoming a bag of candy.
- **Honest decisions:** Inspection never imputes, parses, drops, or coerces. Applied
  preprocessing receives a before/after audit trail.
- **Stable cards:** Notecards have borders, rest flat, lift only on hover, and remain
  readable under host dark mode and reduced motion.
- **Honest exports:** SVG, high-resolution PNG, and PDF respect the styled dimensions.

## Use the skill with the library

The open-source bundle includes the
[`notecard-teacher-style` Codex skill](skills/notecard-teacher-style).

The library knows how to render the cards. The skill teaches an AI when a question,
table, chart, formula, takeaway, or next decision is actually earned. It also forbids
silent preprocessing and conclusions written before the evidence exists.

Copy the bundled skill directory into your Codex skills directory, then restart Codex.
The skill and library are versioned together so the AI does not have to guess which
grammar the installed code expects.

## EDA evidence, not EDA theater

```python
from wm_notecards import wm_compare_fields

evidence = wm_compare_fields(df, fields=["amount_usd", "channel"])

evidence.table   # exact group statistics
evidence.figure  # the distribution shape
```

Canonical EDA recipes return both exact evidence and a purpose-specific visual. They do
not intercept arbitrary DataFrames or manufacture prose insights.

After an approved transformation:

```python
from wm_notecards import PreprocessingDecision, wm_build_preprocessing_log

log = wm_build_preprocessing_log(
    before,
    after,
    [
        PreprocessingDecision(
            field="amount_usd",
            action="impute",
            method="training median",
            reason="Right-skewed measure; preserve a missingness indicator.",
            fit_scope="train_only",
            keep_missing_indicator=True,
        )
    ],
)
```

The decision log starts **after** the action. A suggestion is not an audit trail.

## Export for slides, articles, and sharing

```python
from wm_notecards.rendering import export_figure_wm

export_figure_wm(fig, "exports/chart.svg")
export_figure_wm(fig, "exports/chart.png")
export_figure_wm(fig, "exports/chart.pdf")
```

Export only the artifact—not notebook paths, tokens, internal comments, proprietary
variable names, or private data.

## Colab without a second notebook personality

```bash
uv sync --extra builder
uv run python scripts/build_colab_bootstrap.py \
  --takeover notebooks/lesson.ipynb \
  --scratch notebooks/lesson_scratch.ipynb \
  --notebook-output dist/lesson_COLAB.ipynb
```

Use `--skip-scratch` for a release notebook. Cell tags—not an AI guess—control what
stays open:

| Tag | Behavior |
|---|---|
| `wm-essential` | Keep the evidence open |
| `wm-hide-source` | Hide implementation source; keep output open |
| `wm-collapse-output` | Collapse long raw output |
| `wm-noise` | Hide setup source and collapse setup output |

## Find copies that drifted

```bash
uv run wm-notecards doctor /path/to/project
```

The doctor is read-only. It reports notebooks that redefine canonical helpers, legacy
`wm_theme.py` files, vendored runtimes, and Colab-named copies that should be generated
from one source.

## Develop from source

```bash
git clone https://github.com/wmoore012/wm-notecards.git
cd wm-notecards
uv sync --extra dev --extra svg
uv run ruff check .
uv run mypy src
uv run pytest
uv build
```

Green tests are not visual proof. Public notebooks are also executed and inspected at
desktop and narrow widths before release.

## Contributing

Contributions are welcome—especially accessibility improvements, evidence recipes,
exports, and regression fixtures from real notebook failures.

A new canonical card role needs three different stories and one shared failure mode.
Novelty alone is not enough.

I spent a long time researching, breaking, and rebuilding this system. I am happy to put
the useful parts in one place so the next person can skip some of that friction.

If you also look at a familiar tool and think, “hey, something is off here... let’s fix
it,” connect with [Wilton Moore on LinkedIn](https://www.linkedin.com/in/wiltonmoore/)
or [wmoore012 on GitHub](https://github.com/wmoore012).

Cheers, everyone.

## License

MIT. See [LICENSE](LICENSE).
