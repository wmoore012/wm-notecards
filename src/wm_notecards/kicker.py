"""Structured kicker line for notecard headers.

A *kicker* is the small, all-caps label that sits above a card title —
``CHANNEL • CHAPTER • TOPIC [• TAG]``.  This module parses a compact
comma-separated spec into a frozen dataclass and renders it as inline
HTML or plain text.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wm_notecards._types import ThemeLike


# ── dataclass ────────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class WMKicker:
    """Structured kicker: ``CHANNEL • CHAPTER • TOPIC [• TAG]``.

    Parameters
    ----------
    channel : str
        Stream identifier (``"STANDARD"`` or ``"NOTE"``).
    chapter : str
        Numeric chapter token, e.g. ``"03"``.
    topic : str
        Free-text topic label, e.g. ``"EDA"``.
    tag : str
        Optional trailing qualifier joined by ``" • "``.
    """

    channel: str = "STANDARD"
    chapter: str = "03"
    topic: str = "EDA"
    tag: str = ""

    # -- helpers -------------------------------------------------------

    @staticmethod
    def _is_chapter(token: str) -> bool:
        """Return True when *token* looks like a chapter number."""
        return token.isdigit()

    # -- parsing -------------------------------------------------------

    @classmethod
    def parse(cls, spec: str | None, *, defaults: WMKicker | None = None) -> WMKicker:
        """Build a ``WMKicker`` from a comma-separated spec string.

        Parameters
        ----------
        spec : str | None
            Compact kicker spec, e.g. ``"03, EDA, FRAUD"``.
            Tokens are uppercased and whitespace-normalised.
            ``"NOTE"`` / ``"STANDARD"`` tokens set the channel.
        defaults : WMKicker | None
            Fallback values for any field not provided by *spec*.

        Returns
        -------
        WMKicker
            Parsed (immutable) kicker instance.
        """
        base = defaults or cls()
        if not spec or not str(spec).strip():
            return base

        parts = [
            " ".join(p.split()).upper()
            for p in str(spec).split(",")
            if p.strip()
        ]

        channel = base.channel
        filtered: list[str] = []
        for part in parts:
            if part in ("NOTE", "STANDARD"):
                channel = part
            else:
                filtered.append(part)
        parts = filtered

        chapter, topic, tag = base.chapter, base.topic, base.tag

        if not parts:
            pass
        elif len(parts) == 1:
            if cls._is_chapter(parts[0]):
                chapter = parts[0]
            else:
                topic = parts[0]
        elif len(parts) == 2:
            if cls._is_chapter(parts[0]):
                chapter, topic = parts[0], parts[1]
            else:
                topic, tag = parts[0], parts[1]
        else:
            if cls._is_chapter(parts[0]):
                chapter = parts[0]
                topic = parts[1]
                tag = " • ".join(parts[2:])
            else:
                topic = parts[0]
                tag = " • ".join(parts[1:])

        return cls(channel=channel, chapter=chapter, topic=topic, tag=tag)

    # -- renderers -----------------------------------------------------

    def to_html(self, theme: ThemeLike) -> str:
        """Render the kicker as an inline-HTML ``<div>``.

        Parameters
        ----------
        theme : ThemeLike
            Visual theme supplying ``font_mono``, ``text_muted``,
            and ``accent`` colour tokens.

        Returns
        -------
        str
            Self-contained HTML fragment.
        """
        segs = [self.channel, self.chapter, self.topic]
        if self.tag:
            segs.append(self.tag)
        sep = "<span style='opacity:0.45'> &bull; </span>"
        body = sep.join(
            f"<span style='letter-spacing:0.15em;'>{escape(s)}</span>"
            for s in segs
        )
        return (
            f"<div style='font-family:{theme.font_mono};font-size:11px;"
            f"text-transform:uppercase;color:{theme.text_muted};"
            f"margin-bottom:10px;'>"
            f"<span style='color:{theme.accent}'>&#9632;</span>&nbsp;{body}"
            f"</div>"
        )

    def to_plotly_html(self, theme: ThemeLike) -> str:
        """HTML-escaped plain-text kicker for Plotly annotations.

        Parameters
        ----------
        theme : ThemeLike
            Accepted for API symmetry; not used for styling.

        Returns
        -------
        str
            Escaped version of :meth:`to_plotly_text`.
        """
        return escape(self.to_plotly_text())

    def to_plotly_text(self) -> str:
        """Plain-text kicker prefixed with a filled square.

        Returns
        -------
        str
            e.g. ``"■ STANDARD • 03 • EDA"``.
        """
        segs = [self.channel, self.chapter, self.topic]
        if self.tag:
            segs.append(self.tag)
        return "■ " + " • ".join(segs)

    def to_line(self) -> str:
        """Short plain-text form without channel.

        Returns
        -------
        str
            e.g. ``"03 • EDA • FRAUD"``.
        """
        segs = [self.chapter, self.topic]
        if self.tag:
            segs.append(self.tag)
        return " • ".join(segs)


# ── convenience function ─────────────────────────────────────────────

def kicker_html(theme: ThemeLike, spec: str | None = None) -> str:
    """One-shot parse-and-render shortcut.

    Parameters
    ----------
    theme : ThemeLike
        Visual theme forwarded to :meth:`WMKicker.to_html`.
    spec : str | None
        Comma-separated kicker spec (see :meth:`WMKicker.parse`).

    Returns
    -------
    str
        Ready-to-display HTML fragment.
    """
    return WMKicker.parse(spec).to_html(theme)
