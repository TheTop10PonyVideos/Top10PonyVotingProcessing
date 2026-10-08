from unittest import TestCase
from functions.general import sample_item_without_replacement, pad_csv_rows
import pandas as pd


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
        rows = pd.DataFrame([
            ["A", "B", "C"],
            ["D", "E", "F"],
            ["G", "H", "I"],
        ])

        padded_rows = pad_csv_rows(rows, 4)

        self.assertEqual(len(padded_rows), 4)
        self.assertEqual(len(padded_rows.loc[3]), 3)
        self.assertTrue((padded_rows.iloc[:3] == rows).all().all())
        self.assertTrue((padded_rows.iloc[3].isna()).all())

        padded_rows = pad_csv_rows(rows, 3)
        self.assertEqual(len(padded_rows), 3)
        self.assertTrue((padded_rows == rows).all().all())

        padded_rows = pad_csv_rows(rows, 1)
        self.assertEqual(len(padded_rows), 3)
        self.assertTrue((padded_rows == rows).all().all())
