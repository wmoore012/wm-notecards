"""Build a focused browser proof from the real EDA rendering helpers."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd

from wm_notecards import WMTheme
from wm_notecards import cards as card_module
from wm_notecards import eda as eda_module
from wm_notecards import tables as table_module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("build/readme-eda-proof.html"))
    return parser.parse_args()


def _synthetic_frame() -> pd.DataFrame:
    rng = np.random.default_rng(20260718)
    rows = 84
    frame = pd.DataFrame(
        {
            "record_id": [f"SYN-{index:03d}" for index in range(rows)],
            "month": pd.date_range("2018-01-01", periods=rows, freq="MS"),
            "target": 72 + np.arange(rows) * 0.55 + rng.normal(0, 4.5, rows),
            "exposure": rng.lognormal(mean=1.2, sigma=0.9, size=rows),
            "channel": np.resize(["Direct", "Partner", "Community"], rows),
            "reviewed": np.resize([True, False, True, True], rows),
        }
    )
    frame.loc[[7, 38], "exposure"] = np.nan
    return frame


def _capture_outputs() -> list[str]:
    rendered: list[str] = []

    def capture(obj: Any) -> None:
        rendered.append(str(getattr(obj, "data", obj)))

    card_runtime = cast("Any", card_module)
    eda_runtime = cast("Any", eda_module)
    table_runtime = cast("Any", table_module)
    originals = (card_runtime.display, eda_runtime.display, table_runtime.display)
    card_runtime.display = capture
    eda_runtime.display = capture
    table_runtime.display = capture
    try:
        theme = WMTheme.light()
        frame = _synthetic_frame()
        card_module.question_card(
            theme=theme,
            title="What needs attention before this DataFrame becomes evidence?",
            body=(
                "Nothing changed. First read the field roles. Then inspect shape and "
                "missingness. You still decide what deserves preprocessing."
            ),
            kicker="EDA, source contract, question",
            chip_text="NO AUTOMATIC CHANGES",
        )
        eda_module.display_data_chips(
            frame,
            theme=theme,
            target="target",
            identifier_columns=["record_id"],
            datetime_columns=["month"],
            categorical_columns=["channel"],
        )
        table_module.wm_render_micro_profile_cards(
            frame,
            theme=theme,
            columns=["target", "exposure", "channel", "reviewed"],
            visible_cards=3,
            skew_threshold=1.0,
        )
    finally:
        card_runtime.display, eda_runtime.display, table_runtime.display = originals
    return rendered


def build_html() -> str:
    outputs = _capture_outputs()
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>wm-notecards EDA proof</title>
<style>
*{box-sizing:border-box}html,body{margin:0;background:#EFF1F5;color:#111}
body{padding:22px 18px 40px;overflow-x:hidden}
.proof{max-width:1120px;margin:0 auto}
.proof-label{max-width:1040px;margin:4px auto 14px;font:900 12px/1.4 ui-monospace,monospace;
letter-spacing:.16em;text-transform:uppercase;color:#087D91}
.proof .wm-question-card-shell{margin-top:0!important}
@media(max-width:640px){body{padding:10px 8px 28px}.proof-label{margin-left:8px}}
</style></head><body><main class="proof">
<div class="proof-label">QUESTION → FIELD ROLES → SHAPE → YOUR DECISION</div>
""" + "\n".join(outputs) + "\n</main></body></html>"


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(), encoding="utf-8")
    print(f"Wrote README EDA proof: {args.output.resolve()}")


if __name__ == "__main__":
    main()
