from pathlib import Path
import sys

import pytest


CRAWLER_PATH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CRAWLER_PATH))

from pagination import paginate_text


def test_paginate_text_splits_content():
    text = "A" * 2500
    first = paginate_text(text, page=1, page_size=1000)
    third = paginate_text(text, page=3, page_size=1000)

    assert first.page_count == 3
    assert first.has_next is True
    assert third.text == "A" * 500
    assert third.has_next is False


def test_paginate_text_rejects_bad_ranges():
    with pytest.raises(ValueError):
        paginate_text("A" * 500, page=0, page_size=200)

    with pytest.raises(ValueError):
        paginate_text("A" * 500, page=1, page_size=100)
