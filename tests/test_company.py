"""
Unit tests for the company management module.
"""

import os
import unittest
import tempfile
from pathlib import Path

from facatura.core.db import Database
from facatura.core.company import (
    CompanyManager,
    CompanyError,
    CompanyNotFoundError,
    CompanyValidationError
)


class TestCompanyManager(unittest.TestCase):
    """Test case for the CompanyManager class."""

    def setUp(self):
        """Set up the test case."""
        # Create a temporary database file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        
        # Initialize the database
        self.db = Database(self.db_path)
        self.db.connect()
        self.db.initialize_schema()
        
        # Create a company manager
        self.company_manager = CompanyManager(self.db)
        
        # Sample valid company data
        self.valid_company_data = {
            "name": "Test Company SRL",
            "registration_number": "RO12345678",
            "vat_number": "RO12345678",
            "address": "123 Test Street",
            "city": "Bucharest",
            "county": "Bucharest",
            "postal_code": "123456",
            "country": "Romania",
            "bank_name": "Test Bank",
            "bank_account": "RO49AAAA1B31007593840000",
            "email": "contact@testcompany.ro",
            "phone": "+40 123 456 789",
            "website": "https://testcompany.ro",
            "notes": "This is a test company"
        }

    def tearDown(self):
        """Tear down the test case."""
        self.db.close()
        self.temp_dir.cleanup()

    def test_create_company(self):
        """Test creating a company."""
        # Create a company
        company_id = self.company_manager.create_company(self.valid_company_data)
        
        # Check that the company was created
        self.assertIsNotNone(company_id)
        self.assertGreater(company_id, 0)
        
        # Retrieve the company and check its data
        company = self.company_manager.get_company(company_id)
        self.assertEqual(company["name"], self.valid_company_data["name"])
        self.assertEqual(company["registration_number"], self.valid_company_data["registration_number"])

    def test_create_company_validation_error(self):
        """Test creating a company with invalid data."""
        # Missing required fields
        invalid_data = {
            "name": "Test Company"
            # Missing other required fields
        }
        
        with self.assertRaises(CompanyValidationError):
            self.company_manager.create_company(invalid_data)
        
        # Invalid registration number
        invalid_data = self.valid_company_data.copy()
        invalid_data["registration_number"] = "invalid"
        
        with self.assertRaises(CompanyValidationError):
            self.company_manager.create_company(invalid_data)
        
        # Invalid email
        invalid_data = self.valid_company_data.copy()
        invalid_data["email"] = "invalid-email"
        
        with self.assertRaises(CompanyValidationError):
            self.company_manager.create_company(invalid_data)

    def test_get_company(self):
        """Test retrieving a company."""
        # Create a company
        company_id = self.company_manager.create_company(self.valid_company_data)
        
        # Retrieve the company
        company = self.company_manager.get_company(company_id)
        
        # Check the company data
        self.assertEqual(company["id"], company_id)
        self.assertEqual(company["name"], self.valid_company_data["name"])
        self.assertEqual(company["registration_number"], self.valid_company_data["registration_number"])
        
        # Try to retrieve a non-existent company
        with self.assertRaises(CompanyNotFoundError):
            self.company_manager.get_company(9999)

    def test_get_company_by_registration_number(self):
        """Test retrieving a company by registration number."""
        # Create a company
        self.company_manager.create_company(self.valid_company_data)
        
        # Retrieve the company by registration number
        company = self.company_manager.get_company_by_registration_number(
            self.valid_company_data["registration_number"]
        )
        
        # Check the company data
        self.assertEqual(company["name"], self.valid_company_data["name"])
        self.assertEqual(company["registration_number"], self.valid_company_data["registration_number"])
        
        # Try to retrieve a non-existent company
        with self.assertRaises(CompanyNotFoundError):
            self.company_manager.get_company_by_registration_number("RO99999999")

    def test_list_companies(self):
        """Test listing companies."""
        # Create some companies
        self.company_manager.create_company(self.valid_company_data)
        
        company2_data = self.valid_company_data.copy()
        company2_data["name"] = "Another Company SRL"
        company2_data["registration_number"] = "RO87654321"
        company2_data["email"] = "contact@anothercompany.ro"
        self.company_manager.create_company(company2_data)
        
        # List all companies
        companies = self.company_manager.list_companies()
        self.assertEqual(len(companies), 2)
        
        # List companies with filter
        companies = self.company_manager.list_companies({"name": "Another"})
        self.assertEqual(len(companies), 1)
        self.assertEqual(companies[0]["name"], "Another Company SRL")

    def test_update_company(self):
        """Test updating a company."""
        # Create a company
        company_id = self.company_manager.create_company(self.valid_company_data)
        
        # Update the company
        updated_data = {
            "name": "Updated Company SRL",
            "registration_number": self.valid_company_data["registration_number"],
            "address": "456 Updated Street",
            "city": "Cluj-Napoca",
            "county": "Cluj",
            "country": "Romania",
            "email": "updated@testcompany.ro"
        }
        
        self.company_manager.update_company(company_id, updated_data)
        
        # Retrieve the updated company
        company = self.company_manager.get_company(company_id)
        
        # Check the updated data
        self.assertEqual(company["name"], updated_data["name"])
        self.assertEqual(company["address"], updated_data["address"])
        self.assertEqual(company["city"], updated_data["city"])
        
        # Try to update a non-existent company
        with self.assertRaises(CompanyNotFoundError):
            self.company_manager.update_company(9999, updated_data)

    def test_delete_company(self):
        """Test deleting a company."""
        # Create a company
        company_id = self.company_manager.create_company(self.valid_company_data)
        
        # Delete the company
        self.company_manager.delete_company(company_id)
        
        # Try to retrieve the deleted company
        with self.assertRaises(CompanyNotFoundError):
            self.company_manager.get_company(company_id)
        
        # Try to delete a non-existent company
        with self.assertRaises(CompanyNotFoundError):
            self.company_manager.delete_company(9999)


if __name__ == "__main__":
    unittest.main()