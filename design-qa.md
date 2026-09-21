# Design QA

## Scope

Reviewed the canonical EDA schema comparison, card shells, dense category chart,
scrolling evidence table, synthetic forecasting story, and SVG/PNG/PDF exports.

## Visual references

- Original compact profile-card reference supplied during design QA (March 2026)
- Current schema comparison:
  `assets/wm-notecards-eda-schema-before-after.png`
- Side-by-side QA input:
  `build/design-qa-comparison.png`

The comparison keeps the original's quiet paper surface, bright cyan family, restrained
semantic colors, and strong type hierarchy. The new schema view deliberately trades the
old three-column profile rail for two audit panels because it must make forty fields and
three dtype corrections legible without asking the reader to learn everything at once.

## Verified states

- Card shells keep a one-pixel paper border, rest with no shadow, and lift only on hover.
- Data and status chips are borderless. Chip text has no text shadow or inset shadow.
- Reviewed dtype changes use a restrained outer halo; incomplete fields use a louder
  semantic missingness halo without blurring their labels.
- Desktop and 390-pixel layouts have zero page-level horizontal overflow.
- Long tables own their horizontal scroll and retain zebra striping.
- Dense named bars render horizontally, preventing stacked category labels.
- Table hover is deep ink with cyan text, never a white glow.
- The dark notebook host keeps intentional light card surfaces and readable dark text.
- The EDA example offers bounded imputation candidates, applies an explicit train-only
  median fill with a retained missingness indicator, and renders the resulting audit log.
- Static HTML, notebook, SVG, PNG, and PDF outputs were inspected after generation.

## Test evidence

- `uv run ruff check src tests scripts`
- `uv run mypy src`
- `uv run pytest -q`
- `uv build`
- Browser-visible desktop and narrow-width checks in the in-app browser

passed
