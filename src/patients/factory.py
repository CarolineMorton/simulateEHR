"""
This file contains the code for the PatientFactory object
"""

# External imports
from typing import Optional, List
import numpy as np
from scipy import stats
import polars as pl

# Internal Imports
from src.practices.practice import Practice
from src.patients.patient import Patient
from src.patients.patient_enums import Sex, Ethnicity


class PatientFactory:
    """
    Factory for creating patients within a specific practice.
    Each practice gets their own patient factory initialisd
    with the practice's parameters.
    """
    def __init__(self, practice: Practice):
        self.practice = practice

    def create_patient(self, index: int) -> Patient:
        """
        Creates a single patient using the practice's parameters.
        """
        patient_id = self._generate_patient_id(index)
        sex = self._generate_sex()
        ethnicity = self._generate_ethnicity()
        birth_date = self._generate_birth_date()
        registration_date = self._generate_registration_date(birth_date)
        transfer_date = self._generate_transfer_date(birth_date, registration_date)
        death_date = self._generate_death_date(birth_date, transfer_date)

        return Patient(
            patient_id=patient_id,
            practice_id=self.practice.practice_id,
            birth_date=birth_date,
            registration_date=registration_date,
            sex=sex,
            ethnicity=ethnicity,
            transfer_date=transfer_date,
            death_date=death_date
        )




    def _generate_patient_id(self, index: int) -> int:
        """
        Generate unique patient ID.

        Combines:
        1. Sequential number within practice (index + 1)
        2. Practice ID padded to 3 digits

        Example:
        - index=0, practice_id=1 -> patient_id=1001
        - index=1, practice_id=1 -> patient_id=2001
        - index=0, practice_id=12 -> patient_id=1012

        Args:
            index: Sequential number for patient within practice (0-based)

        Returns:
            int: Unique patient ID

        Note: That we are not using random sorting because we are generating
        one patient at a time. We are using the index to generate the patient ID.
        """
        # Add 1 to index to match Stata's 1-based indexing
        sequential_num = index + 1

        # Combine sequential number with zero-padded practice ID
        patient_id_str = f"{sequential_num}{self.practice.practice_id:03d}"

        return int(patient_id_str)

    def _generate_sex(self) -> Sex:
        """
        Generate patient sex based on practice male proportion
        """
        return Sex.MALE if np.random.random() < self.practice.male_proportion else Sex.FEMALE


    def _generate_ethnicity(self) -> Ethnicity:
        """
        Generate patient ethnicity based on practice proportions.
        Uses same logic as Stata:
        1. Generate random uniform number
        2. Assign ethnicity based on cumulative probabilities

        Unlike the original stata code, we are not adding in missing values
        here, but will use an adaptor pattern to add in missing values at the
        end of the process.
        """
        props = self.practice.ethnicity_proportions
        u = np.random.random()

        # Follow same logic as Stata for consistent results
        if u < props['unknown']:
            return Ethnicity.UNKNOWN

        # Adjust probabilities excluding unknown
        effective_total = 1 - props['unknown']
        u = np.random.random()  # New random number for main assignment

        cumsum = 0
        for eth_name, prop in props.items():
            if eth_name != 'unknown':
                cumsum += prop / effective_total
                if u < cumsum:
                    return Ethnicity[eth_name.upper()]

        # Shouldn't reach here but return white as default
        return Ethnicity.WHITE

    def _generate_birth_date(self) -> int:
        """
        Generate birthdate for a patient.

        Uses practice birth year parameters to:
        1. Generate year using beta distribution between practice's earliest and latest years
        2. Generate random day within that year

        Birth years have a beta distribution skewed towards median year:
        - More patients born near median year
        - Fewer patients at the extremes (earliest/latest years)

        Returns:
            int: Birth date in days since reference date (1960-01-01)
        """
        birth_years = self.practice.birth_years

        # Generate year using beta distribution (same as Stata)
        # Beta(2, 0.5) creates right-skewed distribution
        year = (
                birth_years.earliest_birth_year +
                stats.beta.rvs(2, 0.5) *
                (birth_years.latest_birth_year - birth_years.earliest_birth_year)
        )

        # Generate random day within year
        # This matches Stata's uniform()*365.25 approach
        days_in_year = 365.25  # Account for leap years on average
        day_of_year = np.random.uniform(0, days_in_year)

        # Convert to days since reference date (1960-01-01)
        years_since_reference = year - 1960
        days_since_reference = int(years_since_reference * 365.25 + day_of_year)

        return days_since_reference


    def _generate_registration_date(self, birth_date: int) -> int:
        """
        Generate registration date for a patient.

        Registration date must be:
        1. After patient's birth date
        2. Within practice's registration period
        3. If registration would be before birth date, adjust to be shortly after birth (first 5 years)

        Args:
            birth_date: Patient's birth date in days since reference

        Returns:
            int: Registration date in days since reference
        """
        reg_dates = self.practice.registration_dates

        # Generate initial registration date between practice bounds
        registration_date = np.random.uniform(
            max(0, reg_dates.earliest_registration),
            reg_dates.latest_registration
        )

        # If registration would be before birth, adjust to be 0-5 years after birth
        if birth_date >= registration_date:
            max_years_after_birth = 5
            days_after_birth = np.random.uniform(0, max_years_after_birth * 365.25)
            registration_date = birth_date + days_after_birth

        return int(round(registration_date))

    def _generate_transfer_date(
            self,
            birth_date: int,
            registration_date: int
    ) -> Optional[int]:
        """
        Generate transfer out date for a patient.

        Following Stata logic:
        1. Transfer happens with probability from practice params
        2. Gap between registration and transfer follows practice params
        3. Various exclusion criteria applied:
           - Must be after 1991
           - Must be after patient turns 18
           - Must be before study end (April 2017) #TODO: Get this from a study config

        Args:
            birth_date: Birth date in days since reference
            registration_date: Registration date in days since reference

        Returns:
            Optional[int]: Transfer date in days since reference, or None if no transfer
        """
        transfer_params = self.practice.transfer_params

        # Determine if patient transfers out
        if np.random.random() < transfer_params.transfer_probability:
            # Generate gap between registration and transfer
            gap = np.random.uniform(
                transfer_params.minimum_gap,
                transfer_params.maximum_gap
            )

            potential_transfer = registration_date + gap

            # Apply exclusion criteria
            study_end = self.practice.registration_dates.latest_registration
            min_transfer_date = max(
                11323,  # After 1991
                birth_date + (18 * 365.25) + 7 + np.random.uniform(0, 60)  # After 18 years old
            )

            # Only set transfer date if it meets all criteria
            if (potential_transfer <= study_end and
                    potential_transfer > min_transfer_date):
                return int(round(potential_transfer))

        return None

    def _generate_death_date(
            self,
            birth_date: int,
            transfer_date: Optional[int]
    ) -> Optional[int]:
        """
        Generate death date for a patient.

        Following Stata logic:
        1. Death occurs at 105 years after birth
        2. Unless beyond study end date
        3. Or patient transfers out before death

        Args:
            birth_date: Birth date in days since reference
            transfer_date: Transfer out date in days since reference (if any)

        Returns:
            Optional[int]: Death date in days since reference, or None if no death
        """
        # Calculate potential death date (105 years after birth)
        potential_death = birth_date + int(105 * 365.25)

        # Check if death would be before study end and before transfer (if any)
        if (potential_death <= self.practice.registration_dates.latest_registration and
                (transfer_date is None or potential_death <= transfer_date)):
            return potential_death

        return None

    def create_patients(self) -> List[Patient]:
        """
        Create all patients for this practice and perform final data cleaning.

        Ensures:
        1. All dates are rounded consistently
        2. Patient IDs are unique
        3. Data is properly structured

        Returns:
            List[Patient]: List of validated patients
        """
        # Create patients
        patients = [
            self.create_patient(index)
            for index in range(self.practice.patient_count)
        ]

        # Validate unique IDs
        patient_ids = [p.patient_id for p in patients]
        if len(set(patient_ids)) != len(patient_ids):
            raise ValueError("Duplicate patient IDs found")

        # Sort by patient ID
        patients.sort(key=lambda x: x.patient_id)

        return patients

    @staticmethod
    def save_patients(patients: List[Patient], output_path: str = "patients.parquet"):
        """
        Save patients to file in standardized format.

        Args:
            patients: List of patients to save
            output_path: Path to save file
        """
        # Convert to polars DataFrame with columns in specific order
        data = [{
            'patid': p.patient_id,
            'pracid': p.practice_id,
            'dob_hidden': p.birth_date,
            'sex': str(p.sex),
            'eth5': str(p.ethnicity),
            'crd': p.registration_date,
            'tod': p.transfer_date if p.transfer_date else None,
            'deathdate': p.death_date if p.death_date else None,
        } for p in patients]

        # Create DataFrame from the generated data
        df = pl.DataFrame(data)

        # Save to csv format
        df.write_csv("test.csv")

        # Save to parquet format
        # df.write_parquet(output_path)

