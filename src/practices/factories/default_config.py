
import numpy as np

from src.practices.factories.config import PracticeConfig, DemographicConfig, EthnicityConfig, RegistrationConfig


def get_default_config() -> PracticeConfig:
    """
    Get default configuration if a config_path is not provided.

    Returns:
        PracticeConfig object containing all necessary parameters
        This is made up of:
            - Ethnicity Config
            - Demographic Config
            - Registration Config
    """
    return PracticeConfig(
        ethnicity=EthnicityConfig(
            correlation_matrix=np.array([
                [1, 0.78, 0.70, 0.73, 0.09],
                [0.78, 1, 0.71, 0.74, 0.04],
                [0.70, 0.71, 1, 0.60, 0.04],
                [0.73, 0.74, 0.60, 1, 0.009],
                [0.09, 0.04, 0.04, 0.009, 1]
            ]),
            means=np.array([-5.3, -5.6, -5.7, -6.3, -5.2]),
            standard_deviations=np.array([1.7, 1.7, 1.3, 1.1, 1.7]),
            ethnicity_names=['south_asian', 'black', 'other', 'mixed', 'unknown']
        ),
        demographics=DemographicConfig(
            male_proportion_mean=0.4,
            male_proportion_sd=0.05,
            min_yob_mean=1910,
            min_yob_sd=5,
            med_yob_mean=1943,
            med_yob_sd=5,
            max_yob_mean=1980,
            max_yob_sd=5
        ),
        registration=RegistrationConfig(
            last_registration_date=20926,
            min_registration_offset=-4890,
            min_registration_sd=5000,
            med_registration_offset=11000,
            med_registration_sd=2400,
            transfer_probability_mean=0.2,
            transfer_probability_sd=0.075,
            min_transfer_gap=400,
            min_transfer_gap_sd=20,
            med_transfer_gap_mean=7000,
            med_transfer_gap_sd=2000,
            max_transfer_gap_mean=22400,
            max_transfer_gap_sd=8000
        ),
        practice_size_df1=30,
        practice_size_df2=20,
        practice_size_multiplier=1000
    )
