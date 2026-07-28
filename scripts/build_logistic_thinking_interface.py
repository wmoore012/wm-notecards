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
            """# Can a logistic model find customers who may leave next month?

> I’m new here. Thank you for having me—I mean that. I’m learning in public,
> and this is the tool I needed while I was learning.

We are data scientists. We make visualizations for a living.

**Why are we still doing machine learning in MS-DOS?**

This public lab uses one deterministic synthetic customer file. Every rerun keeps
the same rows, the same missing values, and the same outcome-generating process,
so the story changes only when the analysis changes.

"""
        ),
        _code(
            """from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from wm_notecards import (
    PreprocessingDecision,
    WMTheme,
    init_notebook,
    wm_build_preprocessing_log,
)
from wm_notecards.cards import (
    question_card,
    takeaway_card,
    wm_counterintuitive_card,
    wm_formula_card,
)
from wm_notecards.charts import style_fig_wm, wm_render_figure_card
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
snapshot_month = np.repeat(pd.date_range("2024-01-01", periods=12, freq="MS"), 100)
signup_date = snapshot_month - pd.to_timedelta(rng.integers(45, 900, rows), unit="D")
tenure_months = np.maximum(1, ((snapshot_month - signup_date).days / 30.4).astype(int))
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
    "analyst_note": [f"review batch {i % 8}" for i in range(rows)],
    "snapshot_month": snapshot_month.strftime("%Y-%m-%d"),
})
customers.loc[rng.choice(rows, 34, replace=False), "monthly_spend"] = None
customers.loc[rng.choice(rows, 19, replace=False), "region"] = None
customers.loc[rng.choice(rows, 27, replace=False), "comment"] = None

assert customers.shape == (rows, 40)
assert 0.10 < customers["left_service"].mean() < 0.45"""
        ),
        new_markdown_cell(
            """## Can recent behavior separate customers who leave from customers who stay?

Account activity, subscription context, and support behavior are measured at one
monthly snapshot. The target records whether the customer leaves in the next month."""
        ),
        _code(
            """question_card(
    theme=theme,
    title="Can recent behavior separate customers who leave from customers who stay?",
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
reviewed["snapshot_month"] = pd.to_datetime(reviewed["snapshot_month"], errors="raise")
reviewed["monthly_spend"] = pd.to_numeric(reviewed["monthly_spend"], errors="coerce")
reviewed["renewal_month"] = pd.to_numeric(reviewed["renewal_month"], errors="raise")

describe_columns = [
    "monthly_spend", "tenure_months", "sessions_30d", "days_since_login",
    "support_tickets",
]
reviewed[describe_columns].describe().round(2).T"""
        ),
        _code(
            """source_checks = pd.DataFrame([
    {"check": "Rows loaded", "result": f"{len(reviewed):,}", "status": "PASS"},
    {"check": "Duplicate rows", "result": int(reviewed.duplicated().sum()), "status": "PASS"},
    {"check": "Duplicate customer IDs", "result": int(reviewed["customer_id"].duplicated().sum()), "status": "PASS"},
    {"check": "Target outside 0/1", "result": int((~reviewed["left_service"].isin([0, 1])).sum()), "status": "PASS"},
    {"check": "Unparsed observation months", "result": int(reviewed["snapshot_month"].isna().sum()), "status": "PASS"},
])
wm_render_styler(
    source_checks.style,
    theme=theme,
    title="Did the file arrive intact?",
    subtitle="Identity, target, and time checks pass before missingness gets its own decision.",
    kicker="02, source contract, checks",
)"""
        ),
        _code(
            """missing_counts = reviewed.isna().sum().loc[lambda values: values.gt(0)].sort_values(ascending=False)
missing_counts.rename("missing").to_frame()"""
        ),
        _code(
            """missing_summary = missing_counts.rename("missing").to_frame()
missing_summary["complete"] = len(reviewed) - missing_summary["missing"]
missing_summary["missing share"] = missing_summary["missing"] / len(reviewed)

missing_fig = go.Figure()
missing_fig.add_trace(go.Bar(
    x=missing_summary["complete"],
    y=missing_summary.index,
    orientation="h",
    marker_color="#D8DEE3",
    name="Complete",
    hovertemplate="%{y}: %{x:,} complete<extra></extra>",
))
missing_fig.add_trace(go.Bar(
    x=missing_summary["missing"],
    y=missing_summary.index,
    orientation="h",
    marker_color=theme.color_missing_accent,
    text=[
        f"{count:,} missing · {share:.1%}"
        for count, share in zip(
            missing_summary["missing"], missing_summary["missing share"], strict=True
        )
    ],
    textposition="outside",
    cliponaxis=False,
    name="Missing",
    hovertemplate="%{y}: %{x:,} missing<extra></extra>",
))
missing_fig.update_layout(barmode="stack", showlegend=False)
missing_fig.update_xaxes(title="Rows", range=[0, len(reviewed) * 1.16], tickformat=",")
missing_fig.update_yaxes(autorange="reversed", title=None)
style_fig_wm(
    missing_fig,
    theme=theme,
    title="Most fields are complete. Three are not.",
    subtitle="Gold marks the exact gaps the preprocessing decision must account for",
    category_policy="preserve",
)
wm_render_figure_card(
    missing_fig,
    theme=theme,
    file_stub="logistic_missingness_first_pass",
    kicker="02, missingness, evidence",
)"""
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
    missing_decisions[["field", "candidate", "decision"]].style,
    theme=theme,
    title="What should happen to each gap?",
    subtitle="The chart above finds every gap; this receipt records the next action.",
    kicker="02, missingness, human decision",
    wrap_columns={"candidate": 220},
)"""
        ),
        _code(
            """display_data_chips(
    reviewed,
    theme=theme,
    target="left_service",
    identifier_columns=["customer_id"],
    datetime_columns=["signup_date"],
    categorical_columns=["plan", "channel", "region", "device", "market"],
)"""
        ),
        _code(
            """target_counts = (
    reviewed["left_service"]
    .map({0: "Stayed", 1: "Left next month"})
    .value_counts()
    .rename_axis("outcome")
    .reset_index(name="customers")
)
target_counts["share"] = target_counts["customers"] / len(reviewed)
target_counts"""
        ),
        _code(
            """target_fig = go.Figure(go.Bar(
    x=target_counts["outcome"],
    y=target_counts["customers"],
    marker_color=["#D8DEE3", theme.accent],
    text=[f"{count:,} · {share:.1%}" for count, share in zip(
        target_counts["customers"], target_counts["share"], strict=True
    )],
    textposition="outside",
    cliponaxis=False,
    hovertemplate="%{x}: %{y:,} customers<extra></extra>",
))
target_fig.update_xaxes(title=None)
target_fig.update_yaxes(title="Customers", rangemode="tozero")
style_fig_wm(
    target_fig,
    theme=theme,
    title="Leaving is the smaller outcome—but not a tiny one",
    subtitle="The validation metrics must reward finding leavers, not merely predicting the majority",
    category_policy="preserve",
)
wm_render_figure_card(
    target_fig,
    theme=theme,
    file_stub="logistic_target_balance",
    kicker="03, target balance, evidence",
)"""
        ),
        _code(
            """wm_render_micro_profile_cards(
    reviewed,
    theme=theme,
    columns=[
        "monthly_spend", "tenure_months", "sessions_30d",
        "days_since_login", "support_tickets",
    ],
    visible_cards=3,
    skew_threshold=1.0,
)"""
        ),
        _code(
            """numeric_by_outcome = reviewed.assign(
    outcome=reviewed["left_service"].map({0: "Stayed", 1: "Left next month"})
)
relationship_fig = go.Figure()
for outcome, color in [("Stayed", "#AAB5BD"), ("Left next month", theme.accent)]:
    values = numeric_by_outcome.loc[
        numeric_by_outcome["outcome"].eq(outcome), "days_since_login"
    ]
    relationship_fig.add_trace(go.Box(
        y=values,
        name=outcome,
        marker_color=color,
        boxpoints="outliers",
        hovertemplate=f"{outcome}<br>Days since login: %{{y:.1f}}<extra></extra>",
    ))
relationship_fig.update_yaxes(title="Days since last login")
relationship_fig.update_xaxes(title=None)
style_fig_wm(
    relationship_fig,
    theme=theme,
    title="Customers who leave have usually been away longer",
    subtitle="The box shows the middle half; points beyond the whiskers remain visible",
    category_policy="preserve",
)
wm_render_figure_card(
    relationship_fig,
    theme=theme,
    file_stub="logistic_days_since_login_by_outcome",
    kicker="03, numeric relationship, evidence",
)"""
        ),
        _code(
            """wm_render_micro_profile_cards(
    reviewed,
    theme=theme,
    columns=["plan", "channel", "region"],
    visible_cards=3,
)"""
        ),
        _code(
            """plan_rates = (
    reviewed.groupby("plan", dropna=False)["left_service"]
    .agg(customers="size", leavers="sum", leave_rate="mean")
    .sort_values("leave_rate", ascending=True)
    .reset_index()
)
plan_rates"""
        ),
        _code(
            """plan_fig = go.Figure(go.Bar(
    x=plan_rates["leave_rate"],
    y=plan_rates["plan"],
    orientation="h",
    marker_color=["#B9C4CB", "#82DCE8", theme.accent],
    text=[
        f"{rate:.1%} · {leavers}/{customers}"
        for rate, leavers, customers in zip(
            plan_rates["leave_rate"], plan_rates["leavers"],
            plan_rates["customers"], strict=True
        )
    ],
    textposition="outside",
    cliponaxis=False,
    hovertemplate="%{y}: %{x:.1%}<extra></extra>",
))
plan_fig.update_xaxes(title="Leave rate", tickformat=".0%", rangemode="tozero")
plan_fig.update_yaxes(title=None)
style_fig_wm(
    plan_fig,
    theme=theme,
    title="Starter-plan customers leave more often in this sample",
    subtitle="Rates include both numerator and denominator so a small group cannot look louder than it is",
    category_policy="preserve",
)
wm_render_figure_card(
    plan_fig,
    theme=theme,
    file_stub="logistic_plan_leave_rate",
    kicker="03, categorical relationship, evidence",
)"""
        ),
        _code(
            """eda_takeaway = takeaway_card(
    theme=theme,
    title="Three clues earn the modeling test: absence, support friction, and plan context.",
    metric=f"Leave rate: {reviewed['left_service'].mean():.1%}",
    body=("Customers who left had usually been away longer, while plan groups did not "
          "share one common leave rate. These are associations in synthetic data—not causes."),
    bullets=[
        "Missing monthly spend stays visible through a missingness indicator.",
        "Days since login and support tickets are candidate behavior signals.",
        "Plan is context worth testing, not a reason to contact someone by itself.",
    ],
    kicker="03, EDA, takeaway",
)"""
        ),
        _code(
            """association_rows = []
for field in [
    "monthly_spend", "tenure_months", "sessions_30d",
    "days_since_login", "support_tickets", "discount_rate",
]:
    complete = reviewed[[field, "left_service"]].dropna()
    association_rows.append({
        "field": field,
        "correlation with leaving": complete[field].corr(complete["left_service"]),
    })
numeric_associations = (
    pd.DataFrame(association_rows)
    .assign(magnitude=lambda frame: frame["correlation with leaving"].abs())
    .sort_values("magnitude", ascending=True)
)
numeric_associations.drop(columns="magnitude").round(3)"""
        ),
        _code(
            """association_fig = go.Figure(go.Bar(
    x=numeric_associations["correlation with leaving"],
    y=numeric_associations["field"],
    orientation="h",
    marker_color=[
        theme.accent if value >= 0 else "#6B7B88"
        for value in numeric_associations["correlation with leaving"]
    ],
    text=[f"{value:+.2f}" for value in numeric_associations["correlation with leaving"]],
    textposition="outside",
    cliponaxis=False,
    hovertemplate="%{y}: %{x:+.3f}<extra></extra>",
))
association_fig.add_vline(x=0, line_color="#38444D", line_width=1)
association_fig.update_xaxes(title="Pearson correlation with leaving", range=[-0.35, 0.45])
association_fig.update_yaxes(title=None)
style_fig_wm(
    association_fig,
    theme=theme,
    title="Recent absence has the clearest one-field relationship with leaving",
    subtitle="Direction is descriptive, not causal; the model still has to survive later months",
    category_policy="preserve",
)
wm_render_figure_card(
    association_fig,
    theme=theme,
    file_stub="logistic_numeric_target_associations",
    kicker="03, numeric relationships, evidence",
)"""
        ),
        _code(
            """feature_ledger = pd.DataFrame([
    {
        "field": "customer_id",
        "observed evidence": "Unique on every row.",
        "allowed role": "Review lookup only",
        "candidate transformation": "None",
        "validation test": "Confirm exclusion from model matrix.",
        "boundary": "Direct identifier; do not learn customer identity.",
        "decision": "EXCLUDE",
    },
    {
        "field": "signup_date",
        "observed evidence": "A customer signup date.",
        "allowed role": "Time context",
        "candidate transformation": "Signup month or tenure",
        "validation test": "Fit derived rules on training rows only.",
        "boundary": "Raw date can proxy product or campaign changes.",
        "decision": "DERIVE",
    },
    {
        "field": "region",
        "observed evidence": "19 missing values; four named markets.",
        "allowed role": "Candidate context",
        "candidate transformation": "Training-only category encoding",
        "validation test": "Compare PR and error slices with/without region.",
        "boundary": "Review geographic proxy and fairness risk.",
        "decision": "TEST",
    },
    {
        "field": "comment",
        "observed evidence": "Free text with 27 missing values.",
        "allowed role": "Human review context",
        "candidate transformation": "Separate text study",
        "validation test": "No text enters this baseline model.",
        "boundary": "May contain private or post-outcome information.",
        "decision": "HOLD OUT",
    },
])
feature_ledger"""
        ),
        _code(
            """feature_receipt = feature_ledger[[
    "field", "decision", "observed evidence", "validation test"
]].rename(columns={
    "observed evidence": "evidence",
    "validation test": "next check",
})
wm_render_styler(
    feature_receipt.style,
    theme=theme,
    title="What enters the model, what changes form, and what stays out?",
    subtitle="The full ledger remains in the dataframe; this is the decision-sized view.",
    kicker="04, feature decision ledger",
    wrap_columns={
        "evidence": 230,
        "next check": 260,
    },
)"""
        ),
        new_markdown_cell(
            """## Can the model learn without seeing the future?

January through September teach the preprocessing and coefficients. October
through December stay untouched until validation."""
        ),
        _code(
            """question_card(
    theme=theme,
    title="Can the model learn without seeing the future?",
    body=("A random row split would let later observation months influence earlier ones. "
          "We keep the last three months intact and carry training decisions forward."),
    kicker="04, time split, question",
)"""
        ),
        _code(
            """validation_start = pd.Timestamp("2024-10-01")
train = reviewed.loc[reviewed["snapshot_month"] < validation_start].copy()
validation = reviewed.loc[reviewed["snapshot_month"] >= validation_start].copy()
assert train["snapshot_month"].max() < validation["snapshot_month"].min()

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
    title="What did training fill—and what stayed missing?",
    subtitle="Only monthly spend is filled here; region and comment keep their original gaps.",
    kicker="04, preprocessing, audit trail",
    wrap_columns={"method": 220, "reason": 260},
)"""
        ),
        _code(
            """split_summary = pd.DataFrame([
    {
        "split": "Training",
        "months": "Jan–Sep 2024",
        "rows": len(train),
        "purpose": "Learn preprocessing and model coefficients",
    },
    {
        "split": "Validation",
        "months": "Oct–Dec 2024",
        "rows": len(validation),
        "purpose": "Compare models and choose an outreach threshold",
    },
])
split_summary"""
        ),
        _code(
            """split_fig = go.Figure()
split_fig.add_trace(go.Scatter(
    x=[pd.Timestamp("2024-01-01"), pd.Timestamp("2024-09-30")],
    y=["Training", "Training"],
    mode="lines+markers+text",
    line={"color": "#222A31", "width": 28},
    marker={"color": "#222A31", "size": 18},
    text=["", f"Jan–Sep · {len(train):,} rows"],
    textposition="top left",
    hovertemplate="Training: Jan–Sep 2024<extra></extra>",
))
split_fig.add_trace(go.Scatter(
    x=[validation_start, pd.Timestamp("2024-12-31")],
    y=["Validation", "Validation"],
    mode="lines+markers+text",
    line={"color": theme.accent, "width": 28},
    marker={"color": theme.accent, "size": 18},
    text=["", f"Oct–Dec · {len(validation):,} rows"],
    textposition="top left",
    hovertemplate="Validation: Oct–Dec 2024<extra></extra>",
))
split_fig.update_layout(showlegend=False)
split_fig.update_xaxes(title="Observation month", tickformat="%b %Y")
split_fig.update_yaxes(title=None, categoryorder="array", categoryarray=["Validation", "Training"])
style_fig_wm(
    split_fig,
    theme=theme,
    title="The model learns from nine months. The last three stay untouched.",
    subtitle="Every preprocessing choice is fitted on Jan–Sep, then carried forward into Oct–Dec",
    category_policy="preserve",
)
wm_render_figure_card(
    split_fig,
    theme=theme,
    file_stub="logistic_chronological_split",
    kicker="04, chronological split, evidence",
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
model_specs = {
    "Activity only": (behavior_features, []),
    "Activity + account context": (numeric_features, categorical_features),
}
model_contract = pd.DataFrame([
    {
        "model": name,
        "numeric fields": len(numeric),
        "categorical fields": len(categorical),
        "question": (
            "Does recent behavior separate leavers?"
            if name == "Activity only"
            else "Does account context add useful separation?"
        ),
    }
    for name, (numeric, categorical) in model_specs.items()
])
model_contract"""
        ),
        _code(
            """wm_render_styler(
    model_contract.style,
    theme=theme,
    title="What does each challenger get to know?",
    subtitle="The second model must beat behavior alone to justify the added context.",
    kicker="05, model contract, challengers",
    wrap_columns={"question": 300},
)"""
        ),
        _code(
            r'''wm_formula_card(
    title="Two preparation lanes meet at one logistic model",
    theme=theme,
    items=[
        {
            "label": "NUMERIC LANE",
            "latex": r"x_{num} \\rightarrow \\operatorname{median}_{train} \\rightarrow \\operatorname{scale}",
            "fallback": "numeric -> training median -> standard scale",
        },
        {
            "label": "CATEGORY LANE",
            "latex": r"x_{cat} \\rightarrow \\operatorname{mode}_{train} \\rightarrow \\operatorname{one\\!-\\!hot}",
            "fallback": "category -> training mode -> one-hot columns",
        },
        {
            "label": "MODEL",
            "latex": r"P(y=1 \\mid x)=\\sigma(\\beta_0 + x^T\\beta)",
            "fallback": "prepared fields -> probability of leaving next month",
        },
    ],
    subtitle="Every learned value comes from Jan–Sep; Oct–Dec only receives the result.",
    kicker="05, preprocessing, contract",
)'''
        ),
        _code(
            """def _pipeline(numeric: list[str], categorical: list[str]) -> Pipeline:
    \"\"\"Build one leakage-safe preprocessing and logistic-regression path.\"\"\"
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
    ])""",
            noise=True,
        ),
        _code(
            """train = prepared.loc[prepared["snapshot_month"] < validation_start].copy()
validation = prepared.loc[prepared["snapshot_month"] >= validation_start].copy()
assert train["snapshot_month"].max() < validation["snapshot_month"].min()

models: dict[str, Pipeline] = {}
model_probabilities: dict[str, np.ndarray] = {}
for name, (numeric, categorical) in model_specs.items():
    features = numeric + categorical
    model = _pipeline(numeric, categorical)
    model.fit(train[features], train[target])
    probabilities = model.predict_proba(validation[features])[:, 1]
    models[name] = model
    model_probabilities[name] = probabilities
fit_receipt = pd.DataFrame({
    "model": list(models),
    "training rows": len(train),
    "validation rows": len(validation),
    "fit status": "fitted",
})
fit_receipt"""
        ),
        _code(
            """score_rows: list[dict[str, float | str]] = []
for name, probabilities in model_probabilities.items():
    predictions = (probabilities >= 0.50).astype(int)
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
scores.round(3)"""
        ),
        _code(
            """validation_prevalence = float(validation[target].mean())
prevalence_receipt = pd.DataFrame([{
    "validation rows": len(validation),
    "leavers": int(validation[target].sum()),
    "stayers": int((validation[target] == 0).sum()),
    "leave prevalence": validation_prevalence,
    "outcome prevalence": validation_prevalence,
}])
prevalence_receipt"""
        ),
        _code(
            """wm_render_styler(
    prevalence_receipt.style.format({
        "leave prevalence": "{:.1%}",
        "outcome prevalence": "{:.1%}",
    }),
    theme=theme,
    title="How hard is the less-common outcome before a model gets credit?",
    subtitle="A random ranking starts at the share of validation customers who left.",
    kicker="05, target prevalence, evidence",
)"""
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
            """pr_fig = go.Figure()
for model_name, probabilities in model_probabilities.items():
    precision_values, recall_values, _ = precision_recall_curve(
        validation[target], probabilities
    )
    pr_fig.add_trace(go.Scatter(
        x=recall_values,
        y=precision_values,
        mode="lines",
        name=model_name,
        line={"width": 3},
    ))
pr_fig.add_hline(
    y=validation_prevalence,
    line_dash="dash",
    line_color="#38444D",
    annotation_text=f"Outcome prevalence: {validation_prevalence:.1%}",
    annotation_position="bottom right",
)
pr_fig.update_xaxes(title="Recall", tickformat=".0%", range=[0, 1])
pr_fig.update_yaxes(title="Precision", tickformat=".0%", range=[0, 1])
style_fig_wm(
    pr_fig,
    theme=theme,
    title="How much precision survives as we ask the model to find more leavers?",
    subtitle=f"Validation only · {len(validation):,} customers · dashed line = random-ranking precision",
)
wm_render_figure_card(
    pr_fig,
    theme=theme,
    file_stub="logistic_precision_recall",
    kicker="05, precision recall, validation",
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
        _code(
            """threshold_fig = go.Figure()
threshold_fig.add_trace(go.Scatter(
    x=thresholds["threshold"],
    y=thresholds["precision"],
    mode="lines+markers",
    name="Precision",
    line={"width": 3, "color": theme.accent},
))
threshold_fig.add_trace(go.Scatter(
    x=thresholds["threshold"],
    y=thresholds["recall"],
    mode="lines+markers",
    name="Recall",
    line={"width": 3, "color": "#B74C5F"},
))
threshold_fig.update_xaxes(title="Outreach threshold", tickformat=".0%")
threshold_fig.update_yaxes(title="Share", tickformat=".0%", range=[0, 1])
style_fig_wm(
    threshold_fig,
    theme=theme,
    title="Lowering the threshold finds more leavers—and contacts more stayers",
    subtitle="Validation evidence · exact false-positive and missed-leaver counts remain in the table",
)
wm_render_figure_card(
    threshold_fig,
    theme=theme,
    file_stub="logistic_threshold_tradeoff",
    kicker="07, threshold, visual tradeoff",
)"""
        ),
        _code(
            """selected_threshold = 0.40
selected_prediction = (winner_probability >= selected_threshold).astype(int)
selected_tn, selected_fp, selected_fn, selected_tp = confusion_matrix(
    validation[target], selected_prediction
).ravel()
confusion_receipt = pd.DataFrame([
    {"actual": "Stayed", "predicted stayed": selected_tn, "predicted left": selected_fp},
    {"actual": "Left", "predicted stayed": selected_fn, "predicted left": selected_tp},
])
assert int(confusion_receipt[["predicted stayed", "predicted left"]].to_numpy().sum()) == len(validation)
confusion_receipt"""
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
            """wm_render_styler(
    confusion_receipt.style,
    theme=theme,
    title="At 0.40, who receives outreach—and who gets missed?",
    subtitle=f"Validation confusion counts · threshold {selected_threshold:.2f} · n={len(validation):,}",
    kicker="07, confusion counts, selected threshold",
)"""
        ),
        _code(
            """confusion_values = np.array([
    [selected_tn, selected_fp],
    [selected_fn, selected_tp],
])
confusion_fig = go.Figure(go.Heatmap(
    z=confusion_values,
    x=["Predicted stayed", "Predicted left"],
    y=["Actually stayed", "Actually left"],
    text=confusion_values,
    texttemplate="%{text:,}",
    colorscale=[[0, "#F4F5F2"], [1, theme.accent]],
    showscale=False,
    hovertemplate="%{y}<br>%{x}: %{z:,}<extra></extra>",
))
confusion_fig.update_yaxes(autorange="reversed", title=None)
confusion_fig.update_xaxes(title=None)
style_fig_wm(
    confusion_fig,
    theme=theme,
    title="At 0.40, who receives outreach—and who gets missed?",
    subtitle=f"Validation counts · threshold {selected_threshold:.2f} · n={len(validation):,}",
    category_policy="preserve",
)
wm_render_figure_card(
    confusion_fig,
    theme=theme,
    file_stub="logistic_confusion_matrix",
    kicker="07, confusion matrix, selected threshold",
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
        _code(
            """coefficient_plot = top_coefficients.sort_values("coefficient")
coefficient_fig = go.Figure(go.Bar(
    x=coefficient_plot["coefficient"],
    y=coefficient_plot["feature"],
    orientation="h",
    marker_color=[
        theme.accent if value > 0 else "#6B7B88"
        for value in coefficient_plot["coefficient"]
    ],
    text=[f"{value:+.2f}" for value in coefficient_plot["coefficient"]],
    textposition="outside",
    cliponaxis=False,
    hovertemplate="%{y}<br>coefficient %{x:+.3f}<extra></extra>",
))
coefficient_fig.add_vline(x=0, line_color="#38444D", line_width=1)
coefficient_fig.update_xaxes(title="Logistic coefficient after preprocessing")
coefficient_fig.update_yaxes(title=None)
style_fig_wm(
    coefficient_fig,
    theme=theme,
    title="Which fitted signals push the score up—or pull it down?",
    subtitle="Positive weights move toward leaving; negative weights move toward staying",
    category_policy="preserve",
)
wm_render_figure_card(
    coefficient_fig,
    theme=theme,
    file_stub="logistic_coefficient_directions",
    kicker="08, coefficients, visual evidence",
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
