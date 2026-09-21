from unittest.mock import patch

import pytest

from wm_notecards.boot import init_notebook
from wm_notecards.layout import notebook_layout_css


def test_default_does_not_emit_layout_overrides():
    assert notebook_layout_css() == ""
    with patch("wm_notecards.boot.display") as display:
        init_notebook(inline_matplotlib=False)
    assert "wm-responsive-layout" not in display.call_args[0][0].data


def test_opt_in_is_injected_after_existing_styles():
    with patch("wm_notecards.boot.display") as display:
        init_notebook(layout="responsive", inline_matplotlib=False)
    html = display.call_args[0][0].data
    assert html.index("wm-responsive-layout") > html.index("wm-notebook-css")
    assert ":last-child:nth-child(odd)" in html
    assert "td:nth-of-type(7)" in html
    assert ".output_container .output {" not in html


def test_invalid_preset_fails_before_mutating_renderer():
    with patch("wm_notecards.boot.pio") as pio, patch("wm_notecards.boot.display") as display:
        with pytest.raises(ValueError, match="layout"):
            init_notebook(layout="typo")
        display.assert_not_called()
        assert not pio.mock_calls
