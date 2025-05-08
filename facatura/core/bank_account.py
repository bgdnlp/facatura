"""
Bank account management module.

This module provides a class for managing bank account records.
"""

from typing import Dict, List, Optional, Union
from .db import DatabaseManager


class BankAccount:
    """
    A class for managing bank account records.
    """

    def __init__(self, db_path: str = 'facatura.db'):
        """
        Initialize the BankAccount with a path to the database file.

        Args:
            db_path (str): Path to the database file. Defaults to 'facatura.db'.
        """
        self.db_manager = DatabaseManager(db_path)

    def create(self, bank_name: str, account_number: str, entity_id: int, entity_type: str,
               swift_code: Optional[str] = None, iban: Optional[str] = None,
               currency: str = 'RON', is_default: bool = False) -> int:
        """
        Create a new bank account record.

        Args:
            bank_name (str): Name of the bank.
            account_number (str): Account number.
            entity_id (int): ID of the entity (company or client).
            entity_type (str): Type of the entity ('company' or 'client').
            swift_code (Optional[str]): SWIFT code. Defaults to None.
            iban (Optional[str]): IBAN. Defaults to None.
            currency (str): Currency. Defaults to 'RON'.
            is_default (bool): Whether this is the default account. Defaults to False.

        Returns:
            int: ID of the created bank account.

        Raises:
            ValueError: If entity_type is not 'company' or 'client'.
            ValueError: If bank_name or account_number is empty.
            ValueError: If entity_id is not a positive integer.
        """
        # Validate input
        if not bank_name:
            raise ValueError("Bank name cannot be empty")
        if not account_number:
            raise ValueError("Account number cannot be empty")
        if entity_id <= 0:
            raise ValueError("Entity ID must be a positive integer")
        if entity_type not in ('company', 'client'):
            raise ValueError("Entity type must be 'company' or 'client'")

        # If this is set as default, unset any existing default for this entity
        if is_default:
            with self.db_manager:
                self.db_manager.execute(
                    "UPDATE bank_accounts SET is_default = 0 WHERE entity_id = ? AND entity_type = ?",
                    (entity_id, entity_type)
                )

        # Insert the new bank account
        with self.db_manager:
            cursor = self.db_manager.execute(
                """
                INSERT INTO bank_accounts (
                    bank_name, account_number, swift_code, iban, currency, entity_id, entity_type, is_default
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (bank_name, account_number, swift_code, iban, currency, entity_id, entity_type, is_default)
            )
            return cursor.lastrowid

    def get(self, account_id: int) -> Optional[Dict]:
        """
        Get a bank account by ID.

        Args:
            account_id (int): ID of the bank account.

        Returns:
            Optional[Dict]: Bank account data, or None if not found.
        """
        with self.db_manager:
            return self.db_manager.fetch_one(
                "SELECT * FROM bank_accounts WHERE id = ?",
                (account_id,)
            )

    def get_by_entity(self, entity_id: int, entity_type: str) -> List[Dict]:
        """
        Get all bank accounts for an entity.

        Args:
            entity_id (int): ID of the entity (company or client).
            entity_type (str): Type of the entity ('company' or 'client').

        Returns:
            List[Dict]: List of bank account data.

        Raises:
            ValueError: If entity_type is not 'company' or 'client'.
        """
        if entity_type not in ('company', 'client'):
            raise ValueError("Entity type must be 'company' or 'client'")

        with self.db_manager:
            return self.db_manager.fetch_all(
                "SELECT * FROM bank_accounts WHERE entity_id = ? AND entity_type = ?",
                (entity_id, entity_type)
            )

    def get_default(self, entity_id: int, entity_type: str) -> Optional[Dict]:
        """
        Get the default bank account for an entity.

        Args:
            entity_id (int): ID of the entity (company or client).
            entity_type (str): Type of the entity ('company' or 'client').

        Returns:
            Optional[Dict]: Default bank account data, or None if not found.

        Raises:
            ValueError: If entity_type is not 'company' or 'client'.
        """
        if entity_type not in ('company', 'client'):
            raise ValueError("Entity type must be 'company' or 'client'")

        with self.db_manager:
            return self.db_manager.fetch_one(
                "SELECT * FROM bank_accounts WHERE entity_id = ? AND entity_type = ? AND is_default = 1",
                (entity_id, entity_type)
            )

    def update(self, account_id: int, **kwargs) -> bool:
        """
        Update a bank account.

        Args:
            account_id (int): ID of the bank account.
            **kwargs: Fields to update.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            ValueError: If trying to update id, entity_id, or entity_type.
        """
        # Check if the bank account exists
        account = self.get(account_id)
        if not account:
            return False

        # Validate input
        if 'id' in kwargs:
            raise ValueError("Cannot update account ID")
        if 'entity_id' in kwargs:
            raise ValueError("Cannot update entity ID")
        if 'entity_type' in kwargs:
            raise ValueError("Cannot update entity type")

        # If setting as default, unset any existing default
        if kwargs.get('is_default'):
            with self.db_manager:
                self.db_manager.execute(
                    "UPDATE bank_accounts SET is_default = 0 WHERE entity_id = ? AND entity_type = ?",
                    (account['entity_id'], account['entity_type'])
                )

        # Build the update query
        allowed_fields = {'bank_name', 'account_number', 'swift_code', 'iban', 'currency', 'is_default'}
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return True  # Nothing to update

        set_clause = ", ".join(f"{field} = ?" for field in update_fields)
        values = list(update_fields.values())
        values.append(account_id)

        # Update the bank account
        with self.db_manager:
            cursor = self.db_manager.execute(
                f"UPDATE bank_accounts SET {set_clause} WHERE id = ?",
                tuple(values)
            )
            return cursor.rowcount > 0

    def delete(self, account_id: int) -> bool:
        """
        Delete a bank account.

        Args:
            account_id (int): ID of the bank account.

        Returns:
            bool: True if successful, False otherwise.
        """
        with self.db_manager:
            cursor = self.db_manager.execute(
                "DELETE FROM bank_accounts WHERE id = ?",
                (account_id,)
            )
            return cursor.rowcount > 0

    def set_default(self, account_id: int) -> bool:
        """
        Set a bank account as the default for its entity.

        Args:
            account_id (int): ID of the bank account.

        Returns:
            bool: True if successful, False otherwise.
        """
        # Get the bank account to find its entity
        account = self.get(account_id)
        if not account:
            return False

        # Unset any existing default
        with self.db_manager:
            self.db_manager.execute(
                "UPDATE bank_accounts SET is_default = 0 WHERE entity_id = ? AND entity_type = ?",
                (account['entity_id'], account['entity_type'])
            )
            
            # Set this account as default
            cursor = self.db_manager.execute(
                "UPDATE bank_accounts SET is_default = 1 WHERE id = ?",
                (account_id,)
            )
            return cursor.rowcount > 0