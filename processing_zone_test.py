import unittest
from processing_zone import find_unnecessary_ion

class TestProcessingZone(unittest.TestCase):
    def test_find_unnecessary_ion_with_ions_not_in_flat_seq(self):
        parking_ions = [1, 2, 3, 4]
        flat_seq = [5, 6, 7, 8]
        result = find_unnecessary_ion(parking_ions, flat_seq)
        self.assertIn(result, parking_ions)

    def test_find_unnecessary_ion_with_all_ions_in_flat_seq(self):
        parking_ions = [1, 2, 3, 4]
        flat_seq = [4, 3, 2, 1]
        result = find_unnecessary_ion(parking_ions, flat_seq)
        self.assertEqual(result, 1)

    def test_find_unnecessary_ion_with_mixed_ions(self):
        parking_ions = [1, 2, 3, 4]
        flat_seq = [3, 4, 5, 6]
        result = find_unnecessary_ion(parking_ions, flat_seq)
        self.assertIn(result, [1, 2])

    def test_find_unnecessary_ion_with_empty_flat_seq(self):
        parking_ions = [1, 2, 3, 4]
        flat_seq = []
        result = find_unnecessary_ion(parking_ions, flat_seq)
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()