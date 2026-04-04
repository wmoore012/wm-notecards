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
