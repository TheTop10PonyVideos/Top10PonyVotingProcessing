from unittest import TestCase
from functions.general import sample_item_without_replacement


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
