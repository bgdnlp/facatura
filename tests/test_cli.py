"""
Tests for the CLI module.
"""

import os
import tempfile
import sqlite3
from click.testing import CliRunner
from facatura.cli import main


def test_main():
    """Test the main CLI entry point."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Facatura - Romanian invoicing application" in result.output


def test_version():
    """Test the version command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_create_invoice():
    """Test the create-invoice command."""
    runner = CliRunner()
    result = runner.invoke(main, ["create-invoice", "--client", "Test Client"])
    assert result.exit_code == 0
    assert "Creating invoice for client: Test Client" in result.output


def test_init_database():
    """Test the init command to initialize the database."""
    runner = CliRunner()
    
    # Use a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Run the init command with the temporary database path
        result = runner.invoke(main, ["init", "--db-path", temp_db_path])
        assert result.exit_code == 0
        assert "Database initialization completed successfully" in result.output
        
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