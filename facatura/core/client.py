"""
Client management module.

This module provides a class for managing client records.
"""

from typing import Dict, List, Optional, Union
from .db import DatabaseManager
from .bank_account import BankAccount


class Client:
    """
    A class for managing client records.
    """

    def __init__(self, db_path: str = 'facatura.db'):
        """
        Initialize the Client with a path to the database file.

        Args:
            db_path (str): Path to the database file. Defaults to 'facatura.db'.
        """
        self.db_path = db_path
        self.db_manager = DatabaseManager(db_path)
        self.bank_account = BankAccount(db_path)

    def create(self, name: str, address: str, city: str, fiscal_code: str,
               registration_number: Optional[str] = None, county: Optional[str] = None,
               postal_code: Optional[str] = None, country: str = 'Romania',
               vat_payer: bool = True, phone: Optional[str] = None,
               email: Optional[str] = None, website: Optional[str] = None) -> int:
        """
        Create a new client record.

        Args:
            name (str): Client name.
            address (str): Client address.
            city (str): Client city.
            fiscal_code (str): Client fiscal code.
            registration_number (Optional[str]): Client registration number. Defaults to None.
            county (Optional[str]): Client county. Defaults to None.
            postal_code (Optional[str]): Client postal code. Defaults to None.
            country (str): Client country. Defaults to 'Romania'.
            vat_payer (bool): Whether the client is a VAT payer. Defaults to True.
            phone (Optional[str]): Client phone. Defaults to None.
            email (Optional[str]): Client email. Defaults to None.
            website (Optional[str]): Client website. Defaults to None.

        Returns:
            int: ID of the created client.

        Raises:
            ValueError: If name, address, city, or fiscal_code is empty.
            ValueError: If a client with the same fiscal_code already exists.
        """
        # Validate input
        if not name:
            raise ValueError("Client name cannot be empty")
        if not address:
            raise ValueError("Client address cannot be empty")
        if not city:
            raise ValueError("Client city cannot be empty")
        if not fiscal_code:
            raise ValueError("Client fiscal code cannot be empty")

        # Check if a client with the same fiscal code already exists
        with self.db_manager:
            existing = self.db_manager.fetch_one(
                "SELECT id FROM clients WHERE fiscal_code = ?",
                (fiscal_code,)
            )
            if existing:
                raise ValueError(f"A client with fiscal code '{fiscal_code}' already exists")

            # Insert the new client
            cursor = self.db_manager.execute(
                """
                INSERT INTO clients (
                    name, address, city, county, postal_code, country,
                    registration_number, fiscal_code, vat_payer,
                    phone, email, website
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (name, address, city, county, postal_code, country,
                 registration_number, fiscal_code, vat_payer,
                 phone, email, website)
            )
            return cursor.lastrowid

    def get(self, client_id: int) -> Optional[Dict]:
        """
        Get a client by ID.

        Args:
            client_id (int): ID of the client.

        Returns:
            Optional[Dict]: Client data, or None if not found.
        """
        with self.db_manager:
            return self.db_manager.fetch_one(
                "SELECT * FROM clients WHERE id = ?",
                (client_id,)
            )

    def get_by_fiscal_code(self, fiscal_code: str) -> Optional[Dict]:
        """
        Get a client by fiscal code.

        Args:
            fiscal_code (str): Fiscal code of the client.

        Returns:
            Optional[Dict]: Client data, or None if not found.
        """
        with self.db_manager:
            return self.db_manager.fetch_one(
                "SELECT * FROM clients WHERE fiscal_code = ?",
                (fiscal_code,)
            )

    def get_all(self) -> List[Dict]:
        """
        Get all clients.

        Returns:
            List[Dict]: List of client data.
        """
        with self.db_manager:
            return self.db_manager.fetch_all("SELECT * FROM clients")

    def update(self, client_id: int, **kwargs) -> bool:
        """
        Update a client.

        Args:
            client_id (int): ID of the client.
            **kwargs: Fields to update.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            ValueError: If trying to update id.
            ValueError: If trying to update fiscal_code to one that already exists.
        """
        # Check if the client exists
        client = self.get(client_id)
        if not client:
            return False

        # Validate input
        if 'id' in kwargs:
            raise ValueError("Cannot update client ID")

        # Check if fiscal_code is being updated to one that already exists
        if 'fiscal_code' in kwargs and kwargs['fiscal_code'] != client['fiscal_code']:
            with self.db_manager:
                existing = self.db_manager.fetch_one(
                    "SELECT id FROM clients WHERE fiscal_code = ?",
                    (kwargs['fiscal_code'],)
                )
                if existing:
                    raise ValueError(f"A client with fiscal code '{kwargs['fiscal_code']}' already exists")

        # Build the update query
        allowed_fields = {
            'name', 'address', 'city', 'county', 'postal_code', 'country',
            'registration_number', 'fiscal_code', 'vat_payer',
            'phone', 'email', 'website', 'default_bank_account'
        }
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return True  # Nothing to update

        set_clause = ", ".join(f"{field} = ?" for field in update_fields)
        values = list(update_fields.values())
        values.append(client_id)

        # Update the client
        with self.db_manager:
# Update the client
        with self.db_manager:
            try:
                cursor = self.db_manager.execute(
                    f"UPDATE clients SET {set_clause} WHERE id = ?",
                    tuple(values)
                )
                return cursor.rowcount > 0
            except Exception as e:
                # Log the error
                print(f"Error updating client: {str(e)}")
                return False

    def delete(self, client_id: int) -> bool:
        """
                f"UPDATE clients SET {set_clause} WHERE id = ?",
                tuple(values)
            )
            return cursor.rowcount > 0

    def delete(self, client_id: int) -> bool:
        """
        Delete a client.

        Args:
            client_id (int): ID of the client.

        Returns:
            bool: True if successful, False otherwise.
        """
        # Get all bank accounts for this client
        bank_accounts = self.bank_account.get_by_entity(client_id, 'client')
        
bank_accounts = self.bank_account.get_by_entity(client_id, 'client')
        
        with self.db_manager:
            try:
                # Delete all bank accounts for this client
                for account in bank_accounts:
                    self.db_manager.execute(
                        "DELETE FROM bank_accounts WHERE id = ?",
                        (account['id'],)
                    )
                
                # Delete the client
                cursor = self.db_manager.execute(
                    "DELETE FROM clients WHERE id = ?",
                    (client_id,)
                )
                return cursor.rowcount > 0
            except Exception as e:
                # Log the error and rollback the transaction
                print(f"Error deleting client: {str(e)}")
                self.db_manager.rollback()
                return False

    def add_bank_account(self, client_id: int, bank_name: str, account_number: str,
                         swift_code: Optional[str] = None, iban: Optional[str] = None,
            # Delete all bank accounts for this client
            for account in bank_accounts:
                self.db_manager.execute(
                    "DELETE FROM bank_accounts WHERE id = ?",
                    (account['id'],)
                )
            
            # Delete the client
            cursor = self.db_manager.execute(
                "DELETE FROM clients WHERE id = ?",
                (client_id,)
            )
            return cursor.rowcount > 0

    def add_bank_account(self, client_id: int, bank_name: str, account_number: str,
                         swift_code: Optional[str] = None, iban: Optional[str] = None,
                         currency: str = 'RON', is_default: bool = False) -> int:
        """
        Add a bank account to a client.

        Args:
            client_id (int): ID of the client.
            bank_name (str): Name of the bank.
            account_number (str): Account number.
            swift_code (Optional[str]): SWIFT code. Defaults to None.
            iban (Optional[str]): IBAN. Defaults to None.
            currency (str): Currency. Defaults to 'RON'.
            is_default (bool): Whether this is the default account. Defaults to False.

        Returns:
            int: ID of the created bank account.

        Raises:
            ValueError: If the client does not exist.
        """
        # Check if the client exists
        client = self.get(client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} does not exist")

        # Create the bank account
        account_id = self.bank_account.create(
            bank_name, account_number, client_id, 'client',
            swift_code, iban, currency, is_default
        )

        # If this is the default account, update the client
        if is_default:
            self.update(client_id, default_bank_account=account_id)

        return account_id

    def get_bank_accounts(self, client_id: int) -> List[Dict]:
        """
        Get all bank accounts for a client.

        Args:
            client_id (int): ID of the client.

        Returns:
            List[Dict]: List of bank account data.

        Raises:
            ValueError: If the client does not exist.
        """
        # Check if the client exists
        client = self.get(client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} does not exist")

        # Get all bank accounts for this client
        return self.bank_account.get_by_entity(client_id, 'client')

    def set_default_bank_account(self, client_id: int, account_id: int) -> bool:
        """
        Set a bank account as the default for a client.

        Args:
            client_id (int): ID of the client.
            account_id (int): ID of the bank account.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            ValueError: If the client does not exist.
            ValueError: If the bank account does not exist or does not belong to the client.
        """
        # Check if the client exists
        client = self.get(client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} does not exist")

        # Check if the bank account exists and belongs to the client
        account = self.bank_account.get(account_id)
        if not account or account['entity_id'] != client_id or account['entity_type'] != 'client':
            raise ValueError(f"Bank account with ID {account_id} does not exist or does not belong to the client")

        # Set the bank account as default
        if self.bank_account.set_default(account_id):
            # Update the client's default bank account
            return self.update(client_id, default_bank_account=account_id)
        return False