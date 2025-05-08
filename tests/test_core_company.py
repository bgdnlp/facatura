"""
Tests for the core.company module.
"""

import os
import tempfile
import sqlite3
import pytest
from facatura.core.company import CompanyManager
from facatura.db.setup_db import setup_database


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


def test_create_company(temp_db):
    """Test creating a company."""
    company_manager = CompanyManager(temp_db)
    
    # Test with valid data
    company_data = {
        'name': 'Test Company',
        'address': '123 Test Street',
        'city': 'Test City',
        'county': 'Test County',
        'postal_code': '123456',
        'country': 'Romania',
        'registration_number': 'J12/345/2023',
        'fiscal_code': 'RO12345678',
        'vat_payer': True,
        'phone': '0123456789',
        'email': 'test@example.com',
        'website': 'https://example.com'
    }
    
    success, result = company_manager.create_company(company_data)
    assert success is True
    assert isinstance(result, int)
    
    # Test with missing required field
    incomplete_data = {
        'name': 'Incomplete Company',
        'address': '456 Test Avenue',
        # Missing city
        'registration_number': 'J12/456/2023',
        'fiscal_code': 'RO87654321'
    }
    
    success, error = company_manager.create_company(incomplete_data)
    assert success is False
    assert "Missing required field" in error
    
    # Test with duplicate fiscal code
    duplicate_data = company_data.copy()
    duplicate_data['name'] = 'Duplicate Company'
    
    success, error = company_manager.create_company(duplicate_data)
    assert success is False
    assert "already exists" in error


def test_get_company_by_id(temp_db):
    """Test retrieving a company by ID."""
    company_manager = CompanyManager(temp_db)
    
    # Create a test company
    company_data = {
        'name': 'Get By ID Company',
        'address': '789 Test Boulevard',
        'city': 'Test City',
        'registration_number': 'J12/789/2023',
        'fiscal_code': 'RO98765432'
    }
    
    success, company_id = company_manager.create_company(company_data)
    assert success is True
    
    # Test retrieving the company by ID
    success, company = company_manager.get_company_by_id(company_id)
    assert success is True
    assert company['name'] == 'Get By ID Company'
    assert company['fiscal_code'] == 'RO98765432'
    
    # Test retrieving a non-existent company
    success, error = company_manager.get_company_by_id(9999)
    assert success is False
    assert "No company found" in error


def test_get_company_by_fiscal_code(temp_db):
    """Test retrieving a company by fiscal code."""
    company_manager = CompanyManager(temp_db)
    
    # Create a test company
    company_data = {
        'name': 'Get By Fiscal Code Company',
        'address': '101 Test Lane',
        'city': 'Test City',
        'registration_number': 'J12/101/2023',
        'fiscal_code': 'RO10101010'
    }
    
    success, _ = company_manager.create_company(company_data)
    assert success is True
    
    # Test retrieving the company by fiscal code
    success, company = company_manager.get_company_by_fiscal_code('RO10101010')
    assert success is True
    assert company['name'] == 'Get By Fiscal Code Company'
    
    # Test retrieving a non-existent company
    success, error = company_manager.get_company_by_fiscal_code('NONEXISTENT')
    assert success is False
    assert "No company found" in error


def test_update_company(temp_db):
    """Test updating a company."""
    company_manager = CompanyManager(temp_db)
    
    # Create a test company
    company_data = {
        'name': 'Update Company',
        'address': '202 Test Road',
        'city': 'Test City',
        'registration_number': 'J12/202/2023',
        'fiscal_code': 'RO20202020'
    }
    
    success, company_id = company_manager.create_company(company_data)
    assert success is True
    
    # Test updating the company
    update_data = {
        'name': 'Updated Company',
        'phone': '9876543210',
        'email': 'updated@example.com'
    }
    
    success, message = company_manager.update_company(company_id, update_data)
    assert success is True
    assert "updated successfully" in message
    
    # Verify the update
    success, company = company_manager.get_company_by_id(company_id)
    assert success is True
    assert company['name'] == 'Updated Company'
    assert company['phone'] == '9876543210'
    assert company['email'] == 'updated@example.com'
    
    # Test updating a non-existent company
    success, error = company_manager.update_company(9999, update_data)
    assert success is False
    assert "No company found" in error


def test_delete_company(temp_db):
    """Test deleting a company."""
    company_manager = CompanyManager(temp_db)
    
    # Create a test company
    company_data = {
        'name': 'Delete Company',
        'address': '303 Test Avenue',
        'city': 'Test City',
        'registration_number': 'J12/303/2023',
        'fiscal_code': 'RO30303030'
    }
    
    success, company_id = company_manager.create_company(company_data)
    assert success is True
    
    # Test deleting the company
    success, message = company_manager.delete_company(company_id)
    assert success is True
    assert "deleted successfully" in message
    
    # Verify the deletion
    success, error = company_manager.get_company_by_id(company_id)
    assert success is False
    assert "No company found" in error
    
    # Test deleting a non-existent company
    success, error = company_manager.delete_company(9999)
    assert success is False
    assert "No company found" in error


def test_list_companies(temp_db):
    """Test listing companies."""
    company_manager = CompanyManager(temp_db)
    
    # Create multiple test companies
    companies = [
        {
            'name': 'List Company 1',
            'address': '404 Test Street',
            'city': 'Test City A',
            'registration_number': 'J12/404/2023',
            'fiscal_code': 'RO40404040'
        },
        {
            'name': 'List Company 2',
            'address': '505 Test Boulevard',
            'city': 'Test City B',
            'registration_number': 'J12/505/2023',
            'fiscal_code': 'RO50505050'
        },
        {
            'name': 'List Company 3',
            'address': '606 Test Lane',
            'city': 'Test City A',
            'registration_number': 'J12/606/2023',
            'fiscal_code': 'RO60606060'
        }
    ]
    
    for company_data in companies:
        success, _ = company_manager.create_company(company_data)
        assert success is True
    
    # Test listing all companies
    success, all_companies = company_manager.list_companies()
    assert success is True
    assert len(all_companies) >= 3  # There might be companies from other tests
    
    # Test filtering companies by city
    success, filtered_companies = company_manager.list_companies({'city': 'Test City A'})
    assert success is True
    assert len(filtered_companies) == 2
    assert all(company['city'] == 'Test City A' for company in filtered_companies)