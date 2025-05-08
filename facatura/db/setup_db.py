#!/usr/bin/env python3
"""
Database setup script for facatura.

This script creates the necessary tables in an SQLite database for the facatura application.

How to run on MacOS and Linux:
1. Make sure you have Python 3.6+ installed
2. Navigate to the project root directory
3. Run: python -m facatura.db.setup_db
   or: python3 -m facatura.db.setup_db

Alternatively, you can use the CLI command:
facatura init
"""

import sqlite3
import sys
import pathlib


# Default database path
DEFAULT_DB_PATH = pathlib.Path.home() / '.facatura' / 'facatura.db'


def create_tables(db_path=None):
    """
    Create the necessary tables in the SQLite database.
    
    Args:
        db_path: Path to the SQLite database file. If None, uses the default path.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    
    # Ensure the directory exists
    db_dir = pathlib.Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Connect to the database (will create it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create companies table (invoice issuers)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            county TEXT NOT NULL,
            postal_code TEXT,
            country TEXT NOT NULL DEFAULT 'Romania',
            registration_number TEXT NOT NULL,
            fiscal_code TEXT NOT NULL,
            bank_name TEXT,
            bank_account TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            logo_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create clients table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            county TEXT NOT NULL,
            postal_code TEXT,
            country TEXT NOT NULL DEFAULT 'Romania',
            registration_number TEXT,
            fiscal_code TEXT NOT NULL,
            bank_name TEXT,
            bank_account TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create products/services table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            unit TEXT NOT NULL,
            price_per_unit REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'RON',
            vat_rate REAL NOT NULL DEFAULT 19.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create currency exchange table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS currency_exchange (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            from_currency TEXT NOT NULL,
            to_currency TEXT NOT NULL,
            rate REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, from_currency, to_currency)
        )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_currency_date ON currency_exchange(date)')
        
        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        
        return True
    
    except sqlite3.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


def main():
    """Main function to run the script directly."""
    db_path = DEFAULT_DB_PATH
    
    # Check if a custom path was provided
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    print(f"Setting up database at: {db_path}")
    
    if create_tables(db_path):
        print("Database setup completed successfully.")
        return 0
    else:
        print("Database setup failed.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())