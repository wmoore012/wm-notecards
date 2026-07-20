"""Concrete theme dataclass with light / dark factory presets."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Literal

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

ThemeMode = Literal["light", "dark"]

# ---------------------------------------------------------------------------
# Font stacks
# ---------------------------------------------------------------------------

WM_FONT_DISPLAY: str = (
    "Inter, Space Grotesk, ui-sans-serif, system-ui, -apple-system, "
    "Segoe UI, Roboto, Arial"
)
WM_FONT_MONO: str = (
    "JetBrains Mono, Space Mono, ui-monospace, SFMono-Regular, "
    "Menlo, Consolas, Liberation Mono, monospace"
)

# ---------------------------------------------------------------------------
# Default color palettes
# ---------------------------------------------------------------------------

WM_LIGHT_COLORWAY: tuple[str, ...] = (
    "#111111",
    "#16C7E8",
    "#B74C5F",
    "#2F6BFF",
    "#D88C2E",
    "#149E9E",
)

WM_DARK_COLORWAY: tuple[str, ...] = (
    "#F5F5F5",
    "#16C7E8",
    "#C56779",
    "#2F6BFF",
    "#D88C2E",
    "#00FF9D",
)

WM_LIGHT_CATEGORY_PALETTE: tuple[str, ...] = (
    "#16C7E8",
    "#2F6BFF",
    "#B74C5F",
    "#D88C2E",
    "#0F766E",
    "#4C6475",
    "#7A7F36",
    "#00A3E0",
    "#A05A2C",
    "#5B6C8F",
    "#9B6E00",
    "#4C6475",
)

WM_DARK_CATEGORY_PALETTE: tuple[str, ...] = (
    "#16C7E8",
    "#2F6BFF",
    "#C56779",
    "#D88C2E",
    "#00FF9D",
    "#8A96A3",
    "#9AA04A",
    "#46B8FF",
    "#C98438",
    "#6B7280",
    "#F4B556",
    "#375A7F",
)

# ---------------------------------------------------------------------------
# Default dimensions
# ---------------------------------------------------------------------------

WM_DEFAULT_WIDTH: int = 860
WM_DEFAULT_HEIGHT: int = 420
WM_DEFAULT_EXPORT_SCALE: int = 3


# ---------------------------------------------------------------------------
# Theme dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class WMTheme:
    """Shared render tokens for cards, tables, and charts.

    Parameters
    ----------
    mode : ThemeMode
        ``"light"`` or ``"dark"``.
    font_display : str
        CSS font-family stack for headings and body text.
    font_mono : str
        CSS font-family stack for code and numeric values.
    export_scale : int
        Plotly static-export resolution multiplier.
    width, height : int
        Default figure dimensions in CSS pixels.
    shell_radius : int
        Border-radius for card shells (px).
    shell_pad_x, shell_pad_top, shell_pad_bottom : int
        Internal padding for card shells (px).
    shell_title_size, shell_table_title_size : int
        Font sizes for shell headings (px).
    shell_title_gap : int
        Gap between title and content rule (px).
    shell_rule_width : int
        Width of the decorative rule beneath titles (px).
    shell_role_marker_size : int
        Diameter of the role-indicator dot (px).
    accent : str
        Primary accent colour (hex).
    colorway : tuple[str, ...]
        Ordered trace colours for Plotly figures.
    card_bg, plot_bg : str
        Background colours for cards and chart areas.
    text_main, text_muted : str
        Primary and secondary text colours.
    grid, border : str
        Gridline and border colours (typically rgba).
    tooltip_bg : str
        Background colour for chart tooltips.
    heat_neg, heat_mid, heat_pos : str
        Three-stop diverging colour scale (low / mid / high).
    color_mean_bg, color_min_bg, color_max_bg : str
        Highlight backgrounds for summary-statistic cells.
    color_count_bg : str
        Background for count-statistic cells.
    color_missing_bg, color_missing_txt : str
        Background and text colour for missing-value indicators.
    table_header_bg, table_stripe_bg : str
        Table header and alternating-row backgrounds.
    table_hover_bg, table_hover_text, table_hover_border : str
        Hover-state colours for interactive tables.
    category_palette : tuple[str, ...]
        Extended qualitative palette for categorical encodings.

    Examples
    --------
    >>> t = WMTheme.light()
    >>> t.mode
    'light'
    >>> t_dark = WMTheme.dark()
    >>> t_dark.card_bg
    '#0B1017'
    """

    mode: ThemeMode = "light"

    # -- typography ---------------------------------------------------------
    font_display: str = WM_FONT_DISPLAY
    font_mono: str = WM_FONT_MONO

    # -- dimensions ---------------------------------------------------------
    export_scale: int = WM_DEFAULT_EXPORT_SCALE
    width: int = WM_DEFAULT_WIDTH
    height: int = WM_DEFAULT_HEIGHT

    # -- shell geometry -----------------------------------------------------
    shell_radius: int = 18
    shell_pad_x: int = 24
    shell_pad_top: int = 22
    shell_pad_bottom: int = 18
    shell_title_size: int = 34
    shell_table_title_size: int = 24
    shell_title_gap: int = 14
    shell_rule_width: int = 132
    shell_role_marker_size: int = 10

    # -- colours: accent & colorway -----------------------------------------
    accent: str = "#16C7E8"
    colorway: tuple[str, ...] = WM_LIGHT_COLORWAY

    # -- colours: surfaces --------------------------------------------------
    card_bg: str = "#FFFFFF"
    plot_bg: str = "#F3F3EF"

    # -- colours: text & chrome ---------------------------------------------
    text_main: str = "#111111"
    text_muted: str = "rgba(17,17,17,0.60)"
    grid: str = "rgba(17,17,17,0.10)"
    border: str = "rgba(17,17,17,0.14)"
    tooltip_bg: str = "#FFFFFF"

    # -- colours: heatmap ---------------------------------------------------
    heat_neg: str = "#B74C5F"
    heat_mid: str = "#F3F3EF"
    heat_pos: str = "#16C7E8"

    # -- colours: summary stats ---------------------------------------------
    color_mean_bg: str = "rgba(0, 204, 122, 0.15)"
    color_min_bg: str = "rgba(230, 0, 76, 0.15)"
    color_max_bg: str = "rgba(0, 184, 204, 0.15)"
    color_count_bg: str = "rgba(17, 17, 17, 0.06)"
    color_missing_bg: str = "rgba(184, 138, 27, 0.18)"
    color_missing_txt: str = "#9B6E00"

    # -- colours: table chrome ----------------------------------------------
    table_header_bg: str = "#ECECE7"
    # Visible enough to scan across wide tables, quiet enough to remain below
    # semantic status fills in the preattentive hierarchy.
    table_stripe_bg: str = "rgba(17,17,17,0.055)"
    table_hover_bg: str = "#10212B"
    table_hover_text: str = "#16C7E8"
    table_hover_border: str = "rgba(22,199,232,0.22)"

    # -- colours: categorical -----------------------------------------------
    category_palette: tuple[str, ...] = WM_LIGHT_CATEGORY_PALETTE

    # -- factory class methods ----------------------------------------------

    @staticmethod
    def light(
        *,
        accent: str = "#16C7E8",
        support: str = "#B74C5F",
        warning: str = "#D88C2E",
        card_bg: str = "#FFFFFF",
        plot_bg: str = "#F3F3EF",
        table_header_bg: str = "#ECECE7",
        hover_bg: str = "#10212B",
        hover_text: str = "#16C7E8",
        hover_border: str = "rgba(22,199,232,0.22)",
    ) -> WMTheme:
        """Return a light-mode theme with optional accent overrides."""
        return replace(
            WMTheme(),
            accent=accent,
            colorway=("#111111", accent, support, "#2F6BFF", warning, "#149E9E"),
            card_bg=card_bg,
            plot_bg=plot_bg,
            tooltip_bg=card_bg,
            heat_neg=support,
            heat_mid=plot_bg,
            heat_pos=accent,
            color_count_bg="rgba(17, 17, 17, 0.06)",
            color_missing_bg="rgba(184, 138, 27, 0.18)",
            color_missing_txt="#9B6E00",
            table_header_bg=table_header_bg,
            table_hover_bg=hover_bg,
            table_hover_text=hover_text,
            table_hover_border=hover_border,
            category_palette=(
                accent,
                "#2F6BFF",
                support,
                warning,
                "#0F766E",
                "#4C6475",
                "#7A7F36",
                "#00A3E0",
                "#A05A2C",
                "#5B6C8F",
                "#9B6E00",
                "#4C6475",
            ),
        )

    @staticmethod
    def dark() -> WMTheme:
        """Return a dark-mode theme with inverted surfaces and adjusted chroma."""
        return WMTheme(
            mode="dark",
            accent="#16C7E8",
            colorway=WM_DARK_COLORWAY,
            card_bg="#0B1017",
            plot_bg="#070B11",
            text_main="#F5F5F5",
            text_muted="rgba(235,245,255,0.72)",
            grid="rgba(255,255,255,0.07)",
            border="rgba(255,255,255,0.10)",
            tooltip_bg="#101624",
            heat_neg="#C56779",
            heat_mid="#0B1017",
            heat_pos="#16C7E8",
            color_mean_bg="rgba(0, 255, 157, 0.12)",
            color_min_bg="rgba(255, 51, 102, 0.15)",
            color_max_bg="rgba(0, 229, 255, 0.12)",
            color_count_bg="rgba(255, 255, 255, 0.08)",
            color_missing_bg="rgba(216, 140, 46, 0.22)",
            color_missing_txt="#F4B556",
            table_header_bg="#0E141E",
            table_stripe_bg="rgba(255,255,255,0.045)",
            table_hover_bg="#08131A",
            table_hover_text="#16C7E8",
            table_hover_border="rgba(22,199,232,0.24)",
            category_palette=WM_DARK_CATEGORY_PALETTE,
        )

    # -- derived properties -------------------------------------------------

    @property
    def heatmap_colorscale(self) -> list[list[Any]]:
        """Three-stop Plotly-compatible colour scale from *neg* to *pos*."""
        return [[0.0, self.heat_neg], [0.5, self.heat_mid], [1.0, self.heat_pos]]
