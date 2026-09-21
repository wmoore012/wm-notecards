# Publishing and motion boundary

Beautiful data work does not require every surface to move. Motion earns its place only
when it clarifies reading order, continuity, or a state change.

## Notebook runtime

The notebook runtime ships with one short CSS arrival cue and a restrained hover cue.
Both use transform/opacity and disappear under `prefers-reduced-motion`.

The runtime does not load GSAP, ScrollTrigger, Flip, Lenis, or Three.js. This keeps
notebooks printable, offline-friendly, portable, and readable when JavaScript is
restricted.

## Experimental Notecard Story Publisher

A separate static publisher is the right home for richer motion. It should consume an
already executed, privacy-reviewed notebook and produce semantic HTML. The notebook
remains canonical.

Useful motion jobs:

- Reveal a question, then its answer and evidence as one chapter.
- Use Flip when the reader explicitly changes between overview and focused-card mode.
- Use Flip for a before/after comparison where the same artifact changes position.
- Use ScrollTrigger for chapter progress in an article, not to hide core evidence.
- Animate transform and opacity only; refresh triggers after images and fonts settle.

Motion must not:

- reorder evidence without a visible control,
- pin a chart so long that the reader loses page position,
- replace native scrolling,
- animate every card merely because it can,
- depend on WebGL,
- make the reduced-motion version a lesser or incomplete story.

## Launch recommendation

Do not ship scroll-cinema, Lenis, or Three.js in v0.1. The visual claim is stronger when
the core notebook proves that typography, color, spacing, and evidence design can make
data science feel modern without spectacle.

Prototype the Story Publisher after launch with only GSAP core, Flip, and ScrollTrigger.
Pin versions, register plugins once, clean up observers and triggers, and keep the
static final state as the default HTML. Add performance, keyboard, reduced-motion, and
no-JavaScript tests before calling it supported.

## Motion acceptance gate

- The content and reading order are complete without JavaScript.
- `prefers-reduced-motion: reduce` shows the final state immediately.
- Only transform and opacity animate in continuous motion.
- No permanent `will-change` declarations.
- ScrollTrigger instances are created in document order and cleaned up.
- Dynamic layout changes call one debounced refresh.
- No development markers or tooling ship.
- A low-power mobile run stays responsive.
- Motion makes the teaching job clearer in a before/after review.
