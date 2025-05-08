"""
Tests for the database setup module.
"""

import os
import tempfile
import sqlite3
import pytest
from facatura.db.setup_db import setup_database


def test_setup_database():
    """Test the setup_database function."""
    # Use a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Run the setup_database function
        result = setup_database(temp_db_path)
        assert result is True
        
        # Verify that the database was created and has the expected tables
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Check if all required tables exist
        required_tables = [
            'companies', 
            'clients', 
            'products_services', 
            'currency_exchange',
            'bank_accounts'
        ]
        
        for table in required_tables:
            assert table in tables, f"Table '{table}' not found in the database"
        
        # Check bank_accounts table structure
        cursor.execute("PRAGMA table_info(bank_accounts)")
        columns = {row[1]: row for row in cursor.fetchall()}
        assert 'entity_id' in columns
        assert 'entity_type' in columns
        assert 'is_default' in columns
        
        # Check companies table structure
        cursor.execute("PRAGMA table_info(companies)")
        columns = {row[1]: row for row in cursor.fetchall()}
        assert 'default_bank_account' in columns
        
        # Check clients table structure
        cursor.execute("PRAGMA table_info(clients)")
        columns = {row[1]: row for row in cursor.fetchall()}
        assert 'default_bank_account' in columns
        
        # Check if the currency_exchange table has the default currencies
        cursor.execute("SELECT currency_code FROM currency_exchange;")
        currencies = [currency[0] for currency in cursor.fetchall()]
        
        expected_currencies = ['RON', 'EUR', 'USD', 'GBP']
        for currency in expected_currencies:
            assert currency in currencies, f"Currency '{currency}' not found in the database"
        
        conn.close()
    
    finally:
        # Clean up the temporary database file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


def test_setup_database_idempotent():
    """Test that running setup_database multiple times doesn't cause errors."""
    # Use a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Run the setup_database function twice
        result1 = setup_database(temp_db_path)
        result2 = setup_database(temp_db_path)
        
        assert result1 is True
        assert result2 is True
        
        # Verify that the database still has the expected tables
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Check if all required tables exist
        required_tables = [
            'companies', 
            'clients', 
            'products_services', 
            'currency_exchange',
            'bank_accounts'
        ]
        
        for table in required_tables:
            assert table in tables, f"Table '{table}' not found in the database"
        
        conn.close()
    
    finally:
        # Clean up the temporary database file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)