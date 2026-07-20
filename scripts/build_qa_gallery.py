"""Build a browser QA gallery from the real public rendering helpers."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go

from wm_notecards import WMTheme
from wm_notecards import tables as table_module
from wm_notecards._html import card_shell_html, plot_shell_html, shell_header_html
from wm_notecards.charts import style_fig_wm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("build/qa-gallery.html"))
    return parser.parse_args()


def _question_card(theme: WMTheme) -> str:
    header = shell_header_html(
        title="Can a long decision question and its status coexist without covering each other?",
        subtitle=(
            "The chip, title, and teaching note must wrap as one deliberate composition at every width."
        ),
        theme=theme,
        kicker="08 • FAIR • RESPONSIVE CONTRACT",
        chip_text="Opportunity requiring human review",
        eyebrow="QUESTION",
    )
    content = header + (
        "<p class='qa-body'>Direct answer: yes—the metadata yields space, the title stays left-aligned, "
        "and the decision remains readable.</p>"
    )
    return card_shell_html(
        content,
        theme,
        card_class="qa-question-card",
        role_idle="rgba(98,150,255,.34)",
        role_hover="#6B9CFF",
    )


def _dense_chart(theme: WMTheme) -> str:
    labels = [
        "Benny the Butcher",
        "JID",
        "Chance the Rapper",
        "Mick Jenkins",
        "Young M.A",
        "Kenny Beats",
        "Sam Dew",
        "Maxo Kream",
        "Freddie Gibbs",
        "Isaiah Rashad",
        "Bas",
        "Kenny Mason",
    ]
    fig = go.Figure(go.Bar(x=labels, y=[0.64, 0.60, 0.59, 0.57, 0.56, 0.54, 0.52, 0.49, 0.47, 0.44, 0.38, 0.32]))
    # Explicit types reproduce the reviewer-found regression: transposition must
    # move axis types as well as axis titles.
    fig.update_xaxes(type="category", title_text="Peer artist")
    fig.update_yaxes(type="linear", title_text="Reviewed score")
    style_fig_wm(
        fig,
        title="Named categories become readable before labels can collide",
        subtitle="Twelve long peer names trigger the horizontal release policy automatically",
        theme=theme,
    )
    fig.update_layout(width=920)
    chart = fig.to_html(full_html=False, include_plotlyjs=True, config={"displayModeBar": False})
    return plot_shell_html(chart, theme, figure_width=920)


def _long_table(theme: WMTheme) -> str:
    frame = pd.DataFrame(
        {
            "metric": [f"Ranking evidence lane {index + 1}" for index in range(20)],
            "leader with a deliberately long label": [
                "Item KNN, User KNN, or reviewed baseline" for _ in range(20)
            ],
            "best value": [round(0.07 + index * 0.0031, 4) for index in range(20)],
            "evidence boundary and interpretation": [
                "One held-out item per person; treat this row as comparative evidence, not production proof."
                for _ in range(20)
            ],
        }
    )
    rendered: list[str] = []
    original_display = table_module.display

    def capture(obj: Any) -> None:
        rendered.append(str(obj.data))

    try:
        table_module.display = capture
        table_module.wm_render_styler(
            frame.style.format({"best value": "{:.4f}"}),
            theme=theme,
            title="Who leads each top-N metric?",
            subtitle="The table owns its scroll instead of escaping or pretending every row fits.",
            kicker="09 • RECOMMENDATION • EVIDENCE",
            chip_text="20 reviewed rows",
            wrap_columns={"evidence boundary and interpretation": 360},
        )
    finally:
        table_module.display = original_display
    return rendered[-1]


def build_html() -> str:
    theme = WMTheme.light()
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>wm-notecards responsive QA gallery</title>
<style>
*{{box-sizing:border-box}} html,body{{margin:0;min-height:100%;background:#24283b}}
body{{padding:24px 14px 64px;font-family:{theme.font_display}}}
.qa-label{{max-width:{theme.width}px;margin:30px auto 8px;color:#8BE9FF;font:800 12px {theme.font_mono};letter-spacing:.16em}}
.qa-body{{font-size:18px;line-height:1.6;margin:0}}
@media(max-width:640px){{body{{padding:10px 8px 40px}}.qa-label{{margin-top:20px}}}}
</style></head><body>
<div class="qa-label">CARD WRAP CONTRACT</div>{_question_card(theme)}
<div class="qa-label">DENSE CATEGORY CONTRACT</div>{_dense_chart(theme)}
<div class="qa-label">TABLE STRETCH + SCROLL CONTRACT</div>{_long_table(theme)}
</body></html>"""


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(), encoding="utf-8")
    print(f"Wrote QA gallery: {args.output.resolve()}")


if __name__ == "__main__":
    main()
