"""wm-notecards — visual storytelling cards for data-science notebooks.

Quick start::

    from wm_notecards import WMTheme, init_notebook

    theme = WMTheme.light()
    init_notebook(theme)

Then use cards, tables, charts, and pictograms::

    from wm_notecards.cards import question_pair, takeaway_card
    from wm_notecards.tables import wm_render_styler
    from wm_notecards.charts import wm_render_figure_card
    from wm_notecards.pictogram import pictogram_card
"""
from __future__ import annotations

# ── Core (always available) ──────────────────────────────────────────
from wm_notecards.boot import enable_cow_warn, init_notebook
from wm_notecards.kicker import WMKicker
from wm_notecards.theme import WMTheme

__all__ = [
    # boot
    "init_notebook",
    "enable_cow_warn",
    # theme
    "WMTheme",
    # kicker
    "WMKicker",
]
