"""Plotly figure styling and chart-card rendering for WM notecards.

Public API
----------
- :func:`style_fig_wm` — apply the WM card aesthetic to any Plotly figure.
- :func:`show_fig_wm` — display a styled figure inside a notebook.
- :func:`wm_render_figure_card` — render a figure inside a WM card shell.
- :func:`wm_line_panels` — multi-panel line chart with per-metric callouts.
"""
from __future__ import annotations

import contextlib
import re
import sys
from html import escape
from numbers import Number
from textwrap import wrap
from typing import TYPE_CHECKING, Any, Literal, cast

import pandas as pd
import plotly.graph_objects as go
from IPython.display import HTML, display
from plotly.subplots import make_subplots

from wm_notecards._html import plot_shell_html, rgba_css
from wm_notecards.kicker import WMKicker

if TYPE_CHECKING:
    from collections.abc import Iterable

    from wm_notecards._types import ThemeLike, WMCardRole, WMVerdictTone

# ── Private constants ───────────────────────────────────────────────
_PLOT_BR_RE = re.compile(r"<br\s*/?>", flags=re.IGNORECASE)
_LEGACY_PLOTLY_COLORS = {
    "#1f77b4": "accent",
    "#2ca02c": "teal",
    "#d62728": "negative",
    "#ff7f0e": "warning",
}


# ── Text wrapping ───────────────────────────────────────────────────

def _wrap_plot_text(text: str | None, *, max_chars: int) -> tuple[str | None, int]:
    """Wrap *text* into ``<br>``-joined lines, returning line count.

    Parameters
    ----------
    text : str | None
        Raw text to wrap.  ``None`` / empty returns ``(None, 0)``.
    max_chars : int
        Target line width in characters.

    Returns
    -------
    tuple[str | None, int]
        ``(html, n_lines)`` — HTML-escaped, ``<br>``-joined result and
        the number of logical lines produced.
    """
    if not text:
        return None, 0

    normalized = _PLOT_BR_RE.sub("\n", str(text))
    lines: list[str] = []
    for block in normalized.splitlines() or [normalized]:
        stripped = block.strip()
        if not stripped:
            continue
        lines.extend(
            wrap(
                stripped,
                width=max_chars,
                break_long_words=False,
                break_on_hyphens=False,
            )
            or [stripped]
        )

    html = "<br>".join(escape(line) for line in (lines or [normalized.strip()]))
    return html, max(1, len(lines) or 1)


# ── Bar-chart axis helpers ──────────────────────────────────────────

def _auto_wrap_bar_axis_labels(fig: go.Figure) -> tuple[int, int]:
    """Wrap long bar-chart axis labels and return sizing deltas.

    Returns
    -------
    tuple[int, int]
        ``(extra_left_margin, extra_height)`` in pixels.
    """
    left_margin = 0
    extra_height = 0

    for trace in fig.data:
        if getattr(trace, "type", None) != "bar":
            continue
        orientation: str = getattr(trace, "orientation", "v")
        raw_values = getattr(trace, "y" if orientation == "h" else "x", None)
        if raw_values is None or len(raw_values) == 0:
            continue

        wrapped_values, max_line_length, total_extra, changed = (
            _wrap_bar_labels(raw_values, orientation)
        )
        if not changed:
            continue

        trace.update(**{("y" if orientation == "h" else "x"): wrapped_values})
        extra_height = max(
            extra_height,
            total_extra * (26 if orientation == "h" else 16),
        )
        if orientation == "h":
            left_margin = max(
                left_margin,
                min(340, max(128, 64 + max_line_length * 8)),
            )
        else:
            fig.update_xaxes(tickangle=-18)

    return left_margin, extra_height


def _wrap_bar_labels(
    raw_values: object,
    orientation: str,
) -> tuple[list[str], int, int, bool]:
    """Wrap a sequence of bar labels, returning wrapped list and metrics.

    Returns
    -------
    tuple[list[str], int, int, bool]
        ``(wrapped_values, max_line_length, total_extra_lines, changed)``.
    """
    wrap_width = 28 if orientation == "h" else 14
    wrapped_values: list[str] = []
    max_line_length = 0
    total_extra = 0
    changed = False

    for raw in cast("Iterable[object]", raw_values):
        label = str(raw)
        wrapped, line_count = _wrap_plot_text(label, max_chars=wrap_width)
        wrapped_label = wrapped or escape(label)
        changed = changed or ("<br>" in wrapped_label)
        wrapped_values.append(wrapped_label)
        total_extra += max(0, line_count - 1)
        max_line_length = max(
            max_line_length,
            max(
                (len(part) for part in wrapped_label.split("<br>")),
                default=len(label),
            ),
        )

    return wrapped_values, max_line_length, total_extra, changed


# ── Figure introspection ────────────────────────────────────────────

def _figure_uses_colorbar(fig: go.Figure) -> bool:
    """Return ``True`` if any trace in *fig* requests a colour bar."""
    for trace in fig.data:
        if getattr(trace, "coloraxis", None):
            return True
        if getattr(trace, "showscale", False):
            return True
        marker = getattr(trace, "marker", None)
        if marker is None:
            continue
        if getattr(marker, "showscale", False) or getattr(marker, "coloraxis", None):
            return True
    return False


def _header_height_growth(*, title_lines: int, subtitle_lines: int) -> int:
    """Extra pixels needed when the header wraps beyond one line."""
    return max(0, title_lines - 1) * 26 + max(0, subtitle_lines - 1) * 16


def _minimum_plot_area_height(fig: go.Figure) -> int:
    """Compute minimum plot-area height based on bar count."""
    max_h_bars = 0
    max_v_bars = 0

    for trace in fig.data:
        if getattr(trace, "type", None) != "bar":
            continue
        orientation: str = getattr(trace, "orientation", "v")
        values = getattr(trace, "y" if orientation == "h" else "x", None)
        count = len(values) if values is not None else 0
        if orientation == "h":
            max_h_bars = max(max_h_bars, count)
        else:
            max_v_bars = max(max_v_bars, count)

    if max_h_bars:
        return max(240, min(420, 26 * max_h_bars))
    if max_v_bars:
        return max(220, min(300, 34 * max_v_bars))
    return 220


def _should_show_legend(fig: go.Figure) -> bool:
    """Decide whether the legend deserves real space in the card layout.

    WM chart cards should not spend ~50px of bottom margin on a legend
    that a reader will never need. By default we show legends only when
    there is more than one legendable trace. If a caller explicitly sets
    ``layout.showlegend = True``, we respect that and keep the legend even
    for a single trace.
    """
    layout_showlegend = getattr(fig.layout, "showlegend", None)
    if layout_showlegend is False:
        return False

    legendable_traces = 0
    for trace in fig.data:
        if getattr(trace, "visible", True) is False:
            continue
        if getattr(trace, "showlegend", None) is False:
            continue
        legendable_traces += 1

    if layout_showlegend is True:
        return legendable_traces > 0
    return legendable_traces > 1


def _legacy_color_replacements(theme: ThemeLike) -> dict[str, str]:
    """Map common plotting defaults onto the active WM semantic palette."""
    palette = tuple(getattr(theme, "category_palette", ()))
    colorway = tuple(getattr(theme, "colorway", (theme.accent,)))
    return {
        "accent": theme.accent,
        "teal": palette[4] if len(palette) > 4 else colorway[-1],
        "negative": getattr(theme, "heat_neg", colorway[2]),
        "warning": colorway[4] if len(colorway) > 4 else "#D88C2E",
    }


def _normalize_legacy_trace_colors(fig: go.Figure, theme: ThemeLike) -> None:
    """Replace exact Matplotlib/Plotly default colors with WM tokens.

    Only exact, well-known defaults are changed. Deliberately chosen custom
    colors and continuous scales are left untouched.
    """
    replacements = _legacy_color_replacements(theme)
    for trace in fig.data:
        for container_name in ("line", "marker"):
            container = getattr(trace, container_name, None)
            color = getattr(container, "color", None) if container is not None else None
            if not isinstance(color, str):
                continue
            token = _LEGACY_PLOTLY_COLORS.get(color.lower())
            if token:
                cast("Any", container).color = replacements[token]


def _vertical_bar_categories(fig: go.Figure) -> list[object]:
    """Return ordered unique categories used by vertical bar traces."""
    categories: list[object] = []
    for trace in fig.data:
        if getattr(trace, "type", None) != "bar":
            continue
        if getattr(trace, "orientation", "v") == "h":
            continue
        raw_values = getattr(trace, "x", None)
        if raw_values is None:
            continue
        for value in raw_values:
            if value not in categories:
                categories.append(value)
    return categories


def _apply_bar_category_policy(
    fig: go.Figure,
    *,
    category_policy: Literal["auto", "preserve"],
    max_categories: int,
    allow_dense_categories: bool,
) -> None:
    """Prevent unreadable categorical bar charts before they render.

    String-heavy vertical bars become horizontal when the label density is
    unsafe. Charts above the hard category limit must be reduced, faceted, or
    explicitly opted out so an LLM cannot silently recreate a label pile-up.
    """
    categories = _vertical_bar_categories(fig)
    if not categories:
        return
    if len(categories) > max_categories and not allow_dense_categories:
        raise ValueError(
            f"Categorical bar chart has {len(categories)} categories; the WM release "
            f"limit is {max_categories}. Use top-N, facet the chart, or pass "
            "allow_dense_categories=True after a visual review."
        )
    if category_policy == "preserve":
        return
    if any(isinstance(value, Number) and not isinstance(value, bool) for value in categories):
        return

    labels = [str(value) for value in categories]
    should_transpose = len(labels) >= 10 or max(map(len, labels), default=0) > 14
    if not should_transpose:
        return

    for trace in fig.data:
        if getattr(trace, "type", None) != "bar":
            continue
        if getattr(trace, "orientation", "v") == "h":
            continue
        old_x = getattr(trace, "x", None)
        old_y = getattr(trace, "y", None)
        trace.update(x=old_y, y=old_x, orientation="h")

    old_x_title = str(getattr(getattr(fig.layout.xaxis, "title", None), "text", "") or "")
    old_y_title = str(getattr(getattr(fig.layout.yaxis, "title", None), "text", "") or "")
    fig.update_xaxes(title_text=old_y_title or None)
    fig.update_yaxes(title_text=old_x_title or None, autorange="reversed")


# ── Kicker / chip annotation helpers ───────────────────────────────

def _plotly_kicker_text(kicker: str | None) -> str | None:
    """Convert a raw kicker spec to Plotly-safe plain text.

    Tries ``WMKicker.parse(kicker).to_plotly_text()`` first, then
    ``.to_line()``, and finally falls back to bullet-prefixed raw text.

    Parameters
    ----------
    kicker : str | None
        Raw kicker string (e.g. ``"STANDARD,03,EDA"``).

    Returns
    -------
    str | None
        Plain text suitable for Plotly title prepend, or ``None``.
    """
    if not kicker:
        return None
    parsed = WMKicker.parse(kicker)
    to_plotly = getattr(parsed, "to_plotly_text", None)
    if callable(to_plotly):
        return str(to_plotly())
    to_line = getattr(parsed, "to_line", None)
    if callable(to_line):
        return f"■ {to_line()}"
    return str(kicker).replace("&BULL;", "•").replace("&bull;", "•")


def _prepend_kicker_to_title(
    fig: go.Figure,
    *,
    kicker_text: str,
    theme: ThemeLike,
) -> None:
    """Insert a kicker line above the existing Plotly title."""
    title = getattr(fig.layout, "title", None)
    current_text = str(getattr(title, "text", "") or "")
    if not current_text or kicker_text in current_text:
        return

    kicker_span = (
        f"<span style='font-family:{theme.font_mono};font-size:11px;"
        f"letter-spacing:0.14em;text-transform:uppercase;"
        f"color:{theme.text_muted};'>{escape(kicker_text)}</span>"
    )
    fig.update_layout(title=dict(text=f"{kicker_span}<br>{current_text}"))


def _add_header_chip(
    fig: go.Figure,
    *,
    chip_text: str,
    theme: ThemeLike,
) -> None:
    """Add a status-chip annotation to the top-right of the figure."""
    chip_color: str = getattr(theme, "heat_neg", theme.accent)
    chip_label = str(chip_text).strip().upper()
    annotations = list(getattr(fig.layout, "annotations", ()) or ())
    if any(
        str(getattr(ann, "text", "") or "") == chip_label
        for ann in annotations
    ):
        return
    annotations.append(
        go.layout.Annotation(
            xref="paper",
            yref="paper",
            x=0.970,
            y=1.255,
            xanchor="right",
            yanchor="top",
            align="right",
            showarrow=False,
            bgcolor=theme.card_bg,
            bordercolor=rgba_css(chip_color, 0.34),
            borderwidth=1,
            borderpad=8,
            text=chip_label,
            font=dict(
                family=theme.font_mono,
                size=11,
                color=chip_color,
            ),
        )
    )
    fig.update_layout(annotations=annotations)


# ── Value formatting ────────────────────────────────────────────────

def _format_panel_value(
    value: float,
    *,
    value_format: str | None,
    prefix: str = "",
    suffix: str = "",
) -> str:
    """Format a numeric value with optional prefix/suffix."""
    body = format(value, value_format) if value_format else f"{value:g}"
    return f"{prefix}{body}{suffix}"


# =====================================================================
# Public API
# =====================================================================

def style_fig_wm(
    fig: go.Figure,
    *,
    title: str,
    theme: ThemeLike,
    kicker: str | None = None,
    subtitle: str | None = None,
    show_kicker: bool = True,
    legend_bottom: bool = True,
    center_title: bool = False,
    margin_overrides: dict[str, int] | None = None,
    paper_transparent: bool = False,
    category_policy: Literal["auto", "preserve"] = "auto",
    max_categories: int = 24,
    allow_dense_categories: bool = False,
    normalize_legacy_colors: bool = True,
) -> go.Figure:
    """Apply the WM card aesthetic to any Plotly figure.

    Configures typography, colour-way, margins, axis styling, legend
    placement, and hover labels to match the WM visual language.

    .. warning::

       REGRESSION WARNING: Do NOT set ``config={'responsive': True}``.
       Charts must stay non-responsive for centering.

    Parameters
    ----------
    fig : go.Figure
        Plotly figure to style **in-place**.
    title : str
        Card headline — auto-wrapped to fit the plot width.
    theme : ThemeLike
        Active visual theme.
    kicker : str | None
        Kicker spec (currently unused by this function; reserved for
        callers that attach a kicker before styling).
    subtitle : str | None
        Secondary line below the title.  Falls back to any subtitle
        already set on the figure.
    show_kicker : bool
        Whether to render the kicker (reserved, forwarded by callers).
    legend_bottom : bool
        Place the legend below the plot area (``True``) or to the
        right (``False``).
    center_title : bool
        Horizontally center the title instead of left-aligning it.
    margin_overrides : dict[str, int] | None
        Per-side pixel overrides merged into the default margins.
    paper_transparent : bool
        When ``True`` the paper background is fully transparent.
    category_policy : {``"auto"``, ``"preserve"``}
        ``"auto"`` turns label-heavy vertical bars into horizontal bars.
    max_categories : int
        Hard release limit for vertical categorical bars.
    allow_dense_categories : bool
        Explicit visual-review escape hatch for charts above the limit.
    normalize_legacy_colors : bool
        Replace exact Matplotlib/Plotly defaults with semantic WM tokens.

    Returns
    -------
    go.Figure
        The same *fig* instance, styled in-place.
    """
    if max_categories < 1:
        raise ValueError("max_categories must be at least 1.")
    _apply_bar_category_policy(
        fig,
        category_policy=category_policy,
        max_categories=max_categories,
        allow_dense_categories=allow_dense_categories,
    )
    if normalize_legacy_colors:
        _normalize_legacy_trace_colors(fig, theme)

    show_legend = _should_show_legend(fig)
    margin = dict(l=64, r=72, t=102, b=112 if (legend_bottom and show_legend) else 62)
    if margin_overrides:
        margin.update(margin_overrides)

    muted_text = (
        "rgba(17,17,17,0.78)" if theme.mode == "light" else theme.text_muted
    )
    wrapped_left_margin, extra_height = _auto_wrap_bar_axis_labels(fig)
    if wrapped_left_margin:
        margin["l"] = max(margin["l"], wrapped_left_margin)
    if _figure_uses_colorbar(fig):
        margin["r"] = max(margin["r"], 124)

    existing_subtitle = _read_existing_subtitle(fig)
    figure_width = int(getattr(fig.layout, "width", 0) or theme.width)
    plot_width = max(360, figure_width - margin["l"] - margin["r"])

    title_html, title_lines = _wrap_plot_text(
        title,
        max_chars=max(24, min(42, plot_width // 17)),
    )
    subtitle_text = subtitle if subtitle is not None else existing_subtitle
    subtitle_html, subtitle_lines = _wrap_plot_text(
        subtitle_text,
        max_chars=max(46, min(96, plot_width // 8)),
    )
    header_growth = _header_height_growth(
        title_lines=title_lines,
        subtitle_lines=subtitle_lines,
    )
    margin["t"] += header_growth

    theme_height = int(getattr(theme, "height", 400) or 400)
    target_plot_height = _minimum_plot_area_height(fig)
    figure_height = max(
        int(getattr(fig.layout, "height", 0) or theme_height)
        + extra_height
        + header_growth,
        margin["t"] + margin["b"] + target_plot_height,
    )
    title_x = (
        0.5
        if center_title
        else min(0.42, max(0.0, margin["l"] / max(figure_width, 1)))
    )

    colorway = list(getattr(theme, "colorway", (theme.accent,)))
    tooltip_bg = getattr(theme, "tooltip_bg", theme.card_bg)

    _apply_layout(
        fig,
        theme=theme,
        figure_width=figure_width,
        figure_height=figure_height,
        margin=margin,
        muted_text=muted_text,
        colorway=colorway,
        tooltip_bg=tooltip_bg,
        title_html=title_html,
        title_x=title_x,
        center_title=center_title,
        subtitle_html=subtitle_html,
        paper_transparent=paper_transparent,
        legend_bottom=legend_bottom,
        show_legend=show_legend,
    )

    axis_style = dict(
        gridcolor=theme.grid,
        zeroline=False,
        ticks="outside",
        ticklen=6,
        tickwidth=1,
        tickfont=dict(family=theme.font_mono, size=11, color=muted_text),
        title=dict(
            font=dict(family=theme.font_mono, size=12, color=muted_text),
            standoff=18,
        ),
        showline=False,
        automargin=True,
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)

    _clean_bar_traces(fig)
    _pad_outside_text_bars(fig)
    return fig


# ── style_fig_wm sub-helpers (keep nesting ≤ 2) ────────────────────

def _read_existing_subtitle(fig: go.Figure) -> str | None:
    """Extract the existing subtitle text from a Plotly figure."""
    try:
        st = getattr(fig.layout.title, "subtitle", None)
        return getattr(st, "text", None) if st is not None else None
    except Exception:
        return None


def _apply_layout(
    fig: go.Figure,
    *,
    theme: ThemeLike,
    figure_width: int,
    figure_height: int,
    margin: dict[str, int],
    muted_text: str,
    colorway: list[str],
    tooltip_bg: str,
    title_html: str | None,
    title_x: float,
    center_title: bool,
    subtitle_html: str | None,
    paper_transparent: bool,
    legend_bottom: bool,
    show_legend: bool,
) -> None:
    """Apply the main ``update_layout`` call for :func:`style_fig_wm`."""
    subtitle_suffix = ""
    if subtitle_html:
        # Plotly's ``title.subtitle`` is positioned as if the title occupies
        # one line.  It therefore overlaps auto-wrapped, multi-line titles.
        # Keep both strings in the same SVG text flow so every rendered line
        # reserves its own vertical space.
        subtitle_suffix = (
            "<br><span style='font-family:"
            f"{theme.font_mono}; font-size:13px; font-weight:400;"
            f" letter-spacing:0; color:{muted_text};'>{subtitle_html}</span>"
        )

    fig.update_layout(
        width=figure_width,
        height=figure_height,
        autosize=False,
        paper_bgcolor=(
            "rgba(0,0,0,0)" if paper_transparent else theme.card_bg
        ),
        plot_bgcolor=theme.plot_bg,
        colorway=colorway,
        font=dict(family=theme.font_mono, size=12, color=muted_text),
        title=dict(
            text=(
                f"<span style='font-family:{theme.font_display};"
                f" font-weight:900; letter-spacing:-0.8px;'>"
                f"{title_html}</span>{subtitle_suffix}"
            ),
            x=title_x,
            xanchor="center" if center_title else "left",
            y=0.975,
            yanchor="top",
            pad=dict(t=10, b=0),
            font=dict(size=30, color=theme.text_main),
        ),
        margin=margin,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(
                family=theme.font_mono, size=12, color=theme.text_main,
            ),
            orientation="h" if legend_bottom else "v",
            yanchor="bottom" if legend_bottom else "top",
            y=-0.40 if legend_bottom else 1.0,
            xanchor="left",
            x=0.0,
        ),
        showlegend=show_legend,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=tooltip_bg,
            bordercolor=theme.border,
            font=dict(
                family=theme.font_mono, size=12, color=theme.text_main,
            ),
        ),
    )


def _clean_bar_traces(fig: go.Figure) -> None:
    """Remove marker outlines and enable clip-off for bar traces."""
    for trace in fig.data:
        marker = getattr(trace, "marker", None)
        if getattr(trace, "type", None) == "bar":
            with contextlib.suppress(Exception):
                trace.update(cliponaxis=False)
        if marker is None:
            continue
        try:
            trace.update(marker_line_width=0)
        except Exception:
            continue


def _pad_outside_text_bars(fig: go.Figure) -> None:
    """Add value-axis padding so ``textposition='outside'`` text fits."""
    for axis_name, orientation, value_attr in (
        ("xaxis", "h", "x"),
        ("yaxis", "v", "y"),
    ):
        bar_values = _collect_outside_bar_values(fig, orientation, value_attr)
        if not bar_values:
            continue

        axis = getattr(fig.layout, axis_name, None)
        if getattr(axis, "range", None) if axis is not None else None:
            continue

        max_val = max(bar_values)
        min_val = min(bar_values)
        span = max_val - min_val
        max_abs = max(abs(max_val), abs(min_val))
        base_pad = 0.01 if max_abs <= 1.0 else 0.25
        padding = max(span * 0.10, abs(max_val) * 0.08, base_pad)
        axis_range = [min(0.0, min_val), max_val + padding]

        if axis_name == "xaxis":
            fig.update_xaxes(range=axis_range)
        else:
            fig.update_yaxes(range=axis_range)


def _collect_outside_bar_values(
    fig: go.Figure,
    orientation: str,
    value_attr: str,
) -> list[float]:
    """Collect numeric bar values that use ``textposition='outside'``."""
    values: list[float] = []
    for trace in fig.data:
        if getattr(trace, "type", None) != "bar":
            continue
        if getattr(trace, "orientation", "v") != orientation:
            continue
        if getattr(trace, "textposition", None) != "outside":
            continue
        series = pd.to_numeric(
            pd.Series(getattr(trace, value_attr, [])),
            errors="coerce",
        ).dropna()
        if not series.empty:
            values.extend(series.astype(float).tolist())
    return values


# ── show_fig_wm ─────────────────────────────────────────────────────

def show_fig_wm(
    fig: go.Figure,
    *,
    file_stub: str,
    theme: ThemeLike,
    mode: Literal["notebook", "export"] = "notebook",
) -> None:
    """Display a styled Plotly figure inside a centred card shell.

    The HTML shell is **the** single source of truth for the outer card
    border, padding, radius, and shadow.  The Plotly figure itself must
    **not** draw a second outer card border.

    **Google Colab (``mode="notebook"`` only):** uses ``fig.show(renderer="colab")``
    without the HTML shell — Plotly JS inside :func:`plot_shell_html` often fails
    there (blank card). **Jupyter / VS Code** keep ``fig.to_html`` +
    :func:`plot_shell_html` so figures stay centred with WM card background.

    Parameters
    ----------
    fig : go.Figure
        Styled figure (typically after :func:`style_fig_wm`).
    file_stub : str
        Base filename used for the image-export button.
    theme : ThemeLike
        Active visual theme.
    mode : ``"notebook"`` | ``"export"``
        Rendering target (currently both go through ``IPython.display``).
    """
    export_scale = float(getattr(theme, "export_scale", 2.0) or 2.0)
    config: dict[str, object] = {
        "displaylogo": False,
        "responsive": False,
        "displayModeBar": False,
        "toImageButtonOptions": {
            "format": "svg",
            "filename": file_stub,
            "width": fig.layout.width,
            "height": fig.layout.height,
            "scale": export_scale,
        },
    }
    figure_width = int(getattr(fig.layout, "width", 0) or theme.width)
    figure_height = int(
        getattr(fig.layout, "height", 0)
        or getattr(theme, "height", 400)
        or 400
    )

    # REGRESSION GUARD: Only Colab reliably breaks on plot_shell_html + embedded
    # Plotly (blank white card). Jupyter / VS Code need the shell for centering +
    # card_bg — do not route them through fig.show() alone.
    if mode == "notebook" and "google.colab" in sys.modules:
        fig.update_layout(
            autosize=False,
            width=min(figure_width, 960),
            height=figure_height,
        )
        config = {
            **config,
            "toImageButtonOptions": {
                "format": "svg",
                "filename": file_stub,
                "width": fig.layout.width,
                "height": fig.layout.height,
                "scale": export_scale,
            },
        }
        fig.show(config=config, renderer="colab")
        return

    figure_html = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config=config,
        default_width=f"{figure_width}px",
        default_height=f"{figure_height}px",
    )
    display(
        HTML(
            plot_shell_html(
                figure_html,
                theme,
                figure_width=figure_width,
            )
        )
    )


# ── wm_render_figure_card ───────────────────────────────────────────

def wm_render_figure_card(
    fig: go.Figure,
    *,
    theme: ThemeLike,
    file_stub: str,
    role: WMCardRole = "chart",
    kicker: str | None = None,
    verdict_tone: WMVerdictTone = "neutral",
    mode: Literal["notebook", "export"] = "notebook",
    chip_text: str | None = None,
) -> None:
    """Render a Plotly figure inside a complete WM card shell.

    Attaches kicker and chip annotations to the figure, then delegates
    to :func:`show_fig_wm` for shell-wrapped display.

    .. warning::

       REGRESSION WARNING: The plot shell owns centering, padding,
       radius, and shadow.  The figure must NOT draw a second outer
       card border.

    Parameters
    ----------
    fig : go.Figure
        Styled figure (typically after :func:`style_fig_wm`).
    theme : ThemeLike
        Active visual theme.
    file_stub : str
        Base filename for the export button.
    role : WMCardRole
        Card role — must be ``"chart"`` or ``"verdict"``.
    kicker : str | None
        Kicker spec prepended above the figure title.
    verdict_tone : WMVerdictTone
        Tone token (reserved for downstream role-colour logic).
    mode : ``"notebook"`` | ``"export"``
        Rendering target.
    chip_text : str | None
        Optional status chip in the top-right corner.

    Raises
    ------
    ValueError
        If *role* is not ``"chart"`` or ``"verdict"``.
    """
    if role not in ("chart", "verdict"):
        raise ValueError(
            "wm_render_figure_card supports chart or verdict roles only."
        )

    fig_width = int(getattr(fig.layout, "width", 0) or theme.width)
    fig.update_layout(
        width=min(fig_width, theme.width),
        paper_bgcolor=(
            "rgba(0,0,0,0)" if mode == "notebook" else theme.card_bg
        ),
    )

    _apply_kicker_annotation(fig, kicker=kicker, theme=theme)
    _apply_chip_annotation(fig, chip_text=chip_text, theme=theme)
    show_fig_wm(fig, file_stub=file_stub, theme=theme, mode=mode)


def _apply_kicker_annotation(
    fig: go.Figure,
    *,
    kicker: str | None,
    theme: ThemeLike,
) -> None:
    """Prepend a kicker to the figure title with margin adjustments."""
    annotation_text = _plotly_kicker_text(kicker)
    if not annotation_text:
        return
    current_margin = getattr(fig.layout, "margin", None)
    top_margin = int(getattr(current_margin, "t", 0) or 0)
    theme_height = int(getattr(theme, "height", 400) or 400)
    current_height = int(getattr(fig.layout, "height", 0) or theme_height)
    _prepend_kicker_to_title(fig, kicker_text=annotation_text, theme=theme)
    new_top = max(top_margin + 22, 128)
    fig.update_layout(
        margin=dict(t=new_top),
        height=current_height + max(0, new_top - top_margin),
    )


def _apply_chip_annotation(
    fig: go.Figure,
    *,
    chip_text: str | None,
    theme: ThemeLike,
) -> None:
    """Add a chip annotation with margin adjustments."""
    if not chip_text:
        return
    current_margin = getattr(fig.layout, "margin", None)
    top_margin = int(getattr(current_margin, "t", 0) or 0)
    theme_height = int(getattr(theme, "height", 400) or 400)
    current_height = int(getattr(fig.layout, "height", 0) or theme_height)
    # KEEP THIS HIGH.  If this margin shrinks, the validation chip lands
    # on top of subplot titles and looks broken in saved notebooks.
    new_top = max(top_margin + 64, 218)
    _add_header_chip(fig, chip_text=chip_text, theme=theme)
    fig.update_layout(
        margin=dict(t=new_top),
        height=current_height + max(0, new_top - top_margin),
    )


# ── wm_line_panels ──────────────────────────────────────────────────

def wm_line_panels(
    df: pd.DataFrame,
    *,
    x_col: str,
    y_cols: list[str],
    theme: ThemeLike,
    title: str,
    subtitle: str | None = None,
    kicker: str | None = None,
    y_labels: dict[str, str] | None = None,
    colors: dict[str, str] | None = None,
    value_formats: dict[str, str] | None = None,
    value_prefixes: dict[str, str] | None = None,
    value_suffixes: dict[str, str] | None = None,
    panel_notes: dict[str, str] | None = None,
    width: int | None = None,
    height: int | None = None,
) -> go.Figure:
    """Build a stacked multi-panel line chart with per-metric callouts.

    Each metric gets its own subplot row with a fill-to-zero area,
    median reference line, and a right-hand callout showing the latest
    value.

    Parameters
    ----------
    df : pd.DataFrame
        Source data frame.
    x_col : str
        Column used as the shared x-axis (parsed as datetime).
    y_cols : list[str]
        One column per panel row.
    theme : ThemeLike
        Active visual theme.
    title : str
        Card headline.
    subtitle : str | None
        Secondary line below the title.
    kicker : str | None
        Kicker spec passed through to :func:`style_fig_wm`.
    y_labels : dict[str, str] | None
        Display-name overrides keyed by column name.
    colors : dict[str, str] | None
        Per-column trace colour overrides.
    value_formats : dict[str, str] | None
        Python format specs keyed by column (e.g. ``{".2f"}``).
    value_prefixes : dict[str, str] | None
        String prepended to formatted values (e.g. ``"$"``).
    value_suffixes : dict[str, str] | None
        String appended to formatted values (e.g. ``"%"``).
    panel_notes : dict[str, str] | None
        Per-panel note that replaces the default subplot title.
    width : int | None
        Override figure width in pixels.
    height : int | None
        Override figure height in pixels.

    Returns
    -------
    go.Figure
        Fully styled multi-panel figure.

    Raises
    ------
    ValueError
        If *y_cols* is empty.
    """
    if not y_cols:
        raise ValueError("y_cols must contain at least one column.")

    y_labels = y_labels or {}
    colors = colors or {}
    value_formats = value_formats or {}
    value_prefixes = value_prefixes or {}
    value_suffixes = value_suffixes or {}
    panel_notes = panel_notes or {}

    plot_df = df.copy()
    plot_df[x_col] = pd.to_datetime(plot_df[x_col])

    panel_height = 140
    subplot_titles = [
        panel_notes.get(col, y_labels.get(col, col.replace("_", " ").title()))
        for col in y_cols
    ]
    fig = make_subplots(
        rows=len(y_cols),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=subplot_titles,
    )
    subplot_title_count = len(fig.layout.annotations)

    palette = list(getattr(theme, "colorway", (theme.accent,))[1:]) or list(
        getattr(theme, "category_palette", (theme.accent,))
    )
    max_callout_chars = 0

    for row, col in enumerate(y_cols, start=1):
        label = y_labels.get(col, col.replace("_", " ").title())
        color = colors.get(col, palette[(row - 1) % len(palette)])
        value_fmt = value_formats.get(col, "")
        value_pfx = value_prefixes.get(col, "")
        value_sfx = value_suffixes.get(col, "")

        max_callout_chars = _add_panel_trace(
            fig,
            plot_df=plot_df,
            x_col=x_col,
            col=col,
            row=row,
            label=label,
            color=color,
            value_format=value_fmt,
            value_prefix=value_pfx,
            value_suffix=value_sfx,
            theme=theme,
            panel_notes=panel_notes,
            y_labels=y_labels,
            max_callout_chars=max_callout_chars,
        )

    theme_height = int(getattr(theme, "height", 400) or 400)
    style_fig_wm(
        fig,
        title=title,
        subtitle=subtitle,
        theme=theme,
        kicker=kicker,
        show_kicker=bool(kicker),
        legend_bottom=False,
        margin_overrides={
            "r": max(116, min(220, 80 + max_callout_chars * 7)),
            "t": 164,
            "b": 86,
            "l": 74,
        },
    )
    fig.update_layout(
        width=width or theme.width,
        height=height or max(theme_height + 60, panel_height * len(y_cols) + 190),
        hovermode="x unified",
        plot_bgcolor=theme.card_bg,
    )

    _style_subplot_titles(
        fig,
        y_cols=y_cols,
        subplot_title_count=subplot_title_count,
        panel_notes=panel_notes,
        y_labels=y_labels,
        colors=colors,
        palette=palette,
        theme=theme,
    )
    fig.update_xaxes(
        showgrid=False,
        tickformat="%b\n%Y",
        title_text="Month",
        row=len(y_cols),
        col=1,
    )
    for row in range(1, len(y_cols)):
        fig.update_xaxes(showticklabels=False, title_text="", row=row, col=1)

    return fig


# ── wm_line_panels sub-helpers ──────────────────────────────────────

def _add_panel_trace(
    fig: go.Figure,
    *,
    plot_df: pd.DataFrame,
    x_col: str,
    col: str,
    row: int,
    label: str,
    color: str,
    value_format: str,
    value_prefix: str,
    value_suffix: str,
    theme: ThemeLike,
    panel_notes: dict[str, str],
    y_labels: dict[str, str],
    max_callout_chars: int,
) -> int:
    """Add a single panel trace with median line and last-value callout.

    Returns the updated *max_callout_chars*.
    """
    series = pd.to_numeric(plot_df[col], errors="coerce")
    valid = series.dropna()

    fig.add_trace(
        go.Scatter(
            x=plot_df[x_col],
            y=series,
            mode="lines+markers",
            name=label,
            showlegend=False,
            line=dict(color=color, width=3),
            marker=dict(
                size=8, color=color,
                line=dict(color=theme.card_bg, width=1.5),
            ),
            fill="tozeroy",
            fillcolor=rgba_css(color, 0.10),
            hovertemplate=(
                f"{label}<br>Month=%{{x|%b %Y}}<br>"
                f"Level={value_prefix}%{{y{value_format}}}"
                f"{value_suffix}<extra></extra>"
            ),
        ),
        row=row,
        col=1,
    )

    if not valid.empty:
        max_callout_chars = _add_panel_annotations(
            fig,
            valid=valid,
            row=row,
            color=color,
            value_format=value_format or None,
            value_prefix=value_prefix,
            value_suffix=value_suffix,
            theme=theme,
            max_callout_chars=max_callout_chars,
        )

    fig.update_yaxes(
        title_text="" if panel_notes.get(col) else label,
        row=row,
        col=1,
        gridcolor=theme.grid,
        tickfont=dict(
            family=theme.font_mono, size=11, color=theme.text_muted,
        ),
        tickformat=value_format or None,
        rangemode="tozero",
    )
    return max_callout_chars


def _add_panel_annotations(
    fig: go.Figure,
    *,
    valid: pd.Series[Any],
    row: int,
    color: str,
    value_format: str | None,
    value_prefix: str,
    value_suffix: str,
    theme: ThemeLike,
    max_callout_chars: int,
) -> int:
    """Add median line and last-value callout to a panel row.

    Returns the updated *max_callout_chars*.
    """
    median = float(valid.median())
    fig.add_hline(  # pyright: ignore[reportArgumentType]
        y=median,
        row=row,
        col=1,
        line_width=1,
        line_dash="dot",
        line_color=rgba_css(color, 0.42),
    )

    last_value = float(valid.iloc[-1])
    last_label = _format_panel_value(
        last_value,
        value_format=value_format,
        prefix=value_prefix,
        suffix=value_suffix,
    )
    max_callout_chars = max(max_callout_chars, len(last_label))
    fig.add_annotation(
        xref="paper",
        yref=f"y{'' if row == 1 else row}",
        x=1.03,
        y=last_value,
        text=(
            f"<span style='font-family:{theme.font_mono};font-size:11px;"
            f"font-weight:700;color:{theme.text_main};'>"
            f"{escape(last_label)}</span>"
        ),
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        bgcolor=theme.card_bg,
        bordercolor=rgba_css(color, 0.28),
        borderwidth=1,
        borderpad=5,
    )
    return max_callout_chars


def _style_subplot_titles(
    fig: go.Figure,
    *,
    y_cols: list[str],
    subplot_title_count: int,
    panel_notes: dict[str, str],
    y_labels: dict[str, str],
    colors: dict[str, str],
    palette: list[str],
    theme: ThemeLike,
) -> None:
    """Restyle subplot title annotations to match WM typography."""
    for idx, col in enumerate(y_cols[:subplot_title_count]):
        panel_title = panel_notes.get(
            col, y_labels.get(col, col.replace("_", " ").title()),
        )
        color = colors.get(col, palette[idx % len(palette)])
        fig.layout.annotations[idx].update(
            x=0.0,
            xanchor="left",
            align="left",
            yshift=10,
            text=(
                f"<span style='color:{color};font-size:13px;'>&#9632;</span>"
                f"&nbsp;<span style='font-family:{theme.font_mono};"
                f"font-size:12px;font-weight:800;letter-spacing:0.20em;"
                f"text-transform:uppercase;color:{theme.text_main};'>"
                f"{escape(str(panel_title))}</span>"
            ),
        )
