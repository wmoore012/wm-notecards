"""Notebook initialisation helpers for wm-notecards.

Handles Plotly renderer selection, matplotlib font resolution, centering
CSS, MathJax bootstrap, pandas Copy-on-Write warnings, and Colab
dark-mode defense.
"""

from __future__ import annotations

import os
import sys
import warnings
from functools import cache, lru_cache
from typing import Any, cast

import pandas as pd
import plotly.io as pio
from IPython.core.getipython import get_ipython
from IPython.display import HTML, display

# ---------------------------------------------------------------------------
# Module-level sentinel
# ---------------------------------------------------------------------------

_NOTEBOOK_READY: bool = False


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _default_plotly_renderer() -> str:
    """Pick a renderer that works in modern notebook front-ends."""
    if "google.colab" in sys.modules:
        return "colab"
    if os.environ.get("VSCODE_PID") or os.environ.get("TERM_PROGRAM") == "vscode":
        return "plotly_mimetype+notebook_connected"
    return "plotly_mimetype+notebook_connected"


def _font_stack(stack: str) -> list[str]:
    """Split a CSS-style font stack into individual family names."""
    return [part.strip().strip("'\"") for part in stack.split(",") if part.strip()]


@lru_cache(maxsize=1)
def _installed_mpl_font_names() -> frozenset[str]:
    """Return the set of font family names available to matplotlib."""
    try:
        from matplotlib import font_manager as fm  # noqa: WPS433
    except Exception:
        return frozenset()
    return frozenset(font.name for font in fm.fontManager.ttflist)


def _apply_matplotlib_theme_fonts() -> None:
    """Push the WMTheme font stacks into matplotlib rcParams.

    Wraps the assignment in ``warnings.catch_warnings()`` so that
    ``findfont`` noise is suppressed (V3 fix).
    """
    try:
        import matplotlib as mpl  # noqa: WPS433
        from wm_theme import WMTheme  # noqa: WPS433
    except Exception:
        return

    theme = WMTheme()
    sans = resolve_mpl_font_family(theme.font_display, fallback="DejaVu Sans")
    mono = resolve_mpl_font_family(theme.font_mono, fallback="DejaVu Sans Mono")

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="findfont:")
        mpl.rcParams["font.family"] = sans
        mpl.rcParams["font.sans-serif"] = sans
        mpl.rcParams["font.monospace"] = mono


def _centering_css() -> str:
    """Return a ``<style>`` block that centres notebook outputs.

    Targets JupyterLab, classic Jupyter, VS Code, and Colab output
    containers so that Plotly charts, HTML cards, and inline SVGs stay
    centred regardless of the front-end.
    """
    return """
<style id="wm-notebook-css">
.jp-OutputArea-output,
.jp-OutputArea-child,
.jp-RenderedPlotly,
.jp-RenderedHTMLCommon,
.cell-output-display,
.output_subarea.output_html.rendered_html,
.output,
.output_area {
  width: 100% !important;
  max-width: 100% !important;
  display: block !important;
}

.jp-RenderedPlotly,
.jp-RenderedHTMLCommon,
.cell-output-display,
.output_subarea.output_html.rendered_html {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: flex-start !important;
}

.jp-RenderedPlotly,
.cell-output-display .plotly-graph-div,
.cell-output-display .js-plotly-plot,
.jp-RenderedHTMLCommon .plotly-graph-div,
.jp-RenderedHTMLCommon .js-plotly-plot,
.output_subarea.output_html.rendered_html .plotly-graph-div,
.output_subarea.output_html.rendered_html .js-plotly-plot {
  width: auto !important;
  max-width: 100% !important;
}

.js-plotly-plot,
.plotly-graph-div,
.plot-container.plotly,
.svg-container {
  display: block !important;
  margin-left: auto !important;
  margin-right: auto !important;
}

.svg-container {
  width: auto !important;
  max-width: 100% !important;
}

.jp-OutputArea-output .plotly-graph-div,
.jp-OutputArea-output .js-plotly-plot,
.jp-OutputArea-child .plotly-graph-div,
.jp-OutputArea-child .js-plotly-plot,
.jp-RenderedPlotly .plotly-graph-div,
.jp-RenderedPlotly .js-plotly-plot,
.cell-output-display .plotly-graph-div,
.cell-output-display .js-plotly-plot,
.output_subarea.output_html.rendered_html .plotly-graph-div,
.output_subarea.output_html.rendered_html .js-plotly-plot {
  margin-left: auto !important;
  margin-right: auto !important;
  max-width: 100% !important;
}

.wm-plot-shell,
.wm-plot-shell-wrap,
.wm-plot-shell .js-plotly-plot,
.wm-plot-shell .plotly-graph-div,
.wm-plot-shell .svg-container {
  display: block !important;
  max-width: 100% !important;
}

.wm-plot-shell-wrap {
  display: flex !important;
  justify-content: center !important;
  align-items: flex-start !important;
  width: 100% !important;
  margin: 0 auto !important;
  padding-top: 8px !important;
  text-align: center !important;
  box-sizing: border-box !important;
}

.wm-plot-shell {
  display: block !important;
  margin-left: auto !important;
  margin-right: auto !important;
  text-align: left !important;
  box-sizing: border-box !important;
}

.wm-markdown-card,
.wm-table-card,
.wm-fe-decision-card,
.wm-check-card-shell,
.wm-formula-card,
.wm-glossary-card,
.wm-counterintuitive-card,
.wm-figure-card,
.wm-inline-svg-card,
.wm-pictogram-card,
.wm-question-card-shell {
  display: block !important;
  margin-left: auto !important;
  margin-right: auto !important;
}

.wm-inline-svg-card svg,
.wm-formula-card svg,
.wm-counterintuitive-card svg {
  display: block !important;
  max-width: 100% !important;
  height: auto !important;
  margin-left: auto !important;
  margin-right: auto !important;
}
</style>
""".strip()


def _dark_mode_defense_css() -> str:
    """Return a ``<style>`` block that prevents Colab dark mode from
    overriding card colours.

    Uses CSS custom properties so downstream cards can opt into a
    different palette while still being shielded from the host
    environment's ``color-scheme`` override.
    """
    return """
<style id="wm-dark-mode-defense">
.wm-card, .wm-card * { color-scheme: light !important; }
.wm-card {
  background: var(--wm-card-bg, #FFFFFF) !important;
  color: var(--wm-text-main, #111111) !important;
}
</style>
""".strip()


def _mathjax_bootstrap_html() -> str:
    """Return a ``<script>`` block that configures and lazy-loads MathJax 3."""
    return """
<script>
(function () {
  if (!window.wmTypesetMath) {
    window.wmTypesetMath = function (target) {
      const node = typeof target === "string" ? document.getElementById(target) : target;
      if (!node) {
        return;
      }

      const tryTypeset = function () {
        if (window.MathJax && typeof window.MathJax.typesetPromise === "function") {
          window.MathJax.typesetPromise([node]).catch(function () {});
          return true;
        }
        return false;
      };

      if (tryTypeset()) {
        return;
      }

      let attempts = 0;
      const retry = function () {
        if (tryTypeset()) {
          return;
        }
        attempts += 1;
        if (attempts < 40) {
          window.setTimeout(retry, 250);
        }
      };
      retry();
    };
  }

  if (!window.wmMathJaxConfigured) {
    window.MathJax = window.MathJax || {};
    window.MathJax.tex = Object.assign(
      {
        inlineMath: [["\\\\(", "\\\\)"]],
        displayMath: [["\\\\[", "\\\\]"]],
        processEscapes: true
      },
      window.MathJax.tex || {}
    );
    window.MathJax.options = Object.assign(
      {
        skipHtmlTags: ["script", "noscript", "style", "textarea", "pre", "code"]
      },
      window.MathJax.options || {}
    );
    window.MathJax.startup = Object.assign(
      { typeset: false },
      window.MathJax.startup || {}
    );
    window.wmMathJaxConfigured = true;
  }

  if (!document.getElementById("wm-mathjax-script")) {
    const script = document.createElement("script");
    script.id = "wm-mathjax-script";
    script.async = true;
    script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js";
    document.head.appendChild(script);
  }
})();
</script>
""".strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@cache
def resolve_mpl_font_family(
    stack: str,
    *,
    fallback: str = "DejaVu Sans",
) -> list[str]:
    """Resolve a CSS-like font stack to installed matplotlib font names.

    Parameters
    ----------
    stack : str
        Comma-separated CSS font-family string
        (e.g. ``"Inter, Helvetica Neue, sans-serif"``).
    fallback : str, optional
        Safe font that ships with matplotlib, appended when present.
        Defaults to ``"DejaVu Sans"``.

    Returns
    -------
    list[str]
        Ordered list of installed font family names ending with
        *fallback*.  If nothing in *stack* is installed, returns
        ``[fallback]``.
    """
    installed = _installed_mpl_font_names()
    resolved: list[str] = []
    for family in _font_stack(stack):
        if family in installed and family not in resolved:
            resolved.append(family)

    if fallback and fallback in installed and fallback not in resolved:
        resolved.append(fallback)

    return resolved or [fallback]


def init_notebook(
    *,
    renderer: str | None = None,
    html_styler: bool = True,
    inline_matplotlib: bool = True,
    retina: bool = True,
) -> None:
    """Initialise notebook display defaults once per kernel.

    Call this at the top of every notebook to configure Plotly, matplotlib,
    pandas HTML styling, centering CSS, MathJax, and Colab dark-mode
    defense in one shot.

    Parameters
    ----------
    renderer : str | None, optional
        Plotly renderer override.  Auto-detected when *None*.
    html_styler : bool, optional
        Enable ``pandas.io.formats.style`` HTML repr.  Default *True*.
    inline_matplotlib : bool, optional
        Run ``%matplotlib inline``.  Default *True*.
    retina : bool, optional
        Use retina-resolution figures.  Default *True*.
    """
    global _NOTEBOOK_READY  # noqa: WPS420

    if html_styler:
        pd.set_option("display.notebook_repr_html", True)
        pd.options.styler.render.repr = "html"

    pio.renderers.default = renderer or _default_plotly_renderer()

    ipy = get_ipython()
    if ipy is not None and inline_matplotlib:
        ipy.run_line_magic("matplotlib", "inline")
        if retina:
            ipy.run_line_magic("config", "InlineBackend.figure_format = 'retina'")

    _apply_matplotlib_theme_fonts()

    display(
        HTML(
            _centering_css()
            + "\n"
            + _dark_mode_defense_css()
            + "\n"
            + _mathjax_bootstrap_html()
        ),
    )

    _NOTEBOOK_READY = True


def enable_cow_warn() -> None:
    """Enable Copy-on-Write warning mode for pandas < 3.0.

    Safe no-op when pandas >= 3.0 (CoW is the default there).

    Examples
    --------
    >>> from wm_notecards.boot import enable_cow_warn
    >>> enable_cow_warn()
    """
    try:
        major, minor = (int(x) for x in pd.__version__.split(".")[:2])
    except Exception:
        return
    if (major, minor) < (3, 0):
        cast("Any", pd.options.mode).copy_on_write = "warn"
