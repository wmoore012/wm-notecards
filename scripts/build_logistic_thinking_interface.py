"""Build the public logistic-regression thinking-interface notebook.

Ordinary Markdown and Pandas output appear first; the corresponding notecard
response follows in the next cell. Screenshot-only notebook imitations are not
part of this builder.
"""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUTPUT = Path("examples/logistic_regression_thinking_interface.ipynb")


def _code(source: str, *, noise: bool = False) -> nbformat.NotebookNode:
    """Return a code cell with the public-example source visibility contract."""
    tags = ["wm-noise"] if noise else ["wm-essential", "wm-hide-source"]
    cell = new_code_cell(source)
    cell.metadata["tags"] = tags
    return cell


def build_notebook() -> nbformat.NotebookNode:
    """Return a deterministic, screenshot-ready logistic-regression notebook."""
    cells = [
        new_markdown_cell(
            """# Will this customer leave next month?

> I’m new here. Thank you for having me—I mean that. I’m learning in public,
> and this is the tool I needed while I was learning.

We are data scientists. We make visualizations for a living.

**Why are we still doing machine learning in MS-DOS?**

"""
        ),
        _code(
            """from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from wm_notecards import PreprocessingDecision, WMTheme, init_notebook, wm_build_preprocessing_log
from wm_notecards.cards import (
    preview_card,
    question_card,
    takeaway_card,
    wm_counterintuitive_card,
)
from wm_notecards.eda import display_data_chips
from wm_notecards.tables import (
    display_cols_by_dtype,
    wm_render_micro_profile_cards,
    wm_render_styler,
)

theme = WMTheme.light()
init_notebook()
RNG_SEED = 20260724""",
            noise=True,
        ),
        _code(
            """rng = np.random.default_rng(RNG_SEED)
rows = 1_200
signup_date = pd.Timestamp("2022-01-01") + pd.to_timedelta(
    rng.integers(0, 900, rows), unit="D"
)
tenure_months = np.maximum(
    1, ((pd.Timestamp("2025-01-01") - signup_date).days / 30.4).astype(int)
)
plan = rng.choice(["Starter", "Plus", "Pro"], rows, p=[0.48, 0.36, 0.16])
channel = rng.choice(["Direct", "Partner", "Community"], rows, p=[0.52, 0.29, 0.19])
region = rng.choice(["North", "South", "West", "East"], rows, p=[0.38, 0.27, 0.21, 0.14])
support_tickets = rng.poisson(1.2, rows)
sessions_30d = rng.poisson(8.5, rows)
days_since_login = np.clip(rng.gamma(2.1, 3.4, rows), 0, 45)
monthly_spend = np.round(
    rng.lognormal(3.25, 0.38, rows) + np.select(
        [plan == "Plus", plan == "Pro"], [18.0, 52.0], default=0.0
    ),
    2,
)
discount_rate = rng.choice([0.0, 0.10, 0.20], rows, p=[0.62, 0.27, 0.11])
renewal_month = rng.integers(1, 13, rows)

logit = (
    -2.55
    + 0.105 * days_since_login
    + 0.31 * support_tickets
    - 0.085 * sessions_30d
    - 0.013 * tenure_months
    + 0.95 * (plan == "Starter")
    - 0.70 * (plan == "Pro")
    + 0.72 * (discount_rate >= 0.20)
)
leave_probability = 1 / (1 + np.exp(-logit))
left_service = rng.binomial(1, leave_probability)

customers = pd.DataFrame({
    "customer_id": [f"CUS-{i:05d}" for i in range(rows)],
    "signup_date": signup_date.strftime("%Y-%m-%d"),
    "left_service": left_service,
    "plan": plan,
    "channel": channel,
    "region": region,
    "monthly_spend": monthly_spend.astype(str),
    "tenure_months": tenure_months,
    "sessions_30d": sessions_30d,
    "days_since_login": np.round(days_since_login, 1),
    "support_tickets": support_tickets,
    "discount_rate": discount_rate,
    "renewal_month": renewal_month.astype(str),
    "device": rng.choice(["Mobile", "Desktop", "Tablet"], rows, p=[0.61, 0.31, 0.08]),
    "browser": rng.choice(["Chrome", "Safari", "Firefox"], rows, p=[0.58, 0.28, 0.14]),
    "market": rng.choice(["US", "CA", "GB", "AU"], rows, p=[0.55, 0.20, 0.15, 0.10]),
    "campaign": rng.choice(["Organic", "Referral", "Launch"], rows, p=[0.51, 0.31, 0.18]),
    "email_opens_30d": rng.poisson(4.1, rows),
    "feature_clicks_30d": rng.poisson(12.5, rows),
    "invoices_paid": rng.poisson(8.2, rows),
    "late_payments_12m": rng.poisson(0.8, rows),
    "team_size": rng.integers(1, 75, rows),
    "projects_active": rng.integers(0, 18, rows),
    "storage_gb": np.round(rng.gamma(2.5, 8.0, rows), 1),
    "api_calls_30d": rng.integers(0, 9_000, rows),
    "exports_30d": rng.poisson(3.5, rows),
    "collaborators_30d": rng.integers(0, 22, rows),
    "mobile_sessions_30d": rng.poisson(4.5, rows),
    "desktop_sessions_30d": rng.poisson(5.0, rows),
    "help_articles_30d": rng.poisson(1.4, rows),
    "survey_score": rng.integers(1, 11, rows),
    "nps_group": rng.choice(["Detractor", "Passive", "Promoter"], rows, p=[0.24, 0.31, 0.45]),
    "autopay": rng.choice([True, False], rows, p=[0.72, 0.28]),
    "annual_plan": rng.choice([True, False], rows, p=[0.41, 0.59]),
    "used_onboarding": rng.choice([True, False], rows, p=[0.68, 0.32]),
    "admin_role": rng.choice([True, False], rows, p=[0.36, 0.64]),
    "comment": [f"synthetic account note {i}" for i in range(rows)],
    "source_note": [f"generated customer {i}" for i in range(rows)],
    "analyst_note": [f"review cohort {i % 8}" for i in range(rows)],
    "snapshot_month": "2025-01",
})
customers.loc[rng.choice(rows, 34, replace=False), "monthly_spend"] = None
customers.loc[rng.choice(rows, 19, replace=False), "region"] = None
customers.loc[rng.choice(rows, 27, replace=False), "comment"] = None

assert customers.shape == (rows, 40)
assert 0.10 < customers["left_service"].mean() < 0.45"""
        ),
        new_markdown_cell(
            """## Will this customer leave next month?

We will use account activity, subscription context, and support behavior to
predict whether a customer leaves in the next month."""
        ),
        _code(
            """question_card(
    theme=theme,
    title="Will this customer leave next month?",
    body=("Before we model anything: is leaving measured clearly, and did time, money, "
          "and category fields arrive in forms we can trust?"),
    kicker="01, source question",
)"""
        ),
        _code(
            """raw_preview = customers[[
    "customer_id", "signup_date", "left_service", "plan", "monthly_spend",
]].head(6)
raw_preview"""
        ),
        _code(
            """display_cols_by_dtype(
    customers.dtypes,
    theme,
    "Which fields arrived ready to model?",
    expected_types={
        "signup_date": "time",
        "monthly_spend": "numeric",
        "renewal_month": "numeric",
    },
)"""
        ),
        _code(
            """reviewed = customers.copy()
reviewed["signup_date"] = pd.to_datetime(reviewed["signup_date"], errors="raise")
reviewed["monthly_spend"] = pd.to_numeric(reviewed["monthly_spend"], errors="coerce")
reviewed["renewal_month"] = pd.to_numeric(reviewed["renewal_month"], errors="raise")

describe_columns = [
    "monthly_spend", "tenure_months", "sessions_30d", "days_since_login",
    "support_tickets",
]
reviewed[describe_columns].describe().round(2).T"""
        ),
        _code(
            """wm_render_micro_profile_cards(
    reviewed,
    theme=theme,
    columns=describe_columns,
    visible_cards=2,
    skew_threshold=1.0,
)"""
        ),
        _code(
            """missing_counts = reviewed.isna().sum().loc[lambda values: values.gt(0)].sort_values(ascending=False)
missing_counts.rename("missing").to_frame()"""
        ),
        _code(
            """missing_decisions = pd.DataFrame([
    {
        "field": "monthly_spend",
        "candidate": "training median + missing flag",
        "reason": "Right-skewed measure; keep the missing event visible.",
        "decision": "USE",
    },
    {
        "field": "region",
        "candidate": "confirm source meaning",
        "reason": "Unknown and not applicable are not the same category.",
        "decision": "WAIT",
    },
    {
        "field": "comment",
        "candidate": "leave missing",
        "reason": "Optional prose does not need an invented sentence.",
        "decision": "KEEP NULL",
    },
])
wm_render_styler(
    missing_decisions.style,
    theme=theme,
    title="What should happen to each gap?",
    kicker="02, missingness, human decision",
    wrap_columns={"candidate": 190, "reason": 280},
)"""
        ),
        _code(
            """split_at = int(len(reviewed) * 0.80)
train = reviewed.iloc[:split_at].copy()
validation = reviewed.iloc[split_at:].copy()
train_median = float(train["monthly_spend"].median())
prepared = reviewed.copy()
prepared["monthly_spend_missing"] = prepared["monthly_spend"].isna()
prepared["monthly_spend"] = prepared["monthly_spend"].fillna(train_median)

decision_log = wm_build_preprocessing_log(
    reviewed,
    prepared,
    [PreprocessingDecision(
        field="monthly_spend",
        action="impute",
        method=f"training median ({train_median:.2f})",
        reason="Preserve rows and keep a missingness indicator.",
        fit_scope="train_only",
        keep_missing_indicator=True,
    )],
)
decision_log"""
        ),
        _code(
            """wm_render_styler(
    decision_log.style,
    theme=theme,
    title="What did the training split decide to fill?",
    kicker="03, preprocessing, audit trail",
    wrap_columns={"method": 220, "reason": 260},
)"""
        ),
        new_markdown_cell(
            """## Model preparation

Exclude the customer ID. Use the first 80% of rows for training. Impute numerical
fields with the training median, scale numerical fields, and one-hot encode
categorical fields."""
        ),
        _code(
            """preview_card(
    theme=theme,
    title="The model gets behavior. The ID stays with the human.",
    body=("Training learns medians, scales, and categories. Validation only receives "
          "those decisions; it does not get to rewrite them."),
    bullets=[
        "Exclude customer_id: it identifies a row but does not describe behavior.",
        "Fit preprocessing on training rows only.",
        "Keep monthly_spend_missing beside the filled value.",
    ],
    kicker="04, model boundary",
)"""
        ),
        _code(
            """display_data_chips(
    prepared,
    theme=theme,
    target="left_service",
    identifier_columns=["customer_id"],
    datetime_columns=["signup_date"],
    categorical_columns=["plan", "channel", "region", "device", "market"],
)"""
        ),
        _code(
            """target = "left_service"
numeric_features = [
    "monthly_spend", "tenure_months", "sessions_30d", "days_since_login",
    "support_tickets", "discount_rate", "monthly_spend_missing",
]
categorical_features = ["plan", "channel", "region"]
behavior_features = [
    "tenure_months", "sessions_30d", "days_since_login", "support_tickets",
]


def _pipeline(numeric: list[str], categorical: list[str]) -> Pipeline:
    transformers: list[tuple[str, Any, list[str]]] = []
    if numeric:
        transformers.append((
            "numeric",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
                ("scale", StandardScaler()),
            ]),
            numeric,
        ))
    if categorical:
        transformers.append((
            "categorical",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encode", OneHotEncoder(handle_unknown="ignore")),
            ]),
            categorical,
        ))
    return Pipeline([
        ("prepare", ColumnTransformer(transformers)),
        ("model", LogisticRegression(max_iter=1_500, random_state=RNG_SEED)),
    ])


train = prepared.iloc[:split_at].copy()
validation = prepared.iloc[split_at:].copy()
model_specs = {
    "Activity only": (behavior_features, []),
    "Activity + account context": (numeric_features, categorical_features),
}
models: dict[str, Pipeline] = {}
score_rows: list[dict[str, float | str]] = []
for name, (numeric, categorical) in model_specs.items():
    features = numeric + categorical
    model = _pipeline(numeric, categorical)
    model.fit(train[features], train[target])
    probabilities = model.predict_proba(validation[features])[:, 1]
    predictions = (probabilities >= 0.50).astype(int)
    models[name] = model
    score_rows.append({
        "model": name,
        "accuracy": accuracy_score(validation[target], predictions),
        "ROC AUC": roc_auc_score(validation[target], probabilities),
        "PR AUC": average_precision_score(validation[target], probabilities),
        "precision @ .50": precision_score(validation[target], predictions, zero_division=0),
        "recall @ .50": recall_score(validation[target], predictions, zero_division=0),
    })

scores = pd.DataFrame(score_rows).sort_values("PR AUC", ascending=False).reset_index(drop=True)
assert scores["PR AUC"].between(0, 1).all()
assert scores.iloc[0]["model"] == 'Activity + account context'"""
        ),
        _code(
            """scores.round(3)"""
        ),
        _code(
            """wm_render_styler(
    scores.style.format({column: "{:.3f}" for column in scores.columns if column != "model"}),
    theme=theme,
    title="Which model survives validation?",
    subtitle="PR AUC leads because leaving is the less common outcome.",
    kicker="05, validation, evidence",
)"""
        ),
        _code(
            """winner_name = str(scores.iloc[0]["model"])
winner_numeric, winner_categorical = model_specs[winner_name]
winner_features = winner_numeric + winner_categorical
winner = models[winner_name]
winner_probability = winner.predict_proba(validation[winner_features])[:, 1]

threshold_rows = []
for threshold in [0.30, 0.40, 0.50, 0.60]:
    prediction = (winner_probability >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(validation[target], prediction).ravel()
    threshold_rows.append({
        "threshold": threshold,
        "precision": precision_score(validation[target], prediction, zero_division=0),
        "recall": recall_score(validation[target], prediction, zero_division=0),
        "false positives": int(fp),
        "missed leavers": int(fn),
    })
thresholds = pd.DataFrame(threshold_rows)
thresholds.round(3)"""
        ),
        new_markdown_cell(
            """## Accuracy can be misleading

Because most customers stay, a model can achieve high accuracy while missing many
customers who leave. Precision and recall have to stay in the conversation."""
        ),
        _code(
            """wm_counterintuitive_card(
    theme=theme,
    title="A higher accuracy can still lose the customers we meant to find.",
    why_misread=("The largest class is ‘stays.’ Predicting it often can make the headline "
                 "number look reassuring."),
    ordinary_process=("A 0.50 threshold favors certainty. It can leave uncertain—but useful—"
                      "retention candidates below the line."),
    conclusion_boundary=("Choose the threshold from the cost of a missed leaver and an "
                         "unnecessary outreach—not from accuracy alone."),
    kicker="06, threshold, conclusion boundary",
)"""
        ),
        _code(
            """wm_render_styler(
    thresholds.style.format({
        "threshold": "{:.2f}", "precision": "{:.1%}", "recall": "{:.1%}",
    }),
    theme=theme,
    title="What changes when recall matters more?",
    subtitle="Moving the threshold finds more leavers and also creates more outreach.",
    kicker="07, threshold, tradeoff",
)"""
        ),
        _code(
            """feature_names = winner.named_steps["prepare"].get_feature_names_out()
coefficients = pd.DataFrame({
    "feature": feature_names,
    "coefficient": winner.named_steps["model"].coef_[0],
})
coefficients["absolute weight"] = coefficients["coefficient"].abs()
top_coefficients = coefficients.nlargest(10, "absolute weight").drop(columns="absolute weight")
top_coefficients.round(3)"""
        ),
        _code(
            """wm_render_styler(
    top_coefficients.style.format({"coefficient": "{:+.3f}"}),
    theme=theme,
    title="Which signals move the probability most?",
    subtitle="Positive weights push toward leaving; negative weights push toward staying.",
    kicker="08, coefficients, evidence",
    wrap_columns={"feature": 260},
)"""
        ),
        new_markdown_cell(
            """## Conclusion

The account-context model performed best on the validation rows. Its probability
scores can rank a retention queue; they cannot make the outreach decision."""
        ),
        _code(
            """best = scores.iloc[0]
takeaway_card(
    theme=theme,
    title="The model earns a retention queue—not the right to make the decision.",
    metric=f"{winner_name} · validation PR AUC {best['PR AUC']:.3f}",
    body=("Account context adds useful separation on this synthetic hold-out. The score "
          "can rank outreach; it cannot tell us why a person left or whether contact is welcome."),
    bullets=[
        "Choose a threshold from outreach capacity and the cost of missed leavers.",
        "Monitor PR AUC and recall on later months before trusting the ranking.",
        "Keep the final action with the human team.",
    ],
    kicker="09, recommendation, your decision",
)"""
        ),
        new_markdown_cell(
            """---

Jupyter gave me `df.describe()`.

I wanted `df.explain()`.

The questions are predictable.

**The notebook should be too.**"""
        ),
    ]
    cells[0].metadata["tags"] = ["wm-essential"]
    cells[-1].metadata["tags"] = ["wm-essential"]
    return new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "wm-notecards",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3"},
        },
    )


def main() -> None:
    """Write the deterministic public notebook."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(build_notebook(), OUTPUT)
    print(f"Wrote {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
