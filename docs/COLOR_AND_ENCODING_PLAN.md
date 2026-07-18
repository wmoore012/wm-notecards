# Color and encoding plan

Color communicates meaning; it does not decorate model names.

## Default roles

| Role | Encoding |
|---|---|
| Primary observed series | near-black in light mode; near-white in dark mode |
| Focus/evidence | cyan accent |
| Comparison/support | blue or teal |
| Negative/failure | rose, only when the value is semantically negative |
| Warning/uncertainty | amber |
| Missing/not evaluated | neutral missingness fill |

Line style carries a second channel: solid for observations, dashed for forecasts or
counterfactuals, and dotted for baselines. Never require hue alone to distinguish two
series.

## SVD/authorship plan

Hamilton and Madison are categories, not good/bad outcomes. Give each author one
stable, similarly salient hue across SVD and MiniLM models. Use a neutral sand fill
for model disagreement and a neutral gray fill for missing/not-evaluated states.

Requirements:

- Keep author colors identical across tables, charts, legends, and direct labels.
- Add text or symbols to every colored classification cell.
- Reserve rose-as-error for actual error states; if rose represents an author, explain
  that categorical role and do not reuse it for failure in the same artifact.
- Check light mode, dark mode, grayscale, and common color-vision deficiencies.
- Use border or hatch differences when a screenshot/export could remove context.
- Never infer authorship certainty from saturation or darkness.

### Target categorical tokens

| Meaning | Target token | Hex | Secondary encoding |
|---|---|---:|---|
| Hamilton | `--wm-author-hamilton` | `#007C91` | `HAMILTON` text and teal left border |
| Madison | `--wm-author-madison` | `#6F4C9B` | `MADISON` text and violet left border |
| Model disagreement | `--wm-author-disagreement` | `#E8E1D2` | `No`/split label and sand fill |
| Missing/not evaluated | `--wm-missing` | `#D7D9DC` | em dash or `Not evaluated` label |

This pair avoids the runtime's rose failure and amber warning roles. The author hues
are deliberately similar in visual weight: neither author is encoded as the default,
the error, or the more-confident result.

### Migration gate

1. Define the four tokens once in the shared theme and remove notebook-local author
   hex values.
2. Update every SVD and MiniLM table, chart, legend, and direct label in one change.
3. Preserve author text plus the colored border; fill alone never carries identity.
4. Add snapshot/token tests that fail if failure rose is reused for an author.
5. Check light, dark, grayscale, deuteranopia, and printed/PDF output before release.

Until that migration is complete, the current rose-as-Madison artifact is
**conditionally readable but not palette-approved**. Direct labels prevent ambiguity,
but the screenshot must not be used as the canonical public example.
