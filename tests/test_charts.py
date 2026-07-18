import plotly.graph_objects as go
import pytest

from wm_notecards import WMTheme
from wm_notecards.charts import style_fig_wm


def _styled_line_chart(*, n_traces: int, force_showlegend: bool | None = None) -> go.Figure:
    fig = go.Figure()
    for idx in range(n_traces):
        fig.add_trace(
            go.Scatter(
                x=[1, 2, 3],
                y=[idx + 1, idx + 2, idx + 3],
                mode="lines",
                name=f"Trace {idx + 1}",
            )
        )
    if force_showlegend is not None:
        fig.update_layout(showlegend=force_showlegend)

    style_fig_wm(
        fig,
        title="Legend spacing regression check",
        subtitle="The chart shell should not waste space on unused legends.",
        theme=WMTheme.light(),
    )
    return fig


def test_single_trace_chart_hides_legend_and_collapses_bottom_margin() -> None:
    fig = _styled_line_chart(n_traces=1)

    assert fig.layout.showlegend is False
    assert fig.layout.margin.b == 62


def test_multi_trace_chart_keeps_legend_and_bottom_margin() -> None:
    fig = _styled_line_chart(n_traces=2)

    assert fig.layout.showlegend is True
    assert fig.layout.margin.b == 112


def test_subtitle_shares_title_text_flow_to_prevent_overlap() -> None:
    fig = _styled_line_chart(n_traces=2)

    assert "<br><span" in fig.layout.title.text
    assert "chart shell should not waste space" in fig.layout.title.text
    # Plotly materializes an empty Subtitle object even when no subtitle field is set.
    # Its text must remain empty because wm-notecards owns subtitle flow in title.text.
    assert fig.layout.title.subtitle.text is None


def test_explicit_single_trace_legend_still_gets_space() -> None:
    fig = _styled_line_chart(n_traces=1, force_showlegend=True)

    assert fig.layout.showlegend is True
    assert fig.layout.margin.b == 112


def test_dense_named_bars_transpose_before_labels_can_collide() -> None:
    labels = [f"Peer artist with a deliberately long name {idx}" for idx in range(12)]
    fig = go.Figure(go.Bar(x=labels, y=list(range(12)), marker_color="#1f77b4"))
    fig.update_layout(xaxis_title="Peer artist", yaxis_title="Score")

    style_fig_wm(fig, title="Rank mass", theme=WMTheme.light())

    assert fig.data[0].orientation == "h"
    assert [label.replace("<br>", " ") for label in fig.data[0].y] == labels
    assert fig.layout.xaxis.title.text == "Score"
    assert fig.layout.yaxis.title.text == "Peer artist"
    assert fig.data[0].marker.color == WMTheme.light().accent


def test_too_many_bar_categories_require_explicit_review() -> None:
    fig = go.Figure(go.Bar(x=[f"peer-{idx}" for idx in range(25)], y=list(range(25))))

    with pytest.raises(ValueError, match="Use top-N"):
        style_fig_wm(fig, title="Unreadable", theme=WMTheme.light())


def test_dense_category_escape_hatch_is_explicit() -> None:
    fig = go.Figure(go.Bar(x=[f"peer-{idx}" for idx in range(25)], y=list(range(25))))

    style_fig_wm(
        fig,
        title="Reviewed dense chart",
        theme=WMTheme.light(),
        allow_dense_categories=True,
    )

    assert fig.data[0].orientation == "h"
