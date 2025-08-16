import json
import unittest
from unittest.mock import patch

from utils import gpt_receipt_parser


class TestGptReceiptParser(unittest.TestCase):
    @patch("utils.gpt_receipt_parser.openai")
    def test_parse_receipt(self, mock_openai):
        sample_items = {
            "items": [
                {
                    "producto_id": 1,
                    "nombre_producto": "Cafe",
                    "cantidad": 2,
                    "costo_unitario": 10,
                }
            ]
        }
        mock_openai.ChatCompletion.create.return_value = {
            "choices": [
                {"message": {"content": json.dumps(sample_items)}}
            ]
        }
        items = gpt_receipt_parser.parse_receipt("dummy.png")
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["nombre_producto"], "Cafe")
        self.assertEqual(item["cantidad"], 2)
        self.assertEqual(item["costo_unitario"], 10)


if __name__ == "__main__":
    unittest.main()
