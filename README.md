# wm-notecards

## Please hear me out. I’m new here.

> I’m new to this community. Thank you for having me—I mean that. I’m learning in
> public, and this is the tool I needed while I was learning.

We are data scientists. We make data visualizations for a living.

**Why are we still doing machine learning in MS-DOS?**

I almost failed Machine Learning. Not because the math was impossible. Because I kept
forgetting what I had already learned while staring at walls of notebook output.

I came here from music production and audio engineering: glowing rooms, tactile
instruments, modern tools with vintage soul. In creative work, how a tool feels changes
how you think with it.

This is not just vibe. A data frame represents the real world and the people affected
by our decisions. That is hard to remember when the interface keeps handing us this:

```text
NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN
NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN
12   133  32   131  131  3345 343  35
```

![Before-and-after demonstration of a raw notebook becoming a notecard thinking interface](https://raw.githubusercontent.com/wmoore012/wm-notecards/main/assets/wm-notecards-demo.gif)

Jupyter gave me `df.describe()`.

I wanted `df.explain()`.

So I built the thinking interface I wish I had on day one:

> question → direct answer → evidence → takeaway → your decision

`wm-notecards` helps a notebook remember the argument, teach the evidence, and return
the consequential choice to the human. Teaching is a side effect. Thinking is the
product.

If you have ever reached cell 47 and forgotten what happened in cell 12, you are
probably the person I built this for.

Open source. If you think notebooks can be better, come help.

## Install

```bash
uv add "wm-notecards @ git+https://github.com/wmoore012/wm-notecards.git"
```

The shorter `uv add wm-notecards` command will be documented after the first PyPI
release; it is intentionally not claimed before that release exists.

Then make one notebook section feel like a conversation:

```python
from wm_notecards import WMTheme, init_notebook

theme = WMTheme.light()
init_notebook(theme)
```

## What is enforced (and why)

- **Readable categories:** Dense named bar charts become horizontal; charts above 24
  categories require an explicit visual-review override.
- **Tables you can actually scan:** Neutral tables use visible alternating row shades;
  long tables stretch, scroll in both directions, and keep headers visible.
- **Preattentive hierarchy:** Answer-first titles, position, size, one restrained
  accent, zebra rows, and semantic state fills establish the reading order before a
  reader consciously decodes the values.
- **Context without collisions:** Header chips wrap instead of covering subtitles or
  chart annotations.
- **Motion with consent:** New cards arrive with a brief attention cue, hover gently,
  and respect `prefers-reduced-motion`.
- **Color sanity:** Legacy plotting defaults map onto a consistent semantic palette,
  with text, line style, or borders carrying a second channel.
- **Honest exports:** SVG, high-resolution PNG, and PDF use the styled figure
  dimensions instead of silently clipping the evidence.
- **Regression pressure:** Tests cover card shells, chart density, table overflow and
  striping, semantic colors, pictograms, formulas, icons, and static rendering.

These guarantees target the failures that are hardest to catch from code alone:
stacked category labels, clipped evidence, drifting fonts, callouts covering prose,
and notebook output that looks correct only at one width.

## Develop from source

```bash
git clone https://github.com/wmoore012/wm-notecards.git
cd wm-notecards
uv sync --extra dev --extra svg
uv run pytest
```

Style and render a figure:

```python
import plotly.express as px

from wm_notecards import WMTheme, init_notebook
from wm_notecards.charts import style_fig_wm, wm_render_figure_card

theme = WMTheme.light()
init_notebook(theme)

fig = px.bar(
    peer_scores.head(10),
    x="score",
    y="peer_artist",
    orientation="h",
)
style_fig_wm(
    fig,
    title="The reranker creates room beyond the obvious peers",
    subtitle="Top 10 reviewed peers; higher is stronger",
    theme=theme,
)
wm_render_figure_card(
    fig,
    theme=theme,
    file_stub="peer-opportunity",
    kicker="STANDARD,08,FAIR",
    chip_text="Reviewed",
)
```

## Card grammar

| Card | Job |
|---|---|
| Question | Frame a real decision or uncertainty |
| Formula | Show the math briefly before using it |
| Evidence table | Preserve exact values |
| Evidence visual | Reveal shape, order, or relative gaps |
| Takeaway | Answer the section question loudly |
| Counterintuitive | Explain why the result is easy to overread |
| Verdict | State a bounded pass/check/fail conclusion |
| Next-think | Return the next choice to the learner |

Tables and charts are paired only when they do different jobs. A table supplies exact
values; a chart supplies visual structure. If one merely repeats the other, remove it.

## Release-quality chart behavior

The default categorical policy is intentionally opinionated:

```python
style_fig_wm(fig, title="...", theme=theme)
```

- 10–24 named categories: vertical bars become horizontal automatically.
- More than 24 named categories: rendering raises a `ValueError` and asks for top-N,
  faceting, or an explicit reviewed override.
- Custom colors stay custom; exact Matplotlib/Plotly default colors are normalized.

Use `allow_dense_categories=True` only after observing the rendered chart at desktop
and narrow widths. The full release gate is in
[docs/OPEN_SOURCE_GRAPH_CHECKLIST.md](docs/OPEN_SOURCE_GRAPH_CHECKLIST.md).
The supplied real-world examples and their current pass/fail decisions are recorded
in [docs/SCREENSHOT_AUDIT.md](docs/SCREENSHOT_AUDIT.md).

## Export for slides, articles, and sharing

```python
from wm_notecards.rendering import export_figure_wm

export_figure_wm(fig, "exports/chart.svg")       # editable vector
export_figure_wm(fig, "exports/chart.png")       # 3× share/slide default
export_figure_wm(fig, "exports/chart.pdf")       # print
```

Export only the artifact—not notebook paths, tokens, internal comments, proprietary
variable names, or private data.

## Colab builder

The portable builder embeds the package and selected project files into an initial
helper cell, clears execution state, and keeps a takeover notebook as the canonical
cell order:

```bash
uv sync --extra builder
uv run python scripts/build_colab_bootstrap.py \
  --takeover notebooks/lesson.ipynb \
  --scratch notebooks/lesson_scratch.ipynb \
  --notebook-output dist/lesson_COLAB.ipynb
```

Use `--skip-scratch` for a release notebook. Inspect the generated notebook before
sharing; embedded source is still source.

## Notecard Teacher Style skill

The distributable AI-authoring skill lives at
[`skills/notecard-teacher-style`](skills/notecard-teacher-style). It preserves the
lead-first teaching loop, careful anomaly language, visual QA requirement, and the
human-in-the-loop decision boundary.

## Development gates

```bash
uv sync --extra dev --extra svg
uv run ruff check .
uv run mypy src
uv run pytest --cov=wm_notecards --cov-report=term-missing
uv build
```

Build success is not visual proof. For browser-visible changes, observe the expected
card, chart, and table end states at desktop and narrow widths before opening a release
PR.

## Contributing

Contributions are welcome—especially new card roles, accessibility improvements,
better evidence checks, export workflows, and regression fixtures from real notebook
failures. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

## License

MIT. See [LICENSE](LICENSE).
