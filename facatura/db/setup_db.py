#!/usr/bin/env python3
"""
Database setup script for Facatura - Romanian invoicing application.

This script creates the necessary SQLite database tables for the Facatura application.

How to run:
-----------
On MacOS and Linux:
1. Make the script executable:
   $ chmod +x setup_db.py
2. Run the script:
   $ ./setup_db.py

Alternatively, you can run it with Python directly:
   $ python3 setup_db.py

The script will create a database file named 'facatura.db' in the current directory
if it doesn't exist, or update the schema if the file already exists.
"""

import os
import sqlite3
import sys


def setup_database(db_path='facatura.db'):
    """
    Set up the SQLite database with all necessary tables.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    print(f"Setting up database at {db_path}...")
    
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
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
        vat_number TEXT,
        bank_name TEXT,
        bank_account TEXT,
        email TEXT,
        phone TEXT,
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
        vat_number TEXT,
        bank_name TEXT,
        bank_account TEXT,
        email TEXT,
        phone TEXT,
        contact_person TEXT,
        notes TEXT,
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
        is_service BOOLEAN NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create currency exchange table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS currency_exchange (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        currency_code TEXT NOT NULL,
        exchange_rate REAL NOT NULL,
        date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(currency_code, date)
    )
    ''')
    
    # Insert default currencies
    cursor.execute('''
    INSERT OR IGNORE INTO currency_exchange (currency_code, exchange_rate, date)
    VALUES 
        ('RON', 1.0, date('now')),
        ('EUR', 4.9, date('now')),
        ('USD', 4.5, date('now')),
        ('GBP', 5.7, date('now'))
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database setup completed successfully!")


if __name__ == "__main__":
    # Use the default database path or allow specifying a custom path
    db_path = 'facatura.db'
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    setup_database(db_path)