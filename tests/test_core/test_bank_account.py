"""
Tests for the BankAccount class.
"""

import os
import tempfile
import sqlite3
import pytest
from facatura.db.setup_db import setup_database
from facatura.core.bank_account import BankAccount


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
def bank_account(temp_db):
    """Create a BankAccount instance for testing."""
    return BankAccount(temp_db)


@pytest.fixture
def sample_entity(temp_db):
    """Create a sample entity (company) for testing."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    # Insert a sample company
    cursor.execute(
        """
        INSERT INTO companies (
            name, address, city, registration_number, fiscal_code
        ) VALUES (?, ?, ?, ?, ?)
        """,
        ('Test Company', '123 Test St', 'Test City', 'J12/345/2021', 'RO12345678')
    )
    company_id = cursor.lastrowid
    
    # Insert a sample client
    cursor.execute(
        """
        INSERT INTO clients (
            name, address, city, fiscal_code
        ) VALUES (?, ?, ?, ?)
        """,
        ('Test Client', '456 Test Ave', 'Test City', 'RO87654321')
    )
    client_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return {'company_id': company_id, 'client_id': client_id}


def test_create_bank_account(bank_account, sample_entity):
    """Test creating a bank account."""
    # Create a bank account for a company
    company_account_id = bank_account.create(
        'Test Bank', '123456789', sample_entity['company_id'], 'company',
        'TESTSWIFT', 'RO49AAAA1B31007593840000', 'RON', True
    )
    assert company_account_id > 0
    
    # Create a bank account for a client
    client_account_id = bank_account.create(
        'Test Bank', '987654321', sample_entity['client_id'], 'client',
        'TESTSWIFT', 'RO49AAAA1B31007593840001', 'RON', True
    )
    assert client_account_id > 0


def test_get_bank_account(bank_account, sample_entity):
    """Test getting a bank account."""
    # Create a bank account
    account_id = bank_account.create(
        'Test Bank', '123456789', sample_entity['company_id'], 'company',
        'TESTSWIFT', 'RO49AAAA1B31007593840000', 'RON', True
    )
    
    # Get the bank account
    account = bank_account.get(account_id)
    assert account is not None
    assert account['bank_name'] == 'Test Bank'
    assert account['account_number'] == '123456789'
    assert account['entity_id'] == sample_entity['company_id']
    assert account['entity_type'] == 'company'
    assert account['swift_code'] == 'TESTSWIFT'
    assert account['iban'] == 'RO49AAAA1B31007593840000'
    assert account['currency'] == 'RON'
    assert account['is_default'] == 1


def test_get_by_entity(bank_account, sample_entity):
    """Test getting bank accounts by entity."""
    # Create multiple bank accounts for a company
    bank_account.create(
        'Test Bank 1', '123456789', sample_entity['company_id'], 'company',
        'TESTSWIFT1', 'RO49AAAA1B31007593840000', 'RON', True
    )
    bank_account.create(
        'Test Bank 2', '234567890', sample_entity['company_id'], 'company',
        'TESTSWIFT2', 'RO49AAAA1B31007593840001', 'EUR', False
    )
    
    # Get bank accounts for the company
    accounts = bank_account.get_by_entity(sample_entity['company_id'], 'company')
    assert len(accounts) == 2
    assert accounts[0]['bank_name'] == 'Test Bank 1'
    assert accounts[1]['bank_name'] == 'Test Bank 2'


def test_get_default(bank_account, sample_entity):
    """Test getting the default bank account."""
    # Create multiple bank accounts for a company
    bank_account.create(
        'Test Bank 1', '123456789', sample_entity['company_id'], 'company',
        'TESTSWIFT1', 'RO49AAAA1B31007593840000', 'RON', True
    )
    bank_account.create(
        'Test Bank 2', '234567890', sample_entity['company_id'], 'company',
        'TESTSWIFT2', 'RO49AAAA1B31007593840001', 'EUR', False
    )
    
    # Get the default bank account
    default_account = bank_account.get_default(sample_entity['company_id'], 'company')
    assert default_account is not None
    assert default_account['bank_name'] == 'Test Bank 1'
    assert default_account['is_default'] == 1


def test_update_bank_account(bank_account, sample_entity):
    """Test updating a bank account."""
    # Create a bank account
    account_id = bank_account.create(
        'Test Bank', '123456789', sample_entity['company_id'], 'company',
        'TESTSWIFT', 'RO49AAAA1B31007593840000', 'RON', True
    )
    
    # Update the bank account
    result = bank_account.update(
        account_id,
        bank_name='Updated Bank',
        account_number='987654321',
        swift_code='UPDATEDSWIFT',
        iban='RO49AAAA1B31007593840001',
        currency='EUR'
    )
    assert result is True
    
    # Get the updated bank account
    account = bank_account.get(account_id)
    assert account['bank_name'] == 'Updated Bank'
    assert account['account_number'] == '987654321'
    assert account['swift_code'] == 'UPDATEDSWIFT'
    assert account['iban'] == 'RO49AAAA1B31007593840001'
    assert account['currency'] == 'EUR'


def test_delete_bank_account(bank_account, sample_entity):
    """Test deleting a bank account."""
    # Create a bank account
    account_id = bank_account.create(
        'Test Bank', '123456789', sample_entity['company_id'], 'company',
        'TESTSWIFT', 'RO49AAAA1B31007593840000', 'RON', True
    )
    
    # Delete the bank account
    result = bank_account.delete(account_id)
    assert result is True
    
    # Try to get the deleted bank account
    account = bank_account.get(account_id)
    assert account is None


def test_set_default(bank_account, sample_entity):
    """Test setting a bank account as default."""
    # Create multiple bank accounts for a company
    account_id1 = bank_account.create(
        'Test Bank 1', '123456789', sample_entity['company_id'], 'company',
        'TESTSWIFT1', 'RO49AAAA1B31007593840000', 'RON', True
    )
    account_id2 = bank_account.create(
        'Test Bank 2', '234567890', sample_entity['company_id'], 'company',
        'TESTSWIFT2', 'RO49AAAA1B31007593840001', 'EUR', False
    )
    
    # Set the second account as default
    result = bank_account.set_default(account_id2)
    assert result is True
    
    # Get the default bank account
    default_account = bank_account.get_default(sample_entity['company_id'], 'company')
    assert default_account is not None
    assert default_account['id'] == account_id2
    assert default_account['is_default'] == 1
    
    # Check that the first account is no longer default
    account1 = bank_account.get(account_id1)
    assert account1['is_default'] == 0


def test_validation_errors(bank_account, sample_entity):
    """Test validation errors."""
    # Test empty bank name
    with pytest.raises(ValueError, match="Bank name cannot be empty"):
        bank_account.create(
            '', '123456789', sample_entity['company_id'], 'company',
            'TESTSWIFT', 'RO49AAAA1B31007593840000', 'RON', True
        )
    
    # Test empty account number
    with pytest.raises(ValueError, match="Account number cannot be empty"):
        bank_account.create(
            'Test Bank', '', sample_entity['company_id'], 'company',
            'TESTSWIFT', 'RO49AAAA1B31007593840000', 'RON', True
        )
    
    # Test invalid entity ID
    with pytest.raises(ValueError, match="Entity ID must be a positive integer"):
        bank_account.create(
            'Test Bank', '123456789', 0, 'company',
            'TESTSWIFT', 'RO49AAAA1B31007593840000', 'RON', True
        )
    
    # Test invalid entity type
    with pytest.raises(ValueError, match="Entity type must be 'company' or 'client'"):
        bank_account.create(
            'Test Bank', '123456789', sample_entity['company_id'], 'invalid',
            'TESTSWIFT', 'RO49AAAA1B31007593840000', 'RON', True
        )
    
    # Test updating ID
    account_id = bank_account.create(
        'Test Bank', '123456789', sample_entity['company_id'], 'company',
        'TESTSWIFT', 'RO49AAAA1B31007593840000', 'RON', True
    )
    with pytest.raises(ValueError, match="Cannot update account ID"):
        bank_account.update(account_id, id=999)
    
    # Test updating entity ID
    with pytest.raises(ValueError, match="Cannot update entity ID"):
        bank_account.update(account_id, entity_id=999)
    
    # Test updating entity type
    with pytest.raises(ValueError, match="Cannot update entity type"):
        bank_account.update(account_id, entity_type='client')