from __future__ import annotations

import plotly.graph_objects as go
import pytest

from wm_notecards import WMTheme, pictogram, rendering
from wm_notecards._colors import WMGradient, generate_discrete_gradient_wm, generate_gradient_wm
from wm_notecards._html import chip_html, plot_shell_html, shell_header_html
from wm_notecards.icons import get_icon, list_icons
from wm_notecards.kicker import WMKicker, kicker_html


def test_gradients_are_clamped_and_plotly_ready() -> None:
    smooth = generate_gradient_wm(n=5, vmin=0, vmax=1, low="#ffffff", high="#000000")
    stepped = generate_discrete_gradient_wm(
        n=4, vmin=-1, vmax=1, low="#B74C5F", high="#16C7E8"
    )

    assert smooth.color_for(-9) == smooth.hex_colors[0]
    assert smooth.color_for(9) == smooth.hex_colors[-1]
    assert len(smooth.plotly_colorscale) == 5
    assert len(stepped.colorscale) == 8
    with pytest.raises(ValueError):
        generate_gradient_wm(n=1, low="white", high="black")
    with pytest.raises(ValueError):
        WMGradient(("#fff",), (0.0,), ((0.0, "#fff"),))


def test_every_registered_icon_builds_svg() -> None:
    names = list_icons()
    assert {"person", "globe", "chart_bar"}.issubset(names)
    for name in names:
        icon = get_icon(name)
        assert "<" in icon.svg_builder("#16C7E8", 0.8)
    with pytest.raises(KeyError):
        get_icon("not-an-icon")


def test_kicker_and_html_shell_wrap_long_metadata() -> None:
    theme = WMTheme.light()
    kicker = WMKicker.parse("NOTE,08,FAIR,MODEL REVIEW")
    assert kicker.to_line() == "08 • FAIR • MODEL REVIEW"
    assert "■ NOTE" in kicker.to_plotly_text()
    assert "font-family" in kicker_html(theme, "08,FAIR")

    chip = chip_html("Opportunity that needs more words", theme)
    header = shell_header_html(
        title="Rank mass shifts",
        theme=theme,
        eyebrow="CHART",
        chip_text="Opportunity that needs more words",
    )
    assert "white-space:normal" in chip
    assert "wm-shell-toprow" in header

    shell = plot_shell_html("<div>plot</div>", theme, figure_width=860)
    assert "wm-plot-scroll" in shell
    assert "scroll horizontally" in shell


def test_pictogram_validates_and_renders(monkeypatch: pytest.MonkeyPatch) -> None:
    rendered: list[str] = []
    monkeypatch.setattr(pictogram, "display", lambda obj: rendered.append(str(obj.data)))
    pictogram.pictogram_card(
        percent=0.37,
        headline="Tracks declining",
        subtitle="37 of 100",
        theme=WMTheme.light(),
        icon="arrow_down",
        chip_text="Evidence",
        kicker="03,EDA",
    )
    assert "pictogram grid" in rendered[-1]
    assert "INFOGRAPHIC" in rendered[-1]
    with pytest.raises(ValueError, match="below 1%"):
        pictogram.pictogram_card(percent=0.0, headline="x", subtitle="x", theme=WMTheme.light())
    with pytest.raises(ValueError, match="Unknown icon"):
        pictogram.pictogram_card(
            percent=0.5, headline="x", subtitle="x", theme=WMTheme.light(), icon="bad"
        )


def test_rendering_helpers_make_accessible_static_markup(monkeypatch: pytest.MonkeyPatch) -> None:
    svg = b"<?xml version='1.0'?><svg width='10' height='10'><rect width='10' height='10'/></svg>"
    markup = rendering._inline_svg_markup(svg, file_stub="Rank mass / opportunity")
    assert 'role="img"' in markup
    assert 'aria-label="Rank mass / opportunity"' in markup
    assert rendering._safe_export_stub(" Rank mass / opportunity ") == "Rank_mass_opportunity"

    monkeypatch.setattr(rendering, "_export_svg_bytes", lambda fig, file_stub: svg)
    proof = rendering.collect_rendering_proof()
    assert proof["ok"] is True
    assert proof["svg_bytes"] == len(svg)

    fig = go.Figure(go.Bar(x=["A"], y=[1]))
    rendering._prepare_figure_card(
        fig,
        theme=WMTheme.light(),
        file_stub="proof",
        role="chart",
        kicker="03,EDA",
        chip_text="Reviewed",
        mode="notebook",
    )
    assert fig.layout.margin.t >= 218
    assert any(annotation.text == "REVIEWED" for annotation in fig.layout.annotations)


def test_export_helper_uses_styled_dimensions(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_write_image(self, path, **kwargs):
        calls.append({"path": path, **kwargs})

    monkeypatch.setattr(go.Figure, "write_image", fake_write_image)
    fig = go.Figure(go.Bar(x=["A"], y=[1]))
    fig.update_layout(width=900, height=500)

    output = rendering.export_figure_wm(fig, tmp_path / "share-card.png")

    assert output.name == "share-card.png"
    assert calls[-1]["width"] == 900
    assert calls[-1]["height"] == 500
    assert calls[-1]["scale"] == 3.0
    with pytest.raises(ValueError, match="svg"):
        rendering.export_figure_wm(fig, tmp_path / "chart.jpg")
