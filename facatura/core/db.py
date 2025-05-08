"""
Database connection and management for facatura.

This module provides functionality for connecting to and managing the SQLite database
used by the facatura application.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional, Union, Dict, Any, List, Tuple


class Database:
    """Database connection manager for facatura."""

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        """
        Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file. If None, a default path will be used.
        """
        if db_path is None:
            # Use default path in user's home directory
            home_dir = Path.home()
            data_dir = home_dir / ".facatura"
            data_dir.mkdir(exist_ok=True)
            self.db_path = data_dir / "facatura.db"
        else:
            self.db_path = Path(db_path)

        self.conn = None
        self.cursor = None

    def connect(self) -> None:
        """Connect to the database."""
        self.conn = sqlite3.connect(self.db_path)
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Return rows as dictionaries
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def commit(self) -> None:
        """Commit the current transaction."""
        if self.conn:
            self.conn.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""
        if self.conn:
            self.conn.rollback()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a SQL query.

        Args:
            query: SQL query to execute
            params: Parameters for the query

        Returns:
            The cursor object
        """
        if not self.conn:
            self.connect()
        return self.conn.execute(query, params)

    def executemany(self, query: str, params_list: List[tuple]) -> sqlite3.Cursor:
        """
        Execute a SQL query with multiple parameter sets.

        Args:
            query: SQL query to execute
            params_list: List of parameter tuples for the query

        Returns:
            The cursor object
        """
        if not self.conn:
            self.connect()
        return self.conn.executemany(query, params_list)

    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Execute a query and fetch one result.

        Args:
            query: SQL query to execute
            params: Parameters for the query

        Returns:
            A dictionary with the result row or None if no result
        """
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a query and fetch all results.

        Args:
            query: SQL query to execute
            params: Parameters for the query

        Returns:
            A list of dictionaries with the result rows
        """
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def initialize_schema(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        # Create companies table
        self.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            registration_number TEXT NOT NULL UNIQUE,
            vat_number TEXT,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            county TEXT NOT NULL,
            postal_code TEXT,
            country TEXT NOT NULL DEFAULT 'Romania',
            bank_name TEXT,
            bank_account TEXT,
            email TEXT,
            phone TEXT,
            website TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Add more tables as needed for the invoicing application
        
        # Commit the changes
        self.commit()


def get_db(db_path: Optional[Union[str, Path]] = None) -> Database:
    """
    Get a database connection.

    Args:
        db_path: Path to the SQLite database file. If None, a default path will be used.

    Returns:
        A Database instance
    """
    db = Database(db_path)
    db.connect()
    db.initialize_schema()
    return db