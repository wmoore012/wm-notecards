"""Pandas Styler rendering inside WM card shells.

Key functions
-------------
- :func:`wm_render_styler` — render any Styler inside a WM table card.
- :func:`wm_render_micro_profile_cards` — mini variable summaries with
  KDE plots, dtype chips, and stats grids.  The system's replacement
  for raw ``df.describe()`` output.
- :func:`wm_fe_decision_table` — feature-engineering pass/fail table.
- :func:`style_df_wm` — quick themed styling for a DataFrame / Styler.
"""
from __future__ import annotations

import numbers
import re
from dataclasses import dataclass, replace
from html import escape
from typing import TYPE_CHECKING, Any, cast

import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from IPython.display import HTML, display

from wm_notecards._html import (
    card_shell_css,
    rgba_css,
    shell_header_html,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from pandas.io.formats.style import Styler

    from wm_notecards._types import ThemeLike


# ── Constants ────────────────────────────────────────────────────────

_ALLOWED_FE_CALLS = frozenset({
    "Pass: lead candidate",
    "Pass: support only",
    "Pass: guardrail only",
    "Pass: written-case only",
    "Fail: descriptive only",
    "Fail: stop here",
})

_NUMERIC_RE = re.compile(r"^-?[\d,$%().\s]+$")

_SEMANTIC_STATUS_ALIASES: dict[str, str] = {
    "before": "before",
    "original": "before",
    "raw": "raw",
    "after": "after",
    "clean": "cleaned",
    "cleaned": "cleaned",
    "pass": "pass",
    "passed": "pass",
    "ok": "pass",
    "success": "pass",
    "fail": "fail",
    "failed": "fail",
    "error": "fail",
    "warn": "warn",
    "warning": "warn",
    "caution": "warn",
    "cached": "cached",
    "cache": "cached",
    "missing": "missing",
    "na": "missing",
    "null": "missing",
}

_SEMANTIC_STATUSES: tuple[str, ...] = (
    "before",
    "after",
    "pass",
    "fail",
    "warn",
    "cached",
    "missing",
    "raw",
    "cleaned",
)

# Maps dtype strings → palette index for dtype chips.
_DTYPE_PALETTE: dict[str, int] = {
    "int8": 0, "int16": 0, "int32": 0, "int64": 0,
    "uint8": 0, "uint16": 0, "uint32": 0, "uint64": 0,
    "float16": 1, "float32": 1, "float64": 1,
    "object": 2, "string": 2,
    "bool": 3,
    "datetime64": 4, "datetime64[ns]": 4, "datetime64[ns, UTC]": 4,
    "category": 5,
}


# ── WMTableTheme ─────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class WMTableTheme:
    """Table-level theme tokens that sit on top of the card theme.

    Controls CSS class names, hover interactivity, and scrollbar styling.
    Frozen so you can pass it around safely; use ``dataclasses.replace``
    when you need a variant.
    """

    table_class: str = "wm-table"
    card_class: str = "wm-table-card"
    interactive_rows: bool = True
    interactive_shell: bool = False
    max_visible_rows: int = 12
    scroll_height: int = 560

    def css(self, theme: ThemeLike) -> str:
        """Generate the full ``<style>`` block for this table config."""
        shell = card_shell_css(theme, card_class=self.card_class)
        hover = self._hover_css(theme) if self.interactive_rows else ""
        return f"{shell}<style>{self._base_css(theme)}{hover}" \
               f"{self._scrollbar_css(theme)}{self._print_css()}</style>"

    # -- CSS sub-sections (kept separate for readability) --

    def _base_css(self, theme: ThemeLike) -> str:
        tc = self.table_class
        cc = self.card_class
        lift = "translateY(-2px)" if self.interactive_shell else "none"
        shadow_hover = (
            "0 20px 34px -20px rgba(0,0,0,0.28)"
            if self.interactive_shell and theme.mode == "light"
            else "0 12px 22px -14px rgba(0,0,0,0.20)"
            if theme.mode == "light" else "none"
        )
        return f"""
div.{cc} {{ overflow: hidden; }}
div.{cc}:hover {{ transform: {lift}; box-shadow: {shadow_hover}; }}
div.{cc} .wm-table-scroll {{
  overflow: auto;
  width: 100%; max-width: 100%; box-sizing: border-box;
  scrollbar-width: thin;
  scrollbar-color: {theme.table_header_bg} transparent;
  border-radius: 14px;
}}
div.{cc} .wm-table-scroll--bounded thead th {{
  position: sticky; top: 0; z-index: 2;
}}
table.{tc} {{
  width: max-content; min-width: 100%;
  font-family: {theme.font_mono}; font-size: 13px;
  border-collapse: separate; border-spacing: 0;
}}
table.{tc} thead th {{
  font-family: {theme.font_display}; font-size: 12px; font-weight: 800;
  color: {theme.text_muted}; text-transform: uppercase;
  letter-spacing: 0.09em; line-height: 1.25; padding: 12px 16px;
  border-bottom: 1px solid {theme.border};
  border-right: 1px solid {theme.grid};
  background: {theme.table_header_bg}; text-align: left;
  white-space: normal; max-width: 180px; vertical-align: bottom;
}}
table.{tc} tbody td {{
  padding: 12px 16px;
  border-bottom: 1px solid {theme.grid};
  border-right: 1px solid {theme.grid};
  color: {theme.text_main}; font-variant-numeric: tabular-nums;
  white-space: normal; word-break: break-word; line-height: 1.5;
  vertical-align: top;
  transition: background-color 0.14s ease, color 0.14s ease;
}}
table.{tc} thead th:last-child,
table.{tc} tbody td:last-child {{ border-right: none; }}
table.{tc} tbody tr:nth-child(even) td {{
  background: {theme.table_stripe_bg};
}}
table.{tc} tbody tr:last-child td {{ border-bottom: none; }}
"""

    def _hover_css(self, theme: ThemeLike) -> str:
        tc = self.table_class
        hbg = theme.table_hover_bg
        htx = theme.table_hover_text
        hbd = theme.table_hover_border
        return f"""
table.{tc} tbody tr:hover td {{
  background: {hbg} !important; color: {htx} !important;
  border-top-color: {hbd} !important;
  border-bottom-color: {hbd} !important;
  box-shadow: inset 0 1px 0 {hbd}, inset 0 -1px 0 {hbd};
}}
table.{tc} tbody tr:hover td a,
table.{tc} tbody tr:hover td span {{
  color: {htx} !important;
}}
"""

    def _scrollbar_css(self, theme: ThemeLike) -> str:
        cc = self.card_class
        return f"""
div.{cc} .wm-table-scroll::-webkit-scrollbar {{ width:10px; height:10px; }}
div.{cc} .wm-table-scroll::-webkit-scrollbar-track {{
  background: transparent;
}}
div.{cc} .wm-table-scroll::-webkit-scrollbar-thumb {{
  background: {theme.table_header_bg};
  border: 1px solid {theme.text_main}; border-radius: 999px;
}}
"""

    def _print_css(self) -> str:
        cc = self.card_class
        tc = self.table_class
        return f"""
@media print {{
  div.{cc} {{ overflow: visible !important; }}
  div.{cc} .wm-table-scroll {{
    overflow: visible !important; max-width: 100% !important;
    max-height: none !important;
  }}
  table.{tc} {{ width: 100% !important; table-layout: auto !important; }}
  table.{tc} thead th, table.{tc} tbody td {{
    white-space: normal !important; max-width: none !important;
    overflow-wrap: anywhere !important;
  }}
}}
"""


_DEFAULT_TABLE_THEME = WMTableTheme()


# ── Scalar helpers ───────────────────────────────────────────────────


def _fg_for_fill(color: str) -> str:
    """Pick black or white foreground based on background luminance."""
    r, g, b = mcolors.to_rgb(color)
    # BT.601 luma — good enough for chip contrast.
    return "#111111" if 0.299 * r + 0.587 * g + 0.114 * b > 0.62 else "#FFFFFF"


def _is_missing(value: object) -> bool:
    """Return True if *value* is NaN / NaT / None (scalar only)."""
    try:
        flag = pd.isna(cast("Any", value))
    except Exception:
        return False
    if isinstance(flag, (bool, np.bool_)):
        return bool(flag)
    arr = np.asarray(flag)
    return bool(arr.size == 1 and arr.flat[0])


def _to_float(value: object) -> float | None:
    """Try to coerce *value* to a Python float.

    Returns ``None`` when the value can't be interpreted as a number.
    This is used by the outlier-report styler to read rate columns
    that might arrive as strings like ``"3.5%"``.
    """
    num = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return None if _is_missing(num) else float(cast("float", num))


def _fmt(value: object) -> str:
    """Format a scalar for table display (comma-separated, 2 decimals)."""
    if _is_missing(value):
        return "—"
    if isinstance(value, numbers.Real) and not isinstance(value, bool):
        n = float(value)
        return f"{int(n):,}" if n.is_integer() else f"{n:,.2f}"
    return str(value)


def _mode_text(series: pd.Series[Any]) -> str:
    """Return the mode of a series as a display string, truncated."""
    mode = series.dropna().mode()
    if mode.empty:
        return "—"
    top = str(mode.iloc[0])
    return escape(top if len(top) <= 30 else top[:27] + "…")


# ── Column alignment ────────────────────────────────────────────────


def _looks_numeric(series: pd.Series[Any]) -> bool:
    """Heuristic: should this column be right-aligned?"""
    if pd.api.types.is_numeric_dtype(series):
        return True
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    # Text columns that look like dates ("2024-01-15 …").
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        sample = series.dropna().astype(str).head(20)
        if not sample.empty and sample.map(
            lambda v: bool(re.match(r"^\d{4}-\d{2}-\d{2}", v))
        ).all():
            return True
        if not sample.empty and sample.map(
            lambda v: bool(_NUMERIC_RE.match(v))
        ).all():
            return True
    return False


def _normalize_wrap(
    wrap: dict[str, int] | list[str] | tuple[str, ...] | set[str] | None,
) -> dict[str, int]:
    """Normalize ``wrap_columns`` to ``{col: max_width_px}``."""
    if wrap is None:
        return {}
    if isinstance(wrap, dict):
        return {str(c): max(120, int(w)) for c, w in wrap.items()}
    return {str(c): 360 for c in wrap}


def _align_css(
    df: pd.DataFrame,
    table_class: str,
    wrap: dict[str, int] | list[str] | tuple[str, ...] | set[str] | None = None,
) -> str:
    """Generate per-column alignment CSS rules."""
    wraps = _normalize_wrap(wrap)
    rules: list[str] = []
    for idx, col in enumerate(df.columns):
        w = wraps.get(str(col))
        if w:
            rules.append(
                f"table.{table_class} tbody td.col{idx} {{"
                f" text-align:left; white-space:normal;"
                f" width:{w}px; max-width:{w}px;"
                f" line-height:1.5; overflow-wrap:anywhere;"
                f" word-break:break-word; }}"
            )
        elif _looks_numeric(df[col]):
            rules.append(
                f"table.{table_class} tbody td.col{idx}"
                f" {{ text-align:right; white-space:nowrap; }}"
            )
        else:
            rules.append(
                f"table.{table_class} tbody td.col{idx} {{"
                f" text-align:left; white-space:normal; max-width:360px;"
                f" line-height:1.5; overflow-wrap:anywhere;"
                f" word-break:break-word; }}"
            )
    return f"<style>{''.join(rules)}</style>"


# ── Semantic table colour helpers ───────────────────────────────────


def _semantic_key(value: object) -> str | None:
    """Normalize a status-like value to a supported semantic class key."""
    if _is_missing(value):
        return "missing"
    key = str(value).strip().lower().replace("_", " ").replace("-", " ")
    key = " ".join(key.split())
    return _SEMANTIC_STATUS_ALIASES.get(key)


def _semantic_palette(theme: ThemeLike) -> dict[str, tuple[str, str, str]]:
    """Return status -> (background, foreground, border) tokens."""
    if theme.mode == "dark":
        return {
            "before": ("rgba(255, 138, 128, 0.14)", "#FFB4AB", "rgba(255, 138, 128, 0.32)"),
            "after": ("rgba(129, 199, 132, 0.14)", "#A5D6A7", "rgba(129, 199, 132, 0.34)"),
            "pass": ("rgba(129, 199, 132, 0.14)", "#A5D6A7", "rgba(129, 199, 132, 0.34)"),
            "fail": ("rgba(255, 138, 128, 0.14)", "#FFB4AB", "rgba(255, 138, 128, 0.32)"),
            "warn": ("rgba(244, 181, 86, 0.16)", "#F4B556", "rgba(244, 181, 86, 0.34)"),
            "cached": ("rgba(22, 199, 232, 0.13)", "#8BE9FF", "rgba(22, 199, 232, 0.30)"),
            "missing": ("rgba(244, 181, 86, 0.16)", "#F4B556", "rgba(244, 181, 86, 0.34)"),
            "raw": ("rgba(148, 163, 184, 0.14)", "#CBD5E1", "rgba(148, 163, 184, 0.28)"),
            "cleaned": ("rgba(129, 199, 132, 0.14)", "#A5D6A7", "rgba(129, 199, 132, 0.34)"),
        }
    return {
        "before": ("rgba(180, 35, 60, 0.10)", "#9F1D35", "rgba(180, 35, 60, 0.24)"),
        "after": ("rgba(32, 181, 123, 0.12)", "#146C43", "rgba(32, 181, 123, 0.26)"),
        "pass": ("rgba(32, 181, 123, 0.12)", "#146C43", "rgba(32, 181, 123, 0.26)"),
        "fail": ("rgba(180, 35, 60, 0.10)", "#9F1D35", "rgba(180, 35, 60, 0.24)"),
        "warn": ("rgba(216, 140, 46, 0.16)", "#8A5700", "rgba(216, 140, 46, 0.28)"),
        "cached": ("rgba(22, 199, 232, 0.12)", "#087B91", "rgba(22, 199, 232, 0.26)"),
        "missing": ("rgba(216, 140, 46, 0.16)", "#8A5700", "rgba(216, 140, 46, 0.28)"),
        "raw": ("rgba(76, 100, 117, 0.10)", "#3D5362", "rgba(76, 100, 117, 0.22)"),
        "cleaned": ("rgba(32, 181, 123, 0.12)", "#146C43", "rgba(32, 181, 123, 0.26)"),
    }


def semantic_table_css(theme: ThemeLike, *, table_class: str = "wm-table") -> str:
    """Return CSS classes for semantic status cells.

    The classes are theme-aware and Colab-safe.  Use them instead of
    inline red/green styles when a table needs to communicate before/
    after, pass/fail, cached/missing, or raw/cleaned state.
    """
    rules: list[str] = []
    for status, (bg, fg, border) in _semantic_palette(theme).items():
        rules.append(
            f"table.{table_class} tbody td.wm-semantic--{status} {{"
            f" background-color:{bg} !important;"
            f" color:{fg} !important;"
            f" border-color:{border} !important;"
            " font-weight:800;"
            "}}"
        )
        rules.append(
            f"table.{table_class} tbody td.wm-semantic--{status} code,"
            f"table.{table_class} tbody td.wm-semantic--{status} span {{"
            f" color:{fg} !important;"
            "}}"
        )
    return f"<style>{''.join(rules)}</style>"


def _semantic_td_classes(
    df: pd.DataFrame,
    *,
    semantic_columns: Sequence[str] | None,
    semantic_by_column: Mapping[str, str] | None,
) -> pd.DataFrame:
    """Build a Styler ``td`` class frame for semantic cell colouring."""
    classes = pd.DataFrame("", index=df.index, columns=df.columns)
    selected = set(df.columns if semantic_columns is None else semantic_columns)
    for column in selected:
        if column not in df.columns:
            continue
        classes[column] = df[column].map(
            lambda value: (
                f"wm-semantic--{key}" if (key := _semantic_key(value)) else ""
            )
        )
    for column, status in (semantic_by_column or {}).items():
        if column not in df.columns:
            continue
        key = _semantic_key(status)
        if key:
            classes[column] = f"wm-semantic--{key}"
    return classes


def style_semantic_wm(
    data: Styler | pd.DataFrame,
    *,
    theme: ThemeLike,
    semantic_columns: Sequence[str] | None = None,
    semantic_by_column: Mapping[str, str] | None = None,
    hide_index: bool = True,
) -> Styler:
    """Return a Styler with reusable semantic status classes.

    ``semantic_columns`` reads status words from cell values.  Use
    ``semantic_by_column`` when whole columns have a role, such as a
    before/after comparison table.
    """
    styler = data.style if isinstance(data, pd.DataFrame) else data
    frame = cast("pd.DataFrame", cast("Any", styler).data)
    classes = _semantic_td_classes(
        frame,
        semantic_columns=semantic_columns,
        semantic_by_column=semantic_by_column,
    )
    styler = styler.set_td_classes(classes)
    if hide_index:
        styler = styler.hide(axis="index")
    return styler


# ── Public styling functions ─────────────────────────────────────────


def style_describe_wm(
    summary: pd.DataFrame, theme: ThemeLike,
) -> Styler:
    """Style ``df.describe()`` with colour-coded rows for key stats.

    Rows named ``mean``, ``min``, ``max`` get light tints so they jump
    out visually.  The ``count`` row highlights columns whose count is
    less than the maximum (i.e. columns with missing values).
    """
    styles = pd.DataFrame("", index=summary.index, columns=summary.columns)
    tints = {
        "mean": theme.color_mean_bg,
        "min": theme.color_min_bg,
        "max": theme.color_max_bg,
    }
    for label, bg in tints.items():
        if label in summary.index:
            styles.loc[label, :] = f"background-color:{bg}; color:inherit"

    if "count" in summary.index:
        row = summary.loc["count"]
        if isinstance(row, pd.DataFrame):
            row = row.iloc[0]
        counts = pd.to_numeric(row, errors="coerce")
        for column in counts.index[counts != counts.max()]:
            styles.loc["count", column] = (
                f"background-color:{theme.color_count_bg}; color:inherit"
            )

    styled: Any = summary.style.apply(lambda _: styles, axis=None).format(_fmt)
    return cast("Styler", styled)


def style_outlier_report_wm(
    df: pd.DataFrame, theme: ThemeLike,
) -> Styler:
    """Colour-code an outlier report by severity.

    Rows are tinted based on the ``outlier_rate`` column:
    - ≤ 1 %  → green-ish (mean tint)
    - ≤ 5 %  → amber (max tint)
    - ≤ 10 % → blue-ish (count tint)
    - > 10 % → pink (min tint — draws attention)
    """
    def _row_bg(row: pd.Series[Any]) -> list[str]:
        rate = _to_float(row.get("outlier_rate", pd.NA))
        if rate is None:
            bg = theme.color_count_bg
        elif rate <= 0.01:
            bg = theme.color_mean_bg
        elif rate <= 0.05:
            bg = theme.color_max_bg
        elif rate <= 0.10:
            bg = theme.color_count_bg
        else:
            bg = theme.color_min_bg
        return [f"background-color:{bg}; color:inherit"] * len(row)

    fmts: dict[str, object] = {}
    for c in df.columns:
        fmts[c] = "{:.2%}" if c == "outlier_rate" else _fmt

    styled: Any = df.style.apply(_row_bg, axis=1).format(
        cast("Any", fmts),
        na_rep="—",
    )
    return cast("Styler", styled)


def display_cols_by_dtype(
    dtypes: pd.Series[Any],
    theme: ThemeLike,
    group_label: str = "",
) -> None:
    """Show columns grouped by dtype as colourful chips.

    Each dtype family gets its own row with a dark label pill and
    bright per-column chips. Useful right after loading a CSV to see
    what you're working with at a glance.
    """
    palette = list(theme.category_palette)

    def _label(name: str) -> str:
        if name.startswith("datetime64"):
            return "datetime"
        return "text" if name == "object" else name

    def _color(name: str) -> str:
        idx = _DTYPE_PALETTE.get(name, hash(name) % len(palette))
        return palette[idx % len(palette)]

    names = dtypes.map(
        lambda d: d.name if hasattr(d, "name") else str(d)
    )
    groups: list[str] = []
    for raw_name, grp in dtypes.groupby(names, sort=False):
        name = str(raw_name)
        lbl = _label(name)
        count = f" • {len(grp)} columns" if len(grp) > 3 else ""
        chips = "".join(
            f"<span class='wm-chip-item' style='background:{_color(name)};"
            f" color:{_fg_for_fill(_color(name))};'>"
            f"{escape(str(c))}</span>"
            for c in grp.index
        )
        groups.append(
            f"<div class='wm-chip-group'>"
            f"<span class='wm-chip-label'>{escape(lbl + count)}</span>"
            f"<div class='wm-chip-row'>{chips}</div></div>"
        )

    header = (
        f"<div class='wm-chip-note'>{escape(group_label)}</div>"
        if group_label else ""
    )
    css = _dtype_chip_css(theme)
    display(HTML(
        f"{css}<div class='wm-chip-groups'>"
        f"{header}{''.join(groups)}</div>"
    ))


def _dtype_chip_css(theme: ThemeLike) -> str:
    """CSS for the dtype chip layout (used by display_cols_by_dtype)."""
    return f"""<style>
.wm-chip-groups {{ max-width:{theme.width}px; margin:18px auto 24px auto; }}
.wm-chip-note {{
  margin-bottom:10px; font-family:{theme.font_mono};
  font-size:11px; letter-spacing:0.18em;
  text-transform:uppercase; color:{theme.text_muted};
}}
.wm-chip-group {{ margin:0 0 24px 0; }}
.wm-chip-label {{
  display:inline-block; padding:10px 18px; border-radius:18px;
  background:{theme.text_main}; color:{theme.card_bg};
  font-family:{theme.font_mono}; font-size:12px; font-weight:700;
}}
.wm-chip-row {{
  display:flex; flex-wrap:wrap; gap:12px 14px; margin-top:12px;
}}
.wm-chip-item {{
  display:inline-block; padding:10px 18px; border-radius:18px;
  font-family:{theme.font_mono}; font-size:13px; font-weight:800;
  line-height:1.2; letter-spacing:0.01em;
  text-shadow:0 1px 0 rgba(0,0,0,0.16);
  box-shadow:0 10px 18px -14px rgba(0,0,0,0.32);
  transition:transform 0.16s ease, box-shadow 0.16s ease;
}}
.wm-chip-item:hover {{
  transform:translateY(-1px);
  box-shadow:0 14px 24px -16px rgba(0,0,0,0.34);
}}
</style>"""


def style_with_bg(
    obj: pd.DataFrame | pd.Series[Any],
    theme: ThemeLike,
    bg: str | None = None,
    txt: str = "inherit",
) -> Styler:
    """Apply a uniform background tint to a DataFrame or Series.

    Handy for quick highlighting — e.g. showing which rows have
    missing values by painting them gold.
    """
    fill = bg or theme.color_missing_bg
    frame = (
        obj.to_frame(obj.name or "value")
        if isinstance(obj, pd.Series) else obj
    )
    cell = f"background-color:{fill}"
    if txt != "inherit":
        cell += f"; color:{txt}"
    styles = pd.DataFrame(cell, index=frame.index, columns=frame.columns)
    table_styles: list[dict[str, Any]] = [
        {"selector": "table",
         "props": [("font-family", theme.font_mono),
                   ("font-size", "13px")]},
        {"selector": "th",
         "props": [("font-family", theme.font_display),
                   ("font-weight", "700")]},
        {"selector": "td",
         "props": [("font-family", theme.font_mono),
                   ("font-variant-numeric", "tabular-nums")]},
    ]
    return (
        frame.style
        .apply(lambda _: styles, axis=None)
        .set_table_styles(cast("Any", table_styles), overwrite=False)
    )


def style_df_wm(
    styler: Styler | pd.DataFrame,
    title: str | ThemeLike,
    theme: ThemeLike | None = None,
    kicker: str | None = None,
    hide_index: bool = True,
) -> Styler:
    """Quick-style a table to match the WM card language.

    Two call styles for backward compat::

        style_df_wm(df.style, "Results", theme)   # canonical
        style_df_wm(df, theme)                     # legacy shortcut
    """
    if isinstance(styler, pd.DataFrame):
        styler = styler.style
    if theme is None:
        if isinstance(title, str):
            raise TypeError("style_df_wm() missing 'theme' argument")
        theme = cast("Any", title)
        title = "Table"
    elif not isinstance(title, str):
        raise TypeError("title must be a string when theme is provided")

    safe_title = escape(str(title))
    kicker_frag = ""
    if kicker:
        kicker_frag = (
            f"<div style='color:{theme.text_muted};"
            f" font-family:{theme.font_mono}; font-size:11px;"
            f" letter-spacing:0.18em; margin-bottom:8px;"
            f" text-transform:uppercase;'>"
            f"<span style='color:{theme.accent}'>&#9632;</span>"
            f" {escape(kicker)}</div>"
        )

    caption = (
        f"<div style='text-align:left; padding:24px 24px 0 24px;'>"
        f"{kicker_frag}"
        f"<div style='color:{theme.text_main};"
        f" font-family:{theme.font_display}; font-size:21px;"
        f" font-weight:900; letter-spacing:-0.05em;"
        f" margin-bottom:8px;'>{safe_title}</div>"
        f"<div style='width:12%; height:4px;"
        f" background-color:{theme.accent};"
        f" margin-bottom:8px;'></div>"
        f"<div style='width:100%; height:1px;"
        f" background-color:{theme.grid};"
        f" margin-bottom:16px;'></div></div>"
    )

    shadow = (
        "0 10px 18px -10px rgba(0,0,0,0.18)"
        if theme.mode == "light" else "none"
    )
    data = cast("pd.DataFrame", cast("Any", styler).data)
    align_styles = [
        {"selector": f"tbody td.col{i}",
         "props": (
             [("text-align", "right"), ("white-space", "nowrap")]
             if _looks_numeric(data[c])
             else [("text-align", "left"), ("white-space", "normal"),
                   ("line-height", "1.5"), ("max-width", "360px"),
                   ("overflow-wrap", "anywhere")]
         )}
        for i, c in enumerate(data.columns)
    ]
    base_styles: list[dict[str, Any]] = [
        {"selector": "table",
         "props": [("background-color", theme.card_bg),
                   ("color", theme.text_main),
                   ("font-family", theme.font_mono),
                   ("font-size", "13px"),
                   ("border-collapse", "separate"),
                   ("border-spacing", "0"),
                   ("border-radius", "16px"),
                   ("overflow-x", "auto"),
                   ("box-shadow", shadow),
                   ("width", "100%")]},
        {"selector": "thead th",
         "props": [("font-family", theme.font_display),
                   ("font-size", "12px"), ("font-weight", "700"),
                   ("color", theme.text_muted),
                   ("text-transform", "uppercase"),
                   ("letter-spacing", "0.08em"),
                   ("padding", "12px 16px"),
                   ("border-bottom", f"1px solid {theme.border}"),
                   ("border-right", f"1px solid {theme.grid}"),
                   ("background-color", theme.table_header_bg),
                   ("vertical-align", "bottom")]},
        {"selector": "td",
         "props": [("padding", "12px 16px"),
                   ("border-bottom", f"1px solid {theme.grid}"),
                   ("border-right", f"1px solid {theme.grid}"),
                   ("font-variant-numeric", "tabular-nums"),
                   ("line-height", "1.5"),
                   ("vertical-align", "top")]},
        {"selector": "thead th:last-child, tbody td:last-child",
         "props": [("border-right", "none")]},
        {"selector": "tbody tr:nth-child(even) td",
         "props": [("background-color", theme.table_stripe_bg)]},
        {"selector": "caption",
         "props": [("caption-side", "top")]},
        *align_styles,
    ]
    styler = (
        styler.set_caption(caption)
        .set_table_styles(cast("Any", base_styles), overwrite=False)
    )
    if hide_index:
        styler = styler.hide(axis="index")
    return styler


# Convenience wrappers matching the old wm_theme.py API.

def style_describe(summary: pd.DataFrame, theme: ThemeLike) -> Styler:
    """Alias for :func:`style_describe_wm` (backward compat)."""
    return style_describe_wm(summary, theme)


def style_outlier_report(
    df: pd.DataFrame, theme: ThemeLike,
) -> Styler:
    """Alias for :func:`style_outlier_report_wm` (backward compat)."""
    return style_outlier_report_wm(df, theme)


# ── wm_render_styler ─────────────────────────────────────────────────


def wm_render_styler(
    styler: Styler,
    *,
    theme: ThemeLike,
    table_theme: WMTableTheme = _DEFAULT_TABLE_THEME,
    interactive_rows: bool | None = None,
    wrap_card: bool = True,
    title: str | None = None,
    kicker: str | None = None,
    subtitle: str | None = None,
    wrap_columns: (
        dict[str, int] | list[str] | tuple[str, ...] | set[str] | None
    ) = None,
    chip_text: str | None = None,
    max_height: int | None = None,
) -> None:
    """Render a pandas Styler inside a themed WM card shell.

    This is the go-to function for putting any styled table into a
    notebook with the full WM treatment: title, subtitle, kicker,
    column alignment, and hover effects.

    Parameters
    ----------
    styler : Styler
        A ``df.style`` object, optionally with your own formatting.
    theme : ThemeLike
        Active notebook theme (usually ``WMTheme.light()``).
    wrap_columns : dict or list, optional
        Columns that should soft-wrap. Pass a dict of
        ``{col: max_width_px}`` or a list of column names (default
        width 360 px).
    """
    if interactive_rows is not None:
        table_theme = replace(
            table_theme, interactive_rows=interactive_rows,
        )
    styler = styler.set_table_attributes(
        f'class="{table_theme.table_class}"'
    )
    html_table = styler.to_html()
    css = table_theme.css(theme)
    data = cast("pd.DataFrame", cast("Any", styler).data)
    if max_height is None and len(data) > table_theme.max_visible_rows:
        max_height = table_theme.scroll_height
    scroll_class = "wm-table-scroll"
    scroll_style = ""
    if max_height is not None:
        if max_height < 160:
            raise ValueError("max_height must be at least 160 pixels.")
        scroll_class += " wm-table-scroll--bounded"
        scroll_style = f" style='max-height:{int(max_height)}px;'"
    acss = _align_css(data, table_theme.table_class, wrap=wrap_columns)
    scss = semantic_table_css(theme, table_class=table_theme.table_class)

    header = shell_header_html(
        title=title or "",
        theme=theme,
        subtitle=subtitle,
        kicker=kicker,
        chip_text=chip_text,
        eyebrow="TABLE",
    )

    if wrap_card:
        html = (
            f"{css}{acss}{scss}"
            f"<div class='wm-card {table_theme.card_class}'>"
            f"<div class='wm-shell-inner'>{header}</div>"
            f"<div class='{scroll_class}'{scroll_style} tabindex='0' role='region' "
            f"aria-label='{escape(title or 'Data table')}'>{html_table}</div></div>"
        )
    else:
        html = f"{css}{acss}{scss}{header}{html_table}"
    display(HTML(html))


def wm_semantic_table(
    data: Styler | pd.DataFrame,
    *,
    theme: ThemeLike,
    semantic_columns: Sequence[str] | None = None,
    semantic_by_column: Mapping[str, str] | None = None,
    table_theme: WMTableTheme = _DEFAULT_TABLE_THEME,
    interactive_rows: bool | None = None,
    wrap_card: bool = True,
    title: str | None = None,
    kicker: str | None = None,
    subtitle: str | None = None,
    wrap_columns: (
        dict[str, int] | list[str] | tuple[str, ...] | set[str] | None
    ) = None,
    chip_text: str | None = None,
    hide_index: bool = True,
    max_height: int | None = None,
) -> None:
    """Render a DataFrame with theme-aware semantic status colours.

    This is the reusable replacement for notebook-local HTML tables that
    hard-code red/green inline styles.  It works in Colab light and dark
    mode because the colours come from WM semantic CSS classes.
    """
    styler = style_semantic_wm(
        data,
        theme=theme,
        semantic_columns=semantic_columns,
        semantic_by_column=semantic_by_column,
        hide_index=hide_index,
    )
    wm_render_styler(
        styler,
        theme=theme,
        table_theme=table_theme,
        interactive_rows=interactive_rows,
        wrap_card=wrap_card,
        title=title,
        kicker=kicker,
        subtitle=subtitle,
        wrap_columns=wrap_columns,
        chip_text=chip_text,
        max_height=max_height,
    )


def wm_before_after_table(
    data: Styler | pd.DataFrame,
    *,
    theme: ThemeLike,
    before_columns: Sequence[str],
    after_columns: Sequence[str],
    title: str,
    subtitle: str | None = None,
    kicker: str | None = None,
    chip_text: str | None = "Before / after",
    wrap_columns: (
        dict[str, int] | list[str] | tuple[str, ...] | set[str] | None
    ) = None,
    hide_index: bool = True,
) -> None:
    """Render a before/after comparison table with semantic column roles."""
    semantic_by_column = {
        **{str(column): "before" for column in before_columns},
        **{str(column): "after" for column in after_columns},
    }
    wm_semantic_table(
        data,
        theme=theme,
        semantic_by_column=semantic_by_column,
        title=title,
        subtitle=subtitle,
        kicker=kicker,
        chip_text=chip_text,
        wrap_columns=wrap_columns,
        hide_index=hide_index,
    )


# ── wm_fe_decision_table ─────────────────────────────────────────────


def wm_fe_decision_table(
    *,
    rows: Sequence[Mapping[str, str]],
    theme: ThemeLike,
    title: str,
    subtitle: str | None = None,
    kicker: str | None = None,
    chip_text: str | None = None,
) -> None:
    """Render a feature-engineering pass/fail decision table.

    Each row needs ``status`` ("pass" or "fail"), ``call`` (one of the
    allowed FE call strings like "Pass: lead candidate"), and
    ``reason`` (plain-English explanation).
    """
    if not title.strip():
        raise ValueError("title must be non-empty.")
    if not rows:
        raise ValueError("rows must have at least one decision.")

    icons = {
        "pass": ("✓", "#20B57B", "rgba(32,181,123,0.12)"),
        "fail": ("✕", "#B4233C", "rgba(180,35,60,0.10)"),
    }
    rendered: list[str] = []
    for row in rows:
        status = str(row.get("status", "")).strip().lower()
        call = str(row.get("call", "")).strip()
        reason = str(row.get("reason", "")).strip()
        if status not in icons:
            raise ValueError("status must be 'pass' or 'fail'.")
        if call not in _ALLOWED_FE_CALLS:
            raise ValueError(f"Unknown FE call: {call!r}")
        if not reason:
            raise ValueError("Every row needs a non-empty reason.")
        icon, fg, bg = icons[status]
        rendered.append(
            "<tr>"
            f"<td class='wm-fe-icon-cell'>"
            f"<span class='wm-fe-icon'"
            f" style='color:{fg};background:{bg};'>"
            f"{icon}</span></td>"
            f"<td class='wm-fe-call-cell'>{escape(call)}</td>"
            f"<td class='wm-fe-reason-cell'>{escape(reason)}</td>"
            "</tr>"
        )

    header = shell_header_html(
        title=title, theme=theme, subtitle=subtitle,
        kicker=kicker, chip_text=chip_text, eyebrow="TABLE",
    )
    cc = "wm-fe-decision-card"
    tc = "wm-fe-decision-table"
    css = card_shell_css(theme, card_class=cc)
    fe_css = _fe_table_css(theme, tc, cc)
    html = (
        f"{css}{fe_css}"
        f"<div class='wm-card {cc}'>"
        f"<div class='wm-shell-inner'>{header}</div>"
        f"<div class='wm-table-scroll'>"
        f"<table class='{tc}'>"
        "<thead><tr><th></th><th>FE call</th>"
        "<th>Reason in plain English</th></tr></thead>"
        f"<tbody>{''.join(rendered)}</tbody>"
        f"</table></div></div>"
    )
    display(HTML(html))


def _fe_table_css(theme: ThemeLike, tc: str, cc: str) -> str:
    """CSS specific to the FE decision table."""
    return f"""<style>
div.{cc} {{ overflow:hidden; }}
table.{tc} {{
  width:100%; border-collapse:separate; border-spacing:0;
  font-family:{theme.font_mono}; font-size:13px;
}}
table.{tc} thead th {{
  font-family:{theme.font_display}; font-size:12px; font-weight:800;
  color:{theme.text_muted}; text-transform:uppercase;
  letter-spacing:0.09em; padding:12px 16px;
  border-bottom:1px solid {theme.border};
  border-right:1px solid {theme.grid};
  background:{theme.table_header_bg}; text-align:left;
}}
table.{tc} tbody td {{
  padding:14px 16px; border-bottom:1px solid {theme.grid};
  border-right:1px solid {theme.grid}; color:{theme.text_main};
  vertical-align:top; line-height:1.55;
}}
table.{tc} thead th:last-child,
table.{tc} tbody td:last-child {{ border-right:none; }}
table.{tc} tbody tr:nth-child(even) td {{
  background:{theme.table_stripe_bg};
}}
table.{tc} .wm-fe-icon-cell {{
  width:54px; min-width:54px; text-align:center;
  padding-left:12px; padding-right:12px;
}}
table.{tc} .wm-fe-call-cell {{
  min-width:220px; font-family:{theme.font_display};
  font-size:15px; font-weight:800;
}}
table.{tc} .wm-fe-reason-cell {{
  max-width:540px; white-space:normal; overflow-wrap:anywhere;
}}
table.{tc} .wm-fe-icon {{
  display:inline-flex; align-items:center; justify-content:center;
  width:26px; height:26px; border-radius:999px;
  font-family:{theme.font_mono}; font-size:15px; font-weight:800;
  box-shadow:0 0 0 1px {theme.border} inset;
}}
</style>"""


# ── wm_render_micro_profile_cards ────────────────────────────────────


def wm_render_micro_profile_cards(
    df: pd.DataFrame,
    *,
    theme: ThemeLike,
    columns: Sequence[str] | None = None,
    ordinal_columns: Sequence[str] = (),
    max_cards: int = 24,
    visible_cards: int = 5,
    max_categories: int = 6,
) -> None:
    """Render compact variable profile cards in a horizontal rail.

    This is the system's answer to ``df.describe()``: one mini card
    per column, showing dtype, distribution shape, and key stats.

    Numeric cards show a KDE violin, missing/mean/max/median/min/mode.
    Categorical cards show mode + top-category horizontal bars.

    Parameters
    ----------
    df : DataFrame
        The data to profile.
    columns : list of str, optional
        Which columns to show.  Defaults to all columns.
    ordinal_columns : list of str
        Columns that should use a gradient colour scale for bars
        instead of a flat accent colour.
    visible_cards : int
        How many cards fit before the rail scrolls (1–5).
    max_categories : int
        Max categories to show in categorical bar charts.
    """
    if df.empty:
        display(HTML(
            "<div style='opacity:0.75; font-family:monospace'>"
            "No rows to profile.</div>"
        ))
        return

    cols = list(df.columns) if columns is None else list(columns)
    selected = [str(c) for c in cols if str(c) in df.columns][:max_cards]
    if not selected:
        return

    ordinal_set = {str(c) for c in ordinal_columns}
    rail_w = max(1, min(int(visible_cards), 5))
    cards: list[str] = []
    include_plotlyjs: str | bool = "cdn"

    # Colour tokens.
    accent = theme.accent
    cw = getattr(theme, "colorway", [accent])
    warning = cw[4] if len(cw) > 4 else "#F28C28"
    skew_color = cw[3] if len(cw) > 3 else "#2F6BFF"
    chip_fg = cw[3] if len(cw) > 3 else accent
    chip_border = rgba_css(chip_fg, 0.22)

    ordinal_cmap = mcolors.LinearSegmentedColormap.from_list(
        "wm_ord", [accent, accent, warning],
    )
    # Semantic bar colours for yes/no/true/false columns.
    semantic = {
        "yes": accent, "true": accent, "1": accent,
        "no": cw[0] if cw else accent,
        "false": cw[0] if cw else accent,
        "0": cw[0] if cw else accent,
    }

    for col in selected:
        series = df[col]
        dtype_name = str(series.dtype)
        is_num = bool(pd.api.types.is_numeric_dtype(series))
        missing = int(series.isna().sum())
        dtype_chip = (
            f"<span class='wm-micro-dtype'>{escape(dtype_name)}</span>"
        )

        if is_num:
            card, include_plotlyjs = _numeric_card(
                col, series, dtype_chip, missing, theme,
                accent, skew_color, include_plotlyjs,
            )
        else:
            card = _categorical_card(
                col, series, dtype_chip, missing, theme,
                accent, max_categories, ordinal_set,
                ordinal_cmap, semantic,
            )
        cards.append(card)

    css = _micro_css(theme, rail_w, skew_color, chip_fg, chip_border)
    display(HTML(
        f"{css}<section class='wm-micro-rail'>{''.join(cards)}</section>"
    ))


def _numeric_card(
    col: str,
    series: pd.Series[Any],
    dtype_chip: str,
    missing: int,
    theme: ThemeLike,
    accent: str,
    skew_color: str,
    include_plotlyjs: str | bool,
) -> tuple[str, str | bool]:
    """Build one numeric micro-profile card (violin + stats grid)."""
    numeric = pd.to_numeric(series, errors="coerce")
    valid = numeric.dropna()
    skew_value = valid.skew() if len(valid) >= 3 else 0.0
    skew = float(cast("Any", skew_value))
    high_skew = abs(skew) >= 1.0

    if valid.empty:
        violin = "<div class='wm-micro-empty'>No numeric values</div>"
    else:
        import plotly.graph_objects as go

        fig = go.Figure(data=[go.Violin(
            x=valid, orientation="h", points=False,
            line=dict(color=theme.text_main, width=1.4),
            fillcolor=rgba_css(accent, 0.22), opacity=1.0,
            box=dict(visible=True, width=0.34,
                     fillcolor=rgba_css(theme.card_bg, 0.94),
                     line=dict(color=theme.text_main, width=1.4)),
            meanline_visible=False, hoverinfo="skip",
            spanmode="soft", showlegend=False,
        )])
        fig.update_layout(
            width=296, height=82,
            margin=dict(l=8, r=8, t=10, b=8),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
        )
        violin = fig.to_html(
            full_html=False, include_plotlyjs=include_plotlyjs,
            config={"displayModeBar": False, "responsive": False},
        )
        include_plotlyjs = False

    miss_bg = theme.color_missing_bg if missing > 0 else "transparent"
    def _m(v: float | None) -> str:  # noqa: E301
        return _fmt(v)

    mean_v = float(valid.mean()) if not valid.empty else None
    max_v = float(valid.max()) if not valid.empty else None
    med_v = float(valid.median()) if not valid.empty else None
    min_v = float(valid.min()) if not valid.empty else None
    stats = [
        ("Missing", str(missing), miss_bg),
        ("Mean", _m(mean_v), "transparent"),
        ("Max", _m(max_v), "transparent"),
        ("Median", _m(med_v), "transparent"),
        ("Min", _m(min_v), "transparent"),
        ("Mode", _mode_text(series), "transparent"),
    ]
    grid = "".join(
        f"<div class='wm-micro-metric' style='--wm-bg:{bg};'>"
        f"<span class='wm-micro-key'>{k}</span>"
        f"<span class='wm-micro-val'>{escape(v)}</span></div>"
        for k, v, bg in stats
    )
    cls = "wm-micro-card--high-skew" if high_skew else ""
    html = (
        f"<article class='wm-micro-card {cls}'>"
        f"<div class='wm-micro-head'>"
        f"<span class='wm-micro-name'>{escape(col)}</span>"
        f"{dtype_chip}</div>"
        f"<div class='wm-micro-violin'>{violin}</div>"
        f"<div class='wm-micro-grid'>{grid}</div></article>"
    )
    return html, include_plotlyjs


def _categorical_card(
    col: str,
    series: pd.Series[Any],
    dtype_chip: str,
    missing: int,
    theme: ThemeLike,
    accent: str,
    max_categories: int,
    ordinal_set: set[str],
    ordinal_cmap: Any,
    semantic: dict[str, str],
) -> str:
    """Build one categorical micro-profile card (bars + mode)."""
    counts = (
        series.astype("string").fillna("<NA>")
        .value_counts(dropna=False)
    )
    top = counts.head(max_categories)
    mode = _mode_text(series)
    max_count = max(int(top.iloc[0]), 1) if not top.empty else 1

    bars: list[str] = []
    for rank, (label, count) in enumerate(top.items()):
        pct = int(round((int(count) / max_count) * 100))
        norm = str(label).strip().lower()
        bar_color = semantic.get(norm)
        if bar_color is None and col in ordinal_set:
            grad = rank / max(1, len(top) - 1)
            bar_color = mcolors.to_hex(ordinal_cmap(grad))
        if bar_color is None:
            bar_color = accent
        bars.append(
            "<div class='wm-cat-row'>"
            f"<span class='wm-cat-label'>{escape(str(label))}</span>"
            f"<span class='wm-cat-count'>{int(count):,}</span>"
            f"<span class='wm-cat-bar-track'>"
            f"<span class='wm-cat-bar'"
            f" style='width:{pct}%;background:{bar_color};'>"
            f"</span></span></div>"
        )

    return (
        f"<article class='wm-micro-card'>"
        f"<div class='wm-micro-head'>"
        f"<span class='wm-micro-name'>{escape(col)}</span>"
        f"{dtype_chip}</div>"
        f"<div class='wm-micro-mode'>"
        f"<span>Mode</span><strong>{mode}</strong></div>"
        f"<div class='wm-cat-wrap'>{''.join(bars)}</div>"
        f"<div class='wm-micro-missing'>"
        f"Missing: <strong>{missing:,}</strong></div>"
        f"</article>"
    )


def _micro_css(
    theme: ThemeLike,
    rail_w: int,
    skew_color: str,
    chip_fg: str,
    chip_border: str,
) -> str:
    """CSS for the micro profile card rail."""
    max_w = min(
        theme.width + 112, rail_w * 346 + (rail_w - 1) * 18,
    )
    return f"""<style>
.wm-micro-rail {{
  max-width:{max_w}px; margin:18px auto 24px auto;
  display:grid; grid-auto-flow:column;
  grid-auto-columns:332px; gap:18px;
  overflow-x:auto; padding:10px 10px 16px 10px;
}}
.wm-micro-card {{
  border:1px solid {theme.border}; border-radius:16px;
  background:{theme.card_bg} !important;
  color:{theme.text_main} !important;
  padding:18px 16px;
  box-shadow:0 8px 16px -16px rgba(0,0,0,0.14);
}}
.wm-micro-card--high-skew {{
  box-shadow:0 8px 16px -16px rgba(0,0,0,0.14),
    inset 0 3px 0 {rgba_css(skew_color, 0.92)};
}}
.wm-micro-head {{
  display:flex; justify-content:space-between;
  align-items:flex-start; gap:10px; margin-bottom:12px;
}}
.wm-micro-name {{
  font-family:{theme.font_display}; font-size:15px;
  font-weight:800; color:{theme.text_main}; line-height:1.1;
}}
.wm-micro-dtype {{
  font-family:{theme.font_mono}; font-size:11px; font-weight:800;
  color:{chip_fg}; border:1px solid {chip_border};
  background:{theme.card_bg}; padding:3px 10px; border-radius:999px;
}}
.wm-micro-violin {{
  height:102px; padding:8px; background:{theme.plot_bg};
  border:1px solid {theme.grid}; border-radius:14px;
  overflow:hidden; margin-bottom:12px; box-sizing:border-box;
}}
.wm-micro-grid {{
  display:grid; grid-template-columns:1fr 1fr; gap:8px;
}}
.wm-micro-metric {{
  background:var(--wm-bg,transparent);
  border:1px solid {theme.grid}; border-radius:10px;
  padding:8px 12px; display:flex; justify-content:space-between;
  gap:10px; min-width:0;
}}
.wm-micro-key {{
  font-family:{theme.font_mono}; font-size:10px;
  text-transform:uppercase; letter-spacing:0.08em;
  color:{theme.text_muted}; white-space:nowrap;
}}
.wm-micro-val {{
  font-family:{theme.font_mono}; font-size:12px;
  font-weight:700; color:{theme.text_main};
  text-align:right; white-space:nowrap;
}}
.wm-micro-mode {{
  display:flex; justify-content:space-between;
  font-family:{theme.font_mono}; font-size:12px;
  margin:6px 0 10px 0; color:{theme.text_main};
}}
.wm-cat-wrap {{ display:grid; gap:8px; }}
.wm-cat-row {{
  display:grid; grid-template-columns:minmax(80px,1fr) auto;
  gap:6px 8px; align-items:center;
}}
.wm-cat-label, .wm-cat-count {{
  font-family:{theme.font_mono}; font-size:11px;
  color:{theme.text_main};
}}
.wm-cat-label {{
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}}
.wm-cat-bar-track {{
  grid-column:1 / -1; height:7px; border-radius:999px;
  background:{theme.plot_bg}; overflow:hidden;
  border:1px solid {theme.grid};
}}
.wm-cat-bar {{ display:block; height:100%; border-radius:999px; }}
.wm-micro-missing {{
  margin-top:10px; display:inline-flex; align-items:center;
  gap:6px; padding:6px 10px; border-radius:999px;
  border:1px solid {rgba_css(theme.color_missing_txt, 0.18)};
  background:{theme.color_missing_bg};
  font-family:{theme.font_mono}; font-size:11px;
  color:{theme.color_missing_txt};
}}
.wm-micro-missing strong {{ color:{theme.text_main}; }}
.wm-micro-empty {{
  display:flex; align-items:center; justify-content:center;
  height:100%; font-family:{theme.font_mono}; font-size:11px;
  color:{theme.text_muted};
}}
</style>"""
