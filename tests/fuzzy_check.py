from unittest import TestCase
from modules.fuzzy_check import check_similar_values, check_similarities

class TestFuzzyCheck(TestCase):
    def test_check_similar_values(self):
        values = []
        similar_values = check_similar_values(values, 100)
        self.assertEqual(0, len(similar_values))

        values = ['Value']
        similar_values = check_similar_values(values, 100)
        self.assertEqual(0, len(similar_values))

        values = ['Value', 'Value']
        similar_values = check_similar_values(values, 100)
        self.assertEqual(1, len(similar_values))
        self.assertEqual(0, similar_values[0][0])
        self.assertEqual(1, similar_values[0][1])
        self.assertEqual(100, similar_values[0][2])

        values = ['Value', '', 'Value']
        similar_values = check_similar_values(values, 100)
        self.assertEqual(1, len(similar_values))
        self.assertEqual(0, similar_values[0][0])
        self.assertEqual(2, similar_values[0][1])
        self.assertEqual(100, similar_values[0][2])

        values = ['Value A', '', 'Value A', 'Value B']
        similar_values = check_similar_values(values, 100)
        self.assertEqual(1, len(similar_values))
        self.assertEqual(0, similar_values[0][0])
        self.assertEqual(2, similar_values[0][1])
        self.assertEqual(100, similar_values[0][2])

        values = ['Value A', '', 'Value A', 'Value B', 'Value B']
        similar_values = check_similar_values(values, 100, 1)
        self.assertEqual(1, len(similar_values))
        self.assertEqual(3, similar_values[0][0])
        self.assertEqual(4, similar_values[0][1])
        self.assertEqual(100, similar_values[0][2])

        values = ['Value A', '', 'Value A', 'Value B', 'Value B', 'Value C', '', '', 'Value B', 'Value C']
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
        rows_a = [
            ["Cell A1", "Cell A2", "Cell A3"],
            ["Cell A4", "Cell A5", "Cell A6"],
        ]
        similarities = check_similarities(rows_a)

        # We expect 4 similarity results:
        #
        # * Row 0, index 1: "Cell A2"
        # * Row 0, index 2: "Cell A3"
        # * Row 1, index 1: "Cell A5"
        # * Row 1, index 2: "Cell A6"
        #
        # "Cell A1" and "Cell A4" aren't included as the similarity check always
        # skips the first column.
        #
        # rows_b isn't included as the similarity check doesn't actually check
        # anything in the second set of rows.

        self.assertEqual(4, len(similarities))
        self.assertIn((0, 1), similarities)
        self.assertIn((0, 2), similarities)
        self.assertIn((1, 1), similarities)
        self.assertIn((1, 2), similarities)
