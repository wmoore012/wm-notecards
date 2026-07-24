# Pre-launch roadmap

## Launch foundation

- Canonical card roles and EDA conversation are documented and tested.
- Formula SVG rendering repairs real double-brace and display-wrapper failures.
- Tables stripe, scroll on both axes, keep headers visible, and use semantic fills only
  for semantic states.
- Charts defend against dense categories, label collisions, annotation spillover, and
  export-size drift.
- Colab metadata declares which source/output stays open or collapsed.
- The synthetic story demonstrates the public vocabulary without private data.
- Scratch and share notebooks have different presentation contracts and one canonical
  takeover cell order.
- Desktop, narrow, host-dark, saved-HTML, SVG, PNG, and PDF proofs are release gates.

## First community release

- Publish the package and Notecard Teacher Style skill together.
- Ship a static showcase generated from the synthetic notebook.
- Publish a contribution template for a new visual recipe: source question, evidence
  contract, accessibility alternative, exports, and regression fixture.
- Add one text/NLP example and one classification example only after each passes the
  same proof contract as the forecasting story.

## Later, opt-in layers

- Static Story Publisher with semantic HTML first and GSAP enhancement second.
- Flip for focus/compare continuity and ScrollTrigger for chapter pacing, both behind
  reduced-motion and no-JavaScript fallbacks.
- Optional map/globe recipe after geographic and export contracts are proven.
- PowerPoint/article/share-card templates generated from the same export API.

## Explicit non-goals for launch

- No automatic imputation, coercion, or transformation inside EDA display helpers.
- No arbitrary LLM-selected fonts, palettes, or component variants.
- No JavaScript dependency in the notebook runtime.
- No “canonical” component whose only justification is novelty.
- No deployment claim until the static showcase is visually approved and a hosting
  target is chosen explicitly.
