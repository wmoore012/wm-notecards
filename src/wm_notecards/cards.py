"""Card rendering functions for data-science notebooks.

Every public function either renders an IPython HTML card via
``display()`` or returns a ready-to-embed HTML fragment.  Card shell
chrome (CSS, wrapper divs, eyebrow, kicker, rule, divider) is
delegated to :mod:`._html` — this module only builds card-specific
content then wraps it with the shared shell.
"""

from __future__ import annotations

import io
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from html import escape
from typing import TYPE_CHECKING, Any, Literal

import pandas as pd
from IPython.display import HTML, Markdown, display

from ._html import (
    _classes,
    _theme_css_custom_properties,
    card_shell_css,
    card_shell_html,
    shell_header_html,
)
from ._html import (
    chip_html as _chip_html,
)
from ._html import (
    kicker_html as _kicker_html,
)
from ._html import (
    note_html as _note_html,
)

try:
    from .kicker import WMKicker as _WMKicker
except ImportError:  # kicker module not yet installed
    _WMKicker = None  # type: ignore[assignment,misc]

if TYPE_CHECKING:
    from ._types import ThemeLike

# ── Language guide ──────────────────────────────────────────────────
# REGRESSION WARNING: AI agents have deleted or watered-down this
# guide repeatedly.  Every bullet below is load-bearing.  Do NOT
# shorten, rephrase, or remove any line.

WM_NOTEBOOK_LANGUAGE_GUIDE: str = """
DO NOT DELETE OR WATER DOWN THIS GUIDE.

This is the source-only language guide for notebook authors and AI editors.
It should stay available in source code, but embedded runtime copies may replace
it with a short placeholder.

This repo aims for David Malan-style visual instructional teaching:

- lead with the point
- Use down-to-earth language
- Define technical terms on first use
- keep anomaly language careful and review-oriented
- teach the reader how to read the evidence before asking for conclusions

DO NOT DELETE the lead-first rule.
Do not rename the nerdy internal variable names unless the code itself needs it.
Do not flatten the notebook into raw `df.describe()` output just because it is quicker.
Do not confuse unusual behavior with proven fraud.
""".strip()

# ── Type aliases ────────────────────────────────────────────────────

WMCardRole = Literal[
    "terms",
    "preview",
    "table",
    "chart",
    "takeaway",
    "next_think",
    "verdict",
]
"""Semantic card role — drives the role-marker colour and eyebrow label."""

WMVerdictTone = Literal["neutral", "pass", "check", "fail"]
"""Verdict accent: neutral grey, green pass, amber check, red fail."""

QuestionPairSide = Mapping[str, str | None]
"""Loose dict for one side of a question-pair card."""

# ── Metadata dataclass ──────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class WMRoleMeta:
    """Resolved display metadata for a card role.

    Parameters
    ----------
    label : str
        Uppercase text shown in the eyebrow (e.g. ``"TAKEAWAY"``).
    idle_marker : str
        CSS colour for the role-marker dot at rest.
    hover_marker : str
        CSS colour for the role-marker dot on hover.
    """

    label: str
    idle_marker: str
    hover_marker: str


# ── Domain dictionaries ─────────────────────────────────────────────

WM_TERM_DEFINITIONS: dict[str, str] = {
    "queue": "A ranked short list of transactions to review first. It is a triage tool, not a final fraud verdict.",
    "top-k": "The first K rows after sorting by a score. If Top-K is 25, the notebook is looking at the top 25 rows.",
    "amount spike": "A transaction whose amount is unusually high for that same account, not just high in absolute dollars.",
    "z-score": "A way to say how far a value is from that account's usual level. Bigger absolute values mean more unusual behavior.",
    "lift": "How much more common a signal is in the ranked shortlist than in the full file. Lift above 1.0 means the shortlist is concentrating that signal.",
    "context change": "A switch in surrounding account behavior, such as device, IP, location, channel, or merchant.",
    "split-safe": "Built using training data only, so the future does not leak backwards into model features or thresholds.",
    "smoke test": "A fast early check used to see whether the feature set can tell a believable story before heavier modeling starts.",
    "baseline": "The usual level of behavior for the same account or for the full file.",
    "prevalence": "How common something is in the data.",
    "anomaly": "A row that looks unusual relative to the rest of the data. Unusual does not automatically mean fraud.",
    "threshold": "A cut point used to turn a continuous number into a flag or decision rule.",
    "signal": "A feature that may help distinguish suspicious behavior from typical behavior.",
    "friction": "Extra difficulty around access or completion, such as many login attempts.",
    "outlier": "A value that sits far away from the rest of the distribution.",
    "validation": "A held-out slice used to check whether choices still look reasonable away from the training data.",
}

WM_DISPLAY_LABELS: dict[str, str] = {
    "AccountID": "Account",
    "TransactionID": "Transaction",
    "TransactionDate": "Transaction time",
    "TransactionAmount": "Transaction amount",
    "TxnAmount24h": "24-hour dollar total",
    "TxnCount24h": "24-hour transaction count",
    "BurstAmountPerTxn24h": "Average dollars per 24-hour hit",
    "AmountZScoreByAccount": "Amount surprise (Z-score)",
    "LoginAttempts": "Login attempts",
    "MinutesSincePrevTxn": "Minutes since previous transaction",
    "LogMinutesSincePrevTxn": "Log minutes since previous transaction",
    "DeviceChange": "Device changed",
    "IPChange": "IP changed",
    "ChannelChange": "Channel changed",
    "MerchantChange": "Merchant changed",
    "LocationChange": "Location changed",
    "FirstTimeMerchantForAccount": "First merchant for this account",
    "FirstTimeLocationForAccount": "First location for this account",
    "FirstTimeChannelForAccount": "First channel for this account",
    "NewChannelAfterHistory": "New channel after account history",
    "ShortGap24h": "Returned within 24 hours",
    "ShortGap3h": "Returned within 3 hours",
    "AmountSpike": "Amount spike",
    "VelocitySpike": "24-hour velocity spike",
    "VelocityAmountSpike": "24-hour dollar spike",
    "VelocityCountSpike": "24-hour repeat-activity spike",
    "HighLoginAttempts": "High login attempts",
    "ReasonCode": "Case evidence",
    "ReasonCount": "Number of suspicious reasons",
    "StrongReason": "Has several clues pointing the same way",
    "EvidenceScore": "Evidence score",
    "ensembleScore": "Model score",
    "ruleScore": "Rule score",
    "what_to_do": "What to do differently",
}

WM_REASON_DISPLAY_LABELS: dict[str, str] = {
    "New device": "New device for the account",
    "IP changed": "IP address changed",
    "New or changed channel": "New or changed channel",
    "New or changed merchant": "New or changed merchant",
    "New or changed location": "New or changed location",
    "24h velocity spike": "24-hour activity spike",
    "Heavy 24-hour dollar concentration": "Heavy 24-hour dollar concentration",
    "Repeated activity inside 24 hours": "Repeated activity inside 24 hours",
    "Returned within 24 hours": "Returned within 24 hours",
    "Returned within 3 hours": "Returned within 3 hours",
    "New channel after account history": "New channel after account history",
    "24-hour burst signal": "24-hour burst signal",
    "Multivariate outlier with no single dominant flag": "Unusual mix of signals without one dominant reason",
    "STRONG: debit plus identity shift plus amount spike": "Strong pattern: debit + identity shift + amount spike",
    "STRONG: debit burst plus identity shift": "Strong pattern: debit burst + identity shift",
    "STRONG: unusual amount plus short-window burst": "Strong pattern: unusual amount + short-window burst",
    "STRONG: unusual amount plus fast return": "Strong pattern: unusual amount + fast return",
}

WM_REASON_EXPLANATIONS: dict[str, str] = {
    "New device for the account": "The account context shifted at the device level.",
    "IP address changed": "The network context shifted around the transaction.",
    "New or changed channel": "The transaction moved through a different access path.",
    "New or changed merchant": "The merchant context changed around the event.",
    "New or changed location": "The location context changed around the event.",
    "24-hour activity spike": "Money movement clustered unusually fast inside one day.",
    "Heavy 24-hour dollar concentration": "A large amount of money accumulated inside one day for the same account.",
    "Repeated activity inside 24 hours": "The same account returned often enough inside one day to stand out from the usual rhythm.",
    "Returned within 24 hours": "The account came back unusually quickly relative to its usual spacing.",
    "Returned within 3 hours": "The account came back on a very short timetable.",
    "New channel after account history": "The account used a new access path after a prior behavior pattern already existed.",
    "24-hour burst signal": "Several short-window pressure signals lined up inside the same day.",
    "Strong pattern: debit + identity shift + amount spike": "A stacked cash-out pattern is showing up in one row.",
    "Strong pattern: debit burst + identity shift": "A stacked burst pattern is showing up in one row.",
    "Strong pattern: unusual amount + short-window burst": "An unusual amount and a short-window burst are lining up on the same row.",
    "Strong pattern: unusual amount + fast return": "An unusual amount arrived with a faster-than-usual return to the account.",
}

# ── Role / verdict colour maps ──────────────────────────────────────
# REGRESSION WARNING: these rgba/hex pairs drive the identity markers
# on every card.  Changing them silently breaks visual regression tests.

_WM_ROLE_LABELS: dict[WMCardRole, str] = {
    "terms": "TERMS",
    "preview": "PREVIEW",
    "table": "TABLE",
    "chart": "CHART",
    "takeaway": "TAKEAWAY",
    "next_think": "NEXT THINK",
    "verdict": "VERDICT",
}

_WM_ROLE_COLORS: dict[WMCardRole, tuple[str, str]] = {
    "terms": ("rgba(164, 141, 255, 0.34)", "#A48DFF"),
    "preview": ("rgba(98, 150, 255, 0.34)", "#6B9CFF"),
    "table": ("rgba(22, 199, 232, 0.34)", "#16C7E8"),
    "chart": ("rgba(69, 222, 255, 0.34)", "#45DEFF"),
    "takeaway": ("rgba(27, 201, 141, 0.34)", "#1BC98D"),
    "next_think": ("rgba(255, 183, 53, 0.34)", "#FFB735"),
    "verdict": ("rgba(111, 124, 138, 0.34)", "#7B8591"),
}

_WM_VERDICT_COLORS: dict[WMVerdictTone, tuple[str, str]] = {
    "neutral": _WM_ROLE_COLORS["verdict"],
    "pass": ("rgba(32, 181, 123, 0.34)", "#20B57B"),
    "check": ("rgba(244, 168, 36, 0.34)", "#F4A824"),
    "fail": ("rgba(232, 82, 111, 0.34)", "#E8526F"),
}

# ── Lookup helpers ──────────────────────────────────────────────────


def wm_term_definition(term: str) -> str | None:
    """Look up a plain-language definition for *term*.

    Parameters
    ----------
    term : str
        Case-insensitive term to look up (leading/trailing whitespace
        is stripped).

    Returns
    -------
    str or None
        Human-readable definition, or ``None`` if unknown.
    """
    return WM_TERM_DEFINITIONS.get(term.strip().lower())


def wm_display_label(name: str) -> str:
    """Map a raw column name to a human-friendly display label.

    Parameters
    ----------
    name : str
        Column or feature name.

    Returns
    -------
    str
        Display label (falls back to *name* itself if no mapping).
    """
    return WM_DISPLAY_LABELS.get(name, name)


def wm_reason_display_label(name: str) -> str:
    """Map a raw reason code to a reader-friendly label.

    Parameters
    ----------
    name : str
        Reason string as stored in the data.

    Returns
    -------
    str
        Friendlier label (falls back to *name* itself).
    """
    if name.startswith("Amount spike (Z="):
        return name.replace("Amount spike", "Large amount for this account")
    if name.startswith("High login attempts ("):
        return name.replace("High login attempts", "Heavy login friction")
    if name.startswith("Large amount for this account (Z="):
        return name
    if name.startswith("Heavy login friction ("):
        return name
    return WM_REASON_DISPLAY_LABELS.get(name, name)


def wm_reason_explainer(name: str) -> str:
    """Return a one-sentence explanation of a reason code.

    Parameters
    ----------
    name : str
        Raw reason string (will be display-mapped first).

    Returns
    -------
    str
        Explanation sentence.
    """
    display_name = wm_reason_display_label(name)
    if display_name.startswith("Large amount for this account (Z="):
        return "The amount looked unusually large for the same account."
    if display_name.startswith("Heavy login friction ("):
        return "The account needed heavier-than-usual login effort around the event."
    return WM_REASON_EXPLANATIONS.get(
        display_name,
        "This reason adds another plain-language clue to the case story.",
    )


def wm_role_meta(
    role: WMCardRole,
    *,
    verdict_tone: WMVerdictTone = "neutral",
) -> WMRoleMeta:
    """Resolve a card role to its display metadata.

    Parameters
    ----------
    role : WMCardRole
        Semantic card role.
    verdict_tone : WMVerdictTone
        Accent tone (only matters when *role* is ``"verdict"``).

    Returns
    -------
    WMRoleMeta
        Frozen metadata with label, idle marker, and hover marker.
    """
    if role == "verdict":
        idle_marker, hover_marker = _WM_VERDICT_COLORS[verdict_tone]
    else:
        idle_marker, hover_marker = _WM_ROLE_COLORS[role]
    return WMRoleMeta(
        label=_WM_ROLE_LABELS[role],
        idle_marker=idle_marker,
        hover_marker=hover_marker,
    )


# ── Internal render helpers ─────────────────────────────────────────


def _parse_kicker(kicker: str | None) -> str | None:
    """Parse a kicker through WMKicker (if available) and return the line.

    Falls back to returning *kicker* unchanged when the kicker module
    has not been installed.
    """
    if not kicker:
        return None
    if _WMKicker is not None:
        return _WMKicker.parse(kicker).to_line()
    return kicker


def _card_header(
    *,
    title: str,
    theme: ThemeLike,
    role: WMCardRole,
    verdict_tone: WMVerdictTone = "neutral",
    kicker: str | None = None,
    subtitle: str | None = None,
    chip_text: str | None = None,
    title_size: int | None = None,
) -> tuple[WMRoleMeta, str]:
    """Build a standard card header and return ``(role_meta, html)``.

    Combines :func:`wm_role_meta` with :func:`shell_header_html` from
    ``_html`` so callers get both the role colours (for the shell) and
    the rendered header in a single call.
    """
    meta = wm_role_meta(role, verdict_tone=verdict_tone)
    header = shell_header_html(
        title=title,
        theme=theme,
        eyebrow=meta.label,
        kicker=_parse_kicker(kicker),
        subtitle=subtitle,
        chip_text=chip_text,
        title_size=title_size,
    )
    return meta, header


def _standalone_kicker_html(theme: ThemeLike, kicker: str | None) -> str:
    """Kicker line with inline styles for use *outside* a card shell.

    The class-based kicker from ``_html`` requires the shell CSS context.
    This helper is used by :func:`two_up` where the kicker sits above
    the grid, outside any card wrapper.
    """
    if not kicker:
        return ""
    text = _parse_kicker(kicker) or kicker
    return (
        f"<div style='font-family:{theme.font_mono};font-size:11px;"
        f"text-transform:uppercase;letter-spacing:0.14em;"
        f"color:{theme.text_muted};margin-bottom:10px;'>"
        f"{escape(text)}</div>"
    )


# ── Markdown / prose cards ──────────────────────────────────────────


def wm_md(text: str) -> None:
    """Render a raw Markdown string in the notebook output.

    Parameters
    ----------
    text : str
        Markdown content.
    """
    display(Markdown(text))


def _safe_inline_markdown(text: str) -> str:
    """Render the small Markdown subset supported inside prose cards.

    Card copy commonly needs emphasis and inline code, but it must never be
    able to inject arbitrary notebook HTML. Escape first, protect code spans,
    then add only the three explicitly supported tags.
    """
    escaped = escape(text)
    fragments = re.split(r"(`[^`\n]+`)", escaped)
    rendered: list[str] = []
    for fragment in fragments:
        if fragment.startswith("`") and fragment.endswith("`"):
            rendered.append(f"<code>{fragment[1:-1]}</code>")
            continue
        fragment = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", fragment)
        fragment = re.sub(
            r"(?<!\*)\*([^*\n]+)\*(?!\*)",
            r"<em>\1</em>",
            fragment,
        )
        rendered.append(fragment)
    return "".join(rendered).replace("\n", "<br>")


def wm_markdown_card(
    *,
    title: str,
    theme: ThemeLike,
    body: str | None = None,
    bullets: list[str] | None = None,
    note: str | None = None,
    kicker: str | None = None,
    subtitle: str | None = None,
    role: WMCardRole = "preview",
    verdict_tone: WMVerdictTone = "neutral",
    chip_text: str | None = None,
) -> None:
    """General-purpose prose card with optional body, bullets, and note.

    Parameters
    ----------
    title : str
        Card headline.
    theme : ThemeLike
        Active visual theme.
    body : str, optional
        Paragraph text (newlines become ``<br>``).
    bullets : list[str], optional
        Bulleted list items.
    note : str, optional
        Muted footnote box.
    kicker : str, optional
        Small uppercase meta-line above the title.
    subtitle : str, optional
        Secondary line below the title.
    role : WMCardRole
        Card role for eyebrow and colour.
    verdict_tone : WMVerdictTone
        Accent tone (only used when *role* is ``"verdict"``).
    chip_text : str, optional
        Status chip beside the eyebrow.
    """
    if not title.strip():
        raise ValueError("title must be a non-empty string.")
    if body is None and bullets is None and note is None:
        raise ValueError("Provide at least one of: body, bullets, note.")

    meta, header = _card_header(
        title=title,
        theme=theme,
        role=role,
        verdict_tone=verdict_tone,
        kicker=kicker,
        subtitle=subtitle,
        chip_text=chip_text,
    )

    parts: list[str] = [header]

    # REGRESSION WARNING: html.escape is mandatory on all user text —
    # removing it opens XSS in hosted notebook environments.
    if body:
        parts.append(
            f"<div style='font-family:{theme.font_display};"
            f"color:{theme.text_main};font-size:16px;line-height:1.62;'>"
            f"{_safe_inline_markdown(body)}</div>"
        )

    if bullets:
        items = "".join(
            f"<li style='margin:6px 0;line-height:1.55;'>{_safe_inline_markdown(item)}</li>"
            for item in bullets
        )
        parts.append(
            f"<ul style='margin:12px 0 0 0;padding-left:18px;"
            f"font-family:{theme.font_display};color:{theme.text_main};"
            f"font-size:16px;'>{items}</ul>"
        )

    if note:
        parts.append(_note_html(note, theme))

    display(
        HTML(
            card_shell_html(
                "".join(parts),
                theme,
                card_class="wm-markdown-card",
                role_idle=meta.idle_marker,
                role_hover=meta.hover_marker,
            )
        )
    )


# ── Question cards ──────────────────────────────────────────────────


def _question_card_css(theme: ThemeLike) -> str:
    """Extra CSS rules specific to question-card layout."""
    return (
        "<style>"
        ".wm-question-card-shell .wm-question-head{"
        "display:flex;align-items:flex-start;"
        "justify-content:space-between;gap:12px;margin-bottom:10px;}"
        ".wm-question-card-shell .wm-question-head-main{"
        "display:flex;align-items:flex-start;gap:12px;"
        "min-width:0;flex:1 1 auto;}"
        ".wm-question-card-shell .wm-question-dot{"
        "width:10px;height:10px;border-radius:3px;flex:0 0 auto;"
        "background:var(--wm-role-idle);margin-top:14px;"
        "box-shadow:0 0 0 4px rgba(17,17,17,0.04);"
        "transition:background-color 0.18s ease,"
        "box-shadow 0.18s ease,transform 0.18s ease;}"
        ".wm-question-card-shell:hover .wm-question-dot{"
        "background:var(--wm-role-hover);transform:scale(1.06);"
        "box-shadow:0 0 0 5px rgba(17,17,17,0.05);}"
        ".wm-question-card-shell .wm-question-title{"
        f"font-family:{theme.font_display};"
        "font-weight:900;line-height:1.03;letter-spacing:-0.8px;"
        f"color:{theme.text_main};margin:0;}}"
        ".wm-question-card-shell .wm-question-subtitle{"
        f"font-family:{theme.font_mono};font-size:13px;"
        f"line-height:1.5;color:{theme.text_muted};"
        "margin:10px 0 0 0;}"
        ".wm-question-card-shell .wm-question-body{"
        f"font-family:{theme.font_display};"
        f"line-height:1.62;color:{theme.text_main};"
        "margin-top:12px;}"
        ".wm-question-pair{"
        f"max-width:{theme.width}px;margin:16px auto;display:grid;"
        "grid-template-columns:repeat(auto-fit, minmax(320px, 1fr));"
        "gap:16px;align-items:stretch;}"
        ".wm-question-pair .wm-question-card-shell{"
        "margin:0;max-width:none;height:100%;display:flex;}"
        ".wm-question-pair .wm-question-card-shell .wm-shell-inner{"
        "flex:1 1 auto;display:flex;flex-direction:column;}"
        "@media (max-width:640px){"
        ".wm-question-card-shell .wm-question-head{"
        "flex-direction:column;align-items:stretch;gap:10px;}"
        ".wm-question-card-shell .wm-question-head-main{width:100%;}"
        ".wm-question-card-shell .wm-question-head>.wm-shell-chip{"
        "align-self:flex-start;margin-left:22px;}"
        ".wm-question-card-shell .wm-question-title{"
        "font-size:clamp(28px,8.5vw,34px) !important;}"
        "}"
        "</style>"
    )


def _question_card_markup(
    *,
    title: str,
    theme: ThemeLike,
    body: str | None = None,
    kicker: str | None = None,
    subtitle: str | None = None,
    size: Literal["compact", "roomy"] = "compact",
    embedded: bool = False,
    chip_text: str | None = None,
) -> str:
    """Build the full HTML for a single question card.

    Returns the markup string (does not call ``display``).
    """
    if not title.strip():
        raise ValueError("title must be a non-empty string.")
    if body is None and subtitle is None:
        raise ValueError("Provide at least one of: body or subtitle.")
    if size not in {"compact", "roomy"}:
        raise ValueError("size must be 'compact' or 'roomy'.")

    meta = wm_role_meta("preview")
    title_px = 40 if size == "roomy" else 36
    body_px = 17 if size == "roomy" else 16

    base_css = card_shell_css(theme, card_class="wm-question-card-shell")
    extra_css = _question_card_css(theme)

    margin = "0" if embedded else "16px auto"

    kicker_block = _kicker_html(_parse_kicker(kicker) or "", theme)
    chip_block = _chip_html(chip_text or "", theme)

    subtitle_block = (
        f"<div class='wm-question-subtitle'>{escape(subtitle)}</div>" if subtitle else ""
    )
    body_block = (
        f"<div class='wm-question-body' style='font-size:{body_px}px;'>"
        f"{escape(body).replace(chr(10), '<br>')}</div>"
        if body
        else ""
    )

    return (
        f"{base_css}{extra_css}"
        f"<div class='{_classes('wm-question-card-shell')}' style='"
        f"{_theme_css_custom_properties(theme)}"
        f"--wm-role-idle:{meta.idle_marker};"
        f"--wm-role-hover:{meta.hover_marker};"
        f"margin:{margin};max-width:{theme.width}px;'>"
        "<div class='wm-shell-inner'>"
        f"{kicker_block}"
        "<div class='wm-question-head'>"
        "<div class='wm-question-head-main'>"
        "<span class='wm-question-dot' aria-hidden='true'></span>"
        f"<div class='wm-question-title' style='font-size:{title_px}px;'>"
        f"{escape(title)}</div>"
        "</div>"
        f"{chip_block}"
        "</div>"
        f"{subtitle_block}{body_block}"
        "</div></div>"
    )


def question_card(
    *,
    title: str,
    theme: ThemeLike,
    body: str | None = None,
    kicker: str | None = None,
    subtitle: str | None = None,
    size: Literal["compact", "roomy"] = "compact",
    chip_text: str | None = None,
) -> None:
    """Standalone question card with a dot-accent title.

    Parameters
    ----------
    title : str
        Bold question headline.
    theme : ThemeLike
        Active visual theme.
    body : str, optional
        Supporting paragraph text.
    kicker : str, optional
        Small uppercase meta-line.
    subtitle : str, optional
        Muted secondary line below the title.
    size : ``"compact"`` or ``"roomy"``
        Controls title and body font sizes.
    chip_text : str, optional
        Status chip shown beside the title row.
    """
    display(
        HTML(
            _question_card_markup(
                title=title,
                theme=theme,
                body=body,
                kicker=kicker,
                subtitle=subtitle,
                size=size,
                chip_text=chip_text,
            )
        )
    )


def question_pair(
    *,
    theme: ThemeLike,
    left: Mapping[str, str | None] | None = None,
    right: Mapping[str, str | None] | None = None,
    kicker: str | None = None,
    size: Literal["compact", "roomy"] = "compact",
    chip_text: str | None = None,
    left_title: str | None = None,
    left_body: str | None = None,
    right_title: str | None = None,
    right_body: str | None = None,
) -> None:
    """Side-by-side question cards in a responsive grid.

    Parameters
    ----------
    theme : ThemeLike
        Active visual theme.
    left, right : Mapping, optional
        Dicts with ``title``, ``body``, ``subtitle``, ``kicker`` keys.
        When *None*, the ``left_title`` / ``left_body`` / ``right_title``
        / ``right_body`` keyword shortcuts are used instead.
    kicker : str, optional
        Shared kicker above the pair.
    size : ``"compact"`` or ``"roomy"``
        Font-size preset.
    chip_text : str, optional
        Status chip on each card.
    left_title, left_body, right_title, right_body : str, optional
        Convenience shortcuts when *left* / *right* are not supplied.
    """
    if left is None:
        left = {"title": left_title, "body": left_body}
    if right is None:
        right = {"title": right_title, "body": right_body}

    left_html = _question_card_markup(
        title=str(left.get("title", "") or ""),
        theme=theme,
        body=left.get("body"),
        subtitle=left.get("subtitle"),
        kicker=left.get("kicker") or kicker,
        size=size,
        embedded=True,
        chip_text=chip_text,
    )
    right_html = _question_card_markup(
        title=str(right.get("title", "") or ""),
        theme=theme,
        body=right.get("body"),
        subtitle=right.get("subtitle"),
        kicker=right.get("kicker") or kicker,
        size=size,
        embedded=True,
        chip_text=chip_text,
    )
    two_up(
        left_html=left_html,
        right_html=right_html,
        theme=theme,
        kicker=None,
        min_col_px=320,
        gap_px=16,
    )


# ── Layout ──────────────────────────────────────────────────────────


def _two_up_markup(
    *,
    left_html: str,
    right_html: str,
    theme: ThemeLike,
    kicker: str | None = None,
    pair_class: str = "wm-two-up",
    min_col_px: int = 320,
    gap_px: int = 16,
) -> str:
    """Build a two-column responsive grid wrapper."""
    wrapper_meta = (
        f"<div style='max-width:{theme.width}px;margin:0 auto 8px auto;'>"
        f"{_standalone_kicker_html(theme, kicker)}</div>"
        if kicker
        else ""
    )
    layout_css = (
        "<style>"
        f".{pair_class}{{"
        f"width:100%;max-width:{theme.width}px;margin:16px auto;display:grid;"
        "grid-template-columns:repeat(2,minmax(0,1fr));"
        f"gap:{gap_px}px;align-items:stretch;box-sizing:border-box;}}"
        f".{pair_class} > *{{height:100%;min-width:0;}}"
        f"@media(max-width:{min_col_px * 2 + gap_px + 48}px){{"
        f".{pair_class}{{grid-template-columns:minmax(0,1fr);}}"
        "}"
        "</style>"
    )
    return f"{layout_css}{wrapper_meta}<div class='{pair_class}'>{left_html}{right_html}</div>"


def two_up(
    *,
    left_html: str,
    right_html: str,
    theme: ThemeLike,
    kicker: str | None = None,
    min_col_px: int = 320,
    gap_px: int = 16,
) -> None:
    """Display two HTML fragments side by side in a responsive grid.

    Parameters
    ----------
    left_html, right_html : str
        Pre-rendered HTML for each column.
    theme : ThemeLike
        Active visual theme.
    kicker : str, optional
        Shared kicker shown above the grid.
    min_col_px : int
        Minimum column width before the grid wraps to a single column.
    gap_px : int
        Gap between the two columns.
    """
    display(
        HTML(
            _two_up_markup(
                left_html=left_html,
                right_html=right_html,
                theme=theme,
                kicker=kicker,
                min_col_px=min_col_px,
                gap_px=gap_px,
            )
        )
    )


# ── Diagnostic / check card ─────────────────────────────────────────

_CHECK_TONE_COLORS: dict[str, tuple[str, str, str]] = {
    "PASS": ("#2D6A4F", "rgba(45,106,79,0.12)", "rgba(45,106,79,0.22)"),
    "CHECK": ("#B26B00", "rgba(178,107,0,0.14)", "rgba(178,107,0,0.42)"),
    "FAIL": ("#C1121F", "rgba(193,18,31,0.14)", "rgba(193,18,31,0.52)"),
}


def _check_card_css(theme: ThemeLike) -> str:
    """Extra CSS rules for check-row hover effects."""
    table_hover_bg = getattr(theme, "table_hover_bg", theme.plot_bg)
    table_hover_border = getattr(theme, "table_hover_border", theme.border)
    return (
        "<style>"
        ".wm-check-row{"
        "transition:transform 0.18s ease,box-shadow 0.18s ease,"
        "opacity 0.18s ease,background-color 0.18s ease,"
        "border-color 0.18s ease,filter 0.18s ease;"
        "transform-origin:left center;}"
        ".wm-check-badge{"
        "transition:transform 0.18s ease,box-shadow 0.18s ease,"
        "background-color 0.18s ease,color 0.18s ease;"
        "display:inline-block;border:0;text-shadow:none;"
        "box-shadow:none;}"
        ".wm-check-status-dot{"
        "width:11px;height:11px;border-radius:999px;"
        "background:var(--wm-check-dot-fg);"
        "border:1px solid var(--wm-check-dot-fg);"
        "box-shadow:0 0 0 3px var(--wm-check-dot-bg),"
        "0 0 16px -4px var(--wm-check-glow);"
        "transition:transform 0.18s ease,box-shadow 0.18s ease,"
        "background-color 0.18s ease,border-color 0.18s ease;"
        "flex:0 0 auto;}"
        ".wm-check-card-shell .wm-check-row:hover{"
        "opacity:1;filter:none;transform:scale(1.008);"
        f"background:{table_hover_bg} !important;"
        f"border-color:{table_hover_border} !important;"
        "box-shadow:0 18px 28px -20px rgba(0,0,0,0.42);}"
        ".wm-check-card-shell .wm-check-row:hover .wm-check-label,"
        ".wm-check-card-shell .wm-check-row:hover .wm-check-detail{"
        f"color:{theme.accent} !important;}}"
        ".wm-check-card-shell .wm-check-row:hover .wm-check-status-dot{"
        "transform:scale(1.24);"
        "background:var(--wm-check-dot-fg) !important;"
        "box-shadow:0 0 0 5px var(--wm-check-dot-bg),"
        "0 0 26px 4px var(--wm-check-glow),"
        "0 10px 18px -12px rgba(0,0,0,0.45);}"
        ".wm-check-card-shell .wm-check-row:hover .wm-check-badge{"
        "transform:scale(1.06);"
        "box-shadow:0 0 28px 0 var(--wm-check-glow),"
        "0 10px 18px -12px rgba(0,0,0,0.45);}"
        "</style>"
    )


def wm_check_card(
    *,
    title: str,
    checks: Sequence[Mapping[str, str | None]],
    theme: ThemeLike,
    kicker: str | None = None,
    note: str | None = None,
    subtitle: str | None = None,
    chip_text: str | None = None,
) -> None:
    """Checklist card with PASS / CHECK / FAIL status rows.

    Parameters
    ----------
    title : str
        Card headline.
    checks : Sequence[Mapping]
        Each mapping needs ``"label"`` and ``"status"``
        (``"PASS"``, ``"CHECK"``, or ``"FAIL"``).  An optional
        ``"detail"`` key adds a muted sub-line.
    theme : ThemeLike
        Active visual theme.
    kicker : str, optional
        Small uppercase meta-line.
    note : str, optional
        Muted footnote box.
    subtitle : str, optional
        Secondary line below the title.
    chip_text : str, optional
        Status chip beside the eyebrow.
    """
    if not checks:
        raise ValueError("checks must contain at least one row.")

    meta, header = _card_header(
        title=title,
        theme=theme,
        role="verdict",
        kicker=kicker,
        subtitle=subtitle,
        chip_text=chip_text,
    )

    rows: list[str] = []
    for raw in checks:
        label = str(raw.get("label", "") or "").strip()
        status = str(raw.get("status", "") or "").strip().upper()
        detail = str(raw.get("detail", "") or "").strip()
        if not label:
            raise ValueError("each check row needs a non-empty 'label'.")
        if status not in _CHECK_TONE_COLORS:
            raise ValueError(f"unsupported status {status!r}; use PASS, CHECK, or FAIL.")

        fg, bg, glow = _CHECK_TONE_COLORS[status]
        detail_block = (
            f"<div class='wm-check-detail' style='margin-top:4px;"
            f"color:{theme.text_muted};font-family:{theme.font_mono};"
            f"font-size:12px;line-height:1.45;'>{escape(detail)}</div>"
            if detail
            else ""
        )
        rows.append(
            f"<div class='wm-check-row' style='"
            f"--wm-check-dot-fg:{fg};--wm-check-dot-bg:{bg};"
            f"--wm-check-glow:{glow};"
            f"padding:12px 14px;border:1px solid {theme.border};"
            f"border-radius:12px;background:{theme.plot_bg};"
            f"margin-top:10px;'>"
            "<div style='display:flex;align-items:center;"
            "justify-content:space-between;gap:12px;'>"
            "<div style='display:flex;align-items:center;gap:10px;'>"
            "<span class='wm-check-status-dot' aria-hidden='true'></span>"
            f"<div class='wm-check-label' style='font-family:{theme.font_display};"
            f"font-size:15px;font-weight:700;"
            f"color:{theme.text_main};'>{escape(label)}</div>"
            "</div>"
            f"<span class='wm-check-badge' style='font-family:{theme.font_mono};"
            "font-size:11px;font-weight:800;letter-spacing:0.12em;"
            "text-transform:uppercase;padding:5px 8px;border-radius:999px;"
            f"color:{fg};background:{bg};'>{status}</span>"
            f"</div>{detail_block}</div>"
        )

    content = header + "".join(rows) + _note_html(note or "", theme)

    # REGRESSION WARNING: the shell must pair open+close divs exactly.
    # card_shell_html handles this internally.
    display(
        HTML(
            card_shell_html(
                content,
                theme,
                card_class="wm-check-card-shell",
                role_idle=meta.idle_marker,
                role_hover=meta.hover_marker,
                extra_css=_check_card_css(theme),
            )
        )
    )


# ── Glossary card ───────────────────────────────────────────────────


def glossary_card(
    *,
    title: str,
    terms: list[str] | dict[str, str],
    theme: ThemeLike,
    intro: str | None = None,
    kicker: str | None = None,
    note: str | None = None,
) -> None:
    """Term-definition card, optionally auto-looking up built-in terms.

    Parameters
    ----------
    title : str
        Card headline.
    terms : list[str] or dict[str, str]
        When a ``list``, each string is looked up via
        :func:`wm_term_definition`.  When a ``dict``, keys are terms
        and values are definitions.
    theme : ThemeLike
        Active visual theme.
    intro : str, optional
        Introductory paragraph before the term list.
    kicker : str, optional
        Small uppercase meta-line.
    note : str, optional
        Muted footnote box.
    """
    if isinstance(terms, dict):
        items = list(terms.items())
    else:
        unknown = [term for term in terms if wm_term_definition(term) is None]
        if unknown:
            missing = ", ".join(repr(term) for term in unknown)
            raise ValueError(
                "No built-in glossary definition for "
                f"{missing}. Pass a dict of term-to-definition values."
            )
        items = [(term, wm_term_definition(term) or "") for term in terms]

    rows_html = "".join(
        f"<div style='padding:12px 0;border-top:1px solid {theme.grid};'>"
        f"<div style='font-family:{theme.font_display};font-size:16px;"
        f"font-weight:800;color:{theme.text_main};margin-bottom:4px;'>"
        f"{escape(term)}</div>"
        f"<div style='font-family:{theme.font_display};font-size:15px;"
        f"line-height:1.55;color:{theme.text_main};'>"
        f"{escape(defn)}</div></div>"
        for term, defn in items
        if term and defn
    )

    meta, header = _card_header(
        title=title,
        theme=theme,
        role="terms",
        kicker=kicker,
    )

    intro_block = ""
    if intro:
        intro_block = (
            f"<div style='font-family:{theme.font_display};font-size:16px;"
            f"line-height:1.62;color:{theme.text_main};margin-bottom:4px;'>"
            f"{escape(intro)}</div>"
        )

    content = header + intro_block + rows_html + _note_html(note or "", theme)
    display(
        HTML(
            card_shell_html(
                content,
                theme,
                card_class="wm-glossary-card",
                role_idle=meta.idle_marker,
                role_hover=meta.hover_marker,
            )
        )
    )


# ── Convenience wrappers ────────────────────────────────────────────


def preview_card(
    *,
    title: str,
    theme: ThemeLike,
    body: str | None = None,
    bullets: list[str] | None = None,
    kicker: str | None = None,
    subtitle: str | None = None,
    chip_text: str | None = None,
) -> None:
    """Preview-role markdown card (shortcut for ``wm_markdown_card``).

    Parameters
    ----------
    title : str
        Card headline.
    theme : ThemeLike
        Active visual theme.
    body : str, optional
        Paragraph text.
    bullets : list[str], optional
        Bulleted list items.
    kicker : str, optional
        Small uppercase meta-line.
    subtitle : str, optional
        Secondary line below the title.
    chip_text : str, optional
        Status chip beside the eyebrow.
    """
    wm_markdown_card(
        title=title,
        subtitle=subtitle,
        theme=theme,
        body=body,
        bullets=bullets,
        kicker=kicker,
        role="preview",
        chip_text=chip_text,
    )


def takeaway_card(
    *,
    title: str,
    theme: ThemeLike,
    metric: str | None = None,
    body: str,
    bullets: list[str] | None = None,
    kicker: str | None = None,
    note: str | None = None,
    chip_text: str | None = None,
) -> None:
    """Takeaway-role markdown card.

    Parameters
    ----------
    title : str
        Card headline.
    theme : ThemeLike
        Active visual theme.
    metric : str, optional
        Metric subtitle shown below the title.
    body : str
        Main paragraph text.
    bullets : list[str], optional
        Bulleted list items.
    kicker : str, optional
        Small uppercase meta-line.
    note : str, optional
        Muted footnote box.
    chip_text : str, optional
        Status chip beside the eyebrow.
    """
    wm_markdown_card(
        title=title,
        subtitle=metric,
        theme=theme,
        body=body,
        bullets=bullets,
        note=note,
        kicker=kicker,
        role="takeaway",
        chip_text=chip_text,
    )


def next_think_card(
    *,
    title: str,
    theme: ThemeLike,
    body: str | None = None,
    bullets: list[str] | None = None,
    kicker: str | None = None,
    note: str | None = None,
    chip_text: str | None = None,
) -> None:
    """Next-think-role markdown card.

    Parameters
    ----------
    title : str
        Card headline.
    theme : ThemeLike
        Active visual theme.
    body : str, optional
        Paragraph text.
    bullets : list[str], optional
        Bulleted list items.
    kicker : str, optional
        Small uppercase meta-line.
    note : str, optional
        Muted footnote box.
    chip_text : str, optional
        Status chip beside the eyebrow.
    """
    wm_markdown_card(
        title=title,
        theme=theme,
        body=body,
        bullets=bullets,
        note=note,
        kicker=kicker,
        role="next_think",
        chip_text=chip_text,
    )


def verdict_card(
    *,
    title: str,
    theme: ThemeLike,
    verdict: WMVerdictTone,
    body: str,
    metric: str | None = None,
    bullets: list[str] | None = None,
    kicker: str | None = None,
    note: str | None = None,
    chip_text: str | None = None,
) -> None:
    """Verdict-role markdown card with a pass/check/fail accent.

    Parameters
    ----------
    title : str
        Card headline.
    theme : ThemeLike
        Active visual theme.
    verdict : WMVerdictTone
        Accent tone: ``"pass"``, ``"check"``, ``"fail"``, or
        ``"neutral"``.
    body : str
        Main paragraph text.
    metric : str, optional
        Metric subtitle shown below the title.
    bullets : list[str], optional
        Bulleted list items.
    kicker : str, optional
        Small uppercase meta-line.
    note : str, optional
        Muted footnote box.
    chip_text : str, optional
        Status chip beside the eyebrow.
    """
    wm_markdown_card(
        title=title,
        subtitle=metric,
        theme=theme,
        body=body,
        bullets=bullets,
        note=note,
        kicker=kicker,
        role="verdict",
        verdict_tone=verdict,
        chip_text=chip_text,
    )


# ── Numeric highlight cards ─────────────────────────────────────────


def big_number_card(
    *,
    title: str,
    theme: ThemeLike,
    value: str,
    value_label: str,
    body: str,
    kicker: str | None = None,
    subtitle: str | None = None,
    chip_text: str | None = None,
) -> None:
    """Centred hero-number card for a single KPI.

    Parameters
    ----------
    title : str
        Card headline.
    theme : ThemeLike
        Active visual theme.
    value : str
        Large formatted number (e.g. ``"4.2×"``).
    value_label : str
        Small uppercase label above the number.
    body : str
        Explanation paragraph below the number.
    kicker : str, optional
        Small uppercase meta-line.
    subtitle : str, optional
        Secondary line below the title.
    chip_text : str, optional
        Status chip beside the eyebrow.
    """
    meta, header = _card_header(
        title=title,
        theme=theme,
        role="takeaway",
        kicker=kicker,
        subtitle=subtitle,
        chip_text=chip_text,
    )

    number_block = (
        "<div style='max-width:760px;margin:0 auto;text-align:center;'>"
        f"<div style='font-family:{theme.font_mono};font-size:12px;"
        "letter-spacing:0.14em;text-transform:uppercase;"
        f"color:{theme.text_muted};margin-bottom:10px;'>"
        f"{escape(value_label)}</div>"
        f"<div style='font-family:{theme.font_display};font-size:84px;"
        f"font-weight:900;line-height:0.96;color:{theme.accent};"
        f"margin-bottom:14px;'>{escape(value)}</div>"
        f"<div style='width:132px;height:4px;background:{theme.accent};"
        "margin:0 auto 14px auto;'></div>"
        f"<div style='font-family:{theme.font_display};font-size:16px;"
        f"line-height:1.62;color:{theme.text_main};'>"
        f"{escape(body).replace(chr(10), '<br>')}</div>"
        "</div>"
    )

    display(
        HTML(
            card_shell_html(
                header + number_block,
                theme,
                card_class="wm-big-number-card",
                role_idle=meta.idle_marker,
                role_hover=meta.hover_marker,
            )
        )
    )


def stat_card(
    *,
    label: str,
    value: str,
    theme: ThemeLike,
    subtitle: str | None = None,
) -> str:
    """Small inline stat tile (returns HTML, does not display).

    Designed to be placed inside a :func:`two_up` grid or similar
    layout wrapper.

    Parameters
    ----------
    label : str
        Small uppercase label.
    value : str
        Formatted value string.
    theme : ThemeLike
        Active visual theme.
    subtitle : str, optional
        Muted line below the value.

    Returns
    -------
    str
        Self-contained HTML ``<div>`` string.
    """
    subtitle_block = (
        f"<div style='font-family:{theme.font_mono};font-size:12px;"
        f"color:{theme.text_muted};margin-top:6px;'>"
        f"{escape(subtitle)}</div>"
        if subtitle
        else ""
    )
    return (
        f"<div style='padding:12px 14px;border:1px solid {theme.border};"
        f"border-radius:14px;background:{theme.card_bg};'>"
        f"<div style='font-family:{theme.font_mono};font-size:11px;"
        "letter-spacing:0.14em;text-transform:uppercase;"
        f"color:{theme.text_muted};'>{escape(label)}</div>"
        f"<div style='font-family:{theme.font_display};font-size:28px;"
        f"font-weight:900;color:{theme.text_main};margin-top:6px;'>"
        f"{escape(value)}</div>"
        f"{subtitle_block}</div>"
    )


# ── LaTeX / formula helpers ─────────────────────────────────────────
# REGRESSION WARNING: each regex / replacement in _normalize_latex_for_svg
# fixes a real matplotlib rendering bug discovered through production
# notebooks.  Do not "simplify" by removing entries.

_WM_TEXT_CMD_RE: re.Pattern[str] = re.compile(r"\\text\{([^{}]+)\}")
_WM_DISPLAY_WRAPPER_RE: re.Pattern[str] = re.compile(
    r"^\\\[(.*)\\\]$",
    flags=re.DOTALL,
)


def _count_unescaped_char(value: str, char: str) -> int:
    """Count occurrences of *char* that are not preceded by a backslash."""
    count = 0
    escaped = False
    for token in value:
        if escaped:
            escaped = False
            continue
        if token == "\\":
            escaped = True
            continue
        if token == char:
            count += 1
    return count


def _normalize_latex_for_svg(latex: str) -> str:
    """Normalise LaTeX for matplotlib's mathtext renderer.

    Fixes double-escapes, unsupported commands, and mismatched braces
    that commonly appear in notebook-authored LaTeX strings.
    """
    normalized = str(latex).strip()

    while "\\\\" in normalized:
        normalized = normalized.replace("\\\\", "\\")
    normalized = re.sub(r"(?<!\\)\{\{", "{", normalized)
    normalized = re.sub(r"(?<!\\)\}\}", "}", normalized)

    wrapped = _WM_DISPLAY_WRAPPER_RE.match(normalized)
    if wrapped:
        normalized = wrapped.group(1).strip()

    normalized = _WM_TEXT_CMD_RE.sub(
        lambda m: "\\mathrm{" + m.group(1) + "}",
        normalized,
    )
    normalized = normalized.replace(r"\Pr", r"\mathrm{Pr}")
    normalized = normalized.replace(r"\mathbb{1}", r"\mathbf{1}")
    normalized = normalized.replace(
        r"\min_{\{c_i\},\{\mu_k\}}",
        r"\min_{c_i,\mu_k}",
    )
    normalized = normalized.replace(r"\left\lVert", r"\Vert ")
    normalized = normalized.replace(r"\right\rVert", r"\Vert")
    normalized = normalized.replace(r"\lVert", r"\Vert")
    normalized = normalized.replace(r"\rVert", r"\Vert")
    normalized = normalized.replace(r"\le ", r"\leq ")
    normalized = normalized.replace(r"\le}", r"\leq}")
    normalized = normalized.replace(r"\le)", r"\leq)")
    normalized = normalized.replace(r"\ge ", r"\geq ")
    normalized = normalized.replace(r"\ge}", r"\geq}")
    normalized = normalized.replace(r"\ge)", r"\geq)")
    normalized = re.sub(r"\s{2,}", " ", normalized)

    open_braces = _count_unescaped_char(normalized, "{")
    close_braces = _count_unescaped_char(normalized, "}")
    if open_braces > close_braces:
        normalized += "}" * (open_braces - close_braces)

    return normalized


def _render_latex_svg(theme: ThemeLike, latex: str) -> str | None:
    """Render *latex* to an inline SVG using matplotlib.

    Returns ``None`` if matplotlib is unavailable or rendering fails.
    """
    normalized = _normalize_latex_for_svg(latex)
    if not normalized:
        return None

    try:
        import matplotlib.pyplot as plt
    except Exception:
        return None

    figure = plt.figure(figsize=(10, 1.4))
    figure.patch.set_alpha(0.0)
    try:
        figure.text(
            0.01,
            0.5,
            f"${normalized}$",
            fontsize=16,
            color=theme.text_main,
            va="center",
            ha="left",
        )
        buffer = io.StringIO()
        figure.savefig(
            buffer,
            format="svg",
            bbox_inches="tight",
            pad_inches=0.04,
            transparent=True,
        )
    except Exception:
        return None
    finally:
        plt.close(figure)

    svg = buffer.getvalue()
    svg = re.sub(r"<\?xml[^>]*>\s*", "", svg, count=1)
    svg = re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg, count=1)
    return svg.strip()


def _math_block_css(theme: ThemeLike, *, card_class: str) -> str:
    """CSS for the math-grid / math-panel layout inside formula cards."""
    return (
        "<style>"
        f".{card_class} .wm-math-grid{{"
        "display:grid;"
        "grid-template-columns:repeat(auto-fit,minmax(280px,1fr));"
        "gap:14px;margin-bottom:14px;}}"
        f".{card_class} .wm-math-panel{{"
        f"padding:14px;border-radius:14px;"
        f"border:1px solid {theme.border};background:{theme.plot_bg};}}"
        f".{card_class} .wm-math-label{{"
        f"font-family:{theme.font_mono};font-size:11px;"
        "letter-spacing:0.14em;text-transform:uppercase;"
        f"color:{theme.text_muted};margin-bottom:8px;}}"
        f".{card_class} .wm-math-svg{{"
        "display:flex;justify-content:center;align-items:flex-start;"
        "width:100%;margin:0 0 8px 0;}}"
        f".{card_class} .wm-math-svg svg{{"
        "display:block;width:auto;height:auto;"
        "max-width:min(100%,460px);margin:0 auto;}}"
        f".{card_class} .wm-math-tex{{"
        f"font-family:{theme.font_mono};font-size:15px;line-height:1.6;"
        f"color:{theme.text_main};overflow-wrap:anywhere;}}"
        f".{card_class} .wm-math-fallback{{"
        f"font-family:{theme.font_mono};font-size:12px;line-height:1.5;"
        f"color:{theme.text_muted};margin-top:8px;overflow-wrap:anywhere;}}"
        "</style>"
    )


def _math_panel_html(
    theme: ThemeLike,
    item: Mapping[str, str | None],
) -> str:
    """Render a single formula panel (label + LaTeX SVG + fallback)."""
    label = str(item.get("label", "") or "").strip()
    latex = str(item.get("latex", "") or "").strip()
    fallback = str(item.get("fallback", "") or "").strip()
    if not (latex or fallback):
        raise ValueError("math items need at least one of 'latex' or 'fallback'.")

    latex_svg = _render_latex_svg(theme, latex) if latex else None

    if latex_svg:
        latex_block = f"<div class='wm-math-svg'>{latex_svg}</div>"
    elif latex and not fallback:
        latex_block = f"<div class='wm-math-tex'>{escape(_normalize_latex_for_svg(latex))}</div>"
    else:
        latex_block = ""

    fallback_block = f"<div class='wm-math-fallback'>{escape(fallback)}</div>" if fallback else ""
    label_block = f"<div class='wm-math-label'>{escape(label)}</div>" if label else ""
    return f"<div class='wm-math-panel'>{label_block}{latex_block}{fallback_block}</div>"


# ── Formula / counterintuitive cards ────────────────────────────────


def wm_formula_card(
    *,
    title: str,
    theme: ThemeLike,
    items: Sequence[Mapping[str, str | None]],
    subtitle: str | None = None,
    kicker: str | None = None,
    chip_text: str | None = None,
) -> None:
    """Card displaying one or more formula panels in a responsive grid.

    Parameters
    ----------
    title : str
        Card headline.
    theme : ThemeLike
        Active visual theme.
    items : Sequence[Mapping]
        Formula items, each with optional ``"label"``, ``"latex"``,
        and ``"fallback"`` keys.  At least one of ``"latex"`` or
        ``"fallback"`` is required per item.
    subtitle : str, optional
        Secondary line below the title.
    kicker : str, optional
        Small uppercase meta-line.
    chip_text : str, optional
        Status chip beside the eyebrow.
    """
    if not items:
        raise ValueError("items must contain at least one formula block.")

    card_cls = "wm-formula-card"
    meta, header = _card_header(
        title=title,
        theme=theme,
        role="preview",
        kicker=kicker,
        subtitle=subtitle,
        chip_text=chip_text,
        title_size=24,
    )

    grid = (
        "<div class='wm-math-grid'>"
        + "".join(_math_panel_html(theme, item) for item in items)
        + "</div>"
    )

    display(
        HTML(
            card_shell_html(
                header + grid,
                theme,
                card_class=card_cls,
                role_idle=meta.idle_marker,
                role_hover=meta.hover_marker,
                extra_css=_math_block_css(theme, card_class=card_cls),
            )
        )
    )


def wm_counterintuitive_card(
    *,
    theme: ThemeLike,
    why_misread: str,
    ordinary_process: str,
    conclusion_boundary: str,
    title: str = "How this could be counterintuitive",
    subtitle: str | None = None,
    kicker: str | None = None,
    chip_text: str | None = None,
    math_items: Sequence[Mapping[str, str | None]] | None = None,
) -> None:
    """Three-section card for counterintuitive findings.

    Parameters
    ----------
    theme : ThemeLike
        Active visual theme.
    why_misread : str
        Body for the "Why A Novice Might Overread It" section.
    ordinary_process : str
        Body for the "What Ordinary Process Could Also Produce It"
        section.
    conclusion_boundary : str
        Body for the "Correct Conclusion Boundary" section.
    title : str
        Card headline.
    subtitle : str, optional
        Secondary line below the title.
    kicker : str, optional
        Small uppercase meta-line.
    chip_text : str, optional
        Status chip beside the eyebrow.
    math_items : Sequence[Mapping], optional
        Formula panels to show above the sections.
    """
    card_cls = "wm-counterintuitive-card"

    meta, header = _card_header(
        title=title,
        theme=theme,
        role="preview",
        kicker=kicker,
        subtitle=subtitle,
        chip_text=chip_text,
        title_size=24,
    )

    math_block = ""
    if math_items:
        math_block = (
            _math_block_css(theme, card_class=card_cls)
            + "<div class='wm-math-grid'>"
            + "".join(_math_panel_html(theme, item) for item in math_items)
            + "</div>"
        )

    sections = [
        ("Why A Novice Might Overread It", why_misread),
        ("What Ordinary Process Could Also Produce It", ordinary_process),
        ("Correct Conclusion Boundary", conclusion_boundary),
    ]
    section_html = "".join(
        f"<div style='padding:12px 0;border-top:1px solid {theme.grid};'>"
        f"<div style='font-family:{theme.font_mono};font-size:11px;"
        "letter-spacing:0.14em;text-transform:uppercase;"
        f"color:{theme.text_muted};margin-bottom:8px;'>"
        f"{escape(sec_label)}</div>"
        f"<div style='font-family:{theme.font_display};font-size:16px;"
        f"line-height:1.62;color:{theme.text_main};'>"
        f"{escape(sec_body).replace(chr(10), '<br>')}</div></div>"
        for sec_label, sec_body in sections
    )

    display(
        HTML(
            card_shell_html(
                header + math_block + section_html,
                theme,
                card_class=card_cls,
                role_idle=meta.idle_marker,
                role_hover=meta.hover_marker,
            )
        )
    )


# ── Data summary ────────────────────────────────────────────────────


def wm_build_reason_summary(
    reasons: pd.Series[Any],
    *,
    top_n: int = 10,
) -> pd.DataFrame:
    """Aggregate pipe-delimited reason codes into a ranked frequency table.

    Parameters
    ----------
    reasons : pd.Series
        Series of ``" | "``-delimited reason strings.
    top_n : int
        Maximum number of reasons to return.

    Returns
    -------
    pd.DataFrame
        Two-column frame (``reason``, ``count``), sorted by count
        descending then reason ascending.
    """
    counts: dict[str, int] = {}
    for raw in reasons.fillna("").astype(str):
        parts = [wm_reason_display_label(part.strip()) for part in raw.split(" | ") if part.strip()]
        for part in dict.fromkeys(parts):
            counts[part] = counts.get(part, 0) + 1

    summary = pd.DataFrame(
        [{"reason": r, "count": c} for r, c in counts.items()],
    )
    if summary.empty:
        return pd.DataFrame(columns=["reason", "count"])
    result = (
        summary.sort_values(
            ["count", "reason"],
            ascending=[False, True],
            kind="stable",
        )
        .head(top_n)
        .reset_index(drop=True)
    )
    return pd.DataFrame(result)
