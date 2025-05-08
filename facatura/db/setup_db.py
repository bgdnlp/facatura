#!/usr/bin/env python3
"""
Database setup script for facatura.

This script creates the necessary tables in an SQLite database for the facatura application.

How to run on MacOS and Linux:
1. Make sure you have Python 3.6 or higher installed
2. Navigate to the facatura directory
3. Run: python -m facatura.db.setup_db
   or
   Run: facatura init (if the package is installed)

The script will create a database file named 'facatura.db' in the current directory
if it doesn't exist, or update the schema if it does.
"""

import os
import sqlite3
import sys


def setup_database(db_path='facatura.db'):
    """
    Set up the database with the necessary tables.
    
    Args:
        db_path (str): Path to the database file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create bank_accounts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bank_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank_name TEXT NOT NULL,
            account_number TEXT NOT NULL,
            swift_code TEXT,
            iban TEXT,
            currency TEXT DEFAULT 'RON',
            entity_id INTEGER NOT NULL,
            entity_type TEXT NOT NULL,  -- 'company' or 'client'
            is_default BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(entity_id, entity_type, account_number)
        )
        ''')
        
        # Create companies table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            county TEXT,
            postal_code TEXT,
            country TEXT DEFAULT 'Romania',
            registration_number TEXT NOT NULL,
            fiscal_code TEXT NOT NULL,
            vat_payer BOOLEAN DEFAULT 1,
            phone TEXT,
            email TEXT,
            website TEXT,
            logo_path TEXT,
            default_bank_account INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(fiscal_code),
            FOREIGN KEY (default_bank_account) REFERENCES bank_accounts(id)
        )
        ''')
        
        # Create clients table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            county TEXT,
            postal_code TEXT,
            country TEXT DEFAULT 'Romania',
            registration_number TEXT,
            fiscal_code TEXT NOT NULL,
            vat_payer BOOLEAN DEFAULT 1,
            phone TEXT,
            email TEXT,
            website TEXT,
            default_bank_account INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(fiscal_code),
            FOREIGN KEY (default_bank_account) REFERENCES bank_accounts(id)
        )
        ''')
        
        # Create products_services table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            unit_of_measure TEXT NOT NULL,
            price_per_unit REAL NOT NULL,
            currency TEXT DEFAULT 'RON',
            vat_rate REAL DEFAULT 19.0,
            is_service BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create currency_exchange table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS currency_exchange (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency_code TEXT NOT NULL,
            exchange_rate REAL NOT NULL,
            reference_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(currency_code, reference_date)
        )
        ''')
        
        # Insert default currencies
        currencies = [
            ('RON', 1.0),
            ('EUR', None),
            ('USD', None),
            ('GBP', None)
        ]
        
        for currency, rate in currencies:
            try:
                cursor.execute('''
                INSERT INTO currency_exchange (currency_code, exchange_rate, reference_date)
                VALUES (?, ?, date('now'))
                ''', (currency, rate))
            except sqlite3.IntegrityError:
                # Skip if already exists
                pass
        
        conn.commit()
        conn.close()
        
        print(f"Database setup completed successfully at {db_path}")
        return True
        
    except Exception as e:
        print(f"Error setting up database: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # Get the database path from command line arguments or use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'facatura.db'
    setup_database(db_path)