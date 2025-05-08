#!/usr/bin/env python3
"""
Tests for the database setup script.
"""

import os
import sqlite3
import sys
import unittest
import tempfile

# Add the parent directory to the path so we can import the facatura package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from facatura.db.setup_db import setup_database


class TestDatabaseSetup(unittest.TestCase):
    """Test the database setup functionality."""
    
    def setUp(self):
        """Create a temporary database for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, 'test_facatura.db')
    
    def tearDown(self):
        """Clean up the temporary directory."""
        self.temp_dir.cleanup()
    
    def test_database_creation(self):
        """Test that the database is created successfully."""
        setup_database(self.db_path)
        self.assertTrue(os.path.exists(self.db_path))
    
    def test_tables_creation(self):
        """Test that all required tables are created."""
        setup_database(self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Check that all expected tables exist
        expected_tables = ['companies', 'clients', 'products', 'currency_exchange']
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()
    
    def test_companies_table_structure(self):
        """Test that the companies table has the correct structure."""
        setup_database(self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get column info for companies table
        cursor.execute("PRAGMA table_info(companies);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        # Check required columns
        self.assertIn('name', columns)
        self.assertIn('address', columns)
        self.assertIn('registration_number', columns)
        self.assertIn('bank_account', columns)
        
        conn.close()
    
    def test_clients_table_structure(self):
        """Test that the clients table has the correct structure."""
        setup_database(self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get column info for clients table
        cursor.execute("PRAGMA table_info(clients);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        # Check required columns
        self.assertIn('name', columns)
        self.assertIn('address', columns)
        self.assertIn('fiscal_code', columns)
        
        conn.close()
    
    def test_products_table_structure(self):
        """Test that the products table has the correct structure."""
        setup_database(self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get column info for products table
        cursor.execute("PRAGMA table_info(products);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        # Check required columns
        self.assertIn('name', columns)
        self.assertIn('unit', columns)
        self.assertIn('price_per_unit', columns)
        
        conn.close()
    
    def test_currency_exchange_table(self):
        """Test that the currency exchange table has the correct structure and default values."""
        setup_database(self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get column info for currency_exchange table
        cursor.execute("PRAGMA table_info(currency_exchange);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        # Check required columns
        self.assertIn('currency_code', columns)
        self.assertIn('exchange_rate', columns)
        self.assertIn('date', columns)
        
        # Check that default currencies are inserted
        cursor.execute("SELECT currency_code FROM currency_exchange;")
        currencies = [row[0] for row in cursor.fetchall()]
        
        expected_currencies = ['RON', 'EUR', 'USD', 'GBP']
        for currency in expected_currencies:
            self.assertIn(currency, currencies)
        
        conn.close()


if __name__ == '__main__':
    unittest.main()