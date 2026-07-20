# Contributing

Thank you for helping make data-science notebooks easier to understand.

## Start with the teaching contract

A contribution should preserve this sequence:

1. Ask a decision-relevant question.
2. Give the direct answer early.
3. Show evidence that can be independently checked.
4. State uncertainty and conclusion boundaries.
5. Return the consequential next choice to the human.

Do not treat unusual behavior as proven fraud, causation as established by
correlation, or model output as a substitute for human judgment.

## Set up

```bash
uv sync --extra dev --extra svg
uv run pytest
```

## Before a pull request

```bash
uv run ruff check .
uv run mypy src
uv run pytest --cov=wm_notecards --cov-report=term-missing
uv build
```

Then complete `docs/OPEN_SOURCE_GRAPH_CHECKLIST.md` for every changed visual. A build,
an HTTP 200, and a successful click do not prove the notebook journey works. Inspect
the actual rendered end states at desktop and narrow widths.

## Pull request evidence

Include:

- the reader question and expected takeaway;
- the source and metric definition;
- before/after images for visible changes;
- desktop and narrow-width coverage;
- the tests added for the failure mode;
- any remaining limitations or unverified environments.

Never commit `.env`, credentials, proprietary datasets, private notebook paths, or
`.webapp-tester/` artifacts.
