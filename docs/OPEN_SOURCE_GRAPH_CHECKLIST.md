# Open-source graph and notecard release checklist

Every changed graph must pass every applicable item. Record `N/A` with a reason; do
not silently skip a section. A notebook is not ready because it runs—the rendered
reader journey must be observed.

## 1. Question and claim

- [ ] The section begins with a real question or decision, not a topic label.
- [ ] The title gives the direct answer or the exact question.
- [ ] The subtitle explains how to read the evidence, defines the window, or states a
      material boundary.
- [ ] The takeaway answers the opening question without introducing new evidence.
- [ ] The claim is no stronger than the computed result.
- [ ] Correlation, association, prediction, and causation are not conflated.
- [ ] Anomaly/risk language says “signal,” “review,” or “unusual” unless proof exists.
- [ ] The next consequential choice remains explicit and human-owned.

## 2. Source and data quality

- [ ] Source, extraction date, unit of observation, and population are documented.
- [ ] Filters, exclusions, joins, deduplication, and missing-data treatment are stated.
- [ ] Before action, missingness evidence offers bounded candidate methods and keeps the
      decision human-owned. After action, the log names every affected field,
      method/fill value, training-only fit scope, before/after counts, and any retained
      missingness indicator. A no-op does not receive a ceremonial decision card.
- [ ] Row counts reconcile before and after transformations.
- [ ] Category coverage and unknown/unmapped values are reported.
- [ ] Time zones, currencies, units, and date frequencies are explicit.
- [ ] Duplicate entity-period records and impossible values are checked.
- [ ] Example/public data is licensed and contains no private identifiers.
- [ ] Empty API arrays are labeled as missing/unavailable, never silently zero-filled.

## 3. Math and model validity

- [ ] Values are recomputed from the displayed source—not copied from prose.
- [ ] Denominators, signs, units, and aggregation levels are verified.
- [ ] Percentages reconcile to counts; rounding does not change the conclusion.
- [ ] Train/validation/test windows are non-overlapping and chronologically correct.
- [ ] Feature fitting, thresholds, scaling, and imputation use training data only.
- [ ] The baseline is appropriate for the decision and forecast horizon.
- [ ] Metrics use the correct direction (`lower is better` vs `higher is better`).
- [ ] MAPE is not used without addressing zero/near-zero actuals.
- [ ] R² is labeled in-sample or out-of-sample and is not treated as generalization
      proof by itself.
- [ ] Time-series decomposition is labeled descriptive and its period/model form is
      justified.
- [ ] Seasonal forecasts preserve the intended trend/level logic; a “seasonality only”
      line is not accidentally a de-trended residual.
- [ ] Recommender metrics define candidate set, relevance, K, tie handling, and the
      random baseline; a surprising random winner triggers an implementation audit.
- [ ] Top-N leader tables handle ties and metric direction correctly.
- [ ] Model comparisons use the same rows, targets, splits, and preprocessing.
- [ ] Uncertainty, sample size, and sensitivity analysis are shown when they can change
      the decision.

## 4. Visual encoding and color

- [ ] Encodings match the question: position/length before area or decorative color.
- [ ] Preattentive order is deliberate: the answer/decision is strongest, evidence is
      next, and metadata is quiet; not every element competes for attention.
- [ ] A categorical palette is not used as an ordered scale, or vice versa.
- [ ] Color meaning is stable across the notebook.
- [ ] Red/green is not the sole distinction.
- [ ] Forecasts/baselines use line style as well as hue.
- [ ] SVD/authorship categories follow `COLOR_AND_ENCODING_PLAN.md`.
- [ ] Legends and direct labels agree with the plotted traces.
- [ ] Axis titles include units; titles do not repeat axis labels.
- [ ] Zero baselines are used when bar length is being compared.
- [ ] Truncated axes are deliberate, disclosed, and do not exaggerate gaps.
- [ ] Ordering is intentional (value, time, category flow, or teaching sequence).
- [ ] More than 24 named categories is rejected unless top-N/faceting is explicitly
      reviewed; 10–24 named vertical bars become horizontal by default.

## 5. Layout and typography

- [ ] No category labels overlap, stack, clip, or require guessing.
- [ ] Long labels wrap at sensible word boundaries.
- [ ] Header chips wrap and never cover titles, subtitles, annotations, or legends.
- [ ] Annotations remain inside their intended panel at narrow width.
- [ ] The plotting area remains large enough after titles, legends, and color bars.
- [ ] Table text is professionally aligned: labels left, numbers/dates right.
- [ ] Neutral multi-row tables have visible alternating row shades; semantic fills
      override zebra banding only when the fill carries defined meaning.
- [ ] Tables stretch to content and expose both scroll directions when needed.
- [ ] Long tables have a bounded viewport and sticky header; short tables do not gain
      an unnecessary vertical scrollbar.
- [ ] Font roles are consistent: display for headings, mono for metadata/numbers.
- [ ] Card padding, rule widths, radii, and spacing use shared tokens.
- [ ] Notecards keep their paper border and rest flat; elevation appears only on hover.
- [ ] Data/status chips are borderless with crisp text; semantic halos do not blur the
      label itself.
- [ ] Empty, loading, error, and no-data states occupy intentional space—never a blank
      white card.

## 6. Accessibility and interaction

- [ ] Text and essential marks meet WCAG AA contrast at their rendered size.
- [ ] Meaning survives grayscale and common color-vision deficiencies.
- [ ] Keyboard users can focus and scroll overflow regions.
- [ ] SVG/plot output has a useful accessible name or surrounding explanation.
- [ ] Hover content is supplementary; the conclusion is visible without hovering.
- [ ] Motion is subtle, never blocks reading, and respects `prefers-reduced-motion`.
- [ ] The card remains understandable at 200% zoom.
- [ ] Focus indicators and scrollbars remain visible.

## 7. Notebook and browser proof

- [ ] Restart-kernel/run-all completes from the declared environment.
- [ ] The correct kernel and rendering proof are documented.
- [ ] Desktop output was observed, not inferred from a successful test.
- [ ] Narrow/mobile output was observed, including horizontal and vertical scrolling.
- [ ] Light and dark notebook modes were observed where supported.
- [ ] Colab output was observed when the artifact is advertised as Colab-ready.
- [ ] Blank-card, duplicate-border, and out-of-shell fallbacks are absent.
- [ ] A regression test covers each fixed rendering bug when practical.
- [ ] Private `.webapp-tester/` artifacts are ignored and not staged.

## 8. Export and privacy

- [ ] SVG export is visually correct and editable.
- [ ] PNG export is legible at slide/social dimensions and at 1× viewing size.
- [ ] PDF export is checked when print is supported.
- [ ] Exported fonts fall back cleanly on a machine without local author fonts.
- [ ] Cropping includes the full title, subtitle, legend, annotation, and source note.
- [ ] Notebook outputs, metadata, and embedded files contain no secrets or local paths.
- [ ] Internal product names, proprietary comments, and private variables are removed
      from the public runtime/example unless intentionally documented.
- [ ] Generated files are reproducible from committed inputs.

## 9. Final gate

- [ ] Ruff passes.
- [ ] Strict mypy passes.
- [ ] Tests pass at or above the configured coverage threshold.
- [ ] Wheel and source distribution build without warnings.
- [ ] The distributable skill validates.
- [ ] Every declared downstream vendored runtime is byte-for-byte synchronized.
- [ ] An independent reviewer has checked the diff, math boundaries, and screenshots.
- [ ] Known limitations are written down rather than hidden.
