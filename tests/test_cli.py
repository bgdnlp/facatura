"""
Tests for the CLI module.
"""

import os
import tempfile
import sqlite3
from pathlib import Path
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
    """Test the init command with a temporary database."""
    runner = CliRunner()
    
    # Create a temporary directory for the test database
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_facatura.db"
        
        # Run the init command with the test database path
        result = runner.invoke(main, ["init", "--db-path", str(db_path)])
        
        # Check that the command executed successfully
        assert result.exit_code == 0
        assert "Initializing database" in result.output
        assert "Database initialized successfully" in result.output
        
        # Verify that the database file was created
        assert db_path.exists()
        
        # Verify that the tables were created
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
        
        # Close the connection
        conn.close()