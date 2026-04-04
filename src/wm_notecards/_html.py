"""Shared HTML / CSS card-shell generation.

**The** single source of truth for the outer card wrapper, eyebrow,
chip, divider, kicker, note-box, and composed-header patterns used by
every card-type module (markdown, table, chart, pictogram).

Colab dark-mode defence
-----------------------
All critical visual CSS properties — ``background``, ``color``,
``border-color`` — carry ``!important`` so that Colab's dark-mode
injection cannot override the card appearance.

Every card shell ``<div>`` receives the fixed class ``wm-card`` for
downstream CSS targeting, in addition to whatever ``card_class`` the
caller specifies.
"""
from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._types import ThemeLike

# ── Shell dimension defaults ────────────────────────────────────────
# These match the V1 WMTheme dataclass defaults.  Callers can override
# by setting the corresponding attribute on their theme object.
_SHELL_RADIUS: int = 18
_SHELL_PAD_TOP: int = 22
_SHELL_PAD_X: int = 24
_SHELL_PAD_BOTTOM: int = 18
_SHELL_ROLE_MARKER: int = 10
_SHELL_TITLE_SIZE: int = 36
_SHELL_TITLE_GAP: int = 10
_SHELL_RULE_WIDTH: int = 60

_WM_CARD_CLASS: str = "wm-card"
"""Fixed base class added to every card shell for external CSS targeting."""


# ── Private helpers ─────────────────────────────────────────────────

def _dim(theme: ThemeLike, attr: str, default: int) -> int:
    """Read an optional integer dimension from *theme*, with fallback."""
    return int(getattr(theme, attr, default) or default)


def _classes(card_class: str) -> str:
    """Return a combined class string that always includes ``wm-card``."""
    if card_class == _WM_CARD_CLASS:
        return _WM_CARD_CLASS
    return f"{_WM_CARD_CLASS} {card_class}"


# ── Colour helper ───────────────────────────────────────────────────

def rgba_css(color: str, alpha: float) -> str:
    """Convert any matplotlib-parseable colour to an ``rgba(…)`` CSS value.

    Parameters
    ----------
    color : str
        Hex, named, or CSS colour accepted by
        :func:`matplotlib.colors.to_rgba`.
    alpha : float
        Opacity in ``[0, 1]``.

    Returns
    -------
    str
        CSS ``rgba()`` function string,
        e.g. ``"rgba(17, 17, 17, 0.220)"``.
    """
    from matplotlib import colors as mcolors  # deferred so the module stays light

    red, green, blue, _ = mcolors.to_rgba(color)
    return (
        f"rgba({round(red * 255)}, {round(green * 255)}, "
        f"{round(blue * 255)}, {alpha:.3f})"
    )


# ── Card-shell CSS & open/close ─────────────────────────────────────

def card_shell_css(
    theme: ThemeLike,
    *,
    card_class: str = "wm-shell-card",
    hover_lift: bool = True,
) -> str:
    """Generate the ``<style>`` block for the shared card shell classes.

    Parameters
    ----------
    theme : ThemeLike
        Active visual theme.
    card_class : str
        CSS class used as the selector root.
    hover_lift : bool
        When *False* the hover ``transform`` is suppressed (useful for
        table cards whose rows already have their own hover effect).

    Returns
    -------
    str
        A self-contained ``<style>…</style>`` block.
    """
    radius = _dim(theme, "shell_radius", _SHELL_RADIUS)
    pad_top = _dim(theme, "shell_pad_top", _SHELL_PAD_TOP)
    pad_x = _dim(theme, "shell_pad_x", _SHELL_PAD_X)
    pad_bottom = _dim(theme, "shell_pad_bottom", _SHELL_PAD_BOTTOM)
    marker_size = _dim(theme, "shell_role_marker_size", _SHELL_ROLE_MARKER)
    title_size = _dim(theme, "shell_title_size", _SHELL_TITLE_SIZE)
    title_gap = _dim(theme, "shell_title_gap", _SHELL_TITLE_GAP)
    rule_width = _dim(theme, "shell_rule_width", _SHELL_RULE_WIDTH)

    is_light = theme.mode == "light"
    shadow = "0 12px 22px -14px rgba(0,0,0,0.20)" if is_light else "none"
    hover_shadow = "0 20px 34px -20px rgba(0,0,0,0.28)" if is_light else shadow
    marker_glow = (
        "0 0 0 4px rgba(17,17,17,0.04)"
        if is_light
        else "0 0 0 4px rgba(255,255,255,0.05)"
    )
    hover_transform = "translateY(-2px)" if hover_lift else "none"

    return (
        "<style>"
        # ── card wrapper ──
        f".{card_class}{{"
        f"max-width:{theme.width}px !important;"
        "margin:16px auto !important;"
        f"background:{theme.card_bg} !important;"
        f"color:{theme.text_main} !important;"
        f"border:1px solid {theme.border} !important;"
        f"border-radius:{radius}px;"
        f"box-shadow:{shadow};"
        "transition:transform 0.18s ease,box-shadow 0.18s ease,"
        "border-color 0.18s ease;"
        "}"
        # ── hover ──
        f".{card_class}:hover{{"
        f"transform:{hover_transform};"
        f"box-shadow:{hover_shadow};"
        "}"
        # ── inner padding ──
        f".{card_class} .wm-shell-inner{{"
        f"padding:{pad_top}px {pad_x}px {pad_bottom}px {pad_x}px;"
        "}"
        # ── eyebrow row ──
        f".{card_class} .wm-shell-eyebrow{{"
        "display:flex;align-items:center;gap:10px;"
        "margin-bottom:10px;"
        f"font-family:{theme.font_mono};font-size:11px;font-weight:800;"
        f"letter-spacing:0.16em;text-transform:uppercase;"
        f"color:{theme.text_muted} !important;"
        "}"
        # ── top-row (eyebrow + chip side-by-side) ──
        f".{card_class} .wm-shell-toprow{{"
        "display:flex;align-items:flex-start;"
        "justify-content:space-between;gap:12px;"
        "margin-bottom:10px;"
        "}"
        f".{card_class} .wm-shell-toprow .wm-shell-eyebrow{{"
        "margin-bottom:0;"
        "}"
        # ── role marker dot ──
        f".{card_class} .wm-shell-marker{{"
        f"width:{marker_size}px;height:{marker_size}px;"
        "border-radius:3px;"
        "background:var(--wm-role-idle) !important;"
        "transition:background-color 0.18s ease,"
        "transform 0.18s ease,box-shadow 0.18s ease;"
        "flex:0 0 auto;"
        "}"
        f".{card_class}:hover .wm-shell-marker{{"
        "background:var(--wm-role-hover) !important;"
        "transform:scale(1.05);"
        f"box-shadow:{marker_glow};"
        "}"
        # ── kicker ──
        f".{card_class} .wm-shell-kicker{{"
        f"font-family:{theme.font_mono};font-size:11px;"
        f"color:{theme.text_muted} !important;"
        "letter-spacing:0.14em;text-transform:uppercase;"
        "margin-bottom:10px;"
        "}"
        # ── title ──
        f".{card_class} .wm-shell-title{{"
        f"font-family:{theme.font_display};font-size:{title_size}px;"
        "font-weight:900;line-height:1.04;letter-spacing:-0.8px;"
        f"color:{theme.text_main} !important;"
        f"margin-bottom:{title_gap}px;"
        "}"
        # ── subtitle ──
        f".{card_class} .wm-shell-subtitle{{"
        f"font-family:{theme.font_mono};font-size:13px;line-height:1.55;"
        f"color:{theme.text_muted} !important;"
        f"margin-bottom:{title_gap}px;"
        "}"
        # ── accent rule ──
        f".{card_class} .wm-shell-rule{{"
        f"height:4px;width:{rule_width}px;"
        f"background:{theme.accent} !important;"
        "margin:0 0 12px 0;"
        "}"
        # ── grid divider ──
        f".{card_class} .wm-shell-divider{{"
        "height:1px;"
        f"background:{theme.grid} !important;"
        "margin:0 0 14px 0;"
        "}"
        "</style>"
    )


def card_shell_open(
    theme: ThemeLike,
    *,
    card_class: str = "wm-shell-card",
    role_idle: str | None = None,
    role_hover: str | None = None,
    max_width: int | None = None,
    hover_lift: bool = True,
) -> str:
    """Emit the shell CSS **and** the opening ``<div>`` tags.

    Parameters
    ----------
    theme : ThemeLike
        Active visual theme.
    card_class : str
        Additional CSS class on the wrapper (the ``wm-card`` base class
        is always included).
    role_idle : str, optional
        ``--wm-role-idle`` CSS custom property value (marker colour at
        rest).
    role_hover : str, optional
        ``--wm-role-hover`` CSS custom property value.
    max_width : int, optional
        Override for ``max-width`` on the wrapper.  Defaults to
        ``theme.width``.
    hover_lift : bool
        Forwarded to :func:`card_shell_css`.

    Returns
    -------
    str
        CSS ``<style>`` block followed by the opening ``<div>`` tags.
        Pair with :func:`card_shell_close`.
    """
    css = card_shell_css(theme, card_class=card_class, hover_lift=hover_lift)
    width = max_width or theme.width

    custom_props = ""
    if role_idle is not None:
        custom_props += f"--wm-role-idle:{role_idle};"
    if role_hover is not None:
        custom_props += f"--wm-role-hover:{role_hover};"

    return (
        f"{css}"
        f"<div class='{_classes(card_class)}' style='"
        f"{custom_props}max-width:{width}px;'>"
        "<div class='wm-shell-inner'>"
    )


def card_shell_close() -> str:
    """Closing tags that pair with :func:`card_shell_open`.

    Returns
    -------
    str
        ``</div></div>`` — inner + outer wrapper.
    """
    return "</div></div>"


def card_shell_html(
    content: str,
    theme: ThemeLike,
    *,
    card_class: str = "wm-shell-card",
    width: int | None = None,
    shadow: str | None = None,
    role_idle: str | None = None,
    role_hover: str | None = None,
    hover_lift: bool = True,
    extra_css: str = "",
) -> str:
    """Convenience wrapper: CSS + open + *content* + close.

    Parameters
    ----------
    content : str
        Pre-rendered inner HTML to place inside the shell.
    theme : ThemeLike
        Active visual theme.
    card_class : str
        Additional CSS class on the wrapper.
    width : int, optional
        Override ``max-width`` (defaults to ``theme.width``).
    shadow : str, optional
        Override ``box-shadow`` via an inline style on the wrapper.
        When *None* the class-level shadow from :func:`card_shell_css`
        is used.
    role_idle : str, optional
        ``--wm-role-idle`` custom property.
    role_hover : str, optional
        ``--wm-role-hover`` custom property.
    hover_lift : bool
        Forwarded to :func:`card_shell_css`.
    extra_css : str
        Additional ``<style>`` block prepended before the shell CSS.

    Returns
    -------
    str
        Complete, self-contained HTML string ready for
        ``IPython.display.HTML()``.
    """
    css = card_shell_css(theme, card_class=card_class, hover_lift=hover_lift)
    effective_width = width or theme.width

    custom_props = ""
    if role_idle is not None:
        custom_props += f"--wm-role-idle:{role_idle};"
    if role_hover is not None:
        custom_props += f"--wm-role-hover:{role_hover};"

    shadow_style = f"box-shadow:{shadow};" if shadow is not None else ""

    return (
        f"{extra_css}{css}"
        f"<div class='{_classes(card_class)}' style='"
        f"{custom_props}{shadow_style}max-width:{effective_width}px;'>"
        f"<div class='wm-shell-inner'>{content}</div></div>"
    )


# ── Atomic HTML fragments ──────────────────────────────────────────

def eyebrow_html(text: str, theme: ThemeLike) -> str:
    """Small uppercase role label with a role-marker dot.

    The marker inherits its colour from the ``--wm-role-idle`` /
    ``--wm-role-hover`` custom properties set on the card shell.

    Parameters
    ----------
    text : str
        Label text, e.g. ``"TABLE"``, ``"CHART"``, ``"VERDICT"``.
    theme : ThemeLike
        Active visual theme (currently unused, reserved for future
        theming of the eyebrow font).

    Returns
    -------
    str
        HTML ``<div class="wm-shell-eyebrow">`` fragment.
    """
    return (
        "<div class='wm-shell-eyebrow'>"
        "<span class='wm-shell-marker'></span>"
        f"<span>{escape(text)}</span>"
        "</div>"
    )


def chip_html(
    text: str,
    theme: ThemeLike,
    *,
    color: str | None = None,
) -> str:
    """Render a small status chip / pill.

    Parameters
    ----------
    text : str
        Label (auto-escaped, uppercased via CSS).
    theme : ThemeLike
        Active visual theme.
    color : str, optional
        Foreground accent.  Falls back to ``theme.heat_neg`` if
        available, then ``theme.accent``.

    Returns
    -------
    str
        HTML ``<span>`` or empty string when *text* is falsy.
    """
    if not text:
        return ""
    chip_color = color or getattr(theme, "heat_neg", theme.accent)
    return (
        "<span style='display:inline-flex;align-items:center;"
        "justify-content:center;padding:5px 10px;border-radius:999px;"
        f"border:1px solid {rgba_css(chip_color, 0.28)} !important;"
        f"background:{rgba_css(chip_color, 0.10)} !important;"
        f"color:{chip_color} !important;"
        f"font-family:{theme.font_mono};font-size:11px;font-weight:800;"
        "letter-spacing:0.08em;text-transform:uppercase;"
        f"white-space:nowrap;'>{escape(text)}</span>"
    )


def kicker_html(text: str, theme: ThemeLike) -> str:
    """Small uppercase meta-line above the card title.

    Parameters
    ----------
    text : str
        Raw kicker text (auto-escaped).
    theme : ThemeLike
        Active visual theme.

    Returns
    -------
    str
        HTML ``<div class="wm-shell-kicker">`` or empty string when
        *text* is falsy.
    """
    if not text:
        return ""
    return (
        f"<div class='wm-shell-kicker'>{escape(text)}</div>"
    )


def rule_html(theme: ThemeLike) -> str:
    """4 px accent-coloured horizontal rule.

    Parameters
    ----------
    theme : ThemeLike
        Active visual theme.

    Returns
    -------
    str
        HTML ``<div class="wm-shell-rule">`` element.
    """
    return "<div class='wm-shell-rule'></div>"


def divider_html(theme: ThemeLike) -> str:
    """1 px grid-coloured section divider.

    Parameters
    ----------
    theme : ThemeLike
        Active visual theme.

    Returns
    -------
    str
        HTML ``<div class="wm-shell-divider">`` element.
    """
    return "<div class='wm-shell-divider'></div>"


def note_html(text: str, theme: ThemeLike) -> str:
    """Muted note box typically placed at the bottom of a card.

    Parameters
    ----------
    text : str
        Note content (auto-escaped).
    theme : ThemeLike
        Active visual theme.

    Returns
    -------
    str
        HTML ``<div>`` or empty string when *text* is falsy.
    """
    if not text:
        return ""
    return (
        f"<div style='margin-top:14px;padding:10px 12px;border-radius:12px;"
        f"background:{theme.plot_bg} !important;"
        f"border:1px solid {theme.grid} !important;"
        f"color:{theme.text_muted} !important;"
        f"font-family:{theme.font_mono};font-size:12px;'>"
        f"{escape(text)}</div>"
    )


# ── Composed header ────────────────────────────────────────────────

def shell_header_html(
    *,
    title: str,
    theme: ThemeLike,
    eyebrow: str | None = None,
    kicker: str | None = None,
    subtitle: str | None = None,
    chip_text: str | None = None,
    chip_color: str | None = None,
    title_size: int | None = None,
) -> str:
    """Full header block: eyebrow → kicker → title → subtitle → rule → divider.

    Composes the atomic helpers into the standard card header used by
    markdown cards, table cards, formula cards, etc.

    Parameters
    ----------
    title : str
        Main headline (auto-escaped).
    theme : ThemeLike
        Active visual theme.
    eyebrow : str, optional
        Role label for the eyebrow line (e.g. ``"TABLE"``).  When
        *None* the eyebrow row is omitted entirely.
    kicker : str, optional
        Small uppercase meta-line above the title.
    subtitle : str, optional
        Secondary line below the title.
    chip_text : str, optional
        Status chip shown beside the eyebrow.
    chip_color : str, optional
        Override colour for the chip.
    title_size : int, optional
        Override ``font-size`` for the title (in px).

    Returns
    -------
    str
        HTML fragment (not wrapped in a card shell).
    """
    # eyebrow row — optionally paired with a chip
    eyebrow_block = ""
    if eyebrow:
        eb = eyebrow_html(eyebrow, theme)
        ch = chip_html(chip_text or "", theme, color=chip_color)
        eyebrow_block = f"<div class='wm-shell-toprow'>{eb}{ch}</div>" if ch else eb
    elif chip_text:
        ch = chip_html(chip_text, theme, color=chip_color)
        eyebrow_block = (
            f"<div class='wm-shell-toprow'>"
            f"<div></div>{ch}</div>"
        )

    kicker_block = kicker_html(kicker or "", theme)

    title_style = (
        f" style='font-size:{title_size}px;'" if title_size is not None else ""
    )
    subtitle_block = ""
    if subtitle:
        safe = escape(subtitle).replace("\n", "<br>")
        subtitle_block = f"<div class='wm-shell-subtitle'>{safe}</div>"

    return (
        f"{eyebrow_block}"
        f"{kicker_block}"
        f"<div class='wm-shell-title'{title_style}>{escape(title)}</div>"
        f"{subtitle_block}"
        f"{rule_html(theme)}"
        f"{divider_html(theme)}"
    )


# ── Plot / figure shell ────────────────────────────────────────────

def plot_shell_html(
    figure_html: str,
    theme: ThemeLike,
    *,
    figure_width: int,
) -> str:
    """Centered card shell that wraps rendered Plotly figure HTML.

    The plot shell is visually distinct from the standard card shell —
    it uses inline styles so it can size itself to the figure, while
    still sharing the same border-radius, shadow, and background tokens.

    Parameters
    ----------
    figure_html : str
        Pre-rendered Plotly ``fig.to_html(full_html=False, …)`` output.
    theme : ThemeLike
        Active visual theme.
    figure_width : int
        Pixel width of the Plotly figure layout.

    Returns
    -------
    str
        Complete, self-contained HTML string ready for
        ``IPython.display.HTML()``.
    """
    is_light = theme.mode == "light"
    shadow = "0 10px 20px -16px rgba(0,0,0,0.16)" if is_light else "none"
    shell_width = min(int(theme.width) + 48, int(figure_width) + 48)
    radius = _dim(theme, "shell_radius", _SHELL_RADIUS)
    radius = max(radius, 12)
    inner_radius = max(radius - 6, 10)

    return (
        "<div class='wm-card wm-plot-shell-wrap' style='"
        "display:flex;justify-content:center;align-items:flex-start;"
        "width:100%;margin:16px auto;padding:10px 0 6px 0;"
        "box-sizing:border-box;text-align:center;'>"
        f"<div class='wm-plot-shell' style='display:inline-block;"
        f"text-align:left;width:min(100%, {shell_width}px);"
        f"max-width:{shell_width}px !important;"
        f"margin:0 auto;padding:32px 24px 22px 24px;"
        f"background:{theme.card_bg} !important;"
        f"border:1px solid {theme.border} !important;"
        f"border-radius:{radius}px;"
        f"box-shadow:{shadow};overflow:hidden;box-sizing:border-box;'>"
        f"<div style='display:block;width:min(100%, {figure_width}px);"
        f"max-width:{figure_width}px;margin:0 auto;padding-top:14px;"
        f"border-radius:{inner_radius}px;overflow:hidden;"
        f"box-sizing:border-box;'>"
        f"{figure_html}"
        "</div></div></div>"
    )
