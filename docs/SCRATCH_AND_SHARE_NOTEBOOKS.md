# Scratch notebook, share notebook

One notebook should not have to be both a laboratory bench and a finished lesson.

## Scratch is where the thinking moves

A scratch notebook keeps quick checks, alternate hypotheses, failed-but-informative
attempts, and raw diagnostics near the code that produced them. It can be uneven. It
cannot be vague about provenance, split logic, or silent data changes.

Use a few notecards as durable trail markers:

- **Question:** what are we testing right now?
- **Check / limitation:** what broke, changed, or cannot be claimed?
- **Next-think:** what earned another pass?

Collapse dependency logs, repeated summaries, and other visual noise with explicit
`wm-noise` or `wm-collapse-output` tags. Do not polish every experiment into a card.

## Share is where the argument holds still

The takeover/share notebook is the canonical reviewed story:

> question → direct answer → evidence → boundary → takeaway → human decision

It has deterministic cell order, no stale output, no private paths or tokens, and a
clean restart-and-run proof. Questions, evidence, takeaways, verdicts, and decisions
stay open. Colab and static HTML are generated from this notebook rather than maintained
as slightly different stories.

Name a public notebook by its learning promise. `Simple Seasonal Forecasting Lab` tells
a new reader more than `Homework_4_WM_Final` ever could.
