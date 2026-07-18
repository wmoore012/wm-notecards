# Screenshot audit

This is the release record for the thirteen supplied notebook screenshots. A visual
does not pass because it is attractive or because its numbers look plausible. It
passes only when the claim, calculation, encoding, layout, provenance, and rendered
result are all supportable.

Status meanings:

- **Pass** — recomputed or structurally verified and safe within the stated scope.
- **Conditional** — usable only with the named disclosure or follow-up check.
- **Fail** — do not publish the pictured version.

| # | Artifact | Status | Evidence and required action |
|---:|---|---|---|
| 1 | Linear-trend forecast and takeaway | **Pass, bounded** | Recomputed holdout RMSE 606.8201, MAE 427.9007, MAPE 25.2636%; training trend R² 0.540088 and p=9.222e-28. The claim is appropriately limited: trend is real but misses the annual pattern. Disclose that this is one fixed Jan 1993–Dec 1994 holdout, not proof of future performance. |
| 2 | Trend/seasonal/residual decomposition | **Pass after label repair** | The code uses classical additive `seasonal_decompose(period=12)`, not STL. The source generator and notebook now say “Classical additive decomposition.” Treat it as descriptive structure, not a holdout score or causal separation. |
| 3 | Validation overlay | **Pass, bounded** | All series share the same 24-month holdout. The combined model is visibly and numerically strongest among the four pictured models. Keep line style and direct legend labels because hue is not the only channel. |
| 4 | Validation error table | **Pass** | Exact recomputation: trend+seasonality 337.7136/257.4824/14.2501%; linear trend 606.8201/427.9007/25.2636%; SES 688.4844/506.6523/31.7838%; seasonality 838.6621/762.2853/31.4759% for RMSE/MAE/MAPE. Values shown are correctly rounded. Add a seasonal-naive baseline before making a broader forecasting claim. |
| 5 | SES flat forecast | **Pass, bounded** | The flat multi-step path is expected for simple exponential smoothing without seasonal state. Fitted alpha is 0.649296. Do not describe the model as generally incapable; describe this specification on this horizon. |
| 6 | Seasonality-only forecast | **Pass, bounded** | The repeated within-year profile is consistent with the fitted monthly means. Its poor holdout error reflects omitted trend. Keep the training-only fit and fixed holdout explicit. |
| 7 | Trend + seasonality forecast | **Pass, bounded** | Recomputed as the best pictured holdout model; full trend p=4.482e-54. “Best of these four on this holdout” is supported; “best model” without that boundary is not. |
| 8 | Lute + peers city table | **Conditional** | The table correctly names empty-array platforms instead of zero-filling them, but release still requires a source/API snapshot date, uniqueness-key check, and duplicate-city explanation. The visible repeated Cordae rows make that validation mandatory. |
| 9 | Spotify country globe | **Conditional** | The globe needs a dated source, explicit definition of “chart-footprint gap,” unavailable-country encoding, and verification that pale land is not interpreted as zero. A globe is visually engaging but weak for precise country comparison; pair it with a ranked table or accessible list. |
| 10 | Top-N recommender cards | **Fail as pictured; repaired in source** | The original metrics treated every held-out rating as relevant (`ratingCutoff=0`). The library now defaults to rating ≥4 and has regression tests. With one relevant held-out item per user, Recall@K equals cHR and Precision@K equals cHR/K; those are protocol identities, not independent wins. The notebook must also disclose whether evaluation uses the exact candidate set or the popular-item candidate limit. |
| 11 | Christmas forecasting source/pictogram | **Fail as pictured** | 85/690 = 12.3188%, so the count itself is internally consistent, but the large blank card is a rendered-output failure. Release also needs the exact “conservatively labeled” rule, data window, and source provenance. Blank or missing browser output is never an acceptable exported state. |
| 12 | Four-model SVD/MiniLM authorship table | **Conditional, palette not approved** | Text labels and borders make the categories readable, but rose currently represents Madison while rose means failure elsewhere. Migrate to the categorical tokens in `COLOR_AND_ENCODING_PLAN.md`; do not imply confidence through fill darkness. “All four agree” means model agreement, not ground-truth correctness. |
| 13 | Rank-mass peer chart | **Fail as pictured; latest layout repaired** | The pictured x-axis labels collide and the `OPPORTUNITY` chip covers explanatory text. The latest source implementation uses reviewed top-10 horizontal views, and `wm-notecards` now auto-horizontalizes 10–24 named categories and rejects more than 24 without an explicit reviewed override. Chips wrap and cannot float over prose. |

## Cross-cutting release boundaries

- The forecasting screenshots compare four instructional models on one fixed holdout.
  They do not include uncertainty intervals, rolling-origin validation, or a
  seasonal-naive benchmark.
- API-derived music geography is not releasable without a dated snapshot, metric
  definition, and missingness policy.
- Recommender metrics are conditional on relevance and candidate-generation rules.
  State both beside the first result, not only in implementation notes.
- Classification colors encode category, not correctness or confidence.
- Every public example must pass the full
  [open-source graph checklist](OPEN_SOURCE_GRAPH_CHECKLIST.md) in its exported width,
  not only inside the author's notebook.
