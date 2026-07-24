"""Structural protocols and type aliases shared across wm-notecards."""
from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable


@runtime_checkable
class ThemeLike(Protocol):
    """Minimal structural contract for a visual theme object.

    Any object whose public attributes satisfy these properties can be
    used as a theme — no inheritance required.  Optional shell-dimension
    attributes (``shell_radius``, ``shell_pad_top``, …) are read via
    ``getattr`` with sensible defaults.
    """

    @property
    def font_display(self) -> str: ...

    @property
    def font_mono(self) -> str: ...

    @property
    def accent(self) -> str: ...

    @property
    def card_bg(self) -> str: ...

    @property
    def plot_bg(self) -> str: ...

    @property
    def text_main(self) -> str: ...

    @property
    def text_muted(self) -> str: ...

    @property
    def grid(self) -> str: ...

    @property
    def border(self) -> str: ...

    @property
    def width(self) -> int: ...

    @property
    def mode(self) -> str: ...

    @property
    def height(self) -> int: ...

    @property
    def export_scale(self) -> int: ...

    @property
    def colorway(self) -> tuple[str, ...]: ...

    @property
    def category_palette(self) -> tuple[str, ...]: ...

    @property
    def tooltip_bg(self) -> str: ...

    @property
    def heat_neg(self) -> str: ...

    @property
    def heat_mid(self) -> str: ...

    @property
    def heat_pos(self) -> str: ...

    @property
    def color_mean_bg(self) -> str: ...

    @property
    def color_min_bg(self) -> str: ...

    @property
    def color_max_bg(self) -> str: ...

    @property
    def color_count_bg(self) -> str: ...

    @property
    def color_missing_bg(self) -> str: ...

    @property
    def color_missing_txt(self) -> str: ...

    @property
    def color_missing_accent(self) -> str: ...

    @property
    def color_skew_accent(self) -> str: ...

    @property
    def chip_candidate_primary(self) -> str: ...

    @property
    def chip_candidate_secondary(self) -> str: ...

    @property
    def chip_candidate_secondary_text(self) -> str: ...

    @property
    def chip_identifier(self) -> str: ...

    @property
    def chip_time(self) -> str: ...

    @property
    def chip_target(self) -> str: ...

    @property
    def table_header_bg(self) -> str: ...

    @property
    def table_stripe_bg(self) -> str: ...

    @property
    def table_hover_bg(self) -> str: ...

    @property
    def table_hover_text(self) -> str: ...

    @property
    def table_hover_border(self) -> str: ...


# ── Type aliases ─────────────────────────────────────────────────────

ThemeMode = Literal["light", "dark"]

WMCardRole = Literal[
    "question", "evidence", "chart", "table", "pictogram",
    "takeaway", "verdict", "formula", "next_think", "preview",
    "glossary", "counterintuitive", "check",
]

WMVerdictTone = Literal[
    "neutral", "positive", "negative", "caution", "special",
]

CardSize = Literal["sm", "md", "lg"]
CheckStatus = Literal["pass", "fail", "warn", "skip"]
