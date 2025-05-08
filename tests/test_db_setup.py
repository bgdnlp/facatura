"""
Tests for the database setup module.
"""

import os
import tempfile
import sqlite3
from pathlib import Path
import pytest
from facatura.db.setup_db import create_tables


def test_create_tables():
    """Test creating database tables."""
    # Create a temporary directory for the test database
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_facatura.db"
        
        # Create the tables
        result = create_tables(db_path)
        
        # Check that the function returned True (success)
        assert result is True
        
        # Verify that the database file was created
        assert db_path.exists()
        
        # Connect to the database and verify the tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check that all required tables exist
        assert "companies" in tables
        assert "clients" in tables
        assert "products" in tables
        assert "currency_exchange" in tables
        
        # Verify the structure of the companies table
        cursor.execute("PRAGMA table_info(companies)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        assert "name" in columns
        assert "address" in columns
        assert "registration_number" in columns
        assert "fiscal_code" in columns
        assert "bank_account" in columns
        
        # Verify the structure of the clients table
        cursor.execute("PRAGMA table_info(clients)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        assert "name" in columns
        assert "address" in columns
        assert "fiscal_code" in columns
        
        # Verify the structure of the products table
        cursor.execute("PRAGMA table_info(products)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        assert "name" in columns
        assert "unit" in columns
        assert "price_per_unit" in columns
        assert "currency" in columns
        
        # Verify the structure of the currency_exchange table
        cursor.execute("PRAGMA table_info(currency_exchange)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        assert "date" in columns
        assert "from_currency" in columns
        assert "to_currency" in columns
        assert "rate" in columns
        
        # Close the connection
        conn.close()


def test_create_tables_with_existing_directory():
    """Test creating database tables when the directory already exists."""
    # Create a temporary directory for the test database
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "subdir" / "test_facatura.db"
        
        # Create the directory structure
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create the tables
        result = create_tables(db_path)
        
        # Check that the function returned True (success)
        assert result is True
        
        # Verify that the database file was created
        assert db_path.exists()


def test_create_tables_with_invalid_path():
    """Test creating database tables with an invalid path."""
    # Try to create tables with an invalid path (a directory that can't be created)
    if os.name == 'nt':  # Windows
        invalid_path = "\\\\?\\invalid\\path\\test.db"
    else:  # Unix/Linux/MacOS
        invalid_path = "/root/invalid/path/test.db"  # Assuming no root access
    
    # This should return False, not raise an exception
    result = create_tables(invalid_path)
    assert result is False