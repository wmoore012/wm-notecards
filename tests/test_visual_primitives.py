from __future__ import annotations

import types

import plotly.graph_objects as go
import pytest
from IPython.display import Javascript

from wm_notecards import WMTheme, boot, pictogram, rendering
from wm_notecards._colors import WMGradient, generate_discrete_gradient_wm, generate_gradient_wm
from wm_notecards._html import card_shell_css, chip_html, plot_shell_html, shell_header_html
from wm_notecards.icons import get_icon, list_icons
from wm_notecards.kicker import WMKicker, kicker_html


def test_gradients_are_clamped_and_plotly_ready() -> None:
    smooth = generate_gradient_wm(n=5, vmin=0, vmax=1, low="#ffffff", high="#000000")
    stepped = generate_discrete_gradient_wm(n=4, vmin=-1, vmax=1, low="#B74C5F", high="#16C7E8")

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
    assert "overflow-wrap:normal" in chip
    assert "word-break:keep-all" in chip
    assert "hyphens:none" in chip
    assert "overflow-wrap:anywhere" not in chip
    assert "border:0 !important" in chip
    assert "text-shadow:none" in chip
    assert "wm-shell-toprow" in header

    shell = plot_shell_html("<div>plot</div>", theme, figure_width=860)
    assert "wm-plot-scroll" in shell
    assert "scroll horizontally" in shell
    assert "box-shadow:none" in shell
    assert ".wm-plot-shell:hover" in shell


def test_new_output_attention_cue_respects_reduced_motion() -> None:
    theme = WMTheme.light()
    card_css = card_shell_css(theme, card_class="wm-test-card")
    plot_shell = plot_shell_html("<div>plot</div>", theme, figure_width=860)

    for markup in (card_css, plot_shell):
        assert "@keyframes wm-card-arrive" in markup
        assert "animation:wm-card-arrive 0.28s" in markup
        assert "prefers-reduced-motion:reduce" in markup
        assert "animation:none !important" in markup


def test_light_cards_have_roomy_edges_and_cyan_not_white_hover_glow() -> None:
    theme = WMTheme.light()
    css = card_shell_css(theme, card_class="wm-test-card")

    assert "padding:32px 36px 32px 36px" in css
    assert "padding:24px 22px 24px 22px" in css
    assert "rgba(22,199,232,0.18)" in css
    assert "rgba(255,255,255" not in css
    assert theme.tooltip_bg == "#10212B"


def test_notecards_keep_their_border_but_rest_flat_until_hover() -> None:
    theme = WMTheme.light()
    css = card_shell_css(theme, card_class="wm-flat-proof")

    assert f"border:1px solid {theme.border} !important" in css
    assert "box-shadow:none;transition:transform" in css
    assert ".wm-flat-proof:hover{transform:translateY(-2px);box-shadow:0 20px" in css


def test_card_shell_owns_viewport_width_and_only_inner_evidence_may_scroll() -> None:
    css = card_shell_css(WMTheme.light(), card_class="wm-test-card")

    assert "width:100%!important" in css
    assert "min-width:0!important" in css
    assert "box-sizing:border-box!important" in css
    assert "max-width:100%;min-width:0;white-space:normal;overflow-wrap:anywhere" in css


def test_dark_mode_defense_is_theme_aware_and_does_not_paint_plot_wrappers_white() -> None:
    css = boot._dark_mode_defense_css()
    dark_card = card_shell_css(WMTheme.dark(), card_class="wm-dark-proof")
    plot_shell = plot_shell_html("<div>plot</div>", WMTheme.dark(), figure_width=860)

    assert "background: var(--wm-card-bg" not in css
    assert "color-scheme: var(--wm-color-scheme, light)" in css
    assert "--wm-color-scheme:dark" in dark_card
    assert "--wm-text-main:#F5F5F5" in plot_shell
    assert "color-scheme:dark" in plot_shell


def test_mathjax_bootstrap_reuses_host_runtime_instead_of_loading_a_conflicting_copy() -> None:
    html = boot._mathjax_bootstrap_html()

    assert 'script[src*="mathjax" i]' in html
    assert "window.MathJax.Hub.Queue" in html
    assert "!loadedMathJax && !existingMathJaxScript" in html


def test_colab_output_adapter_is_guarded_responsive_and_bounded() -> None:
    javascript = boot._colab_output_height_javascript(5000)

    assert "window.google && window.google.colab" in javascript
    assert "output.setIframeHeight(0, true, { maxHeight: 5000 })" in javascript
    assert "ResizeObserver" in javascript
    assert "requestAnimationFrame" in javascript
    assert "observer.disconnect()" in javascript
    with pytest.raises(ValueError, match="between 800 and 20000"):
        boot._colab_output_height_javascript(799)


def test_init_notebook_emits_output_adapter_only_when_colab_is_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rendered: list[object] = []
    monkeypatch.setitem(boot.sys.modules, "google.colab", types.ModuleType("google.colab"))
    monkeypatch.setattr(boot, "display", rendered.append)
    monkeypatch.setattr(boot, "get_ipython", lambda: None)
    monkeypatch.setattr(boot, "_apply_matplotlib_theme_fonts", lambda: None)

    boot.init_notebook(inline_matplotlib=False)

    adapters = [item for item in rendered if isinstance(item, Javascript)]
    assert len(adapters) == 1
    assert "setIframeHeight" in str(adapters[0].data)


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
    assert "wm-pictogram-card{box-shadow:none" in rendered[-1]
    assert "border:0;box-shadow:none;text-shadow:none" in rendered[-1]
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


def test_plot_chip_owns_a_separate_header_row() -> None:
    shell = plot_shell_html(
        "<div class='figure'>plot</div>",
        WMTheme.light(),
        figure_width=860,
        chip_text="Teal = identity edges",
    )

    assert "wm-plot-chip-row" in shell
    assert "TEAL = IDENTITY EDGES" not in shell  # CSS performs the uppercase transform.
    assert shell.index("<div class='wm-plot-chip-row'") < shell.index("<div class='wm-plot-scroll'")


def test_export_helper_uses_styled_dimensions(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_export(fig, **kwargs):
        calls.append(kwargs)
        return b"image-bytes"

    monkeypatch.setattr(rendering, "_export_image_bytes", fake_export)
    fig = go.Figure(go.Bar(x=["A"], y=[1]))
    fig.update_layout(width=900, height=500)

    output = rendering.export_figure_wm(fig, tmp_path / "share-card.png")

    assert output.name == "share-card.png"
    assert output.read_bytes() == b"image-bytes"
    assert calls[-1]["width"] == 900
    assert calls[-1]["height"] == 520
    assert calls[-1]["scale"] == 3.0
    with pytest.raises(ValueError, match="svg"):
        rendering.export_figure_wm(fig, tmp_path / "chart.jpg")


def test_export_helper_adds_minimum_breathing_room(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[dict[str, object]] = []

    def fake_export(fig, **kwargs):
        calls.append(kwargs)
        return b"image-bytes"

    monkeypatch.setattr(rendering, "_export_image_bytes", fake_export)
    fig = go.Figure(go.Bar(x=["A"], y=[1]))
    fig.update_layout(width=860, height=420)

    rendering.export_figure_wm(fig, tmp_path / "chart.png")

    assert calls[-1]["height"] == 520


def test_vector_exports_keep_human_sized_pages(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_export(fig, **kwargs):
        calls.append(kwargs)
        return b"vector-bytes"

    monkeypatch.setattr(rendering, "_export_image_bytes", fake_export)
    fig = go.Figure(go.Bar(x=["A"], y=[1]))
    fig.update_layout(width=860, height=420)

    for suffix in ("svg", "pdf"):
        output = rendering.export_figure_wm(fig, tmp_path / f"chart.{suffix}")
        assert output.read_bytes() == b"vector-bytes"

    assert [call["scale"] for call in calls] == [1.0, 1.0]
