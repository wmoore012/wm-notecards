"""Pictogram (waffle-grid) infographic card.

Renders a 12×8 SVG icon grid where filled vs empty icons
communicate a proportion visually.  Designed for "X out of 100"
style presentations that feel more human than a plain number.

Usage::

    from wm_notecards.pictogram import pictogram_card

    pictogram_card(
        percent=0.37,
        headline="Tracks with declining streams",
        subtitle="37 of 100 tracks showed week-over-week decline.",
        theme=theme,
        icon="arrow_down",
    )
"""
from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

from IPython.display import HTML, display

from wm_notecards._html import rgba_css
from wm_notecards.icons import ICON_REGISTRY, get_icon
from wm_notecards.kicker import WMKicker

if TYPE_CHECKING:
    from wm_notecards._types import ThemeLike

# ── Grid geometry ────────────────────────────────────────────────────

_COLS: int = 12
_ROWS: int = 8
_TOTAL: int = _COLS * _ROWS
_GAP: int = 6


# ── Public API ───────────────────────────────────────────────────────


def pictogram_card(
    *,
    percent: float,
    headline: str,
    subtitle: str,
    theme: ThemeLike,
    kicker: str | None = None,
    chip_text: str | None = None,
    icon: str = "person",
    big_text: str | None = None,
    big_color: str | None = None,
    filled_alpha: float = 1.0,
    empty_alpha: float = 0.9,
) -> None:
    """Render a pictogram infographic card.

    Parameters
    ----------
    percent : float
        Value in [0.01, 1.0].  Values below 1 % are rejected because
        the grid can't communicate them — use ``big_number_card``
        instead.
    headline : str
        Short label above the big number (e.g. "Tracks declining").
    subtitle : str
        One or two sentences of context shown below the number.
    icon : str
        Key from the icon registry.  Defaults to ``"person"``.
        Pass ``"dot"``, ``"arrow_up"``, ``"brain"``, etc.
        Call ``list_icons()`` to see all options.
    big_text : str, optional
        Override the big label (default: the realized percentage).
    big_color : str, optional
        Override the accent colour used for filled icons and the
        big number.
    """
    _validate(percent, filled_alpha, empty_alpha, icon)

    picon = get_icon(icon)
    filled = max(0, min(_TOTAL, int(round(percent * _TOTAL))))
    realized = filled / _TOTAL * 100.0
    big_label = big_text if big_text is not None else f"{realized:.0f}%"

    mode = getattr(theme, "mode", "light")
    pop = big_color or theme.accent
    empty_color = "#D0CFC9" if mode == "light" else "#1A2030"
    meta_color = (
        "rgba(17,17,17,0.22)" if mode == "light"
        else "rgba(255,255,255,0.20)"
    )
    shadow = (
        "0 12px 22px -14px rgba(0,0,0,0.18)"
        if mode == "light" else "none"
    )

    grid_svg = _build_grid(
        picon, filled, pop, empty_color,
        filled_alpha, empty_alpha,
    )
    chip_frag = _chip_fragment(chip_text, theme, meta_color)
    kicker_line = (
        escape(WMKicker.parse(kicker).to_line()) if kicker else ""
    )

    html = f"""
<div class="wm-card wm-pictogram-card" style="
  max-width:{theme.width}px; margin:16px auto;
  background:{theme.card_bg} !important;
  color:{theme.text_main} !important;
  border:1px solid {theme.border}; border-radius:18px;
  box-shadow:{shadow}; padding:22px 24px 18px 24px;
">
  <div style="display:flex;justify-content:flex-end;
    align-items:center;gap:10px;margin-bottom:8px;">
    {chip_frag}
    <div style="font-family:{theme.font_mono};font-size:11px;
      letter-spacing:0.16em;text-transform:uppercase;
      color:{meta_color};">INFOGRAPHIC</div>
  </div>
  <div style="display:flex;justify-content:center;
    margin:6px 0 18px 0;">
    {grid_svg}
  </div>
  <div style="max-width:760px;margin:0 auto;text-align:center;">
    <div style="font-family:{theme.font_display};font-size:18px;
      font-weight:700;color:{theme.text_muted};
      margin-bottom:2px;">
      {escape(headline)}
    </div>
    <div style="font-family:{theme.font_display};font-size:56px;
      font-weight:900;line-height:1.0;color:{pop};
      margin-bottom:12px;">
      {escape(big_label)}
    </div>
    <div style="width:132px;height:4px;background:{theme.accent};
      margin:0 auto 14px auto;"></div>
    <div style="font-family:{theme.font_display};font-size:16px;
      line-height:1.62;color:{theme.text_main};
      margin-bottom:16px;">
      {escape(subtitle).replace(chr(10), "<br>")}
    </div>
  </div>
  <div style="height:1px;background:{theme.grid};
    margin:0 0 12px 0;"></div>
  <div style="font-family:{theme.font_mono};font-size:11px;
    letter-spacing:0.14em;text-transform:uppercase;
    color:{meta_color};text-align:center;">
    {kicker_line}
  </div>
</div>"""
    display(HTML(html))


# ── Validation ───────────────────────────────────────────────────────


def _validate(
    percent: float,
    filled_alpha: float,
    empty_alpha: float,
    icon: str,
) -> None:
    """Guard against bad inputs before we start generating HTML."""
    if not isinstance(percent, (int, float)) or percent != percent:
        raise TypeError(
            f"percent must be a real number, got {type(percent).__name__}."
        )
    if not 0.0 <= percent <= 1.0:
        raise ValueError(f"percent must be in [0.0, 1.0], got {percent}.")
    if percent < 0.01:
        raise ValueError(
            "percent below 1% makes the pictogram misleading; "
            "use big_number_card instead."
        )
    if icon not in ICON_REGISTRY:
        available = ", ".join(sorted(ICON_REGISTRY)[:8])
        raise ValueError(
            f"Unknown icon {icon!r}.  Available: {available}, …"
        )
    if not 0.0 <= filled_alpha <= 1.0:
        raise ValueError("filled_alpha must be in [0.0, 1.0].")
    if not 0.0 <= empty_alpha <= 1.0:
        raise ValueError("empty_alpha must be in [0.0, 1.0].")


# ── Grid builder ─────────────────────────────────────────────────────


def _build_grid(
    picon: object,
    filled: int,
    pop_color: str,
    empty_color: str,
    filled_alpha: float,
    empty_alpha: float,
) -> str:
    """Render the 12×8 SVG pictogram grid."""
    cw = picon.cell_width  # type: ignore[union-attr]
    ch = picon.cell_height  # type: ignore[union-attr]
    builder = picon.svg_builder  # type: ignore[union-attr]

    cells: list[str] = []
    for idx in range(_TOTAL):
        row, col = divmod(idx, _COLS)
        x = col * (cw + _GAP)
        y = row * (ch + _GAP)
        is_filled = idx < filled
        color = pop_color if is_filled else empty_color
        alpha = filled_alpha if is_filled else empty_alpha
        cells.append(
            f"<g transform='translate({x},{y})'>"
            f"{builder(color, alpha)}</g>"
        )

    grid_w = _COLS * cw + (_COLS - 1) * _GAP
    grid_h = _ROWS * ch + (_ROWS - 1) * _GAP
    return (
        f"<svg width='{grid_w}' height='{grid_h}'"
        f" viewBox='0 0 {grid_w} {grid_h}'"
        f" role='img' aria-label='pictogram grid'>"
        f"{''.join(cells)}</svg>"
    )


# ── Chip fragment ────────────────────────────────────────────────────


def _chip_fragment(
    chip_text: str | None,
    theme: ThemeLike,
    meta_color: str,
) -> str:
    """Build the optional top-right chip."""
    if not chip_text:
        return ""
    chip_color = getattr(theme, "heat_neg", theme.accent)
    return (
        f"<div style=\"display:inline-flex;align-items:center;"
        f"padding:5px 11px;border-radius:999px;"
        f"border:1px solid {rgba_css(chip_color, 0.28)};"
        f"background:{rgba_css(chip_color, 0.10)};"
        f"color:{chip_color};font-family:{theme.font_mono};"
        f"font-size:12px;font-weight:700;letter-spacing:0.08em;"
        f"text-transform:uppercase;\">"
        f"{escape(chip_text)}</div>"
    )
