import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
@dataclass
class EthnicityConfig:
    """Configuration for ethnicity parameters"""
    correlation_matrix: np.ndarray
    means: np.ndarray
    standard_deviations: np.ndarray
    ethnicity_names: List[str]

@dataclass
class DemographicConfig:
    """Configuration for demographic parameters"""
    male_proportion_mean: float
    male_proportion_sd: float
    min_yob_mean: float
    min_yob_sd: float
    med_yob_mean: float
    med_yob_sd: float
    max_yob_mean: float
    max_yob_sd: float

@dataclass
class RegistrationConfig:
    """Configuration for registration dates and transfer parameters"""
    last_registration_date: int  # in days since reference date
    min_registration_offset: float
    min_registration_sd: float
    med_registration_offset: float
    med_registration_sd: float
    transfer_probability_mean: float
    transfer_probability_sd: float
    min_transfer_gap: float
    min_transfer_gap_sd: float
    med_transfer_gap_mean: float
    med_transfer_gap_sd: float
    max_transfer_gap_mean: float
    max_transfer_gap_sd: float

@dataclass
class PracticeConfig:
    """Complete configuration for practice generation"""
    ethnicity: EthnicityConfig
    demographics: DemographicConfig
    registration: RegistrationConfig
    practice_size_df1: int  # degrees of freedom for first chi-square
    practice_size_df2: int  # degrees of freedom for second chi-square
    practice_size_multiplier: float