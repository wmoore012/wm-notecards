"""Build the local HTML used to capture the README demonstration GIF."""

from __future__ import annotations

import argparse
from pathlib import Path

import plotly.graph_objects as go

from wm_notecards import WMTheme
from wm_notecards._html import card_shell_css, card_shell_html, shell_header_html
from wm_notecards.charts import style_fig_wm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("build/readme-demo.html"))
    return parser.parse_args()


def _before_frame(theme: WMTheme) -> str:
    headers = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
    rows = [
        ("monthly_sales", [156, 1610.2, 588.7, 464, 1071, 1514, 2056, 3205]),
        ("forecast_error", [24, -41.3, 340.9, -721, -260, -18, 184, 688]),
        ("peer_score", [40, 0.441, 0.102, 0.006, 0.382, 0.472, 0.521, 0.646]),
        ("rank_delta", [40, 3.2, 6.8, -12, -1, 2, 7, 19]),
    ]
    head = "".join(f"<th>{item}</th>" for item in ["", *headers])
    body = "".join(
        "<tr><th>" + name + "</th>" + "".join(f"<td>{value}</td>" for value in values) + "</tr>"
        for name, values in rows
    )
    return f"""
    <section class="demo-frame before-frame">
      <div class="frame-copy">
        <span class="eyebrow">THE DEFAULT</span>
        <h1>We make data visualizations for a living.</h1>
        <p>Why are we still doing machine learning in MS-DOS?</p>
      </div>
      <div class="terminal">
        <div class="terminal-bar"><span></span><span></span><span></span><code>Out [47]</code></div>
        <table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>
        <div class="terminal-prompt">4 rows × 8 columns</div>
      </div>
      <div class="frame-note">Beautiful analysis. Phone-book reading experience.</div>
    </section>
    """


def _question_frame(theme: WMTheme) -> str:
    header = shell_header_html(
        title="What is this notebook actually helping me decide?",
        theme=theme,
        eyebrow="QUESTION",
        kicker="03 • FORECASTING • QUESTION",
        chip_text="Start here",
    )
    content = (
        header
        + "<p class='card-body'>Direct answer: whether the annual pattern is strong enough "
        "to earn a seasonal model—or whether a simpler trend is honest enough.</p>"
        + "<div class='choice-row'><span>See the exact split</span><span>Compare the models</span></div>"
    )
    card = card_shell_html(
        content,
        theme,
        card_class="wm-demo-question",
        role_idle="rgba(98,150,255,.34)",
        role_hover="#6B9CFF",
    )
    return f"""
    <section class="demo-frame conversation-frame">
      <div class="brandline">wm-notecards <span>question → answer</span></div>
      {card}
      <div class="frame-note">The notebook remembers the thread before asking for attention.</div>
    </section>
    """


def _evidence_frame(theme: WMTheme) -> str:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    actual = [1030, 1240, 1550, 1900, 2250, 2640, 3650, 2660, 2620, 2210, 2580, 2680]
    forecast = [1510, 1690, 1860, 2050, 2210, 2440, 2860, 2800, 2610, 2320, 2430, 2550]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=months, y=actual, name="Validation actual", line={"color": "#149E9E", "width": 4})
    )
    fig.add_trace(
        go.Scatter(
            x=months,
            y=forecast,
            name="Trend + seasonality",
            line={"color": "#B74C5F", "width": 3, "dash": "dash"},
        )
    )
    style_fig_wm(
        fig,
        title="The full model learns both the climb and the annual wave",
        subtitle="Same holdout months; actual is solid, forecast is dashed",
        theme=theme,
        margin_overrides={"t": 128, "b": 90, "l": 76, "r": 40},
    )
    fig.update_layout(width=940, height=470)
    chart = fig.to_html(full_html=False, include_plotlyjs=True, config={"displayModeBar": False})
    return f"""
    <section class="demo-frame evidence-frame">
      <div class="brandline">wm-notecards <span>answer → evidence</span></div>
      <div class="chart-card">{chart}</div>
      <div class="frame-note">The chart shows shape. The notebook still owes you the boundary.</div>
    </section>
    """


def _decision_frame(theme: WMTheme) -> str:
    header = shell_header_html(
        title="The seasonal model earns the next test—not automatic trust",
        theme=theme,
        eyebrow="TAKEAWAY",
        kicker="03 • FORECASTING • TAKEAWAY",
        chip_text="Your decision",
    )
    content = (
        header
        + "<p class='card-body'><strong>Evidence:</strong> lowest holdout RMSE across the four "
        "challengers. <strong>Boundary:</strong> one 24-month window is not production proof.</p>"
        + "<div class='decision-grid'><button>Test changing seasonality</button>"
        "<button>Keep the simpler baseline</button></div>"
    )
    card = card_shell_html(
        content,
        theme,
        card_class="wm-demo-decision",
        role_idle="rgba(27,201,141,.34)",
        role_hover="#1BC98D",
    )
    return f"""
    <section class="demo-frame conversation-frame decision-frame">
      <div class="brandline">wm-notecards <span>evidence → takeaway → your decision</span></div>
      {card}
      <div class="frame-note">AI can compute and suggest. The consequential choice stays human.</div>
    </section>
    """


def build_html() -> str:
    theme = WMTheme.light()
    shared_card_css = card_shell_css(theme, card_class="wm-demo-question") + card_shell_css(
        theme, card_class="wm-demo-decision"
    )
    frames = "".join(
        [_before_frame(theme), _question_frame(theme), _evidence_frame(theme), _decision_frame(theme)]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>wm-notecards README demo</title>{shared_card_css}
<style>
*{{box-sizing:border-box}} html,body{{margin:0;width:100%;height:100%;overflow:hidden}}
body{{background:#24283b;color:#111;font-family:{theme.font_display}}}
.demo-frame{{display:none;width:1200px;height:675px;padding:52px 72px;position:relative;overflow:hidden}}
.brandline{{font-family:{theme.font_mono};font-weight:900;letter-spacing:.08em;color:#16C7E8;margin-bottom:24px}}
.brandline span{{float:right;color:rgba(255,255,255,.58);font-weight:600}}
.frame-copy{{max-width:940px;color:white}} .eyebrow{{font-family:{theme.font_mono};color:#16C7E8;letter-spacing:.18em;font-weight:800}}
.frame-copy h1{{font-size:55px;line-height:1.02;letter-spacing:-2px;margin:16px 0 10px}}
.frame-copy p{{font-size:31px;line-height:1.25;color:rgba(255,255,255,.72);margin:0}}
.terminal{{margin-top:34px;background:#0f1118;border:1px solid #4a5067;border-radius:15px;padding:0 22px 22px;box-shadow:0 24px 50px -30px #000}}
.terminal-bar{{height:48px;display:flex;align-items:center;gap:9px;border-bottom:1px solid #34394b;color:#8991ad}}
.terminal-bar span{{width:12px;height:12px;border-radius:50%;background:#586078}} .terminal-bar span:first-child{{background:#b74c5f}} .terminal-bar code{{margin-left:auto}}
.terminal table{{width:100%;border-collapse:collapse;color:#c8ccda;font-family:{theme.font_mono};font-size:14px}}
.terminal th,.terminal td{{padding:12px 10px;border-bottom:1px solid #292e40;text-align:right}} .terminal th:first-child{{text-align:left;color:#16C7E8}}
.terminal-prompt{{font-family:{theme.font_mono};color:#7f879f;margin-top:14px}}
.conversation-frame{{background:#24283b}} .conversation-frame .wm-card{{margin:42px auto !important;max-width:1000px !important}}
.conversation-frame .wm-shell-inner{{padding:35px 42px 38px !important}} .conversation-frame .wm-shell-title{{font-size:46px !important}}
.card-body{{font-size:22px;line-height:1.58;margin:18px 0 24px}} .choice-row,.decision-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.choice-row span,.decision-grid button{{border:1px solid {theme.border};border-radius:13px;padding:16px 18px;background:{theme.plot_bg};font:700 16px {theme.font_mono};text-align:left;color:#111}}
.decision-grid button{{border-color:#16C7E8;background:rgba(22,199,232,.10)}}
.evidence-frame{{background:#24283b;padding-top:38px}} .chart-card{{background:white;border-radius:20px;border:1px solid {theme.border};height:535px;overflow:hidden;box-shadow:0 22px 44px -28px #000}}
.frame-note{{position:absolute;left:72px;right:72px;bottom:21px;text-align:center;font-family:{theme.font_mono};font-size:14px;color:rgba(255,255,255,.62);letter-spacing:.04em}}
</style></head><body>{frames}
<script>
const frames=[...document.querySelectorAll('.demo-frame')];
const requested=Number(new URLSearchParams(location.search).get('frame') || 0);
frames[Math.max(0,Math.min(frames.length-1,requested))].style.display='block';
</script></body></html>"""


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(), encoding="utf-8")
    print(f"Wrote README demo: {args.output.resolve()}")


if __name__ == "__main__":
    main()
