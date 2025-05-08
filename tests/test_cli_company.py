"""
Tests for the company management CLI commands.
"""

import os
import tempfile
import sqlite3
from click.testing import CliRunner
from facatura.cli import main
from facatura.db.setup_db import setup_database


def test_company_group():
    """Test the company command group."""
    runner = CliRunner()
    result = runner.invoke(main, ["company", "--help"])
    assert result.exit_code == 0
    assert "Manage company records" in result.output


def test_create_company():
    """Test the create company command."""
    runner = CliRunner()
    
    # Use a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Initialize the database
        setup_database(temp_db_path)
        
        # Run the create company command
        result = runner.invoke(main, [
            "company", "create",
            "--db-path", temp_db_path,
            "--name", "Test Company",
            "--address", "123 Test Street",
            "--city", "Test City",
            "--registration-number", "J12/345/2023",
            "--fiscal-code", "RO12345678"
        ])
        
        assert result.exit_code == 0
        assert "Company created successfully" in result.output
        
        # Verify that the company was created
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, fiscal_code FROM companies WHERE fiscal_code = 'RO12345678'")
        company = cursor.fetchone()
        assert company is not None
        assert company[0] == "Test Company"
        conn.close()
        
    finally:
        # Clean up the temporary database file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


def test_get_company():
    """Test the get company command."""
    runner = CliRunner()
    
    # Use a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Initialize the database
        setup_database(temp_db_path)
        
        # Create a test company
        create_result = runner.invoke(main, [
            "company", "create",
            "--db-path", temp_db_path,
            "--name", "Get Company",
            "--address", "456 Test Avenue",
            "--city", "Test City",
            "--registration-number", "J12/456/2023",
            "--fiscal-code", "RO87654321"
        ])
        
        assert create_result.exit_code == 0
        
        # Extract the company ID from the output
        import re
        company_id = re.search(r"ID: (\d+)", create_result.output)
        assert company_id is not None
        company_id = company_id.group(1)
        
        # Test get company by ID
        get_result = runner.invoke(main, [
            "company", "get",
            "--db-path", temp_db_path,
            "--id", company_id
        ])
        
        assert get_result.exit_code == 0
        assert "Get Company" in get_result.output
        assert "RO87654321" in get_result.output
        
        # Test get company by fiscal code
        get_result = runner.invoke(main, [
            "company", "get",
            "--db-path", temp_db_path,
            "--fiscal-code", "RO87654321"
        ])
        
        assert get_result.exit_code == 0
        assert "Get Company" in get_result.output
        
    finally:
        # Clean up the temporary database file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


def test_update_company():
    """Test the update company command."""
    runner = CliRunner()
    
    # Use a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Initialize the database
        setup_database(temp_db_path)
        
        # Create a test company
        create_result = runner.invoke(main, [
            "company", "create",
            "--db-path", temp_db_path,
            "--name", "Update Company",
            "--address", "789 Test Boulevard",
            "--city", "Test City",
            "--registration-number", "J12/789/2023",
            "--fiscal-code", "RO98765432"
        ])
        
        assert create_result.exit_code == 0
        
        # Extract the company ID from the output
        import re
        company_id = re.search(r"ID: (\d+)", create_result.output)
        assert company_id is not None
        company_id = company_id.group(1)
        
        # Update the company
        update_result = runner.invoke(main, [
            "company", "update",
            "--db-path", temp_db_path,
            "--id", company_id,
            "--name", "Updated Company",
            "--phone", "0123456789"
        ])
        
        assert update_result.exit_code == 0
        assert "updated successfully" in update_result.output
        
        # Verify the update
        get_result = runner.invoke(main, [
            "company", "get",
            "--db-path", temp_db_path,
            "--id", company_id
        ])
        
        assert get_result.exit_code == 0
        assert "Updated Company" in get_result.output
        assert "0123456789" in get_result.output
        
    finally:
        # Clean up the temporary database file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


def test_list_companies():
    """Test the list companies command."""
    runner = CliRunner()
    
    # Use a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Initialize the database
        setup_database(temp_db_path)
        
        # Create multiple test companies
        companies = [
            {
                "name": "List Company A",
                "address": "101 Test Lane",
                "city": "City A",
                "registration-number": "J12/101/2023",
                "fiscal-code": "RO10101010"
            },
            {
                "name": "List Company B",
                "address": "202 Test Road",
                "city": "City B",
                "registration-number": "J12/202/2023",
                "fiscal-code": "RO20202020"
            },
            {
                "name": "List Company C",
                "address": "303 Test Street",
                "city": "City A",
                "registration-number": "J12/303/2023",
                "fiscal-code": "RO30303030"
            }
        ]
        
        for company in companies:
            args = ["company", "create", "--db-path", temp_db_path]
            for key, value in company.items():
                args.extend([f"--{key}", value])
            
            result = runner.invoke(main, args)
            assert result.exit_code == 0
        
        # Test listing all companies
        list_result = runner.invoke(main, [
            "company", "list",
            "--db-path", temp_db_path
        ])
        
        assert list_result.exit_code == 0
        assert "Found 3 companies" in list_result.output
        assert "List Company A" in list_result.output
        assert "List Company B" in list_result.output
        assert "List Company C" in list_result.output
        
        # Test filtering companies by city
        filter_result = runner.invoke(main, [
            "company", "list",
            "--db-path", temp_db_path,
            "--city", "City A"
        ])
        
        assert filter_result.exit_code == 0
        assert "List Company A" in filter_result.output
        assert "List Company C" in filter_result.output
        assert "List Company B" not in filter_result.output
        
    finally:
        # Clean up the temporary database file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


def test_delete_company():
    """Test the delete company command."""
    runner = CliRunner()
    
    # Use a temporary file for the database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Initialize the database
        setup_database(temp_db_path)
        
        # Create a test company
        create_result = runner.invoke(main, [
            "company", "create",
            "--db-path", temp_db_path,
            "--name", "Delete Company",
            "--address", "404 Test Avenue",
            "--city", "Test City",
            "--registration-number", "J12/404/2023",
            "--fiscal-code", "RO40404040"
        ])
        
        assert create_result.exit_code == 0
        
        # Extract the company ID from the output
        import re
        company_id = re.search(r"ID: (\d+)", create_result.output)
        assert company_id is not None
        company_id = company_id.group(1)
        
        # Delete the company with confirmation
        delete_result = runner.invoke(main, [
            "company", "delete",
            "--db-path", temp_db_path,
            "--id", company_id
        ], input="y\n")
        
        assert delete_result.exit_code == 0
        assert "deleted successfully" in delete_result.output
        
        # Verify the deletion
        get_result = runner.invoke(main, [
            "company", "get",
            "--db-path", temp_db_path,
            "--id", company_id
        ])
        
        assert get_result.exit_code == 1
        assert "No company found" in get_result.output
        
    finally:
        # Clean up the temporary database file
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)