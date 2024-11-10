import unittest

from src.patients.factory import PatientFactory
from src.practices.factories.standard import StandardPracticeFactory



class TestPatientFactory(unittest.TestCase):
    def setup(self):
        pass

    def test_create_patients_for_one_practice(self):
        # Create a practice factory
        practice_factory = StandardPracticeFactory(seed=9147856)
        practice = practice_factory.create_practice(1)

        # Create a patient factory
        factory = PatientFactory(practice)

        # Create 5 patients
        patients = factory.create_patients()

        factory.save_patients(patients)



if __name__ == '__main__':
    unittest.main()