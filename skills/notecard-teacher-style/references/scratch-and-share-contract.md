# Scratch and share notebook contract

Scratch and share notebooks solve different jobs. Do not force one file to impersonate
both.

## Scratch notebook

Use the scratch notebook as a visible workbench:

- keep quick checks, alternate hypotheses, failed-but-informative attempts, and raw
  diagnostics close to the code that produced them;
- collapse bootstrap, dependency logs, long summaries, and repeated audit output with
  explicit `wm-noise` or `wm-collapse-output` metadata;
- keep the small number of question, preview, warning/check, and next-think cards that
  record why the analysis changed direction;
- prefer rough but labeled evidence over polished unsupported claims;
- preserve source paths and private variables locally, but never carry them into a
  public build.

The scratch notebook may be uneven. It may not be ambiguous about provenance, split
logic, or what changed.

## Takeover / share notebook

Use the takeover notebook as the canonical reviewed story:

- question → answer → evidence → boundary → takeaway → human decision;
- one earned visual job per artifact;
- no duplicate experiments, stale outputs, private paths, tokens, or internal comments;
- deterministic cell order and a clean restart-and-run proof;
- setup source hidden only when the release notebook still explains how to reproduce it;
- output open by default for questions, evidence, takeaways, verdicts, and decisions.

Generate Colab and static-HTML releases from the takeover cell order. Do not manually
maintain a second story with slightly different prose.

## Naming

Name a public notebook by the learning promise, not the class number or private project
folder. Prefer `simple-seasonal-forecasting-lab` over `homework-4-final-v7`.
