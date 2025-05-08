"""
Tests for the Company class.
"""

import os
import tempfile
import sqlite3
import pytest
from facatura.db.setup_db import setup_database
from facatura.core.company import Company


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    # Set up the database
    setup_database(temp_db_path)
    
    yield temp_db_path
    
    # Clean up the temporary database file
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


@pytest.fixture
def company(temp_db):
    """Create a Company instance for testing."""
    return Company(temp_db)


def test_create_company(company):
    """Test creating a company."""
    # Create a company
    company_id = company.create(
        'Test Company',
        '123 Test St',
        'Test City',
        'J12/345/2021',
        'RO12345678',
        county='Test County',
        postal_code='123456',
        country='Romania',
        vat_payer=True,
        phone='0123456789',
        email='test@example.com',
        website='www.example.com',
        logo_path='/path/to/logo.png'
    )
    assert company_id > 0


def test_get_company(company):
    """Test getting a company."""
    # Create a company
    company_id = company.create(
        'Test Company',
        '123 Test St',
        'Test City',
        'J12/345/2021',
        'RO12345678'
    )
    
    # Get the company
    company_data = company.get(company_id)
    assert company_data is not None
    assert company_data['name'] == 'Test Company'
    assert company_data['address'] == '123 Test St'
    assert company_data['city'] == 'Test City'
    assert company_data['registration_number'] == 'J12/345/2021'
    assert company_data['fiscal_code'] == 'RO12345678'


def test_get_by_fiscal_code(company):
    """Test getting a company by fiscal code."""
    # Create a company
    company.create(
        'Test Company',
        '123 Test St',
        'Test City',
        'J12/345/2021',
        'RO12345678'
    )
    
    # Get the company by fiscal code
    company_data = company.get_by_fiscal_code('RO12345678')
    assert company_data is not None
    assert company_data['name'] == 'Test Company'


def test_get_all_companies(company):
    """Test getting all companies."""
    # Create multiple companies
    company.create(
        'Test Company 1',
        '123 Test St',
        'Test City',
        'J12/345/2021',
        'RO12345678'
    )
    company.create(
        'Test Company 2',
        '456 Test Ave',
        'Test City',
        'J12/456/2021',
        'RO87654321'
    )
    
    # Get all companies
    companies = company.get_all()
    assert len(companies) == 2
    assert companies[0]['name'] == 'Test Company 1'
    assert companies[1]['name'] == 'Test Company 2'


def test_update_company(company):
    """Test updating a company."""
    # Create a company
    company_id = company.create(
        'Test Company',
        '123 Test St',
        'Test City',
        'J12/345/2021',
        'RO12345678'
    )
    
    # Update the company
    result = company.update(
        company_id,
        name='Updated Company',
        address='456 Test Ave',
        city='Updated City',
        county='Updated County',
        postal_code='654321',
        country='Updated Country',
        registration_number='J12/456/2021',
        fiscal_code='RO87654321',
        vat_payer=False,
        phone='9876543210',
        email='updated@example.com',
        website='www.updated.com',
        logo_path='/path/to/updated_logo.png'
    )
    assert result is True
    
    # Get the updated company
    company_data = company.get(company_id)
    assert company_data['name'] == 'Updated Company'
    assert company_data['address'] == '456 Test Ave'
    assert company_data['city'] == 'Updated City'
    assert company_data['county'] == 'Updated County'
    assert company_data['postal_code'] == '654321'
    assert company_data['country'] == 'Updated Country'
    assert company_data['registration_number'] == 'J12/456/2021'
    assert company_data['fiscal_code'] == 'RO87654321'
    assert company_data['vat_payer'] == 0
    assert company_data['phone'] == '9876543210'
    assert company_data['email'] == 'updated@example.com'
    assert company_data['website'] == 'www.updated.com'
    assert company_data['logo_path'] == '/path/to/updated_logo.png'


def test_delete_company(company):
    """Test deleting a company."""
    # Create a company
    company_id = company.create(
        'Test Company',
        '123 Test St',
        'Test City',
        'J12/345/2021',
        'RO12345678'
    )
    
    # Delete the company
    result = company.delete(company_id)
    assert result is True
    
    # Try to get the deleted company
    company_data = company.get(company_id)
    assert company_data is None


def test_add_bank_account(company):
    """Test adding a bank account to a company."""
    # Create a company
    company_id = company.create(
        'Test Company',
        '123 Test St',
        'Test City',
        'J12/345/2021',
        'RO12345678'
    )
    
    # Add a bank account to the company
    account_id = company.add_bank_account(
        company_id,
        'Test Bank',
        '123456789',
        'TESTSWIFT',
        'RO49AAAA1B31007593840000',
        'RON',
        True
    )
    assert account_id > 0
    
    # Get the company's bank accounts
    accounts = company.get_bank_accounts(company_id)
    assert len(accounts) == 1
    assert accounts[0]['bank_name'] == 'Test Bank'
    assert accounts[0]['account_number'] == '123456789'
    assert accounts[0]['entity_id'] == company_id
    assert accounts[0]['entity_type'] == 'company'
    assert accounts[0]['is_default'] == 1
    
    # Get the company to check if the default bank account is set
    company_data = company.get(company_id)
    assert company_data['default_bank_account'] == account_id


def test_set_default_bank_account(company):
    """Test setting a bank account as default for a company."""
    # Create a company
    company_id = company.create(
        'Test Company',
        '123 Test St',
        'Test City',
        'J12/345/2021',
        'RO12345678'
    )
    
    # Add multiple bank accounts to the company
    account_id1 = company.add_bank_account(
        company_id,
        'Test Bank 1',
        '123456789',
        'TESTSWIFT1',
        'RO49AAAA1B31007593840000',
        'RON',
        True
    )
    account_id2 = company.add_bank_account(
        company_id,
        'Test Bank 2',
        '987654321',
        'TESTSWIFT2',
        'RO49AAAA1B31007593840001',
        'EUR',
        False
    )
    
    # Set the second account as default
    result = company.set_default_bank_account(company_id, account_id2)
    assert result is True
    
    # Get the company to check if the default bank account is updated
    company_data = company.get(company_id)
    assert company_data['default_bank_account'] == account_id2
    
    # Get the bank accounts to check if the default flag is updated
    accounts = company.get_bank_accounts(company_id)
    for account in accounts:
        if account['id'] == account_id1:
            assert account['is_default'] == 0
        elif account['id'] == account_id2:
            assert account['is_default'] == 1


def test_validation_errors(company):
    """Test validation errors."""
    # Test empty name
    with pytest.raises(ValueError, match="Company name cannot be empty"):
        company.create(
            '',
            '123 Test St',
            'Test City',
            'J12/345/2021',
            'RO12345678'
        )
    
    # Test empty address
    with pytest.raises(ValueError, match="Company address cannot be empty"):
        company.create(
            'Test Company',
            '',
            'Test City',
            'J12/345/2021',
            'RO12345678'
        )
    
    # Test empty city
    with pytest.raises(ValueError, match="Company city cannot be empty"):
        company.create(
            'Test Company',
            '123 Test St',
            '',
            'J12/345/2021',
            'RO12345678'
        )
    
    # Test empty registration number
    with pytest.raises(ValueError, match="Company registration number cannot be empty"):
        company.create(
            'Test Company',
            '123 Test St',
            'Test City',
            '',
            'RO12345678'
        )
    
    # Test empty fiscal code
    with pytest.raises(ValueError, match="Company fiscal code cannot be empty"):
        company.create(
            'Test Company',
            '123 Test St',
            'Test City',
            'J12/345/2021',
            ''
        )
    
    # Test duplicate fiscal code
    company.create(
        'Test Company',
        '123 Test St',
        'Test City',
        'J12/345/2021',
        'RO12345678'
    )
    with pytest.raises(ValueError, match="A company with fiscal code 'RO12345678' already exists"):
        company.create(
            'Another Company',
            '456 Test Ave',
            'Test City',
            'J12/456/2021',
            'RO12345678'
        )
    
    # Test updating ID
    company_id = company.create(
        'Test Company 2',
        '123 Test St',
        'Test City',
        'J12/345/2021',
        'RO87654321'
    )
    with pytest.raises(ValueError, match="Cannot update company ID"):
        company.update(company_id, id=999)
    
    # Test updating fiscal code to one that already exists
    with pytest.raises(ValueError, match="A company with fiscal code 'RO12345678' already exists"):
        company.update(company_id, fiscal_code='RO12345678')
    
    # Test adding bank account to non-existent company
    with pytest.raises(ValueError, match="Company with ID 999 does not exist"):
        company.add_bank_account(
            999,
            'Test Bank',
            '123456789',
            'TESTSWIFT',
            'RO49AAAA1B31007593840000',
            'RON',
            True
        )
    
    # Test getting bank accounts for non-existent company
    with pytest.raises(ValueError, match="Company with ID 999 does not exist"):
        company.get_bank_accounts(999)
    
    # Test setting default bank account for non-existent company
    with pytest.raises(ValueError, match="Company with ID 999 does not exist"):
        company.set_default_bank_account(999, 1)