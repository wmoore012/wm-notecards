"""Opinionated, non-mutating EDA helpers for notebook teaching flows.

The helpers in this module inspect a dataframe and make the decisions that still
belong to a human visible.  They never impute, coerce, drop, scale, or otherwise
change the caller's data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape
from typing import TYPE_CHECKING, Any, Literal, cast

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from IPython.display import HTML, display

from wm_notecards._html import rgba_css
from wm_notecards.cards import question_card
from wm_notecards.tables import wm_render_micro_profile_cards, wm_render_styler

if TYPE_CHECKING:
    from collections.abc import Hashable, Mapping, Sequence

    from wm_notecards._types import ThemeLike

EDAFieldRole = Literal[
    "identifier",
    "time",
    "target",
    "numeric",
    "categorical",
    "boolean / flag",
    "text / high-cardinality",
]

DEFAULT_SKEW_THRESHOLD = 1.0
DEFAULT_CORRELATION_THRESHOLD = 0.80

EDAComparisonKind = Literal[
    "auto",
    "categorical",
    "numeric",
    "numeric_by_category",
    "categorical_by_categorical",
    "numeric_by_numeric",
    "time_by_numeric",
    "missingness",
]
PreprocessingAction = Literal["parse", "coerce", "impute", "drop", "keep", "transform"]
FitScope = Literal["fixed_rule", "train_only", "not_applicable"]
ModelUse = Literal["candidate", "context", "review_only", "exclude", "target"]


@dataclass(frozen=True, slots=True)
class EDADisplayPolicy:
    """Visible, challengeable defaults for canonical EDA rendering."""

    show_complete_percentages: bool = False
    skew_threshold: float = DEFAULT_SKEW_THRESHOLD
    date_parse_threshold: float = 0.90
    boolean_parse_threshold: float = 0.98
    category_top_n: int = 8


@dataclass(frozen=True, slots=True)
class PreprocessingDecision:
    """A transformation the human explicitly approved."""

    field: str
    action: PreprocessingAction
    method: str
    reason: str
    fit_scope: FitScope
    keep_missing_indicator: bool = False


@dataclass(frozen=True, slots=True)
class FeatureDecision:
    """A field's explicit role at the model boundary."""

    field: str
    role: str
    model_use: ModelUse
    reason: str


@dataclass(frozen=True, slots=True)
class EDAComparisonResult:
    """Exact tabular and visual evidence for one EDA question."""

    resolved_fields: tuple[Hashable, ...]
    comparison_kind: str
    table: pd.DataFrame
    figure: go.Figure

# Identifier hints must be complete snake-case tokens.  A loose ``id$`` check
# silently misclassifies ordinary fields such as ``paid`` and ``valid``.
_IDENTIFIER_RE = re.compile(r"(?:^|_)(?:id|uuid|guid|key)$", re.IGNORECASE)
_TIME_NAME_RE = re.compile(r"date|time|timestamp|datetime|month|year|week", re.IGNORECASE)


def _validate_unit_interval(value: float, *, name: str) -> float:
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1 inclusive.")
    return number


def _validate_positive(value: float, *, name: str) -> float:
    number = float(value)
    if not np.isfinite(number) or number <= 0:
        raise ValueError(f"{name} must be a finite number greater than 0.")
    return number


def _format_skew(value: object) -> str:
    """Format a possibly-missing skew value without leaking ``nan``."""
    try:
        number = float(cast("Any", value))
    except (TypeError, ValueError):
        return "—"
    return f"{number:+.2f}" if np.isfinite(number) else "—"


def _infer_role(
    name: str,
    series: pd.Series[Any],
    *,
    target: str | None,
    identifier_columns: set[str],
    datetime_columns: set[str],
    categorical_columns: set[str],
    categorical_max_unique: int,
    text_unique_ratio: float,
) -> EDAFieldRole:
    """Infer a stable EDA role without changing the underlying dtype."""
    if name == target:
        return "target"
    if name in identifier_columns or _IDENTIFIER_RE.search(name):
        return "identifier"
    if name in datetime_columns or pd.api.types.is_datetime64_any_dtype(series):
        return "time"
    if name in categorical_columns or isinstance(series.dtype, pd.CategoricalDtype):
        return "categorical"
    if pd.api.types.is_bool_dtype(series):
        return "boolean / flag"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    observed = int(series.notna().sum())
    unique = int(series.nunique(dropna=True))
    unique_ratio = unique / max(observed, 1)
    if _TIME_NAME_RE.search(name):
        return "time"
    if unique <= categorical_max_unique and unique_ratio < text_unique_ratio:
        return "categorical"
    return "text / high-cardinality"


def _field_guidance(
    *,
    role: EDAFieldRole,
    missing: int,
    missing_share: float,
    unique: int,
    skew: float | None,
    skew_threshold: float,
) -> tuple[str, str]:
    """Return a bounded review status and a plain-English next check."""
    guidance: list[str] = []

    if missing_share >= 1.0:
        guidance.append("All values are missing; recover the source or remove the field.")
    elif missing:
        if role == "numeric":
            guidance.append(
                "Investigate why values are missing; if you choose imputation, fit it on training data only."
            )
        elif role in {"categorical", "boolean / flag", "target"}:
            guidance.append(
                "Investigate missingness before treating it as a category or filling it."
            )
        elif role == "time":
            guidance.append(
                "Inspect unparsed examples and preserve the raw field before any date conversion."
            )
        else:
            guidance.append("Investigate missingness; no fill has been applied.")

    if unique <= 1:
        guidance.append(
            "Only one observed value remains; verify that the field can teach anything."
        )
    if role == "identifier":
        guidance.append(
            "Keep raw identifiers for joins or review, not as model features without a specific reason."
        )
    elif role == "text / high-cardinality":
        guidance.append(
            "Preserve raw text; fit cleaning and vectorization inside the training pipeline."
        )
    elif role == "time":
        guidance.append("Verify timezone, frequency, and chronological ordering before splitting.")

    if skew is not None and abs(skew) >= skew_threshold:
        guidance.append(
            f"|skew| is at least {skew_threshold:g}; inspect scale and unusual values before choosing a transform."
        )

    if guidance:
        return "CHECK", " ".join(guidance)
    return (
        "PASS",
        "No automatic transformation applied; continue with the question this field must answer.",
    )


def wm_build_eda_contract(
    df: pd.DataFrame,
    *,
    target: str | None = None,
    identifier_columns: Sequence[str] = (),
    datetime_columns: Sequence[str] = (),
    categorical_columns: Sequence[str] = (),
    categorical_max_unique: int = 24,
    text_unique_ratio: float = 0.50,
    skew_threshold: float = DEFAULT_SKEW_THRESHOLD,
) -> pd.DataFrame:
    """Build a non-mutating field-by-field EDA decision contract.

    The returned table is intentionally explicit about suggestions.  It does not
    parse dates, coerce strings, impute values, drop columns, or fit preprocessing.
    """
    if categorical_max_unique < 1:
        raise ValueError("categorical_max_unique must be at least 1.")
    ratio = _validate_unit_interval(text_unique_ratio, name="text_unique_ratio")
    skew_limit = _validate_positive(skew_threshold, name="skew_threshold")

    known_columns = {str(column) for column in df.columns}
    explicit = {
        "target": {target} if target is not None else set(),
        "identifier_columns": {str(column) for column in identifier_columns},
        "datetime_columns": {str(column) for column in datetime_columns},
        "categorical_columns": {str(column) for column in categorical_columns},
    }
    unknown = sorted(set().union(*explicit.values()) - known_columns)
    if unknown:
        raise ValueError(f"Unknown dataframe columns: {', '.join(unknown)}")

    rows: list[dict[str, object]] = []
    for raw_name in df.columns:
        name = str(raw_name)
        series = df[raw_name]
        role = _infer_role(
            name,
            series,
            target=target,
            identifier_columns=explicit["identifier_columns"],
            datetime_columns=explicit["datetime_columns"],
            categorical_columns=explicit["categorical_columns"],
            categorical_max_unique=categorical_max_unique,
            text_unique_ratio=ratio,
        )
        missing = int(series.isna().sum())
        missing_share = missing / max(len(series), 1)
        unique = int(series.nunique(dropna=True))
        skew: float | None = None
        if role == "numeric":
            numeric = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)
            valid = numeric.dropna()
            if len(valid) >= 3 and int(valid.nunique()) > 1:
                skew = float(cast("Any", valid.skew()))

        status, guidance = _field_guidance(
            role=role,
            missing=missing,
            missing_share=missing_share,
            unique=unique,
            skew=skew,
            skew_threshold=skew_limit,
        )
        rows.append(
            {
                "field": name,
                "role": role,
                "dtype": str(series.dtype),
                "complete": 1.0 - missing_share,
                "missing": missing,
                "unique": unique,
                "skew": skew,
                "status": status,
                "what deserves a decision": guidance,
            }
        )

    return pd.DataFrame(rows)


def wm_build_category_share_table(
    df: pd.DataFrame,
    columns: Sequence[str],
    *,
    labels: Mapping[str, str] | None = None,
    top_n_per_column: int | None = None,
    include_missing: bool = True,
) -> pd.DataFrame:
    """Return category counts ordered by field and share of all rows."""
    if not columns:
        raise ValueError("columns must contain at least one field.")
    if top_n_per_column is not None and top_n_per_column < 1:
        raise ValueError("top_n_per_column must be at least 1 when provided.")
    unknown = [str(column) for column in columns if str(column) not in df.columns]
    if unknown:
        raise ValueError(f"Unknown dataframe columns: {', '.join(unknown)}")

    total = max(len(df), 1)
    rows: list[dict[str, object]] = []
    for raw_column in columns:
        column = str(raw_column)
        series = df[column].astype("string")
        series = series.fillna("<missing>") if include_missing else series.dropna()
        counts = series.value_counts(dropna=False)
        if top_n_per_column is not None:
            counts = counts.head(top_n_per_column)
        for category, count in counts.items():
            rows.append(
                {
                    "field group": (labels or {}).get(column, column),
                    "category": str(category),
                    "rows": int(count),
                    "share of all rows": int(count) / total,
                }
            )
    return pd.DataFrame(rows)


def wm_build_correlation_clues(
    df: pd.DataFrame,
    *,
    threshold: float = DEFAULT_CORRELATION_THRESHOLD,
    method: Literal["pearson", "spearman", "kendall"] = "pearson",
    top_n: int = 12,
) -> pd.DataFrame:
    """Rank numeric correlation pairs as review clues, never conclusions."""
    limit = _validate_unit_interval(threshold, name="threshold")
    if limit <= 0:
        raise ValueError("threshold must be greater than 0.")
    if top_n < 1:
        raise ValueError("top_n must be at least 1.")

    numeric = df.select_dtypes(include=[np.number]).replace([np.inf, -np.inf], np.nan)
    if numeric.shape[1] < 2:
        return pd.DataFrame(
            columns=[
                "field A",
                "field B",
                "correlation",
                "absolute correlation",
                "status",
                "how to read it",
            ]
        )

    corr = numeric.corr(method=method)
    rows: list[dict[str, object]] = []
    columns = list(corr.columns)
    for left_index, left in enumerate(columns):
        for right in columns[left_index + 1 :]:
            # pandas-stubs has returned both a broad scalar union and ``Any``
            # across supported Python/pandas combinations.  The correlation
            # matrix is numeric by construction, so narrow at this boundary.
            value = cast("Any", corr.loc[left, right])
            if pd.isna(value):
                continue
            absolute = abs(float(value))
            flagged = absolute >= limit
            rows.append(
                {
                    "field A": str(left),
                    "field B": str(right),
                    "correlation": float(value),
                    "absolute correlation": absolute,
                    "status": "CHECK" if flagged else "PASS",
                    "how to read it": (
                        f"At or above the chosen {limit:.2f} review threshold. Check duplicate measurement, shared source, or leakage before dropping either field."
                        if flagged
                        else "Association clue only. This does not establish causation or require a fix."
                    ),
                }
            )
    if not rows:
        return pd.DataFrame(
            columns=[
                "field A",
                "field B",
                "correlation",
                "absolute correlation",
                "status",
                "how to read it",
            ]
        )
    result = pd.DataFrame(rows)
    ranked = (
        result.sort_values(
            ["absolute correlation", "field A", "field B"],
            ascending=[False, True, True],
        )
        .head(top_n)
        .reset_index(drop=True)
    )
    # Normalizing through the constructor keeps the return type stable across
    # pandas-stubs releases used by the supported Python matrix.
    return pd.DataFrame(ranked)


def wm_build_preprocessing_log(
    before: pd.DataFrame,
    after: pd.DataFrame,
    decisions: Sequence[PreprocessingDecision],
) -> pd.DataFrame:
    """Build an audit log from completed work, never from intentions alone."""
    if not decisions:
        raise ValueError("decisions must contain at least one completed action.")
    duplicate_fields = sorted(
        field for field in {item.field for item in decisions}
        if sum(item.field == field for item in decisions) > 1
    )
    if duplicate_fields:
        raise ValueError(f"Duplicate preprocessing decisions: {', '.join(duplicate_fields)}")

    rows: list[dict[str, object]] = []
    for decision in decisions:
        before_exists = decision.field in before.columns
        after_exists = decision.field in after.columns
        if not before_exists:
            raise ValueError(f"Unknown field in before dataframe: {decision.field}")
        if decision.action == "drop" and after_exists:
            raise ValueError(f"Drop decision did not remove field: {decision.field}")
        if decision.action != "drop" and not after_exists:
            raise ValueError(f"Completed decision removed field unexpectedly: {decision.field}")
        missing_before = int(before[decision.field].isna().sum())
        missing_after = int(after[decision.field].isna().sum()) if after_exists else None
        rows.append(
            {
                "field": decision.field,
                "action": decision.action,
                "method": decision.method,
                "reason": decision.reason,
                "fit scope": decision.fit_scope,
                "missing before": missing_before,
                "missing after": missing_after,
                "rows before": len(before),
                "rows after": len(after),
                "missing indicator kept": decision.keep_missing_indicator,
                "status": "APPLIED",
            }
        )
    return pd.DataFrame(rows)


def wm_validate_feature_manifest(
    df: pd.DataFrame,
    decisions: Sequence[FeatureDecision],
) -> pd.DataFrame:
    """Validate the model boundary and return its human-readable manifest."""
    if not decisions:
        raise ValueError("decisions must contain at least one feature decision.")
    fields = [item.field for item in decisions]
    duplicates = sorted({field for field in fields if fields.count(field) > 1})
    if duplicates:
        raise ValueError(f"Duplicate feature decisions: {', '.join(duplicates)}")
    required = {
        item.field for item in decisions if item.model_use in {"candidate", "context", "target"}
    }
    missing = sorted(required - {str(column) for column in df.columns})
    if missing:
        raise ValueError(f"Required manifest fields are missing: {', '.join(missing)}")
    forbidden = {
        item.field for item in decisions if item.model_use in {"exclude", "review_only"}
    }
    reentered = sorted(forbidden & {str(column) for column in df.columns})
    if reentered:
        raise ValueError(f"Excluded fields re-entered the model frame: {', '.join(reentered)}")
    unmanifested = sorted({str(column) for column in df.columns} - set(fields))
    if unmanifested:
        raise ValueError(f"Unmanifested fields entered the model frame: {', '.join(unmanifested)}")
    return pd.DataFrame(
        {
            "field": fields,
            "role": [item.role for item in decisions],
            "model use": [item.model_use for item in decisions],
            "reason": [item.reason for item in decisions],
        }
    )


def _resolve_fields(df: pd.DataFrame, fields: Sequence[str | int]) -> tuple[Hashable, ...]:
    if not 1 <= len(fields) <= 2:
        raise ValueError("fields must contain one or two column names or positions.")
    resolved: list[Hashable] = []
    columns = list(df.columns)
    for field in fields:
        if isinstance(field, int):
            try:
                resolved.append(columns[field])
            except IndexError as exc:
                raise ValueError(f"Column position is out of range: {field}") from exc
        elif field in columns:
            resolved.append(field)
        else:
            raise ValueError(f"Unknown dataframe column: {field}")
    if len(set(resolved)) != len(resolved):
        raise ValueError("fields must resolve to distinct columns.")
    return tuple(resolved)


def _infer_comparison_kind(df: pd.DataFrame, fields: tuple[Hashable, ...]) -> str:
    numeric = [pd.api.types.is_numeric_dtype(df[field]) for field in fields]
    datetime = [pd.api.types.is_datetime64_any_dtype(df[field]) for field in fields]
    if len(fields) == 1:
        return "numeric" if numeric[0] else "categorical"
    if datetime[0] and numeric[1]:
        return "time_by_numeric"
    if datetime[1] and numeric[0]:
        return "time_by_numeric"
    if all(numeric):
        return "numeric_by_numeric"
    if any(numeric):
        return "numeric_by_category"
    return "categorical_by_categorical"


def wm_compare_fields(
    df: pd.DataFrame,
    *,
    fields: Sequence[str | int],
    kind: EDAComparisonKind = "auto",
    top_n: int = 8,
) -> EDAComparisonResult:
    """Return exact table-and-chart evidence for one or two selected fields."""
    if top_n < 1:
        raise ValueError("top_n must be at least 1.")
    resolved = _resolve_fields(df, fields)
    comparison_kind = _infer_comparison_kind(df, resolved) if kind == "auto" else kind
    figure = go.Figure()
    table: pd.DataFrame

    if comparison_kind == "numeric" and len(resolved) == 1:
        field = resolved[0]
        numeric = pd.to_numeric(df[field], errors="coerce").dropna()
        table = numeric.describe().rename("value").to_frame()
        figure.add_trace(
            go.Box(x=numeric, name=str(field), boxpoints="outliers", orientation="h")
        )
    elif comparison_kind == "categorical" and len(resolved) == 1:
        field = resolved[0]
        counts = df[field].astype("string").fillna("<missing>").value_counts().head(top_n)
        table = counts.rename("rows").to_frame()
        table["share"] = table["rows"] / max(len(df), 1)
        figure.add_trace(go.Bar(x=table["rows"], y=table.index.astype(str), orientation="h"))
    elif comparison_kind == "numeric_by_numeric" and len(resolved) == 2:
        left, right = resolved
        pair = df[[left, right]].apply(pd.to_numeric, errors="coerce").dropna()
        table = pair.corr().rename_axis(index="field", columns="compared with")
        figure.add_trace(go.Scatter(x=pair[left], y=pair[right], mode="markers"))
    elif comparison_kind == "numeric_by_category" and len(resolved) == 2:
        numeric_field = next(field for field in resolved if pd.api.types.is_numeric_dtype(df[field]))
        category_field = next(field for field in resolved if field != numeric_field)
        pair = df[[category_field, numeric_field]].dropna()
        grouped = cast("Any", pair.groupby(category_field, dropna=False)[numeric_field])
        table = grouped.agg(
            rows="count", mean="mean", median="median", minimum="min", maximum="max"
        )
        for category, values in pair.groupby(category_field, dropna=False)[numeric_field]:
            figure.add_trace(go.Box(x=values, name=str(category), orientation="h"))
    elif comparison_kind == "categorical_by_categorical" and len(resolved) == 2:
        left, right = resolved
        table = pd.crosstab(df[left], df[right], dropna=False)
        normalized = table.div(table.sum(axis=1).replace(0, np.nan), axis=0)
        for category in normalized.columns:
            figure.add_trace(
                go.Bar(x=normalized[category], y=normalized.index.astype(str), name=str(category), orientation="h")
            )
        figure.update_layout(barmode="stack")
    elif comparison_kind == "time_by_numeric" and len(resolved) == 2:
        time_field = next(field for field in resolved if pd.api.types.is_datetime64_any_dtype(df[field]))
        numeric_field = next(field for field in resolved if field != time_field)
        pair = df[[time_field, numeric_field]].dropna().sort_values(time_field)
        table = pair.set_index(time_field)
        figure.add_trace(go.Scatter(x=pair[time_field], y=pair[numeric_field], mode="lines"))
    elif comparison_kind == "missingness":
        table = pd.DataFrame(
            {"missing": df.isna().sum(), "complete": 1.0 - df.isna().mean()}
        ).sort_values(["missing"], ascending=False)
        figure.add_trace(go.Bar(x=table["missing"], y=table.index.astype(str), orientation="h"))
    else:
        raise ValueError(
            f"Comparison kind {comparison_kind!r} is incompatible with fields {resolved!r}."
        )
    return EDAComparisonResult(resolved, comparison_kind, table, figure)


def _data_chip_css(theme: ThemeLike) -> str:
    return f"""<style>
.wm-data-chip-board{{
  width:100%;max-width:{theme.width}px;margin:18px auto 24px;
  box-sizing:border-box;display:grid;gap:22px;
}}
.wm-data-chip-intro{{
  display:grid;gap:5px;padding:0 2px 2px;
}}
.wm-data-chip-intro strong{{
  font:900 {getattr(theme, 'shell_title_size', 34)}px/1.08 {theme.font_display};
  color:{theme.text_main};letter-spacing:-.025em;
}}
.wm-data-chip-section{{display:grid;gap:12px;}}
.wm-data-chip-section-head{{display:grid;gap:3px;padding:0 2px;}}
.wm-data-chip-section-head strong{{
  font:900 10px/1.35 {theme.font_mono};letter-spacing:.15em;
  text-transform:uppercase;color:{theme.text_main};
}}
.wm-data-chip-group{{
  display:grid;grid-template-columns:minmax(124px,158px) minmax(0,1fr);
  gap:12px 16px;align-items:start;
}}
.wm-data-chip-label{{
  padding:8px 11px;border-radius:999px;background:{theme.text_main};
  color:{theme.card_bg};font:800 11px/1.2 {theme.font_mono};
  letter-spacing:.08em;text-transform:uppercase;text-align:center;
}}
.wm-data-chip-row{{display:flex;flex-wrap:wrap;gap:9px;min-width:0;}}
.wm-data-chip{{
  --wm-chip-color:{theme.accent};--wm-chip-text:#061018;
  display:inline-flex;align-items:baseline;gap:7px;
  max-width:100%;padding:7px 10px;border-radius:999px;
  border:0;
  background:var(--wm-chip-color);color:var(--wm-chip-text);
  font:850 12px/1.25 {theme.font_mono};
  box-shadow:none;text-shadow:none;
}}
.wm-data-chip-name{{overflow-wrap:anywhere;}}
.wm-data-chip-coverage{{font-size:10px;color:var(--wm-chip-text);opacity:.76;white-space:nowrap;}}
.wm-data-chip--missing{{
  --wm-chip-color:{theme.color_missing_bg}!important;
  --wm-chip-text:{theme.color_missing_txt}!important;
  outline:none;
  box-shadow:0 0 0 5px {rgba_css(theme.color_missing_accent, 0.30)},
             0 0 24px -3px {rgba_css(theme.color_missing_accent, 0.78)};
}}
@media(max-width:620px){{
  .wm-data-chip-group{{grid-template-columns:1fr;gap:9px;}}
  .wm-data-chip-label{{width:max-content;max-width:100%;}}
}}
</style>"""


def display_data_chips(
    df: pd.DataFrame,
    *,
    theme: ThemeLike,
    target: str | None = None,
    identifier_columns: Sequence[str] = (),
    datetime_columns: Sequence[str] = (),
    categorical_columns: Sequence[str] = (),
    group_label: str = "Fields grouped by analytical role",
) -> None:
    """Display stable, coverage-aware field chips grouped by EDA role."""
    contract = wm_build_eda_contract(
        df,
        target=target,
        identifier_columns=identifier_columns,
        datetime_columns=datetime_columns,
        categorical_columns=categorical_columns,
    )
    role_order: tuple[EDAFieldRole, ...] = (
        "identifier",
        "time",
        "target",
        "numeric",
        "categorical",
        "boolean / flag",
        "text / high-cardinality",
    )
    fixed_palette: dict[EDAFieldRole, tuple[str, str]] = {
        "identifier": (theme.chip_identifier, "#111111"),
        "time": (theme.chip_time, "#FFFFFF"),
        "target": (theme.chip_target, "#111111"),
    }
    candidate_roles: tuple[EDAFieldRole, ...] = (
        "numeric", "categorical", "boolean / flag", "text / high-cardinality"
    )
    visible_candidates = [
        role for role in candidate_roles if bool((contract["role"] == role).any())
    ]
    candidate_palette: dict[EDAFieldRole, tuple[str, str]] = {
        role: (
            (theme.chip_candidate_primary, "#061018")
            if index % 2 == 0
            else (theme.chip_candidate_secondary, theme.chip_candidate_secondary_text)
        )
        for index, role in enumerate(visible_candidates)
    }
    palette: dict[EDAFieldRole, tuple[str, str]] = {**fixed_palette, **candidate_palette}
    section_specs: tuple[tuple[str, tuple[EDAFieldRole, ...]], ...] = (
        ("Row context", ("identifier", "time")),
        ("Model fields", ("target", "numeric", "categorical", "boolean / flag")),
        ("Special pipeline", ("text / high-cardinality",)),
    )

    role_html: dict[EDAFieldRole, str] = {}
    for role in role_order:
        subset = contract.loc[contract["role"] == role].sort_values(
            ["complete"], ascending=[True], kind="stable"
        )
        if subset.empty:
            continue
        chips: list[str] = []
        for row in subset.to_dict("records"):
            complete = float(row["complete"])
            missing_class = " wm-data-chip--missing" if complete < 1.0 else ""
            chip_color, chip_text = palette[role]
            coverage = (
                f"<span class='wm-data-chip-coverage'>{complete:.0%} complete</span>"
                if complete < 1.0
                else ""
            )
            chips.append(
                f"<span class='wm-data-chip{missing_class}' "
                f"style='--wm-chip-color:{chip_color};--wm-chip-text:{chip_text}'>"
                f"<span class='wm-data-chip-name'>{escape(str(row['field']))}</span>"
                f"{coverage}</span>"
            )
        role_html[role] = (
            "<div class='wm-data-chip-group'>"
            f"<div class='wm-data-chip-label'>{escape(role)}</div>"
            f"<div class='wm-data-chip-row'>{''.join(chips)}</div></div>"
        )

    sections: list[str] = []
    for title, roles in section_specs:
        rows = "".join(role_html[role] for role in roles if role in role_html)
        if not rows:
            continue
        sections.append(
            "<section class='wm-data-chip-section'>"
            "<div class='wm-data-chip-section-head'>"
            f"<strong>{escape(title)}</strong></div>"
            f"{rows}</section>"
        )
    intro = (
        "<div class='wm-data-chip-intro'>"
        f"<strong>{escape(group_label)}</strong>"
        "</div>"
        if group_label
        else ""
    )
    display(
        HTML(
            f"{_data_chip_css(theme)}<section class='wm-data-chip-board'>"
            f"{intro}{''.join(sections)}</section>"
        )
    )


def wm_eda_overview(
    df: pd.DataFrame,
    *,
    theme: ThemeLike,
    target: str | None = None,
    identifier_columns: Sequence[str] = (),
    datetime_columns: Sequence[str] = (),
    categorical_columns: Sequence[str] = (),
    columns: Sequence[str] | None = None,
    skew_threshold: float = DEFAULT_SKEW_THRESHOLD,
    max_cards: int = 24,
    visible_cards: int = 4,
    show_contract: bool = True,
    question_title: str | None = None,
    question_body: str | None = None,
    contract_title: str = "Fields that need a decision",
) -> pd.DataFrame:
    """Render evidence without inventing a question or conclusion for the caller."""
    contract = wm_build_eda_contract(
        df,
        target=target,
        identifier_columns=identifier_columns,
        datetime_columns=datetime_columns,
        categorical_columns=categorical_columns,
        skew_threshold=skew_threshold,
    )
    if question_title is not None:
        question_card(
            theme=theme,
            title=question_title,
            body=question_body,
            kicker="EDA, question",
        )
    display_data_chips(
        df,
        theme=theme,
        target=target,
        identifier_columns=identifier_columns,
        datetime_columns=datetime_columns,
        categorical_columns=categorical_columns,
    )
    wm_render_micro_profile_cards(
        df,
        theme=theme,
        columns=columns,
        max_cards=max_cards,
        visible_cards=visible_cards,
        skew_threshold=skew_threshold,
    )
    if show_contract:
        styled = contract.style.format(
            {
                "complete": "{:.1%}",
                "skew": _format_skew,
            },
            na_rep="—",
        ).hide()
        wm_render_styler(
            styled,
            theme=theme,
            title=contract_title,
            subtitle=(
                f"Review threshold: |skew| ≥ {float(skew_threshold):g}."
            ),
            kicker="EDA, field contract, evidence",
            wrap_columns={"what deserves a decision": 360},
        )
    return contract
