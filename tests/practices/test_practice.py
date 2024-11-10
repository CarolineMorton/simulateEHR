import unittest
from src.practices.practice import Practice, RegistrationDates, TransferParameters, BirthYearParameters


class TestPractice(unittest.TestCase):
    """Tests for the Practice class"""

    def setUp(self):
        """Set up a fresh config before each test"""
        self.config = {
            "practice_id": 1,
            "patient_count": 1000,
            "male_proportion": 0.4,
            "registration_dates": RegistrationDates(
                latest_registration=1,
                earliest_registration=0,
                median_registration=0.5,
            ),
            "transfer_params": TransferParameters(
                transfer_probability=0.5,
                minimum_gap=0,
                median_gap=1,
                maximum_gap=2,
            ),
            "birth_years": BirthYearParameters(
                earliest_birth_year=1900,
                median_birth_year=1950,
                latest_birth_year=2000,
            ),
            "ethnicity_proportions": {
                "white": 0.75,
                "south_asian": 0.15,
                "black": 0.05,
                "other": 0.03,
                "mixed": 0.01,
                "unknown": 0.01
            }
        }

    def test_valid_practice(self):
        """Test that a valid practice can be created"""
        practice = Practice(**self.config)

        self.assertEqual(practice.practice_id, 1)
        self.assertEqual(practice.patient_count, 1000)

    def test_invalid_practice_id(self):
        """Test that invalid practice ID raises appropriate error"""
        self.config["practice_id"] = -1

        with self.assertRaisesRegex(ValueError, "Practice ID must be a positive integer"):
            Practice(**self.config)

    def test_invalid_practice_size(self):
        """Test that invalid patient count raises appropriate error"""
        self.config["patient_count"] = -1

        with self.assertRaisesRegex(ValueError, "Patient count must be a positive integer"):
            Practice(**self.config)

    def test_invalid_male_proportion(self):
        """Test that invalid male proportions raise appropriate errors"""
        # Test proportion > 1
        self.config["male_proportion"] = 1.5
        with self.assertRaisesRegex(ValueError, "Male proportion must be between 0 and 1"):
            Practice(**self.config)

        # Test proportion < 0
        self.config["male_proportion"] = -0.1
        with self.assertRaisesRegex(ValueError, "Male proportion must be between 0 and 1"):
            Practice(**self.config)

    def test_invalid_ethnicity_proportions_sum(self):
        """Test that ethnicity proportions must be valid i.e. add up 1"""
        # Test that proportions must add up to 1
        self.config["ethnicity_proportions"] = {
            "white": 0.5,
            "south_asian": 0.15,
            "black": 0.05,
            "other": 0.03,
            "mixed": 0.01,
            "unknown": 0.02
        }
        with self.assertRaisesRegex(ValueError, "Ethnicity proportions must sum to 1"):
            Practice(**self.config)

    def test_invalid_ethnicity_proportions_individual_valid(self):

        # Test that proportions must be between 0 and 1
        self.config["ethnicity_proportions"] = {
            "white": 1.5,
            "south_asian": 0.15,
            "black": 0.05,
            "other": 0.03,
            "mixed": 0.01,
            "unknown": 0.02
        }
        with self.assertRaisesRegex(ValueError, "Ethnicity proportions must be between 0 and 1"):
            Practice(**self.config)


    def test_ethnicity_keys_present(self):
        self.config["ethnicity_proportions"] = {
            "south_asian": 0.2,
            "black": 0.2,
            "other": 0.2,
            "mixed": 0.2,
            "unknown": 0.2
        }

        with self.assertRaisesRegex(ValueError,
                                    r"Ethnicity proportions must contain exactly these keys: \['black', 'mixed', 'other', 'south_asian', 'unknown', 'white'\]"):
            Practice(**self.config)

if __name__ == '__main__':
    unittest.main()