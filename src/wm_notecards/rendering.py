"""Reliable static SVG figure-card rendering via Kaleido.

Provides structured error diagnostics when static export fails, so that
notebooks surface a clear, actionable diagnostic panel instead of
silently falling back to an interactive Plotly chart outside the WM card
shell.

.. warning::

   REGRESSION WARNING: If chart appears outside the WM card shell, that
   is a kernel problem, not a usable fallback.  Fix the active kernel
   and rerun *Bootstrap / Dependency Setup*, *Imports*, and *Rendering
   Proof*.
"""
from __future__ import annotations

import importlib.metadata as _metadata
import re
import sys
import tempfile
from html import escape
from pathlib import Path
from typing import TYPE_CHECKING

import plotly.graph_objects as go
from IPython.display import HTML, display

from wm_notecards import charts as charts_mod
from wm_notecards._html import plot_shell_html

if TYPE_CHECKING:
    from wm_notecards._types import ThemeLike, WMCardRole, WMVerdictTone

# ── Compiled patterns ────────────────────────────────────────────────
_XML_DECL_RE = re.compile(r"^\s*<\?xml[^>]*>\s*", flags=re.IGNORECASE)
_DOCTYPE_RE = re.compile(r"^\s*<!DOCTYPE[^>]*>\s*", flags=re.IGNORECASE)
_SVG_TAG_RE = re.compile(r"<svg\b([^>]*)>", flags=re.IGNORECASE)
_SAFE_FILE_STUB_RE = re.compile(r"[^A-Za-z0-9._-]+")


# ── Private helpers ──────────────────────────────────────────────────

def _package_version(name: str) -> str:
    """Best-effort version string for an installed package."""
    try:
        return _metadata.version(name)
    except _metadata.PackageNotFoundError:
        return "not installed"
    except Exception as exc:
        return f"unavailable ({exc})"


def _safe_export_stub(file_stub: str) -> str:
    """Sanitise *file_stub* into a filesystem-safe base name."""
    stub = _SAFE_FILE_STUB_RE.sub("_", str(file_stub).strip())
    stub = stub.strip("._-")
    if not stub:
        return "figure"
    return stub[:80]


def _export_svg_bytes(fig: go.Figure, *, file_stub: str) -> bytes:
    """Export *fig* to SVG bytes via Kaleido (lazy import)."""
    import kaleido  # optional dependency — imported lazily

    export_path = Path(tempfile.gettempdir()) / f"{_safe_export_stub(file_stub)}.svg"
    return kaleido.calc_fig_sync(fig, path=export_path, opts={"format": "svg"})


def _inline_svg_markup(svg_bytes: bytes, *, file_stub: str) -> str:
    """Clean up raw SVG bytes and wrap in a centred ``<div>``.

    Strips XML declarations / DOCTYPEs, injects accessibility attributes
    and responsive centering styles, then wraps the SVG in a flex
    container.
    """
    svg_text = svg_bytes.decode("utf-8")
    svg_text = _XML_DECL_RE.sub("", svg_text)
    svg_text = _DOCTYPE_RE.sub("", svg_text)
    match = _SVG_TAG_RE.search(svg_text)
    if match is None:
        raise ValueError("Static Plotly export did not produce SVG markup.")

    svg_attrs = match.group(1).rstrip()
    if "style=" not in svg_attrs:
        svg_attrs += ' style="display:block;max-width:100%;height:auto;margin:0 auto;"'
    if "role=" not in svg_attrs:
        svg_attrs += ' role="img"'
    if "aria-label=" not in svg_attrs:
        svg_attrs += f' aria-label="{escape(file_stub)}"'
    if "preserveAspectRatio=" not in svg_attrs:
        svg_attrs += ' preserveAspectRatio="xMidYMid meet"'

    svg_text = f"{svg_text[: match.start()]}<svg{svg_attrs}>{svg_text[match.end() :]}"
    return (
        '<div style="display:flex;justify-content:center;align-items:flex-start;'
        'width:100%;">'
        f"{svg_text}"
        "</div>"
    )


def _render_export_diagnostic(
    *,
    theme: ThemeLike,
    file_stub: str,
    exc: Exception,
) -> None:
    """Display a structured error panel when static SVG export fails.

    The panel shows Python / Plotly / Kaleido versions alongside the
    exception so the author can diagnose the kernel environment without
    leaving the notebook.
    """
    context = collect_rendering_proof(run_smoke_test=False)
    error_type = escape(type(exc).__name__)
    error_message = escape(str(exc))
    python_executable = escape(str(context["python_executable"]))
    plotly_version = escape(str(context["plotly_version"]))
    kaleido_version = escape(str(context["kaleido_version"]))

    figure_html = f"""
    <div class="wm-render-diagnostic" style="
      width:100%;
      box-sizing:border-box;
      font-family:{theme.font_display};
      color:{theme.text_main};
      padding:8px 4px 2px 4px;
    ">
      <div style="
        font-family:{theme.font_mono};
        font-size:11px;
        letter-spacing:0.16em;
        text-transform:uppercase;
        color:{theme.text_muted};
        margin-bottom:10px;
      ">Chart render failure</div>
      <div style="
        font-size:28px;
        font-weight:900;
        line-height:1.08;
        margin-bottom:12px;
      ">Static SVG export failed in this notebook kernel.</div>
      <div style="
        width:132px;
        height:4px;
        background:{theme.accent};
        margin:0 0 14px 0;
      "></div>
      <div style="
        font-size:16px;
        line-height:1.65;
        color:{theme.text_main};
        margin-bottom:14px;
      ">
        The notebook is stopping here instead of falling back to a raw Plotly chart outside the WM card shell.
        Fix the active kernel, then rerun <strong>Bootstrap / Dependency Setup</strong>, <strong>Imports</strong>,
        and <strong>Rendering Proof</strong>.
      </div>
      <div style="
        display:grid;
        grid-template-columns: 180px 1fr;
        gap:10px 14px;
        align-items:start;
        margin-bottom:16px;
        font-family:{theme.font_mono};
        font-size:12px;
        line-height:1.5;
      ">
        <div style="color:{theme.text_muted};text-transform:uppercase;letter-spacing:0.08em;">Figure</div>
        <div>{escape(file_stub)}</div>
        <div style="color:{theme.text_muted};text-transform:uppercase;letter-spacing:0.08em;">Python</div>
        <div>{python_executable}</div>
        <div style="color:{theme.text_muted};text-transform:uppercase;letter-spacing:0.08em;">Plotly</div>
        <div>{plotly_version}</div>
        <div style="color:{theme.text_muted};text-transform:uppercase;letter-spacing:0.08em;">Kaleido</div>
        <div>{kaleido_version}</div>
        <div style="color:{theme.text_muted};text-transform:uppercase;letter-spacing:0.08em;">Error</div>
        <div>{error_type}: {error_message}</div>
      </div>
      <div style="
        font-family:{theme.font_mono};
        font-size:12px;
        line-height:1.55;
        color:{theme.text_muted};
        background:{theme.plot_bg};
        border:1px solid {theme.border};
        border-radius:12px;
        padding:12px 14px;
      ">
        Expected path: run the notebook from the repo-local environment defined by <code>pyproject.toml</code> and <code>uv.lock</code>.
        If charts ever appear outside the WM cards, treat that as a kernel problem, not a usable fallback.
      </div>
    </div>
    """
    display(
        HTML(
            plot_shell_html(
                figure_html,
                theme,
                figure_width=theme.width,
            )
        )
    )


def _prepare_figure_card(
    fig: go.Figure,
    *,
    theme: ThemeLike,
    file_stub: str,
    role: WMCardRole,
    kicker: str | None,
    chip_text: str | None,
    mode: str,
) -> None:
    """Apply card-level layout adjustments (margins, kicker, chip)."""
    if role not in ("chart", "verdict"):
        raise ValueError("wm_render_figure_card supports chart or verdict roles only.")

    fig_width = int(getattr(fig.layout, "width", 0) or theme.width)
    fig.update_layout(
        width=min(fig_width, theme.width),
        paper_bgcolor="rgba(0,0,0,0)" if mode == "notebook" else theme.card_bg,
    )

    theme_height = int(getattr(theme, "height", 400) or 400)

    annotation_text = charts_mod._plotly_kicker_text(kicker)
    if annotation_text:
        current_margin = getattr(fig.layout, "margin", None)
        top_margin = int(getattr(current_margin, "t", 0) or 0)
        current_height = int(getattr(fig.layout, "height", 0) or theme_height)
        charts_mod._prepend_kicker_to_title(
            fig,
            kicker_text=annotation_text,
            theme=theme,
        )
        new_top_margin = max(top_margin + 22, 128)
        fig.update_layout(
            margin=dict(t=new_top_margin),
            height=current_height + max(0, new_top_margin - top_margin),
        )

    if chip_text:
        current_margin = getattr(fig.layout, "margin", None)
        top_margin = int(getattr(current_margin, "t", 0) or 0)
        current_height = int(getattr(fig.layout, "height", 0) or theme_height)
        new_top_margin = max(top_margin + 64, 218)
        charts_mod._add_header_chip(fig, chip_text=chip_text, theme=theme)
        fig.update_layout(
            margin=dict(t=new_top_margin),
            height=current_height + max(0, new_top_margin - top_margin),
        )


# =====================================================================
# Public API
# =====================================================================

def collect_rendering_proof(*, run_smoke_test: bool = True) -> dict[str, object]:
    """Run a real static-export smoke test in the active kernel.

    Creates a trivial Plotly bar chart and attempts to export it to SVG
    via Kaleido.  The returned dict captures versions, success/failure
    status, and — on failure — the exception details, giving notebooks a
    reliable "rendering proof" cell.

    Parameters
    ----------
    run_smoke_test : bool, default ``True``
        When ``False`` the function skips the actual export and returns
        only environment metadata (useful for the diagnostic panel).

    Returns
    -------
    dict[str, object]
        Keys: ``python_executable``, ``plotly_version``,
        ``kaleido_version``, ``ok`` (``bool | None``),
        ``error_type``, ``error_message``, ``svg_bytes``
        (byte count on success).
    """
    proof: dict[str, object] = {
        "python_executable": sys.executable,
        "plotly_version": _package_version("plotly"),
        "kaleido_version": _package_version("kaleido"),
        "ok": None if not run_smoke_test else False,
        "error_type": None,
        "error_message": None,
        "svg_bytes": None,
    }
    if not run_smoke_test:
        return proof

    fig = go.Figure(go.Bar(x=[1, 2], y=[1, 2]))
    try:
        svg_bytes = _export_svg_bytes(fig, file_stub="rendering_proof")
    except Exception as exc:
        proof["error_type"] = type(exc).__name__
        proof["error_message"] = str(exc)
        return proof

    proof["ok"] = True
    proof["svg_bytes"] = len(svg_bytes)
    return proof


def wm_render_figure_card_reliable(
    fig: go.Figure,
    *,
    theme: ThemeLike,
    file_stub: str,
    role: WMCardRole = "chart",
    kicker: str | None = None,
    verdict_tone: WMVerdictTone = "neutral",
    mode: str = "notebook",
    chip_text: str | None = None,
    prefer_static: bool = True,
) -> None:
    """Render a WM chart card with static-SVG preference and structured failure diagnostics.

    When *prefer_static* is ``True`` (the default), the figure is
    exported to SVG via Kaleido and displayed inside a ``plot_shell_html``
    wrapper.  If the export fails, a full diagnostic panel is rendered
    instead of silently falling back to an interactive chart.

    When *prefer_static* is ``False``, delegates directly to
    :func:`wm_notecards.charts.show_fig_wm` for interactive display.

    .. warning::

       REGRESSION WARNING: If chart appears outside the WM card shell,
       that is a kernel problem, not a usable fallback.

    Parameters
    ----------
    fig : go.Figure
        Plotly figure to render (styled in-place).
    theme : ThemeLike
        Active visual theme providing typography, colours, and
        dimensions.
    file_stub : str
        Base filename for the exported SVG.
    role : WMCardRole, default ``"chart"``
        Card role — must be ``"chart"`` or ``"verdict"``.
    kicker : str | None, default ``None``
        Kicker spec prepended above the figure title.
    verdict_tone : WMVerdictTone, default ``"neutral"``
        Tone token (reserved for downstream role-colour logic).
    mode : str, default ``"notebook"``
        Rendering target — ``"notebook"`` makes the paper transparent.
    chip_text : str | None, default ``None``
        Optional status chip rendered in the figure header.
    prefer_static : bool, default ``True``
        Attempt static SVG export via Kaleido before falling back.

    Raises
    ------
    ValueError
        If *role* is not ``"chart"`` or ``"verdict"``.
    """
    del verdict_tone

    _prepare_figure_card(
        fig,
        theme=theme,
        file_stub=file_stub,
        role=role,
        kicker=kicker,
        chip_text=chip_text,
        mode=mode,
    )

    if prefer_static:
        try:
            svg_bytes = _export_svg_bytes(fig, file_stub=file_stub)
        except Exception as exc:
            _render_export_diagnostic(
                theme=theme,
                file_stub=file_stub,
                exc=exc,
            )
            return

        figure_width = int(getattr(fig.layout, "width", 0) or theme.width)
        display(
            HTML(
                plot_shell_html(
                    _inline_svg_markup(svg_bytes, file_stub=file_stub),
                    theme,
                    figure_width=figure_width,
                )
            )
        )
        return

    charts_mod.show_fig_wm(fig, file_stub=file_stub, theme=theme, mode=mode)
