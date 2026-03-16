import unittest
from app import app, convert_to_ppg, calculate_total_flow_area, calculate_bit_hydraulics

class TestApp(unittest.TestCase):
    def test_convert_to_ppg(self):
        self.assertEqual(convert_to_ppg(1, 'sg'), 8.33)
        self.assertEqual(convert_to_ppg(1, 'ppg'), 1)

if __name__ == '__main__':
    unittest.main()
