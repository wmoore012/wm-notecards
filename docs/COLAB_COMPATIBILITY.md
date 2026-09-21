# Colab compatibility contract

Colab is a host adapter, not the source of truth. The canonical notebook keeps the cell
order and calculations. The builder only embeds public runtime files, clears execution
state, and applies presentation metadata declared by the author.

## Cell visibility tags

Add tags through the notebook cell metadata. The builder recognizes four values.

| Tag | Source | Output | Use for |
|---|---|---|---|
| `wm-essential` | unchanged | open | Questions, evidence, takeaways, verdicts, human decisions |
| `wm-hide-source` | hidden/form view | open | Readable cards whose implementation code is not the lesson |
| `wm-collapse-output` | unchanged | collapsed | Raw model summaries or long audit output |
| `wm-noise` | hidden/form view | collapsed | Bootstrap, package extraction, setup logs |

`wm-essential` wins when it appears with an output-collapse tag. Its output remains
open. Source visibility is independent, so an essential card may also use
`wm-hide-source`.

Untagged cells are preserved. The builder does not inspect prose, function names, or
output length to guess intent.

Example with `nbformat`:

```python
cell.metadata["tags"] = ["wm-essential", "wm-hide-source"]
```

## Output-frame expansion

`init_notebook()` feature-detects Colab's output host and asks rich-output iframes to
grow with their content, up to 5,000 pixels by default:

```python
init_notebook(
    expand_colab_outputs=True,
    colab_max_output_height=5_000,
)
```

The adapter uses a guarded resize observer. If the host API is missing or changes, the
call fails open and ordinary notebook scrolling remains available. Use a larger ceiling
only for a known long card. Prefer a bounded table or collapsed raw output over a
20,000-pixel cell.

## Host dark mode

Every shared shell declares its own surface, text, border, accent, and color-scheme
tokens. The global defense isolates those tokens from host rules without forcing all
cards to white. That means `WMTheme.light()` remains a deliberate light notecard in
Colab dark mode, while `WMTheme.dark()` remains a genuine dark theme.

Test both theme factories. Host dark mode is not permission to invert charts or table
cells after they have been rendered.

## Build policy

```bash
uv run python scripts/build_colab_bootstrap.py \
  --takeover notebooks/lesson.ipynb \
  --scratch notebooks/lesson_scratch.ipynb \
  --notebook-output dist/lesson_COLAB.ipynb
```

- Use `--skip-scratch` for a release notebook.
- Keep the generated helper tagged `wm-noise`.
- Scan embedded files for credentials, private paths, comments, and data.
- Execute a clean copy in an isolated directory before sharing.
- Verify at least one essential card, one collapsed raw output, one long table, and one
  figure card.

## Known boundary

Colab owns the outer notebook document and can change its private presentation
behavior. `wm-notecards` can request a better output height and provide standard
metadata; it cannot guarantee every Colab UI affordance. The fallback must always be a
readable card plus normal page scrolling.
