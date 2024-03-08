from unittest import TestCase
from modules.fuzzy_check import check_similar_values, check_similarities


class TestFuzzyCheck(TestCase):
    def test_check_similar_values(self):
        values = []
        similar_values = check_similar_values(values, 100)
        self.assertEqual(0, len(similar_values))

        values = ["Value"]
        similar_values = check_similar_values(values, 100)
        self.assertEqual(0, len(similar_values))

        values = ["Value", "Value"]
        similar_values = check_similar_values(values, 100)
        self.assertEqual(1, len(similar_values))
        self.assertEqual(0, similar_values[0][0])
        self.assertEqual(1, similar_values[0][1])
        self.assertEqual(100, similar_values[0][2])

        values = ["Value", "", "Value"]
        similar_values = check_similar_values(values, 100)
        self.assertEqual(1, len(similar_values))
        self.assertEqual(0, similar_values[0][0])
        self.assertEqual(2, similar_values[0][1])
        self.assertEqual(100, similar_values[0][2])

        values = ["Value A", "", "Value A", "Value B"]
        similar_values = check_similar_values(values, 100)
        self.assertEqual(1, len(similar_values))
        self.assertEqual(0, similar_values[0][0])
        self.assertEqual(2, similar_values[0][1])
        self.assertEqual(100, similar_values[0][2])

        values = ["Value A", "", "Value A", "Value B", "Value B"]
        similar_values = check_similar_values(values, 100, 1)
        self.assertEqual(1, len(similar_values))
        self.assertEqual(3, similar_values[0][0])
        self.assertEqual(4, similar_values[0][1])
        self.assertEqual(100, similar_values[0][2])

        values = [
            "Value A",
            "",
            "Value A",
            "Value B",
            "Value B",
            "Value C",
            "",
            "",
            "Value B",
            "Value C",
        ]
        similar_values = check_similar_values(values, 100, 2)
        self.assertEqual(4, len(similar_values))
        self.assertEqual(3, similar_values[0][0])
        self.assertEqual(4, similar_values[0][1])
        self.assertEqual(100, similar_values[0][2])
        self.assertEqual(3, similar_values[1][0])
        self.assertEqual(8, similar_values[1][1])
        self.assertEqual(100, similar_values[1][2])
        self.assertEqual(4, similar_values[2][0])
        self.assertEqual(8, similar_values[2][1])
        self.assertEqual(100, similar_values[2][2])
        self.assertEqual(5, similar_values[3][0])
        self.assertEqual(9, similar_values[3][1])
        self.assertEqual(100, similar_values[3][2])

    def test_check_similarities(self):
        # Test empty CSV
        rows = []
        similarities = check_similarities(rows)
        self.assertEqual(0, len(similarities))

        # Test single value CSV
        rows = [["Value 1"]]
        similarities = check_similarities(rows)
        self.assertEqual(0, len(similarities))

        # Test single column CSV
        rows = [["Value 1"], ["Value 2"]]
        similarities = check_similarities(rows)
        self.assertEqual(0, len(similarities))

        # Test 2x2 CSV: should produce no results, as the first column isn't
        # included in similarity checks.
        rows = [["Value 1", "Value 2"], ["Value 3", "Value 4"]]
        similarities = check_similarities(rows)
        self.assertEqual(0, len(similarities))

        # We expect 4 similarity results:
        #
        # * Row 0, column 1: "Value 2"
        # * Row 0, column 2: "Value 3"
        # * Row 1, column 1: "Value 5"
        # * Row 1, column 2: "Value 6"
        #
        # "Value 1" and "Value 4" aren't included as the similarity check always
        # skips the first column.
        rows = [
            ["Value 1", "Value 2", "Value 3"],
            ["Value 4", "Value 5", "Value 6"],
        ]
        similarities = check_similarities(rows)
        self.assertEqual(4, len(similarities))
        self.assertIn((0, 1), similarities)
        self.assertIn((0, 2), similarities)
        self.assertIn((1, 1), similarities)
        self.assertIn((1, 2), similarities)
        self.assertEqual("Value 2", similarities[(0, 1)][0])
        self.assertEqual("Value 3", similarities[(0, 2)][0])
        self.assertEqual("Value 5", similarities[(1, 1)][0])
        self.assertEqual("Value 6", similarities[(1, 2)][0])

        # Test that empty values are skipped
        rows = [
            ["Value 1", "", "Value 2", "", "Value 3", ""],
            ["Value 4", "", "Value 5", "", "Value 6", ""],
        ]
        similarities = check_similarities(rows)
        self.assertEqual(4, len(similarities))
        self.assertIn((0, 2), similarities)
        self.assertIn((0, 4), similarities)
        self.assertIn((1, 2), similarities)
        self.assertIn((1, 4), similarities)
        self.assertEqual("Value 2", similarities[(0, 2)][0])
        self.assertEqual("Value 3", similarities[(0, 4)][0])
        self.assertEqual("Value 5", similarities[(1, 2)][0])
        self.assertEqual("Value 6", similarities[(1, 4)][0])

        # Test non-similarities
        rows = [
            ["AAAAAAAA", "", "BBBBBBBB", "", "CCCCCCCC", "", "DDDDDDDD", ""],
            ["AAAAAAAA", "", "BBBBBBBB", "", "BBBBBBBB", "", "CCCCCCCC", ""],
            ["AAAAAAAA", "", "BBBBBBBB", "", "CCCCCCCC", "", "BBBBBBBB", ""],
            ["AAAAAAAA", "", "CCCCCCCC", "", "BBBBBBBB", "", "BBBBBBBB", ""],
            ["AAAAAAAA", "", "BBBBBBBB", "", "BBBBBBBB", "", "BBBBBBBB", ""],
        ]
        similarities = check_similarities(rows)
        self.assertEqual(9, len(similarities))
        self.assertIn((1, 2), similarities)
        self.assertIn((1, 4), similarities)
        self.assertIn((2, 2), similarities)
        self.assertIn((2, 6), similarities)
        self.assertIn((3, 4), similarities)
        self.assertIn((3, 6), similarities)
        self.assertIn((4, 2), similarities)
        self.assertIn((4, 4), similarities)
        self.assertIn((4, 6), similarities)
