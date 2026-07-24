# Portable and host contract

Use explicit metadata. Do not ask the host or an AI to guess presentation intent.

| Tag | Source | Output | Typical role |
|---|---|---|---|
| `wm-essential` | unchanged | open | Question, evidence, takeaway, verdict, decision |
| `wm-hide-source` | hidden | open | Card implementation code |
| `wm-collapse-output` | unchanged | collapsed | Raw summary or audit log |
| `wm-noise` | hidden | collapsed | Bootstrap and setup |

`wm-essential` wins over output collapse. Source hiding is independent.

Use host adapters only when feature detection succeeds. They must fail open to normal
page scrolling and readable static output. Never hard-code a white dark-mode defense;
each card carries theme-aware surface, text, border, and accent tokens.

Keep GSAP, ScrollTrigger, Flip, Lenis, Three.js, and remote motion dependencies out of
the notebook runtime. Rich motion belongs in a separate static publisher whose semantic
HTML and final reading state remain complete without JavaScript.

Collapse behavior follows notebook intent, not visual size guesses. Scratch notebooks
may collapse raw diagnostics aggressively; takeover/share notebooks keep questions,
evidence, takeaways, verdicts, and human decisions open.
