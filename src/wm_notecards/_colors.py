"""Low-level colour manipulation utilities.

Private module — every function is consumed by sibling modules inside
``wm_notecards``, but nothing here is part of the public API.
All conversions lean on :mod:`matplotlib.colors` so any colour spec
that matplotlib understands (hex, named, ``rgb()``, …) works.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray

# ---------------------------------------------------------------------------
# CSS helpers
# ---------------------------------------------------------------------------


def _rgba_css(color: str, alpha: float) -> str:
    """Convert a colour string and alpha to a CSS ``rgba()`` value.

    Parameters
    ----------
    color : str
        Any colour spec accepted by :func:`matplotlib.colors.to_rgba`
        (hex, named CSS colour, ``"rgb(…)"``, etc.).
    alpha : float
        Opacity in ``[0.0, 1.0]``.

    Returns
    -------
    str
        ``"rgba(R, G, B, A)"`` with integer RGB channels and three-decimal
        alpha (e.g. ``"rgba(22, 199, 232, 0.340)"``).
    """
    red, green, blue, _ = mcolors.to_rgba(color)
    return (
        f"rgba({round(red * 255)}, {round(green * 255)}, "
        f"{round(blue * 255)}, {alpha:.3f})"
    )


def _fg(hex_color: str) -> str:
    """Pick a legible foreground (black or white) for a hex background.

    Uses the ITU-R BT.601 luma formula.  Returns ``"#000"`` for light
    backgrounds and ``"#fff"`` for dark ones.

    Parameters
    ----------
    hex_color : str
        Seven-character hex string **with** the ``#`` prefix
        (e.g. ``"#16C7E8"``).  Malformed inputs fall back to ``"#000"``.

    Returns
    -------
    str
        ``"#000"`` or ``"#fff"``.
    """
    if not (
        isinstance(hex_color, str)
        and hex_color.startswith("#")
        and len(hex_color) == 7
    ):
        return "#000"
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return "#000" if 0.299 * r + 0.587 * g + 0.114 * b > 160 else "#fff"


# ---------------------------------------------------------------------------
# Gradient dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class WMGradient:
    """Immutable mapping from a numeric range to an ordered colour ramp.

    Attributes
    ----------
    hex_colors : tuple[str, ...]
        *n* hex colour strings, one per bin.
    bin_edges : tuple[float, ...]
        *n + 1* monotonically increasing bin boundaries.
    colorscale : tuple[tuple[float, str], ...]
        Plotly-ready ``((position, hex), …)`` pairs.  For a **continuous**
        gradient this has *n* entries; for a **discrete** (stepped) gradient
        it has *2 n* entries (two stops per colour band).
    """

    hex_colors: tuple[str, ...]
    bin_edges: tuple[float, ...]
    colorscale: tuple[tuple[float, str], ...]

    def __post_init__(self) -> None:
        if not self.hex_colors:
            raise ValueError("hex_colors must be non-empty.")
        if len(self.bin_edges) != len(self.hex_colors) + 1:
            raise ValueError(
                f"bin_edges length ({len(self.bin_edges)}) must equal "
                f"hex_colors length + 1 ({len(self.hex_colors) + 1})."
            )

    def color_for(self, value: float) -> str:
        """Return the hex colour for *value*, clamped to the bin range.

        Parameters
        ----------
        value : float
            Scalar to look up.

        Returns
        -------
        str
            Hex colour string from :pyattr:`hex_colors`.
        """
        if value <= self.bin_edges[0]:
            return self.hex_colors[0]
        if value >= self.bin_edges[-1]:
            return self.hex_colors[-1]
        for i in range(len(self.bin_edges) - 1):
            if self.bin_edges[i] <= value < self.bin_edges[i + 1]:
                return self.hex_colors[i]
        return self.hex_colors[-1]

    @property
    def plotly_colorscale(self) -> list[list[float | str]]:
        """Unpack to ``list[list]`` for ``marker=dict(colorscale=…)``."""
        return [[pos, h] for pos, h in self.colorscale]


# ---------------------------------------------------------------------------
# Gradient generators
# ---------------------------------------------------------------------------


def _build_cmap(
    low: str,
    high: str,
) -> mcolors.LinearSegmentedColormap:
    """Build a two-stop linear colourmap from *low* to *high*.

    Parameters
    ----------
    low : str
        Start colour (any matplotlib colour spec).
    high : str
        End colour (any matplotlib colour spec).

    Returns
    -------
    matplotlib.colors.LinearSegmentedColormap
    """
    return mcolors.LinearSegmentedColormap.from_list(
        "wm", [low, high], N=256,
    )


def generate_gradient_wm(
    *,
    n: int = 5,
    vmin: float = 0.0,
    vmax: float = 10.0,
    low: str,
    high: str,
    cmap_name: str | None = None,
) -> WMGradient:
    """Build a **continuous** gradient over ``[vmin, vmax]``.

    When *cmap_name* is ``None`` a two-stop linear ramp from *low* →
    *high* is used; otherwise the named matplotlib colourmap is fetched
    via :func:`matplotlib.pyplot.get_cmap`.

    Parameters
    ----------
    n : int
        Number of colour stops (must be ≥ 2).
    vmin, vmax : float
        Data-space range.  *vmax* must be strictly greater than *vmin*
        and both must be finite.
    low : str
        Start colour of the default ramp.
    high : str
        End colour of the default ramp.
    cmap_name : str | None
        Named matplotlib colourmap override.

    Returns
    -------
    WMGradient
        Frozen gradient with *n* colours and *n + 1* bin edges.

    Raises
    ------
    ValueError
        If *n < 2*, *vmax ≤ vmin*, or either bound is non-finite.
    """
    if n < 2:
        raise ValueError(f"n must be >= 2, got {n}")
    if vmax <= vmin:
        raise ValueError("vmax must be > vmin")
    if not (np.isfinite(vmin) and np.isfinite(vmax)):
        raise ValueError("vmin/vmax must be finite")

    cmap = plt.get_cmap(cmap_name) if cmap_name else _build_cmap(low, high)
    stops: NDArray[np.floating] = np.linspace(0.0, 1.0, n)
    hex_colors = tuple(mcolors.rgb2hex(cmap(float(s))) for s in stops)
    bin_edges = tuple(float(v) for v in np.linspace(vmin, vmax, n + 1))
    colorscale = tuple((float(s), h) for s, h in zip(stops, hex_colors, strict=False))
    return WMGradient(
        hex_colors=hex_colors,
        bin_edges=bin_edges,
        colorscale=colorscale,
    )


def generate_discrete_gradient_wm(
    *,
    n: int = 5,
    vmin: float = 0.0,
    vmax: float = 10.0,
    low: str,
    high: str,
    cmap_name: str | None = None,
) -> WMGradient:
    """Build a **stepped / discrete** gradient over ``[vmin, vmax]``.

    Each colour band occupies an equal-width segment.  The returned
    :pyattr:`WMGradient.colorscale` contains *2 n* entries (two stops
    per band) so Plotly renders flat colour blocks instead of a smooth
    ramp.

    Parameters
    ----------
    n : int
        Number of discrete colour bands (must be ≥ 2).
    vmin, vmax : float
        Data-space range.
    low : str
        Start colour of the default ramp.
    high : str
        End colour of the default ramp.
    cmap_name : str | None
        Named matplotlib colourmap override.

    Returns
    -------
    WMGradient
        Frozen gradient with *n* colours and *n + 1* bin edges.

    Raises
    ------
    ValueError
        If *n < 2*, *vmax ≤ vmin*, or either bound is non-finite.
    """
    if n < 2:
        raise ValueError(f"n must be >= 2, got {n}")
    if vmax <= vmin:
        raise ValueError("vmax must be > vmin")
    if not (np.isfinite(vmin) and np.isfinite(vmax)):
        raise ValueError("vmin/vmax must be finite")

    cmap = plt.get_cmap(cmap_name) if cmap_name else _build_cmap(low, high)
    stops: NDArray[np.floating] = np.linspace(0.0, 1.0, n)
    hex_colors = tuple(mcolors.rgb2hex(cmap(float(s))) for s in stops)
    bin_edges = tuple(float(v) for v in np.linspace(vmin, vmax, n + 1))

    bounds: NDArray[np.floating] = np.linspace(0.0, 1.0, n + 1)
    discrete_cs: list[tuple[float, str]] = []
    for i, color in enumerate(hex_colors):
        discrete_cs.append((float(bounds[i]), color))
        discrete_cs.append((float(bounds[i + 1]), color))

    return WMGradient(
        hex_colors=hex_colors,
        bin_edges=bin_edges,
        colorscale=tuple(discrete_cs),
    )
