"""This file contains the code for the Practice Objects"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class RegistrationDates:
    """
    Registration date information for a practice.

    All dates are stored as days since reference date (1960-01-01).
    """
    latest_registration: float
    earliest_registration: float
    median_registration: float

    def __post_init__(self):
        """
        This is a validator method that checks that the dates are valid.
        """
        if not self.earliest_registration <= self.median_registration <= self.latest_registration:
            raise ValueError(
                "Registration dates must be ordered: earliest <= median <= latest"
            )


@dataclass
class TransferParameters:
    """Parameters controlling patient transfer between practices"""
    transfer_probability: float
    minimum_gap: float
    median_gap: float
    maximum_gap: float

    def __post_init__(self):
        if not 0 <= self.transfer_probability <= 1:
            raise ValueError("Transfer probability must be between 0 and 1")
        if not self.minimum_gap <= self.median_gap <= self.maximum_gap:
            raise ValueError(
                "Transfer gaps must be ordered: minimum <= median <= maximum"
            )
        if self.minimum_gap < 0:
            raise ValueError("Transfer gaps cannot be negative")


@dataclass
class BirthYearParameters:
    """Birth year boundaries for the practice population"""
    earliest_birth_year: float  # Previously min_yob
    median_birth_year: float  # Previously med_yob
    latest_birth_year: float  # Previously max_yob

    def __post_init__(self):
        if not self.earliest_birth_year <= self.median_birth_year <= self.latest_birth_year:
            raise ValueError(
                "Birth years must be ordered: earliest <= median <= latest"
            )
        if not 1800 <= self.earliest_birth_year <= 2024:
            raise ValueError("Birth years must be realistic (between 1800 and 2024)")


@dataclass
class Practice:
    """
    A medical practice containing demographic and registration information.

    Attributes:
        practice_id: Unique identifier for the practice
        patient_count: Number of patients in the practice
        male_proportion: Proportion of male patients
        registration_dates: Dates controlling patient registration periods
        transfer_params: Parameters controlling patient transfers
        birth_years: Birth year parameters for the practice population
        ethnicity_proportions: Proportion of patients in each ethnic group
    """
    practice_id: int
    patient_count: int
    male_proportion: float
    registration_dates: RegistrationDates
    transfer_params: TransferParameters
    birth_years: BirthYearParameters
    ethnicity_proportions: Dict[str, float]

    def __post_init__(self):
        # Validate practice ID
        if self.practice_id <= 0:
            raise ValueError("Practice ID must be a positive integer")

        # Validate patient count
        if self.patient_count <= 0:
            raise ValueError("Patient count must be a positive integer")

        # Validate male proportion
        if not 0 <= self.male_proportion <= 1:
            raise ValueError("Male proportion must be between 0 and 1")

        # Validate ethnicity proportions
        if not all(0 <= prop <= 1 for prop in self.ethnicity_proportions.values()):
            raise ValueError("Ethnicity proportions must be between 0 and 1")
        if not int(sum(self.ethnicity_proportions.values())) == 1:
            raise ValueError("Ethnicity proportions must sum to 1")

        required_ethnicities = {'south_asian', 'black', 'other', 'mixed', 'unknown', 'white'}
        if set(self.ethnicity_proportions.keys()) != required_ethnicities:
            raise ValueError(
                f"Ethnicity proportions must contain exactly these keys: "
                f"{sorted(required_ethnicities)}"
            )
    @property
    def total_ethnicity_proportion(self) -> float:
        """Calculate total of ethnicity proportions (should be 1.0)"""
        return sum(self.ethnicity_proportions.values())

    @property
    def registration_period_days(self) -> float:
        """Calculate the total registration period in days"""
        return (self.registration_dates.latest_registration -
                self.registration_dates.earliest_registration)

    @property
    def birth_year_range(self) -> float:
        """Calculate the range of birth years"""
        return (self.birth_years.latest_birth_year -
                self.birth_years.earliest_birth_year)