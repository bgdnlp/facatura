"""
Tests for the CLI module.
"""

import os
import tempfile
import sqlite3
from click.testing import CliRunner
from facatura.cli import main
from facatura.db.setup_db import setup_database


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
        result = runner.invoke(main, ["--db-path", temp_db_path, "init"])
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


def test_company_commands():
    """Test the company management commands."""
    runner = CliRunner()
    
    # Use a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Initialize the database
        setup_database(temp_db_path)
        
        # Test listing companies when none exist
        result = runner.invoke(main, ["--db-path", temp_db_path, "company", "list"])
        assert result.exit_code == 0
        assert "No companies found" in result.output
        
        # Test adding a company
        result = runner.invoke(main, [
            "--db-path", temp_db_path, "company", "add",
            "--name", "Test Company",
            "--address", "123 Test St",
            "--city", "Test City",
            "--registration-number", "J12/345/2021",
            "--fiscal-code", "RO12345678"
        ])
        assert result.exit_code == 0
        assert "Company added successfully with ID:" in result.output
        
        # Test listing companies after adding one
        result = runner.invoke(main, ["--db-path", temp_db_path, "company", "list"])
        assert result.exit_code == 0
        assert "Test Company" in result.output
        assert "RO12345678" in result.output
        
        # Extract the company ID from the list output
        company_id = int(result.output.split(":")[1].split(":")[0].strip())
        
        # Test showing company details
        result = runner.invoke(main, ["--db-path", temp_db_path, "company", "show", str(company_id)])
        assert result.exit_code == 0
        assert "Test Company" in result.output
        assert "123 Test St" in result.output
        assert "Test City" in result.output
        assert "J12/345/2021" in result.output
        assert "RO12345678" in result.output
        assert "No bank accounts found" in result.output
        
        # Test adding a bank account to the company
        result = runner.invoke(main, [
            "--db-path", temp_db_path, "company", "add-bank-account", str(company_id),
            "--bank-name", "Test Bank",
            "--account-number", "123456789",
            "--swift-code", "TESTSWIFT",
            "--iban", "RO49AAAA1B31007593840000",
            "--default"
        ])
        assert result.exit_code == 0
        assert "Bank account added successfully with ID:" in result.output
        
        # Test showing company details after adding a bank account
        result = runner.invoke(main, ["--db-path", temp_db_path, "company", "show", str(company_id)])
        assert result.exit_code == 0
        assert "Bank Accounts:" in result.output
        assert "Test Bank" in result.output
        assert "123456789" in result.output
        assert "(Default)" in result.output
        
        # Test deleting the company
        result = runner.invoke(main, ["--db-path", temp_db_path, "company", "delete", str(company_id)], input="y\n")
        assert result.exit_code == 0
        assert "deleted successfully" in result.output
        
        # Test listing companies after deletion
        result = runner.invoke(main, ["--db-path", temp_db_path, "company", "list"])
        assert result.exit_code == 0
        assert "No companies found" in result.output
    
    finally:
        # Clean up the temporary database file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


def test_client_commands():
    """Test the client management commands."""
    runner = CliRunner()
    
    # Use a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Initialize the database
        setup_database(temp_db_path)
        
        # Test listing clients when none exist
        result = runner.invoke(main, ["--db-path", temp_db_path, "client", "list"])
        assert result.exit_code == 0
        assert "No clients found" in result.output
        
        # Test adding a client
        result = runner.invoke(main, [
            "--db-path", temp_db_path, "client", "add",
            "--name", "Test Client",
            "--address", "123 Test St",
            "--city", "Test City",
            "--fiscal-code", "RO12345678"
        ])
        assert result.exit_code == 0
        assert "Client added successfully with ID:" in result.output
        
        # Test listing clients after adding one
        result = runner.invoke(main, ["--db-path", temp_db_path, "client", "list"])
        assert result.exit_code == 0
        assert "Test Client" in result.output
        assert "RO12345678" in result.output
        
        # Extract the client ID from the list output
        client_id = int(result.output.split(":")[1].split(":")[0].strip())
        
        # Test showing client details
        result = runner.invoke(main, ["--db-path", temp_db_path, "client", "show", str(client_id)])
        assert result.exit_code == 0
        assert "Test Client" in result.output
        assert "123 Test St" in result.output
        assert "Test City" in result.output
        assert "RO12345678" in result.output
        assert "No bank accounts found" in result.output
        
        # Test adding a bank account to the client
        result = runner.invoke(main, [
            "--db-path", temp_db_path, "client", "add-bank-account", str(client_id),
            "--bank-name", "Test Bank",
            "--account-number", "123456789",
            "--swift-code", "TESTSWIFT",
            "--iban", "RO49AAAA1B31007593840000",
            "--default"
        ])
        assert result.exit_code == 0
        assert "Bank account added successfully with ID:" in result.output
        
        # Test showing client details after adding a bank account
        result = runner.invoke(main, ["--db-path", temp_db_path, "client", "show", str(client_id)])
        assert result.exit_code == 0
        assert "Bank Accounts:" in result.output
        assert "Test Bank" in result.output
        assert "123456789" in result.output
        assert "(Default)" in result.output
        
        # Test deleting the client
        result = runner.invoke(main, ["--db-path", temp_db_path, "client", "delete", str(client_id)], input="y\n")
        assert result.exit_code == 0
        assert "deleted successfully" in result.output
        
        # Test listing clients after deletion
        result = runner.invoke(main, ["--db-path", temp_db_path, "client", "list"])
        assert result.exit_code == 0
        assert "No clients found" in result.output
    
    finally:
        # Clean up the temporary database file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)