import unittest
from datetime import datetime
import main
import pandas as p


class TestTransformations(unittest.TestCase):

    def test_FileName(self):
        filename = 'Privia Family Medicine 113018.xlsx'
        provider_name, file_date = main.name_logic(filename)
        self.assertEqual(provider_name, 'Privia Family Medicine')
        self.assertEqual(file_date, datetime(2018, 11, 30).date())

    def test_Demographics(self):
        fake_data = p.DataFrame()

        fake_data = fake_data.append([{'ID': 31, 'First Name': 'James', 'Middle Name': 'Stark', 'Last Name': 'Holden'
                                          , 'DOB[1]': datetime(1989, 02, 04, 11, 07, 00), 'Sex': 0,
                                       'Favorite Color': 'Red'
                                          , 'Attributed Q1': 'No', 'Attributed Q2': 'No', 'Risk Q1': 0.500000
                                          , 'Risk Q2 ': 0.6000000, 'Risk Increased Flag': 'Yes'}], ignore_index=True)

        demographics = main.demographics(fake_data)
        self.assertEqual(demographics['ID'][0], 31)
        self.assertEqual(demographics['Middle Name'][0], 'S')
        self.assertEqual(demographics['Sex'][0], 'M')

    def test_risk_quarters(self):
        fake_data = p.DataFrame()

        fake_data = fake_data.append([{'ID': 31, 'First Name': 'James', 'Middle Name': 'Stark', 'Last Name': 'Holden'
                                          , 'DOB[1]': datetime(1989, 02, 04, 11, 07, 00), 'Sex': 0,
                                       'Favorite Color': 'Red'
                                          , 'Attributed Q1': 'No', 'Attributed Q2': 'No', 'Risk Q1': 0.500000
                                          , 'Risk Q2 ': 0.6000000, 'Risk Increased Flag': 'Yes'}], ignore_index=True)

        merged = main.risk_quarters(fake_data)

        self.assertEqual(merged['ID'][0], 31)
        self.assertEqual(merged['Quarter'].count(), 2)
        self.assertGreaterEqual(merged['RiskScore'][0], 0.5)
        self.assertLessEqual(merged['RiskScore'][0], 0.6)

if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=2, exit=False)
