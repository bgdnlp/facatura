"""
Database connection manager for the core library.

This module provides a class for managing database connections and executing SQL queries.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union


class DatabaseManager:
    """
    A class for managing database connections and executing SQL queries.
    """

    def __init__(self, db_path: str = 'facatura.db'):
        """
        Initialize the DatabaseManager with a path to the database file.

        Args:
            db_path (str): Path to the database file. Defaults to 'facatura.db'.
        """
        self.db_path = db_path
        self._connection = None

    def connect(self) -> sqlite3.Connection:
        """
        Connect to the database.

        Returns:
            sqlite3.Connection: A connection to the database.
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self) -> None:
        """
        Close the database connection.
        """
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> sqlite3.Cursor:
        """
        Execute a SQL query.

        Args:
            query (str): The SQL query to execute.
            params (Optional[Tuple[Any, ...]]): Parameters for the query.

        Returns:
            sqlite3.Cursor: A cursor object.
        """
        if not self._connection:
            self.connect()
        
        cursor = self._connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor

    def execute_many(self, query: str, params_list: List[Tuple[Any, ...]]) -> sqlite3.Cursor:
        """
        Execute a SQL query with multiple parameter sets.

        Args:
            query (str): The SQL query to execute.
            params_list (List[Tuple[Any, ...]]): List of parameter tuples.

        Returns:
            sqlite3.Cursor: A cursor object.
        """
        if not self._connection:
            self.connect()
        
        cursor = self._connection.cursor()
        cursor.executemany(query, params_list)
        
        return cursor

    def fetch_one(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a SQL query and fetch one result.

        Args:
            query (str): The SQL query to execute.
            params (Optional[Tuple[Any, ...]]): Parameters for the query.

        Returns:
            Optional[Dict[str, Any]]: A dictionary with the result, or None if no result.
        """
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None

    def fetch_all(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and fetch all results.

        Args:
            query (str): The SQL query to execute.
            params (Optional[Tuple[Any, ...]]): Parameters for the query.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries with the results.
        """
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]

    def commit(self) -> None:
        """
        Commit the current transaction.
        """
        if self._connection:
            self._connection.commit()

    def rollback(self) -> None:
        """
        Roll back the current transaction.
        """
        if self._connection:
            self._connection.rollback()

    def __enter__(self) -> 'DatabaseManager':
        """
        Enter a context manager.

        Returns:
            DatabaseManager: The database manager.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit a context manager.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()