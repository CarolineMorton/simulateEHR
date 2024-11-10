"""This file contains the Factory that creates the practices"""

# External imports
from typing import List, Dict
import numpy as np
import scipy.stats as stats

# Internal Imports
from src.practices.practice import Practice, RegistrationDates, TransferParameters, BirthYearParameters
from src.practices.factories.config import PracticeConfig
from src.practices.factories.base import PracticeFactoryBase
from src.practices.factories.default_config import get_default_config



class StandardPracticeFactory(PracticeFactoryBase):
    """
    Practice for implementing a standard practice.
    """
    def __init__(self, seed: int = 9147856, config_path: str = None):
        # Set a seed to allow repeated "randomness"
        np.random.seed(seed)

        # Set the config
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str = None) -> PracticeConfig:
        """
        Load configuration from file or use defaults.

        Args:
            config_path: Path to configuration file

        Returns:
            PracticeConfig object containing all necessary parameters
        """
        if config_path is None:
            return get_default_config()
        else:
            # Here you would implement config file parsing
            raise NotImplementedError("Config file parsing not implemented")

    def _generate_ethnicity_proportions(self) -> Dict[str, float]:
        """
        Generate correlated ethnicity proportions for a practice.

        Returns proportions for each ethnicity:
        - south_asian
        - black
        - other
        - mixed
        - unknown
        - white (calculated as remainder)

        Note: White is calculated as the remainder after other ethnicities
        (excluding unknown), matching the original Stata methodology where:
        P(South Asian) = south_asian/(1-unknown)
        P(Black | not SA) = black/((1-south_asian)*(1-unknown))
        P(Mixed | not SA, not Black) = mixed/((1-black)*(1-south_asian)*(1-unknown))
        P(Other | not SA, not Black, not Mixed) = other/((1-mixed)*(1-black)*(1-south_asian)*(1-unknown))
        P(White) = remainder
        """
        config = self.config.ethnicity

        # Create covariance matrix from standard deviations and correlations
        covariance_matrix = np.outer(
            config.standard_deviations,
            config.standard_deviations
        ) * config.correlation_matrix

        # Generate correlated normal variables
        normal_variates = np.random.multivariate_normal(
            mean=config.means,
            cov=covariance_matrix
        )

        # Convert to raw probabilities
        ethnicity_names = ['south_asian', 'black', 'other', 'mixed', 'unknown']
        raw_probs = {
            name: self.logistic(value)
            for name, value in zip(ethnicity_names, normal_variates)
        }

        # Calculate conditional probabilities
        unknown = raw_probs['unknown']
        effective_total = 1 - unknown  # Total excluding unknown

        # Calculate final proportions following Stata logic
        final_probs = {}
        final_probs['unknown'] = unknown
        final_probs['south_asian'] = raw_probs['south_asian'] / effective_total
        final_probs['black'] = (
                raw_probs['black'] /
                ((1 - raw_probs['south_asian']) * effective_total)
        )
        final_probs['mixed'] = (
                raw_probs['mixed'] /
                ((1 - raw_probs['black']) * (1 - raw_probs['south_asian']) * effective_total)
        )
        final_probs['other'] = (
                raw_probs['other'] /
                ((1 - raw_probs['mixed']) * (1 - raw_probs['black']) *
                 (1 - raw_probs['south_asian']) * effective_total)
        )

        # White is the remainder (excluding unknown)
        final_probs['white'] = (
                                       1 - final_probs['south_asian'] - final_probs['black'] -
                                       final_probs['mixed'] - final_probs['other']
                               ) * (1 - unknown)

        return final_probs

    @staticmethod
    def logistic(x: float) -> float:
        """
        Convert a number to a probability using the logistic function

        Args:
            x (float): Number to convert

        Returns:
            float: Probability between 0 and 1
        """
        return 1 / (1 + np.exp(-x))

    def create_practice(self, practice_id: int) -> Practice:
        """
        Create a single practice with a specific practice id.

        Args:
            practice_id (int): The practice id

        Returns:
            Practice: Practice object
        """
        practice_size = self._generate_practice_size()
        registration_dates = self._generate_registration_dates()
        ethnicity_props = self._generate_ethnicity_proportions()
        male_prop = self._generate_demographics()
        transfer_params = self._generate_transfer_parameters()
        birth_years = self._generate_birth_years()

        practice = Practice(
            practice_id=practice_id,
            patient_count=practice_size,
            male_proportion=male_prop,
            registration_dates=registration_dates,
            transfer_params=transfer_params,
            birth_years=birth_years,
            ethnicity_proportions=ethnicity_props
        )
        return practice

    def _generate_transfer_parameters(self) -> TransferParameters:
        """
        Generate parameters controlling patient transfers between practices.

        Generates:
        1. Transfer probability (typically around 0.2 or 20%)
        2. Gaps between registration and transfer (min, median, max)

        The transfer gaps are constrained to ensure:
        - min_gap < med_gap < max_gap
        - All gaps are non-negative
        - Realistic ranges (e.g., median around 7000 days)

        Returns:
            TransferParameters: Object containing transfer probability and gaps

        Raises:
            ValueError: If configuration parameters are invalid:
                - probabilities not between 0 and 1
                - standard deviations not positive
                - gaps not properly ordered
                - negative gap values
        """
        config = self.config.registration

        # Validate configuration
        if not 0 <= config.transfer_probability_mean <= 1:
            raise ValueError(
                f"Transfer probability mean must be between 0 and 1, "
                f"got {config.transfer_probability_mean}"
            )

        if config.transfer_probability_sd <= 0:
            raise ValueError(
                f"Transfer probability standard deviation must be positive, "
                f"got {config.transfer_probability_sd}"
            )

        if any(sd <= 0 for sd in [
            config.min_transfer_gap_sd,
            config.med_transfer_gap_sd,
            config.max_transfer_gap_sd
        ]):
            raise ValueError("All transfer gap standard deviations must be positive")

        if not (config.min_transfer_gap < config.med_transfer_gap_mean < config.max_transfer_gap_mean):
            raise ValueError("Transfer gap means must be properly ordered")

        # Generate transfer probability
        transfer_probability = np.clip(
            np.random.normal(
                loc=config.transfer_probability_mean,
                scale=config.transfer_probability_sd
            ),
            a_min=0,
            a_max=1
        )

        # Generate transfer gaps
        minimum_gap = np.clip(
            config.min_transfer_gap +
            np.round(
                np.random.normal(0, config.min_transfer_gap_sd),
                decimals=1
            ),
            a_min=0,
            a_max=None
        )

        median_gap = np.clip(
            np.random.normal(
                loc=config.med_transfer_gap_mean,
                scale=config.med_transfer_gap_sd
            ),
            a_min=minimum_gap + 100,  # Ensure gap between min and median
            a_max=None
        )

        maximum_gap = np.clip(
            np.random.normal(
                loc=config.max_transfer_gap_mean,
                scale=config.max_transfer_gap_sd
            ),
            a_min=median_gap + 100,  # Ensure gap between median and max
            a_max=None
        )

        return TransferParameters(
            transfer_probability=transfer_probability,
            minimum_gap=minimum_gap,
            median_gap=median_gap,
            maximum_gap=maximum_gap
        )

    def _generate_practice_size(self) -> int:
        """
        Generate practice size using ratio of chi-square distributions.

        The size is calculated using:
        1. Generate two chi-square random variables with different degrees of freedom
        2. Normalize each by their degrees of freedom (from config)
        3. Take their ratio and multiply by base size (typically 1000)

        This method creates a realistic, skewed distribution of practice sizes
        that matches observed patterns in medical practices.

        Returns:
            int: Number of patients in the practice

        Raises:
            ValueError: If configuration parameters are invalid:
                - degrees of freedom not positive
                - practice size multiplier not positive
        """
        # Validate configuration
        if self.config.practice_size_df1 <= 0 or self.config.practice_size_df2 <= 0:
            raise ValueError(
                f"Degrees of freedom must be positive. Got df1={self.config.practice_size_df1}, "
                f"df2={self.config.practice_size_df2}"
            )

        if self.config.practice_size_multiplier <= 0:
            raise ValueError(
                f"Practice size multiplier must be positive, "
                f"got {self.config.practice_size_multiplier}"
            )

        # Generate chi-square variables and calculate patient count
        n1 = stats.chi2.rvs(df=self.config.practice_size_df1)
        n2 = stats.chi2.rvs(df=self.config.practice_size_df2)

        n_patients = round(
            self.config.practice_size_multiplier *  # Base size (1000)
            (n1 / self.config.practice_size_df1) /  # Normalized first chi-square
            (n2 / self.config.practice_size_df2)  # Normalized second chi-square
        )

        return n_patients

    def _generate_registration_dates(self) -> RegistrationDates:
        """
        Generate registration dates for a practice.

        Generates a set of registration dates with:
        - Latest: Study end date minus exponential offset
        - Earliest: Normal distribution around baseline
        - Median: Normal distribution between earliest and latest

        The dates are constrained to ensure:
        - earliest < median < latest
        - All dates are within study period

        Returns:
            RegistrationDates: Object containing earliest, median, and latest
                              registration dates

        Raises:
            ValueError: If configuration parameters are invalid:
                - registration offsets negative
                - standard deviations not positive
                - dates not properly ordered
        """
        reg_config = self.config.registration

        if any(sd <= 0 for sd in [
            reg_config.min_registration_sd,
            reg_config.med_registration_sd
        ]):
            raise ValueError("All registration date standard deviations must be positive")

        # Generate registration dates
        # Latest registration is study end date minus exponential offset. The expontential offset
        # means that more practices have recent registration dates, some practices will have much earlier
        # dates, and no practices will have registration dates after the study end date. Study date
        # is set by the latest registration date in the config. In the default config this is 20926 days,
        # corresponding to 2017-04-17. The exponential distribution with mean 1500 days (~4 years) creates
        # realistic variation in registration end dates across practices.
        latest_registration = (
                reg_config.last_registration_date -
                np.random.exponential(scale=1500)  # Offset in days, mean=1500
        )

        # Generate earliest registration date using normal distribution
        # The normal distribution creates variation around a baseline offset from the reference date.
        # In default config:
        # - min_registration_offset is -4890 days (~1947 from 1960 reference)
        # - min_registration_sd is 5000 days (~14 years) for realistic practice-to-practice variation
        earliest_registration = np.random.normal(
            loc=reg_config.min_registration_offset,
            scale=reg_config.min_registration_sd
        )

        # Generate median registration date using normal distribution, but constrained
        # to be between earliest and latest dates (with 100-day gaps).
        # In default config:
        # - med_registration_offset is 11000 days (~1990 from 1960 reference)
        # - med_registration_sd is 2400 days (~6.5 years) for variation
        # The np.clip ensures:
        # 1. median date is at least 100 days after earliest date
        # 2. median date is at least 100 days before latest date
        # This creates a reasonable timeline spread for each practice
        median_registration = np.clip(
            np.random.normal(
                loc=reg_config.med_registration_offset,
                scale=reg_config.med_registration_sd
            ),
            a_min=earliest_registration + 100,  # Ensure gap between earliest and median
            a_max=latest_registration - 100  # Ensure gap between median and latest
        )

        return RegistrationDates(
            latest_registration=latest_registration,
            earliest_registration=earliest_registration,
            median_registration=median_registration
        )

    def _generate_demographics(self) -> float:
        """
        Generate demographic parameters for a practice.

        This generates the proportion of male patients in the practice using
        a normal distribution. The proportion is clipped to be between 0 and 1.

        Mean and standard deviation come from configuration:
        - mean typically around 0.4 (40% male)
        - sd typically around 0.05

        Returns:
            float: Proportion of male patients

        Raises:
            ValueError: If configuration parameters are invalid:
                - mean not between 0 and 1
                - standard deviation not positive
        """
        demo_config = self.config.demographics

        # Validate configuration
        if not 0 <= demo_config.male_proportion_mean <= 1:
            raise ValueError(
                f"Male proportion mean must be between 0 and 1, "
                f"got {demo_config.male_proportion_mean}"
            )

        if demo_config.male_proportion_sd <= 0:
            raise ValueError(
                f"Male proportion standard deviation must be positive, "
                f"got {demo_config.male_proportion_sd}"
            )

        male_proportion = np.clip(
            np.random.normal(
                loc=demo_config.male_proportion_mean,
                scale=demo_config.male_proportion_sd
            ),
            a_min=0,
            a_max=1
        )

        return male_proportion

    def _generate_birth_years(self) -> BirthYearParameters:
        """
        Generate birth year parameters for a practice population.

        Generates earliest, median, and latest birth years using normal distributions.
        Typical values:
        - earliest: around 1910 (sd=5)
        - median: around 1943 (sd=5)
        - latest: around 1980 (sd=5)

        Birth years are constrained to ensure:
        - earliest < median < latest
        - Years are within realistic ranges
        - Appropriate gaps between values

        Returns:
            BirthYearParameters: Object containing earliest, median, and latest birth years

        Raises:
            ValueError: If configuration parameters are invalid:
                - standard deviations not positive
                - means not in chronological order
                - years outside realistic range
        """
        config = self.config.demographics

        # Validate configuration
        if any(sd <= 0 for sd in [
            config.min_yob_sd,
            config.med_yob_sd,
            config.max_yob_sd
        ]):
            raise ValueError("All birth year standard deviations must be positive")

        if not (config.min_yob_mean < config.med_yob_mean < config.max_yob_mean):
            raise ValueError(
                f"Birth year means must be in chronological order. Got: "
                f"min={config.min_yob_mean}, "
                f"med={config.med_yob_mean}, "
                f"max={config.max_yob_mean}"
            )

        # Check for realistic range (adjustable based on study requirements)
        if not (1800 <= config.min_yob_mean <= 2024):
            raise ValueError(
                f"Earliest birth year mean must be realistic (1800-2024), "
                f"got {config.min_yob_mean}"
            )

        # Generate birth years
        earliest_birth_year = np.random.normal(
            loc=config.min_yob_mean,
            scale=config.min_yob_sd
        )

        median_birth_year = np.clip(
            np.random.normal(
                loc=config.med_yob_mean,
                scale=config.med_yob_sd
            ),
            a_min=earliest_birth_year + 5,  # Ensure gap between earliest and median
            a_max=None
        )

        latest_birth_year = np.clip(
            np.random.normal(
                loc=config.max_yob_mean,
                scale=config.max_yob_sd
            ),
            a_min=median_birth_year + 5,  # Ensure gap between median and latest
            a_max=None
        )

        # Round to avoid fractional years
        return BirthYearParameters(
            earliest_birth_year=round(earliest_birth_year, 1),
            median_birth_year=round(median_birth_year, 1),
            latest_birth_year=round(latest_birth_year, 1)
        )

    def create_practices(self, number_of_practices: int = 800) -> List[Practice]:
        """
        Create multiple practices with sequential practice IDs.

        This method creates a list of practices by calling create_practice
        for each practice ID from 1 to number_of_practices.

        Args:
            number_of_practices (int): Number of practices to create,
                                     defaults to 800 as per original data

        Returns:
            List[Practice]: List of created Practice objects with unique IDs

        Raises:
            ValueError: If number_of_practices is not positive
        """
        # Validate input
        if number_of_practices <= 0:
            raise ValueError(
                f"Number of practices must be positive, "
                f"got {number_of_practices}"
            )

        # Create list of practices with sequential IDs
        practices = [
            self.create_practice(practice_id=i + 1)
            for i in range(number_of_practices)
        ]

        return practices
