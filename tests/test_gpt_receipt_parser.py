import os
import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from utils import gpt_receipt_parser


def _build_response(data):
    text = json.dumps(data)
    return SimpleNamespace(
        output=[SimpleNamespace(content=[SimpleNamespace(text=text)])]
    )


def test_parse_receipt_image_requires_api_key(tmp_path):
    img = tmp_path / "r.jpg"
    img.write_bytes(b"data")
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            gpt_receipt_parser.parse_receipt_image(str(img))


@patch("utils.gpt_receipt_parser.OpenAI")
def test_parse_receipt_image_initializes_client(OpenAIMock, tmp_path):
    img = tmp_path / "r.png"
    img.write_bytes(b"data")
    fake_client = SimpleNamespace(
        responses=SimpleNamespace(create=lambda **_: _build_response([
            {"producto": "Cafe", "cantidad": 1, "precio": 2}
        ]))
    )
    OpenAIMock.return_value = fake_client
    with patch.dict(os.environ, {"OPENAI_API_KEY": "key"}):
        items = gpt_receipt_parser.parse_receipt_image(str(img))
    assert items == [{"producto": "Cafe", "cantidad": 1, "precio": 2}]
    OpenAIMock.assert_called_once_with(api_key="key")
