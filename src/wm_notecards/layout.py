"""Opt-in notebook layout presets; importing this module changes no display state."""
from __future__ import annotations


def notebook_layout_css(layout: str | None = None) -> str:
    """Return optional layout CSS. None preserves the existing package defaults.

    The responsive preset affects WM components and VS Code rich Plotly outputs
    only. Plain text outputs and ordinary pandas tables retain their layout.
    Requires a modern notebook browser with CSS :has() support. Isolated renderer
    iframes may not inherit notebook CSS; use the WM HTML figure renderer there.
    """
    if layout is None:
        return ""
    if layout != "responsive":
        raise ValueError("layout must be None or 'responsive'")
    return """<style id="wm-responsive-layout">
/* VS Code: target rich figures/cards, never every plain-text output. */
.output_container .output:has(.js-plotly-plot, .plotly-graph-div, [class*="wm-"]) {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
}
.output_container .output > div:has(.js-plotly-plot, .plotly-graph-div, [class*="wm-"]) {
  margin-left: auto !important;
  margin-right: auto !important;
  max-width: 100%;
}
.wm-micro-rail {
  max-width: 860px !important;
  grid-auto-flow: row !important;
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  grid-auto-columns: auto !important;
  overflow-x: visible !important;
}
/* Only an unpaired final card spans both columns. */
.wm-micro-rail > .wm-micro-card:last-child:nth-child(odd) {
  grid-column: 1 / -1;
}
@media (max-width: 720px) {
  .wm-micro-rail {
    grid-template-columns: minmax(0, 1fr) !important;
  }
  .wm-micro-rail > .wm-micro-card:last-child:nth-child(odd) {
    grid-column: auto;
  }
  .wm-table-card:has(tbody tr > td:nth-of-type(5)) {
    overflow-x: auto !important;
    max-width: 100%;
  }
  .wm-table-card:has(tbody tr > td:nth-of-type(5)) table {
    min-width: 700px !important;
  }
  .wm-table-card:has(tbody tr > td:nth-of-type(7)) table {
    min-width: 780px !important;
  }
}
</style>"""
