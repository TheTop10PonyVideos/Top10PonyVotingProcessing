from unittest import TestCase
from functions.general import sample_item_without_replacement, pad_csv_rows


class TestFunctionsGeneral(TestCase):
    def test_sample_item_without_replacement(self):
        items = ["a", "b", "c", "d", "e"]
        sampled_item = sample_item_without_replacement(items)
        self.assertTrue(sampled_item in ["a", "b", "c", "d", "e"])
        self.assertEqual(4, len(items))
        sample_item_without_replacement(items)
        self.assertEqual(3, len(items))
        sample_item_without_replacement(items)
        self.assertEqual(2, len(items))
        sample_item_without_replacement(items)
        self.assertEqual(1, len(items))
        sample_item_without_replacement(items)
        self.assertEqual(0, len(items))

        with self.assertRaises(ValueError):
            sample_item_without_replacement(items)
 
    def test_pad_csv_rows(self):
        rows = [
            ["A", "B", "C"],
            ["D", "E", "F"],
            ["G", "H", "I"],
        ]

        padded_rows = pad_csv_rows(rows, 4)

        self.assertEqual(len(padded_rows), 4)
        self.assertEqual(len(padded_rows[3]), 3)
        self.assertEqual(padded_rows[0][0], "A")
        self.assertEqual(padded_rows[0][1], "B")
        self.assertEqual(padded_rows[0][2], "C")
        self.assertEqual(padded_rows[1][0], "D")
        self.assertEqual(padded_rows[1][1], "E")
        self.assertEqual(padded_rows[1][2], "F")
        self.assertEqual(padded_rows[2][0], "G")
        self.assertEqual(padded_rows[2][1], "H")
        self.assertEqual(padded_rows[2][2], "I")
        self.assertEqual(padded_rows[3][0], "")
        self.assertEqual(padded_rows[3][1], "")
        self.assertEqual(padded_rows[3][2], "")

        padded_rows = pad_csv_rows(rows, 3)
        self.assertEqual(len(padded_rows), 3)
        self.assertEqual(padded_rows[0][0], "A")
        self.assertEqual(padded_rows[0][1], "B")
        self.assertEqual(padded_rows[0][2], "C")
        self.assertEqual(padded_rows[1][0], "D")
        self.assertEqual(padded_rows[1][1], "E")
        self.assertEqual(padded_rows[1][2], "F")
        self.assertEqual(padded_rows[2][0], "G")
        self.assertEqual(padded_rows[2][1], "H")
        self.assertEqual(padded_rows[2][2], "I")

        padded_rows = pad_csv_rows(rows, 1)
        self.assertEqual(len(padded_rows), 3)
        self.assertEqual(padded_rows[0][0], "A")
        self.assertEqual(padded_rows[0][1], "B")
        self.assertEqual(padded_rows[0][2], "C")
        self.assertEqual(padded_rows[1][0], "D")
        self.assertEqual(padded_rows[1][1], "E")
        self.assertEqual(padded_rows[1][2], "F")
        self.assertEqual(padded_rows[2][0], "G")
        self.assertEqual(padded_rows[2][1], "H")
        self.assertEqual(padded_rows[2][2], "I")
