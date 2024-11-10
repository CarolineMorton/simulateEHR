"""
This file contains the code for the Patient Object
"""

# External imports
from typing import Optional
from dataclasses import dataclass

# Internal Imports
from src.patients.patient_enums import Sex, Ethnicity


@dataclass
class Patient:
    """
    Individual patient with all their information.

    All dates are stored as days since reference date (1960-01-01).
    """
    patient_id: int
    practice_id: int
    birth_date: int
    registration_date: int
    sex: Sex
    ethnicity: Ethnicity
    transfer_date: Optional[int] = None
    death_date: Optional[int] = None

    def __post_init__(self):
        """Validate patient data"""
        # Valid dates
        if self.birth_date >= self.registration_date:
            raise ValueError("Birth date must be before registration date")

        if self.transfer_date and self.transfer_date <= self.registration_date:
            raise ValueError("Transfer date must be after registration date")

        if self.death_date:
            if self.death_date <= self.birth_date:
                raise ValueError("Death date must be after birth date")
            if self.transfer_date and self.death_date <= self.transfer_date:
                raise ValueError("Death date must be before transfer date")

        # Type validation
        if not isinstance(self.sex, Sex):
            raise ValueError(f"Sex must be a Sex enum, got {type(self.sex)}")

        if not isinstance(self.ethnicity, Ethnicity):
            raise ValueError(f"Ethnicity must be an Ethnicity enum, got {type(self.ethnicity)}")

