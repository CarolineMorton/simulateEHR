import unittest
from unittest.mock import patch

from src.practices.factories.standard import StandardPracticeFactory
from src.practices.practice import Practice, RegistrationDates, TransferParameters, BirthYearParameters



class TestStandardPracticeFactory(unittest.TestCase):
    """Tests for the StandardPracticeFactory class"""

    def setUp(self):
        """Set up a factory with fixed seed before each test"""
        self.factory = StandardPracticeFactory(seed=9147856)

    def test_generate_practice_size(self):
        """Test practice size generation produces expected results"""
        # Given fixed seed, we can test exact values
        size = self.factory._generate_practice_size()

        self.assertIsInstance(size, int)
        self.assertGreater(size, 0)

        # Test validation
        self.factory.config.practice_size_df1 = -1
        with self.assertRaisesRegex(ValueError, "Degrees of freedom must be positive"):
            self.factory._generate_practice_size()

        self.factory.config.practice_size_df2 = -1
        with self.assertRaisesRegex(ValueError, "Degrees of freedom must be positive"):
            self.factory._generate_practice_size()

    def test_generate_demographics(self):
        """Test demographic generation produces valid male proportions"""
        male_prop = self.factory._generate_demographics()

        self.assertIsInstance(male_prop, float)
        self.assertGreaterEqual(male_prop, 0)
        self.assertLessEqual(male_prop, 1)

        # Test invalid config
        self.factory.config.demographics.male_proportion_mean = 1.5
        with self.assertRaisesRegex(ValueError, "Male proportion mean must be between 0 and 1"):
            self.factory._generate_demographics()

    def test_generate_ethnicity_proportions(self):
        """Test ethnicity proportion generation"""
        ethnicities = self.factory._generate_ethnicity_proportions()

        # Check correct keys present
        expected_keys = {'white', 'south_asian', 'black', 'other', 'mixed', 'unknown'}
        self.assertEqual(set(ethnicities.keys()), expected_keys)

        # Check proportions are valid
        for prop in ethnicities.values():
            self.assertGreaterEqual(prop, 0)
            self.assertLessEqual(prop, 1)

        # Check proportions sum to 1 (within floating point precision)
        total = sum(ethnicities.values())
        total_int = int(total)
        self.assertAlmostEqual(total_int, 1.0, places=7)

    def test_generate_registration_dates(self):
        """Test registration date generation"""
        reg_dates = self.factory._generate_registration_dates()

        self.assertIsInstance(reg_dates, RegistrationDates)

        # Check dates are in correct order
        self.assertLess(reg_dates.earliest_registration, reg_dates.median_registration)
        self.assertLess(reg_dates.median_registration, reg_dates.latest_registration)

        # Check correct values
        self.assertEqual(round(reg_dates.earliest_registration, 0), -6627)
        self.assertEqual(round(int(reg_dates.median_registration), 0), 6618)
        self.assertEqual(round(reg_dates.latest_registration, 0), 20011)


    def test_generate_transfer_parameters(self):
        """Test transfer parameter generation"""
        transfer_params = self.factory._generate_transfer_parameters()

        self.assertIsInstance(transfer_params, TransferParameters)

        # Check gaps are in correct order
        self.assertLess(transfer_params.minimum_gap, transfer_params.median_gap)
        self.assertLess(transfer_params.median_gap, transfer_params.maximum_gap)

        # Check probability is valid
        self.assertGreaterEqual(transfer_params.transfer_probability, 0)
        self.assertLessEqual(transfer_params.transfer_probability, 1)

    def test_generate_birth_years(self):
        """Test birth year generation"""
        birth_years = self.factory._generate_birth_years()

        self.assertIsInstance(birth_years, BirthYearParameters)

        # Check years are in correct order
        self.assertLess(birth_years.earliest_birth_year, birth_years.median_birth_year)
        self.assertLess(birth_years.median_birth_year, birth_years.latest_birth_year)

        # Test invalid config
        self.factory.config.demographics.min_yob_mean = 1700
        with self.assertRaisesRegex(ValueError, "Earliest birth year mean must be realistic"):
            self.factory._generate_birth_years()

    def test_create_practice(self):
        """Test complete practice creation"""
        practice = self.factory.create_practice(practice_id=1)

        self.assertIsInstance(practice, Practice)
        self.assertEqual(practice.practice_id, 1)
        self.assertGreater(practice.patient_count, 0)

    def test_create_practices(self):
        """Test creation of multiple practices"""
        practices = self.factory.create_practices(number_of_practices=5)

        self.assertEqual(len(practices), 5)
        self.assertTrue(all(isinstance(p, Practice) for p in practices))

        # Check practice IDs are unique and sequential
        practice_ids = [p.practice_id for p in practices]
        self.assertEqual(practice_ids, [1, 2, 3, 4, 5])

        # Test invalid input
        with self.assertRaisesRegex(ValueError, "Number of practices must be positive"):
            self.factory.create_practices(number_of_practices=0)

    @patch('numpy.random.seed')
    def test_seed_setting(self, mock_seed):
        """Test that random seed is set correctly"""
        StandardPracticeFactory(seed=42)
        mock_seed.assert_called_with(42)


if __name__ == '__main__':
    unittest.main()