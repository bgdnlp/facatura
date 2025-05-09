"""
Tests for the Client class.
"""

import os
import tempfile
import sqlite3
import pytest
from facatura.db.setup_db import setup_database
from facatura.core.client import Client


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
def client(temp_db):
    """Create a Client instance for testing."""
    return Client(temp_db)


def test_create_client(client):
    """Test creating a client."""
    # Create a client
    client_id = client.create(
        'Test Client',
        '123 Test St',
        'Test City',
        'RO12345678',
        registration_number='J12/345/2021',
        county='Test County',
        postal_code='123456',
        country='Romania',
        vat_payer=True,
        phone='0123456789',
        email='test@example.com',
        website='www.example.com'
    )
    assert client_id > 0


def test_get_client(client):
    """Test getting a client."""
    # Create a client
    client_id = client.create(
        'Test Client',
        '123 Test St',
        'Test City',
        'RO12345678'
    )
    
    # Get the client
    client_data = client.get(client_id)
    assert client_data is not None
    assert client_data['name'] == 'Test Client'
    assert client_data['address'] == '123 Test St'
    assert client_data['city'] == 'Test City'
    assert client_data['fiscal_code'] == 'RO12345678'


def test_get_by_fiscal_code(client):
    """Test getting a client by fiscal code."""
    # Create a client
    client.create(
        'Test Client',
        '123 Test St',
        'Test City',
        'RO12345678'
    )
    
    # Get the client by fiscal code
    client_data = client.get_by_fiscal_code('RO12345678')
    assert client_data is not None
    assert client_data['name'] == 'Test Client'


def test_get_all_clients(client):
    """Test getting all clients."""
    # Create multiple clients
    client.create(
        'Test Client 1',
        '123 Test St',
        'Test City',
        'RO12345678'
    )
    client.create(
        'Test Client 2',
        '456 Test Ave',
        'Test City',
        'RO87654321'
    )
    
    # Get all clients
    clients = client.get_all()
    assert len(clients) == 2
    assert clients[0]['name'] == 'Test Client 1'
    assert clients[1]['name'] == 'Test Client 2'


def test_update_client(client):
    """Test updating a client."""
    # Create a client
    client_id = client.create(
        'Test Client',
        '123 Test St',
        'Test City',
        'RO12345678'
    )
    
    # Update the client
    result = client.update(
        client_id,
        name='Updated Client',
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
        website='www.updated.com'
    )
    assert result is True
    
    # Get the updated client
    client_data = client.get(client_id)
    assert client_data['name'] == 'Updated Client'
    assert client_data['address'] == '456 Test Ave'
    assert client_data['city'] == 'Updated City'
    assert client_data['county'] == 'Updated County'
    assert client_data['postal_code'] == '654321'
    assert client_data['country'] == 'Updated Country'
    assert client_data['registration_number'] == 'J12/456/2021'
    assert client_data['fiscal_code'] == 'RO87654321'
    assert client_data['vat_payer'] == 0
    assert client_data['phone'] == '9876543210'
    assert client_data['email'] == 'updated@example.com'
    assert client_data['website'] == 'www.updated.com'


def test_delete_client(client):
    """Test deleting a client."""
    # Create a client
    client_id = client.create(
        'Test Client',
        '123 Test St',
        'Test City',
        'RO12345678'
    )
    
    # Delete the client
    result = client.delete(client_id)
    assert result is True
    
    # Try to get the deleted client
    client_data = client.get(client_id)
    assert client_data is None


def test_add_bank_account(client):
    """Test adding a bank account to a client."""
    # Create a client
    client_id = client.create(
        'Test Client',
        '123 Test St',
        'Test City',
        'RO12345678'
    )
    
    # Add a bank account to the client
    account_id = client.add_bank_account(
        client_id,
        'Test Bank',
        '123456789',
        'TESTSWIFT',
        'RO49AAAA1B31007593840000',
        'RON',
        True
    )
    assert account_id > 0
    
    # Get the client's bank accounts
    accounts = client.get_bank_accounts(client_id)
    assert len(accounts) == 1
    assert accounts[0]['bank_name'] == 'Test Bank'
    assert accounts[0]['account_number'] == '123456789'
    assert accounts[0]['entity_id'] == client_id
    assert accounts[0]['entity_type'] == 'client'
    assert accounts[0]['is_default'] == 1
    
    # Get the client to check if the default bank account is set
    client_data = client.get(client_id)
    assert client_data['default_bank_account'] == account_id


def test_set_default_bank_account(client):
    """Test setting a bank account as default for a client."""
    # Create a client
    client_id = client.create(
        'Test Client',
        '123 Test St',
        'Test City',
        'RO12345678'
    )
    
    # Add multiple bank accounts to the client
    account_id1 = client.add_bank_account(
        client_id,
        'Test Bank 1',
        '123456789',
        'TESTSWIFT1',
        'RO49AAAA1B31007593840000',
        'RON',
        True
    )
    account_id2 = client.add_bank_account(
        client_id,
        'Test Bank 2',
        '987654321',
        'TESTSWIFT2',
        'RO49AAAA1B31007593840001',
        'EUR',
        False
    )
    
    # Set the second account as default
    result = client.set_default_bank_account(client_id, account_id2)
    assert result is True
    
    # Get the client to check if the default bank account is updated
    client_data = client.get(client_id)
    assert client_data['default_bank_account'] == account_id2
    
    # Get the bank accounts to check if the default flag is updated
    accounts = client.get_bank_accounts(client_id)
    for account in accounts:
        if account['id'] == account_id1:
            assert account['is_default'] == 0
        elif account['id'] == account_id2:
            assert account['is_default'] == 1


def test_validation_errors(client):
    """Test validation errors."""
    # Test empty name
    with pytest.raises(ValueError, match="Client name cannot be empty"):
        client.create(
            '',
            '123 Test St',
            'Test City',
            'RO12345678'
        )
    
    # Test empty address
    with pytest.raises(ValueError, match="Client address cannot be empty"):
        client.create(
            'Test Client',
            '',
            'Test City',
            'RO12345678'
        )
    
    # Test empty city
    with pytest.raises(ValueError, match="Client city cannot be empty"):
        client.create(
            'Test Client',
            '123 Test St',
            '',
            'RO12345678'
        )
    
    # Test empty fiscal code
    with pytest.raises(ValueError, match="Client fiscal code cannot be empty"):
        client.create(
            'Test Client',
            '123 Test St',
            'Test City',
            ''
        )
    
    # Test duplicate fiscal code
    client.create(
        'Test Client',
        '123 Test St',
        'Test City',
        'RO12345678'
    )
    with pytest.raises(ValueError, match="A client with fiscal code 'RO12345678' already exists"):
        client.create(
            'Another Client',
            '456 Test Ave',
            'Test City',
            'RO12345678'
        )
    
    # Test updating ID
    client_id = client.create(
        'Test Client 2',
        '123 Test St',
        'Test City',
        'RO87654321'
    )
    with pytest.raises(ValueError, match="Cannot update client ID"):
        client.update(client_id, id=999)
    
    # Test updating fiscal code to one that already exists
    with pytest.raises(ValueError, match="A client with fiscal code 'RO12345678' already exists"):
        client.update(client_id, fiscal_code='RO12345678')
    
    # Test adding bank account to non-existent client
    with pytest.raises(ValueError, match="Client with ID 999 does not exist"):
        client.add_bank_account(
            999,
            'Test Bank',
            '123456789',
            'TESTSWIFT',
            'RO49AAAA1B31007593840000',
            'RON',
            True
        )
    
    # Test getting bank accounts for non-existent client
    with pytest.raises(ValueError, match="Client with ID 999 does not exist"):
        client.get_bank_accounts(999)
    
    # Test setting default bank account for non-existent client
    with pytest.raises(ValueError, match="Client with ID 999 does not exist"):
        client.set_default_bank_account(999, 1)