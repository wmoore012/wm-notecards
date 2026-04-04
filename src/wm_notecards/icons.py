"""SVG pictogram icon registry for wm-notecards.

Provides a curated set of inline SVG icons designed for pictogram grid
cards.  Every icon renders as a bold, recognisable silhouette inside a
small cell (typically 14–24 px) so that 96 instances tile into a dense
waffle-style visualisation.

Usage::

    from wm_notecards.icons import get_icon, list_icons

    icon = get_icon("person")
    svg  = icon.svg_builder("#E74C3C", 1.0)

    # filter by domain tag
    data_icons = list_icons(tag="data")
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

# ── dataclass ────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class PictogramIcon:
    """A single SVG icon definition for the pictogram grid.

    Parameters
    ----------
    name : str
        Unique registry key (e.g. "person", "checkmark", "brain").
    svg_builder : Callable[[str, float], str]
        Function that accepts (color: str, alpha: float) and returns
        an SVG fragment string (no surrounding <svg> tag).
    cell_width : int
        Width of each grid cell in pixels.
    cell_height : int
        Height of each grid cell in pixels.
    tags : tuple[str, ...]
        Domain tags for AI agent discoverability.
    """

    name: str
    svg_builder: Callable[[str, float], str]
    cell_width: int
    cell_height: int
    tags: tuple[str, ...]


# ── Scale / quantity ─────────────────────────────────────────────────


def _person_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='{color}' fill-opacity='{alpha}'>"
        f"<circle cx='7' cy='4' r='3'/>"
        f"<rect x='4' y='8' width='6' height='8' rx='3'/>"
        f"<rect x='2' y='16' width='10' height='4' rx='2'/>"
        f"</g>"
    )


def _dot_svg(color: str, alpha: float) -> str:
    return (
        f"<circle cx='6' cy='6' r='5' "
        f"fill='{color}' fill-opacity='{alpha}'/>"
    )


def _block_svg(color: str, alpha: float) -> str:
    return (
        f"<rect x='2' y='2' width='20' height='20' rx='4' "
        f"fill='{color}' fill-opacity='{alpha}'/>"
    )


def _stack_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='{color}' fill-opacity='{alpha}'>"
        f"<rect x='3' y='4' width='18' height='4' rx='2'/>"
        f"<rect x='3' y='10' width='18' height='4' rx='2'/>"
        f"<rect x='3' y='16' width='18' height='4' rx='2'/>"
        f"</g>"
    )


def _coin_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='none' stroke='{color}' stroke-opacity='{alpha}' stroke-width='2'>"
        f"<circle cx='12' cy='12' r='10'/>"
        f"<circle cx='12' cy='12' r='5'/>"
        f"</g>"
    )


# ── Status / verdict ────────────────────────────────────────────────


def _checkmark_svg(color: str, alpha: float) -> str:
    return (
        f"<polyline points='4,13 9,18 20,6' fill='none' "
        f"stroke='{color}' stroke-opacity='{alpha}' "
        f"stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/>"
    )


def _x_mark_svg(color: str, alpha: float) -> str:
    return (
        f"<g stroke='{color}' stroke-opacity='{alpha}' "
        f"stroke-width='3' stroke-linecap='round'>"
        f"<line x1='5' y1='5' x2='19' y2='19'/>"
        f"<line x1='19' y1='5' x2='5' y2='19'/>"
        f"</g>"
    )


def _warning_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='{color}' fill-opacity='{alpha}'>"
        f"<path d='M12 2 L22 20 L2 20 Z'/>"
        f"<rect x='11' y='9' width='2' height='6' rx='1' fill='#fff'/>"
        f"<circle cx='12' cy='17' r='1' fill='#fff'/>"
        f"</g>"
    )


def _shield_svg(color: str, alpha: float) -> str:
    return (
        f"<path d='M12 2 L20 6 L20 13 C20 18 12 22 12 22 "
        f"C12 22 4 18 4 13 L4 6 Z' fill='none' "
        f"stroke='{color}' stroke-opacity='{alpha}' stroke-width='2'/>"
    )


def _lock_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='{color}' fill-opacity='{alpha}'>"
        f"<rect x='5' y='11' width='14' height='10' rx='2'/>"
        f"<path d='M8 11 V8 C8 4.7 9.8 3 12 3 C14.2 3 16 4.7 16 8 V11' "
        f"fill='none' stroke='{color}' stroke-opacity='{alpha}' stroke-width='2'/>"
        f"</g>"
    )


# ── Trend / direction ───────────────────────────────────────────────


def _arrow_up_svg(color: str, alpha: float) -> str:
    return (
        f"<g stroke='{color}' stroke-opacity='{alpha}' "
        f"stroke-width='3' stroke-linecap='round' stroke-linejoin='round' fill='none'>"
        f"<line x1='12' y1='20' x2='12' y2='4'/>"
        f"<polyline points='5,10 12,4 19,10'/>"
        f"</g>"
    )


def _arrow_down_svg(color: str, alpha: float) -> str:
    return (
        f"<g stroke='{color}' stroke-opacity='{alpha}' "
        f"stroke-width='3' stroke-linecap='round' stroke-linejoin='round' fill='none'>"
        f"<line x1='12' y1='4' x2='12' y2='20'/>"
        f"<polyline points='5,14 12,20 19,14'/>"
        f"</g>"
    )


def _trend_line_svg(color: str, alpha: float) -> str:
    return (
        f"<g stroke='{color}' stroke-opacity='{alpha}' stroke-width='2' "
        f"stroke-linecap='round' fill='none'>"
        f"<polyline points='3,18 10,12 16,14 21,5'/>"
        f"</g>"
        f"<g fill='{color}' fill-opacity='{alpha}'>"
        f"<circle cx='3' cy='18' r='2'/>"
        f"<circle cx='10' cy='12' r='2'/>"
        f"<circle cx='16' cy='14' r='2'/>"
        f"<circle cx='21' cy='5' r='2'/>"
        f"</g>"
    )


def _wave_svg(color: str, alpha: float) -> str:
    return (
        f"<path d='M2 12 C5 6, 8 6, 12 12 C16 18, 19 18, 22 12' "
        f"fill='none' stroke='{color}' stroke-opacity='{alpha}' "
        f"stroke-width='2.5' stroke-linecap='round'/>"
    )


# ── Analysis ─────────────────────────────────────────────────────────


def _magnifying_glass_svg(color: str, alpha: float) -> str:
    return (
        f"<g stroke='{color}' stroke-opacity='{alpha}' stroke-width='2.5' fill='none'>"
        f"<circle cx='10' cy='10' r='7'/>"
        f"<line x1='15' y1='15' x2='21' y2='21' stroke-linecap='round'/>"
        f"</g>"
    )


def _brain_svg(color: str, alpha: float) -> str:
    return (
        f"<path d='M12 4 C9 4 7 6 7 8 C5 8 4 10 4 12 C4 14 5 16 7 16 "
        f"C7 18 9 20 12 20 C15 20 17 18 17 16 C19 16 20 14 20 12 "
        f"C20 10 19 8 17 8 C17 6 15 4 12 4 Z' "
        f"fill='{color}' fill-opacity='{alpha}'/>"
        f"<line x1='12' y1='4' x2='12' y2='20' "
        f"stroke='#fff' stroke-width='1' stroke-opacity='0.5'/>"
    )


def _lightbulb_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='{color}' fill-opacity='{alpha}'>"
        f"<path d='M12 2 C8 2 5 5 5 9 C5 12 7 14 9 15 L9 19 L15 19 "
        f"L15 15 C17 14 19 12 19 9 C19 5 16 2 12 2 Z'/>"
        f"<rect x='9' y='20' width='6' height='2' rx='1'/>"
        f"</g>"
    )


def _target_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='none' stroke='{color}' stroke-opacity='{alpha}' stroke-width='2'>"
        f"<circle cx='12' cy='12' r='10'/>"
        f"<circle cx='12' cy='12' r='6'/>"
        f"</g>"
        f"<circle cx='12' cy='12' r='2.5' "
        f"fill='{color}' fill-opacity='{alpha}'/>"
    )


def _crosshair_svg(color: str, alpha: float) -> str:
    return (
        f"<g stroke='{color}' stroke-opacity='{alpha}' stroke-width='2' fill='none'>"
        f"<circle cx='12' cy='12' r='8'/>"
        f"<line x1='12' y1='2' x2='12' y2='7'/>"
        f"<line x1='12' y1='17' x2='12' y2='22'/>"
        f"<line x1='2' y1='12' x2='7' y2='12'/>"
        f"<line x1='17' y1='12' x2='22' y2='12'/>"
        f"</g>"
    )


# ── Data ─────────────────────────────────────────────────────────────


def _chart_bar_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='{color}' fill-opacity='{alpha}'>"
        f"<rect x='3' y='12' width='5' height='10' rx='1'/>"
        f"<rect x='10' y='6' width='5' height='16' rx='1'/>"
        f"<rect x='17' y='2' width='5' height='20' rx='1'/>"
        f"</g>"
    )


def _chart_line_svg(color: str, alpha: float) -> str:
    return (
        f"<polyline points='3,18 10,8 17,14 21,4' fill='none' "
        f"stroke='{color}' stroke-opacity='{alpha}' "
        f"stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'/>"
    )


def _table_grid_svg(color: str, alpha: float) -> str:
    return (
        f"<g stroke='{color}' stroke-opacity='{alpha}' stroke-width='2' fill='none'>"
        f"<rect x='3' y='3' width='18' height='18' rx='2'/>"
        f"<line x1='12' y1='3' x2='12' y2='21'/>"
        f"<line x1='3' y1='12' x2='21' y2='12'/>"
        f"</g>"
    )


def _database_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='none' stroke='{color}' stroke-opacity='{alpha}' stroke-width='2'>"
        f"<ellipse cx='12' cy='6' rx='8' ry='4'/>"
        f"<path d='M4 6 V18 C4 20.2 7.6 22 12 22 C16.4 22 20 20.2 20 18 V6'/>"
        f"<path d='M4 12 C4 14.2 7.6 16 12 16 C16.4 16 20 14.2 20 12'/>"
        f"</g>"
    )


def _filter_svg(color: str, alpha: float) -> str:
    return (
        f"<path d='M2 4 L22 4 L14 13 L14 20 L10 22 L10 13 Z' "
        f"fill='{color}' fill-opacity='{alpha}'/>"
    )


# ── Time ─────────────────────────────────────────────────────────────


def _clock_svg(color: str, alpha: float) -> str:
    return (
        f"<g stroke='{color}' stroke-opacity='{alpha}' stroke-width='2' fill='none'>"
        f"<circle cx='12' cy='12' r='10'/>"
        f"<polyline points='12,6 12,12 16,14' "
        f"stroke-linecap='round' stroke-linejoin='round'/>"
        f"</g>"
    )


def _calendar_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='{color}' fill-opacity='{alpha}'>"
        f"<rect x='3' y='5' width='18' height='17' rx='2' "
        f"fill='none' stroke='{color}' stroke-opacity='{alpha}' stroke-width='2'/>"
        f"<rect x='3' y='5' width='18' height='6' rx='2'/>"
        f"<line x1='8' y1='3' x2='8' y2='7' stroke='{color}' "
        f"stroke-opacity='{alpha}' stroke-width='2' stroke-linecap='round'/>"
        f"<line x1='16' y1='3' x2='16' y2='7' stroke='{color}' "
        f"stroke-opacity='{alpha}' stroke-width='2' stroke-linecap='round'/>"
        f"</g>"
    )


def _hourglass_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='{color}' fill-opacity='{alpha}'>"
        f"<path d='M6 2 L18 2 L18 4 L14 10 L18 16 L18 22 L6 22 "
        f"L6 16 L10 10 L6 4 Z'/>"
        f"</g>"
    )


def _stopwatch_svg(color: str, alpha: float) -> str:
    return (
        f"<g stroke='{color}' stroke-opacity='{alpha}' stroke-width='2' fill='none'>"
        f"<circle cx='12' cy='14' r='8'/>"
        f"<polyline points='12,10 12,14 15,16' "
        f"stroke-linecap='round' stroke-linejoin='round'/>"
        f"<line x1='12' y1='2' x2='12' y2='6' stroke-linecap='round'/>"
        f"<line x1='10' y1='2' x2='14' y2='2' stroke-linecap='round'/>"
        f"</g>"
    )


# ── Domain ───────────────────────────────────────────────────────────


def _music_note_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='{color}' fill-opacity='{alpha}'>"
        f"<ellipse cx='9' cy='18' rx='4' ry='3'/>"
        f"<rect x='12' y='4' width='2.5' height='14'/>"
        f"<path d='M14.5 4 Q18 3 20 6 Q18 5 14.5 7 Z'/>"
        f"</g>"
    )


def _dollar_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='none' stroke='{color}' stroke-opacity='{alpha}' "
        f"stroke-width='2.5' stroke-linecap='round'>"
        f"<path d='M16 6 C14 4 9 4 8 7 C7 10 10 11 13 12 "
        f"C16 13 18 14 17 17 C16 20 10 20 8 18'/>"
        f"<line x1='12' y1='2' x2='12' y2='22'/>"
        f"</g>"
    )


def _globe_svg(color: str, alpha: float) -> str:
    return (
        f"<g stroke='{color}' stroke-opacity='{alpha}' stroke-width='1.5' fill='none'>"
        f"<circle cx='12' cy='12' r='10'/>"
        f"<ellipse cx='12' cy='12' rx='5' ry='10'/>"
        f"<line x1='2' y1='9' x2='22' y2='9'/>"
        f"<line x1='2' y1='15' x2='22' y2='15'/>"
        f"</g>"
    )


def _location_pin_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='{color}' fill-opacity='{alpha}'>"
        f"<path d='M12 2 C8 2 5 5.5 5 9.5 C5 15 12 22 12 22 "
        f"C12 22 19 15 19 9.5 C19 5.5 16 2 12 2 Z'/>"
        f"<circle cx='12' cy='9.5' r='3' fill='#fff'/>"
        f"</g>"
    )


def _person_group_svg(color: str, alpha: float) -> str:
    return (
        f"<g fill='{color}' fill-opacity='{alpha}'>"
        f"<circle cx='9' cy='7' r='3'/>"
        f"<path d='M3 19 C3 15 5 13 9 13 C13 13 15 15 15 19'/>"
        f"<circle cx='17' cy='7' r='2.5' fill-opacity='{alpha * 0.6}'/>"
        f"<path d='M13 19 C13 16 14.5 14 17 14 C19.5 14 21 16 21 19' "
        f"fill-opacity='{alpha * 0.6}'/>"
        f"</g>"
    )


# ── Registry ─────────────────────────────────────────────────────────

ICON_REGISTRY: dict[str, PictogramIcon] = {}


def _register(
    name: str,
    builder: Callable[[str, float], str],
    *,
    cell_width: int = 24,
    cell_height: int = 24,
    tags: tuple[str, ...] = (),
) -> None:
    ICON_REGISTRY[name] = PictogramIcon(
        name=name,
        svg_builder=builder,
        cell_width=cell_width,
        cell_height=cell_height,
        tags=tags,
    )


# Scale / quantity
_register("person", _person_svg, cell_width=14, cell_height=22, tags=("scale", "people"))
_register("dot", _dot_svg, cell_width=12, cell_height=12, tags=("scale", "quantity"))
_register("block", _block_svg, tags=("scale", "quantity"))
_register("stack", _stack_svg, tags=("scale", "layers"))
_register("coin", _coin_svg, tags=("scale", "money"))

# Status / verdict
_register("checkmark", _checkmark_svg, tags=("status", "verdict"))
_register("x_mark", _x_mark_svg, tags=("status", "verdict"))
_register("warning", _warning_svg, tags=("status", "alert"))
_register("shield", _shield_svg, tags=("status", "security"))
_register("lock", _lock_svg, tags=("status", "security"))

# Trend / direction
_register("arrow_up", _arrow_up_svg, tags=("trend", "direction"))
_register("arrow_down", _arrow_down_svg, tags=("trend", "direction"))
_register("trend_line", _trend_line_svg, tags=("trend", "data"))
_register("wave", _wave_svg, tags=("trend", "signal"))

# Analysis
_register("magnifying_glass", _magnifying_glass_svg, tags=("analysis", "search"))
_register("brain", _brain_svg, tags=("analysis", "ai"))
_register("lightbulb", _lightbulb_svg, tags=("analysis", "insight"))
_register("target", _target_svg, tags=("analysis", "goal"))
_register("crosshair", _crosshair_svg, tags=("analysis", "precision"))

# Data
_register("chart_bar", _chart_bar_svg, tags=("data", "chart"))
_register("chart_line", _chart_line_svg, tags=("data", "chart"))
_register("table_grid", _table_grid_svg, tags=("data", "table"))
_register("database", _database_svg, tags=("data", "storage"))
_register("filter", _filter_svg, tags=("data", "transform"))

# Time
_register("clock", _clock_svg, tags=("time",))
_register("calendar", _calendar_svg, tags=("time",))
_register("hourglass", _hourglass_svg, tags=("time",))
_register("stopwatch", _stopwatch_svg, tags=("time",))

# Domain
_register("music_note", _music_note_svg, tags=("domain", "music"))
_register("dollar", _dollar_svg, tags=("domain", "money"))
_register("globe", _globe_svg, tags=("domain", "geography"))
_register("location_pin", _location_pin_svg, tags=("domain", "geography"))
_register("person_group", _person_group_svg, tags=("domain", "people"))


# ── Public API ───────────────────────────────────────────────────────


def get_icon(name: str) -> PictogramIcon:
    """Return the icon registered under *name*.

    Raises
    ------
    KeyError
        If *name* is not in the registry.
    """
    try:
        return ICON_REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"Unknown icon {name!r}. "
            f"Available: {', '.join(sorted(ICON_REGISTRY))}"
        ) from None


def list_icons(*, tag: str | None = None) -> list[str]:
    """Return sorted icon names, optionally filtered by *tag*."""
    if tag is None:
        return sorted(ICON_REGISTRY)
    return sorted(
        name
        for name, icon in ICON_REGISTRY.items()
        if tag in icon.tags
    )
