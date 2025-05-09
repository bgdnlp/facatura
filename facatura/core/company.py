"""
Company management module.

This module provides a class for managing company records.
"""

from typing import Dict, List, Optional, Union
from .db import DatabaseManager
from .bank_account import BankAccount


class Company:
    """
    A class for managing company records.
    """

    def __init__(self, db_path: str = 'facatura.db'):
        """
        Initialize the Company with a path to the database file.

        Args:
            db_path (str): Path to the database file. Defaults to 'facatura.db'.
        """
        self.db_path = db_path
        self.db_manager = DatabaseManager(db_path)
        self.bank_account = BankAccount(db_path)

    def create(self, name: str, address: str, city: str, registration_number: str, fiscal_code: str,
               county: Optional[str] = None, postal_code: Optional[str] = None,
               country: str = 'Romania', vat_payer: bool = True, phone: Optional[str] = None,
               email: Optional[str] = None, website: Optional[str] = None,
               logo_path: Optional[str] = None) -> int:
        """
        Create a new company record.

        Args:
            name (str): Company name.
            address (str): Company address.
            city (str): Company city.
            registration_number (str): Company registration number.
            fiscal_code (str): Company fiscal code.
            county (Optional[str]): Company county. Defaults to None.
            postal_code (Optional[str]): Company postal code. Defaults to None.
            country (str): Company country. Defaults to 'Romania'.
            vat_payer (bool): Whether the company is a VAT payer. Defaults to True.
            phone (Optional[str]): Company phone. Defaults to None.
            email (Optional[str]): Company email. Defaults to None.
            website (Optional[str]): Company website. Defaults to None.
            logo_path (Optional[str]): Path to company logo. Defaults to None.

        Returns:
            int: ID of the created company.

        Raises:
            ValueError: If name, address, city, registration_number, or fiscal_code is empty.
            ValueError: If a company with the same fiscal_code already exists.
        """
        # Validate input
        if not name:
            raise ValueError("Company name cannot be empty")
        if not address:
            raise ValueError("Company address cannot be empty")
        if not city:
            raise ValueError("Company city cannot be empty")
        if not registration_number:
            raise ValueError("Company registration number cannot be empty")
        if not fiscal_code:
            raise ValueError("Company fiscal code cannot be empty")

        # Check if a company with the same fiscal code already exists
        with self.db_manager:
            existing = self.db_manager.fetch_one(
                "SELECT id FROM companies WHERE fiscal_code = ?",
                (fiscal_code,)
            )
            if existing:
                raise ValueError(f"A company with fiscal code '{fiscal_code}' already exists")

            # Insert the new company
            cursor = self.db_manager.execute(
                """
                INSERT INTO companies (
                    name, address, city, county, postal_code, country,
                    registration_number, fiscal_code, vat_payer,
                    phone, email, website, logo_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (name, address, city, county, postal_code, country,
                 registration_number, fiscal_code, vat_payer,
                 phone, email, website, logo_path)
            )
            return cursor.lastrowid

    def get(self, company_id: int) -> Optional[Dict]:
        """
        Get a company by ID.

        Args:
            company_id (int): ID of the company.

        Returns:
            Optional[Dict]: Company data, or None if not found.
        """
        with self.db_manager:
            return self.db_manager.fetch_one(
                "SELECT * FROM companies WHERE id = ?",
                (company_id,)
            )

    def get_by_fiscal_code(self, fiscal_code: str) -> Optional[Dict]:
        """
        Get a company by fiscal code.

        Args:
            fiscal_code (str): Fiscal code of the company.

        Returns:
            Optional[Dict]: Company data, or None if not found.
        """
        with self.db_manager:
            return self.db_manager.fetch_one(
                "SELECT * FROM companies WHERE fiscal_code = ?",
                (fiscal_code,)
            )

    def get_all(self) -> List[Dict]:
        """
        Get all companies.

        Returns:
            List[Dict]: List of company data.
        """
        with self.db_manager:
            return self.db_manager.fetch_all("SELECT * FROM companies")

    def update(self, company_id: int, **kwargs) -> bool:
        """
        Update a company.

        Args:
            company_id (int): ID of the company.
            **kwargs: Fields to update.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            ValueError: If trying to update id.
            ValueError: If trying to update fiscal_code to one that already exists.
        """
        # Check if the company exists
        company = self.get(company_id)
        if not company:
            return False

        # Validate input
        if 'id' in kwargs:
            raise ValueError("Cannot update company ID")

        # Check if fiscal_code is being updated to one that already exists
        if 'fiscal_code' in kwargs and kwargs['fiscal_code'] != company['fiscal_code']:
            with self.db_manager:
                existing = self.db_manager.fetch_one(
                    "SELECT id FROM companies WHERE fiscal_code = ?",
                    (kwargs['fiscal_code'],)
                )
                if existing:
                    raise ValueError(f"A company with fiscal code '{kwargs['fiscal_code']}' already exists")

        # Build the update query
        allowed_fields = {
            'name', 'address', 'city', 'county', 'postal_code', 'country',
            'registration_number', 'fiscal_code', 'vat_payer',
            'phone', 'email', 'website', 'logo_path', 'default_bank_account'
        }
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return True  # Nothing to update

        set_clause = ", ".join(f"{field} = ?" for field in update_fields)
        values = list(update_fields.values())
        values.append(company_id)

        # Update the company
        with self.db_manager:
# Update the company
        with self.db_manager:
            try:
                cursor = self.db_manager.execute(
                    f"UPDATE companies SET {set_clause} WHERE id = ?",
                    tuple(values)
                )
                return cursor.rowcount > 0
            except Exception as e:
                # Log the error
                print(f"Error updating company: {str(e)}")
                return False

    def delete(self, company_id: int) -> bool:
        """
                f"UPDATE companies SET {set_clause} WHERE id = ?",
                tuple(values)
            )
            return cursor.rowcount > 0

    def delete(self, company_id: int) -> bool:
        """
        Delete a company.

        Args:
            company_id (int): ID of the company.

        Returns:
            bool: True if successful, False otherwise.
        """
        # Get all bank accounts for this company
        bank_accounts = self.bank_account.get_by_entity(company_id, 'company')
        
bank_accounts = self.bank_account.get_by_entity(company_id, 'company')
        
        with self.db_manager:
            try:
                # Delete all bank accounts for this company
                for account in bank_accounts:
                    self.db_manager.execute(
                        "DELETE FROM bank_accounts WHERE id = ?",
                        (account['id'],)
                    )
                
                # Delete the company
                cursor = self.db_manager.execute(
                    "DELETE FROM companies WHERE id = ?",
                    (company_id,)
                )
                return cursor.rowcount > 0
            except Exception as e:
                self.db_manager.rollback()
                # TODO: Implement proper logging
                print(f"Error deleting company: {e}")
                return False

    def add_bank_account(self, company_id: int, bank_name: str, account_number: str,
                         swift_code: Optional[str] = None, iban: Optional[str] = None,
            # Delete all bank accounts for this company
            for account in bank_accounts:
                self.db_manager.execute(
                    "DELETE FROM bank_accounts WHERE id = ?",
                    (account['id'],)
                )
            
            # Delete the company
            cursor = self.db_manager.execute(
                "DELETE FROM companies WHERE id = ?",
                (company_id,)
            )
            return cursor.rowcount > 0

    def add_bank_account(self, company_id: int, bank_name: str, account_number: str,
                         swift_code: Optional[str] = None, iban: Optional[str] = None,
                         currency: str = 'RON', is_default: bool = False) -> int:
        """
        Add a bank account to a company.

        Args:
            company_id (int): ID of the company.
            bank_name (str): Name of the bank.
            account_number (str): Account number.
            swift_code (Optional[str]): SWIFT code. Defaults to None.
            iban (Optional[str]): IBAN. Defaults to None.
            currency (str): Currency. Defaults to 'RON'.
            is_default (bool): Whether this is the default account. Defaults to False.

        Returns:
            int: ID of the created bank account.

        Raises:
            ValueError: If the company does not exist.
        """
        # Check if the company exists
        company = self.get(company_id)
        if not company:
            raise ValueError(f"Company with ID {company_id} does not exist")

        # Create the bank account
        account_id = self.bank_account.create(
            bank_name, account_number, company_id, 'company',
            swift_code, iban, currency, is_default
        )

        # If this is the default account, update the company
        if is_default:
            self.update(company_id, default_bank_account=account_id)

        return account_id

    def get_bank_accounts(self, company_id: int) -> List[Dict]:
        """
        Get all bank accounts for a company.

        Args:
            company_id (int): ID of the company.

        Returns:
            List[Dict]: List of bank account data.

        Raises:
            ValueError: If the company does not exist.
        """
        # Check if the company exists
        company = self.get(company_id)
        if not company:
            raise ValueError(f"Company with ID {company_id} does not exist")

        # Get all bank accounts for this company
        return self.bank_account.get_by_entity(company_id, 'company')

    def set_default_bank_account(self, company_id: int, account_id: int) -> bool:
        """
        Set a bank account as the default for a company.

        Args:
            company_id (int): ID of the company.
            account_id (int): ID of the bank account.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            ValueError: If the company does not exist.
            ValueError: If the bank account does not exist or does not belong to the company.
        """
        # Check if the company exists
        company = self.get(company_id)
        if not company:
            raise ValueError(f"Company with ID {company_id} does not exist")

        # Check if the bank account exists and belongs to the company
        account = self.bank_account.get(account_id)
        if not account or account['entity_id'] != company_id or account['entity_type'] != 'company':
            raise ValueError(f"Bank account with ID {account_id} does not exist or does not belong to the company")

        # Set the bank account as default
        if self.bank_account.set_default(account_id):
            # Update the company's default bank account
            return self.update(company_id, default_bank_account=account_id)
        return False