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


def test_title_and_hover_label_use_safe_export_and_color_tokens() -> None:
    fig = _styled_line_chart(n_traces=2)

    assert fig.layout.title.y <= 0.94
    assert fig.layout.hoverlabel.bgcolor == "#10212B"
    assert fig.layout.hoverlabel.font.color == WMTheme.light().accent


def test_top_paper_annotation_is_absorbed_into_protected_header_flow() -> None:
    fig = go.Figure(go.Scatter(x=[1, 2], y=[2, 3]))
    fig.add_annotation(
        x=2,
        xref="x",
        y=1.02,
        yref="paper",
        text="Validation window begins Jan 1993",
        showarrow=False,
    )

    style_fig_wm(
        fig,
        title="Full series",
        subtitle="Thousands of litres/month",
        theme=WMTheme.light(),
    )

    assert "Validation window begins Jan 1993" in fig.layout.title.text
    assert list(fig.layout.annotations or ()) == []
    assert fig.layout.margin.t >= 126


def test_bordered_header_chip_is_not_absorbed_as_prose() -> None:
    fig = go.Figure(go.Scatter(x=[1, 2], y=[2, 3]))
    fig.add_annotation(
        x=1,
        xref="paper",
        y=1.08,
        yref="paper",
        text="REVIEWED",
        showarrow=False,
        borderwidth=1,
        bgcolor="#FFFFFF",
    )

    style_fig_wm(fig, title="Reviewed chart", theme=WMTheme.light())

    assert len(fig.layout.annotations or ()) == 1


def test_redundant_validation_annotation_does_not_repeat_subtitle() -> None:
    fig = go.Figure(go.Scatter(x=[1, 2], y=[2, 3]))
    fig.add_annotation(
        x=2,
        xref="x",
        y=1.02,
        yref="paper",
        text="Validation window begins Jan 1993",
        showarrow=False,
    )

    style_fig_wm(
        fig,
        title="Full series",
        subtitle="Dashed line is where validation starts (Jan 1993)",
        theme=WMTheme.light(),
    )

    assert "Validation window begins" not in fig.layout.title.text
    assert "validation starts (Jan 1993)" in fig.layout.title.text
    assert list(fig.layout.annotations or ()) == []


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


def test_dense_bar_transpose_swaps_explicit_axis_types() -> None:
    labels = [f"Peer {idx}" for idx in range(12)]
    fig = go.Figure(go.Bar(x=labels, y=list(range(12))))
    fig.update_xaxes(type="category", title_text="Peer artist")
    fig.update_yaxes(type="linear", title_text="Score")

    style_fig_wm(fig, title="Rank mass", theme=WMTheme.light())

    assert fig.layout.xaxis.type == "linear"
    assert fig.layout.yaxis.type == "category"
    assert fig.layout.xaxis.title.text == "Score"
    assert fig.layout.yaxis.title.text == "Peer artist"


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
