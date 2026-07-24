# Launch product contract

`wm-notecards` is a thinking interface for computational notebooks. It is not a
theme pack, a chart gallery, or an animation framework.

The release is one product with three deliberately separate layers.

| Layer | Job | May depend on | Must not do |
|---|---|---|---|
| Notebook runtime | Render reliable cards, tables, charts, and exports | Python, IPython, Plotly, pandas | Fetch motion libraries, infer analytical intent, hide evidence |
| Colab adapter | Translate explicit author intent into Colab-safe presentation | Guarded host APIs and notebook metadata | Require Colab, fail closed, guess which results are noise |
| Published story | Turn an executed public notebook into an optional article or scrollytelling page | Static HTML and, when enabled, pinned GSAP modules | Change calculations, become the canonical notebook, block reading without JavaScript |

This boundary keeps the learning artifact dependable while leaving room for a more
cinematic sharing surface.

## What ships in the first public release

The launch gate is complete only when all of these are true:

- The Python runtime renders every documented card role.
- A deterministic synthetic notebook demonstrates the full story grammar near the top.
- Tables stripe neutral rows and constrain long prose at the source.
- Dense named bars become horizontal or fail with a useful instruction.
- Chart annotations reserve their own space instead of covering titles or subtitles.
- Light and dark themes retain their own surface and text colors inside host dark mode.
- Colab source/output visibility comes from explicit tags.
- Colab output expansion is feature-detected and fails open.
- SVG, PNG, and PDF exports preserve the styled dimensions and breathing room.
- The Notecard Teacher Style skill ships with the same visual and analytical contract.
- Unit tests, notebook execution, and browser observation all pass.

## What does not belong in the first release

- Heuristic collapsing based on cell text.
- A white global dark-mode override.
- Lenis or other smooth-scroll replacement inside notebooks.
- Three.js or shader backgrounds in notebooks.
- GSAP, ScrollTrigger, or Flip in the Python runtime.
- Motion that hides evidence until the reader scrolls.
- A slightly perturbed copy of a restricted dataset presented as synthetic data.

For public examples, generate data from a documented independent process or use a
dataset with a clear redistribution license. Randomly nudging source values can preserve
the original dataset's structure, people, and licensing risk. The included seasonal
example uses a deterministic equation and seed instead.

## AI authoring decision table

An AI author should make these decisions in order.

| Question | Required action |
|---|---|
| What human decision does this section support? | Write that question before choosing a visual. |
| Is there a direct answer yet? | Put it before the evidence or state that the result is still exploratory. |
| Do exact values matter? | Use a table with controlled widths and stripes. |
| Does shape, order, or change matter? | Use one chart with one reading job. |
| Could a smart beginner overread the result? | Add a counterintuitive boundary card. |
| Is the output setup noise or raw audit evidence? | Add an explicit portable-cell tag. |
| Is a claim visible? | Recompute it from the same object used by the visual. |
| Has the rendered result been observed? | Do not mark the section complete until it has. |

## Release priorities

### Must have

- Runtime reliability across Jupyter, VS Code, Colab, and saved HTML.
- Privacy-safe public examples and embedded bundles.
- Visual regression tests for every previously observed failure.
- An installable authoring skill and a human-readable contribution contract.

### Good first follow-up

- An experimental static Story Publisher that consumes executed public artifacts.
- A card gallery that exercises long, empty, error, light, dark, and narrow states.
- Share-card presets for social, slides, articles, and email.

### Later, after evidence

- GSAP Flip for explicit focus or compare transitions in published stories.
- ScrollTrigger for progressive story chapters, with reduced-motion parity.
- Contribution telemetry that contains no notebook data.

Promotion into the protected runtime requires proof across at least two assignments or
model families and no notebook-local layout patch.

## Launch verification matrix

| Surface | Minimum proof |
|---|---|
| Python API | Unit tests, type check, lint, built wheel |
| Notebook | Restart/run all, zero warnings, complete visible fields |
| Colab build | Clean build, embedded runtime wins, intent metadata preserved |
| Browser | Desktop, narrow, host-dark simulation, keyboard scroll, no console errors |
| Exports | Inspect SVG, 3x PNG, and PDF at final dimensions |
| Public bundle | Secret/path scan and license review of every included asset |

Passing code is necessary. Observing the reader's end state is the release contract.
