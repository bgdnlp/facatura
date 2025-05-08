"""
Company management module for facatura.

This module provides functionality for managing company records in the database.
"""

import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from facatura.core.db import Database, get_db


class CompanyError(Exception):
    """Base exception for company-related errors."""
    pass


class CompanyNotFoundError(CompanyError):
    """Exception raised when a company is not found."""
    pass


class CompanyValidationError(CompanyError):
    """Exception raised when company data validation fails."""
    pass


class CompanyManager:
    """Class for managing company records in the database."""

    def __init__(self, db: Optional[Database] = None):
        """
        Initialize the company manager.

        Args:
            db: Database instance. If None, a new connection will be created.
        """
        self.db = db if db is not None else get_db()

    def close(self) -> None:
        """Close the database connection."""
        if self.db:
            self.db.close()

    def validate_company_data(self, data: Dict[str, Any]) -> None:
        """
        Validate company data.

        Args:
            data: Company data to validate

        Raises:
            CompanyValidationError: If validation fails
        """
        errors = []

        # Check required fields
        required_fields = ['name', 'registration_number', 'address', 'city', 'county', 'country']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Field '{field}' is required")

        # Validate registration number (CUI) format - basic validation for Romanian CUI
        if 'registration_number' in data and data['registration_number']:
            reg_num = data['registration_number'].strip()
            if not re.match(r'^RO?\d{6,10}$', reg_num) and not re.match(r'^\d{6,10}$', reg_num):
                errors.append("Invalid registration number format. Expected format: RO###### or ######")

        # Validate VAT number if provided
        if 'vat_number' in data and data['vat_number']:
            vat = data['vat_number'].strip()
            if not re.match(r'^[A-Z]{2}\d{2,12}$', vat):
                errors.append("Invalid VAT number format. Expected format: XX##### (country code + numbers)")

        # Validate email if provided
        if 'email' in data and data['email']:
            email = data['email'].strip()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors.append("Invalid email format")

        # Validate phone if provided
        if 'phone' in data and data['phone']:
            phone = data['phone'].strip()
            if not re.match(r'^\+?[0-9\s\-()]{8,20}$', phone):
                errors.append("Invalid phone number format")

        # Validate website if provided
        if 'website' in data and data['website']:
            website = data['website'].strip()
            if not re.match(r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/?.*$', website):
                errors.append("Invalid website format. Expected format: http(s)://example.com")

        if errors:
            raise CompanyValidationError("\n".join(errors))

    def create_company(self, company_data: Dict[str, Any]) -> int:
        """
        Create a new company record.

        Args:
            company_data: Dictionary containing company data

        Returns:
            The ID of the newly created company

        Raises:
            CompanyValidationError: If validation fails
        """
        # Validate the company data
        self.validate_company_data(company_data)

        # Prepare the data for insertion
        fields = []
        placeholders = []
        values = []

        for key, value in company_data.items():
            if key != 'id':  # Skip ID field as it's auto-generated
                fields.append(key)
                placeholders.append('?')
                values.append(value)

        # Build the SQL query
        query = f'''
        INSERT INTO companies ({', '.join(fields)})
        VALUES ({', '.join(placeholders)})
        '''

        try:
            cursor = self.db.execute(query, tuple(values))
            self.db.commit()
            return cursor.lastrowid
        except Exception as e:
            self.db.rollback()
            if "UNIQUE constraint failed: companies.registration_number" in str(e):
                raise CompanyValidationError(
                    f"A company with registration number '{company_data.get('registration_number')}' already exists"
                ) from e
            raise CompanyError(f"Failed to create company: {str(e)}") from e

    def get_company(self, company_id: int) -> Dict[str, Any]:
        """
        Get a company by ID.

        Args:
            company_id: The ID of the company to retrieve

        Returns:
            A dictionary containing the company data

        Raises:
            CompanyNotFoundError: If the company is not found
        """
        company = self.db.fetchone(
            "SELECT * FROM companies WHERE id = ?",
            (company_id,)
        )

        if not company:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")

        return company

    def get_company_by_registration_number(self, registration_number: str) -> Dict[str, Any]:
        """
        Get a company by registration number.

        Args:
            registration_number: The registration number of the company to retrieve

        Returns:
            A dictionary containing the company data

        Raises:
            CompanyNotFoundError: If the company is not found
        """
        company = self.db.fetchone(
            "SELECT * FROM companies WHERE registration_number = ?",
            (registration_number,)
        )

        if not company:
            raise CompanyNotFoundError(f"Company with registration number {registration_number} not found")

        return company

    def list_companies(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List companies, optionally filtered.

        Args:
            filters: Dictionary of field-value pairs to filter by

        Returns:
            A list of dictionaries containing company data
        """
        query = "SELECT * FROM companies"
        params = []

        if filters:
            conditions = []
            for field, value in filters.items():
                if field in ['name', 'city', 'county', 'country']:
                    conditions.append(f"{field} LIKE ?")
                    params.append(f"%{value}%")
                else:
                    conditions.append(f"{field} = ?")
                    params.append(value)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY name"
        return self.db.fetchall(query, tuple(params))

    def update_company(self, company_id: int, company_data: Dict[str, Any]) -> None:
        """
        Update a company record.

        Args:
            company_id: The ID of the company to update
            company_data: Dictionary containing updated company data

        Raises:
            CompanyNotFoundError: If the company is not found
            CompanyValidationError: If validation fails
        """
        # Check if the company exists
        self.get_company(company_id)

        # Validate the company data
        self.validate_company_data(company_data)

        # Prepare the data for update
        set_clauses = []
        values = []

        for key, value in company_data.items():
            if key != 'id':  # Skip ID field as it can't be updated
                set_clauses.append(f"{key} = ?")
                values.append(value)

        # Add updated_at timestamp
        set_clauses.append("updated_at = ?")
        values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # Add the company ID to the values
        values.append(company_id)

        # Build the SQL query
        query = f'''
        UPDATE companies
        SET {', '.join(set_clauses)}
        WHERE id = ?
        '''

        try:
            self.db.execute(query, tuple(values))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            if "UNIQUE constraint failed: companies.registration_number" in str(e):
                raise CompanyValidationError(
                    f"A company with registration number '{company_data.get('registration_number')}' already exists"
                ) from e
            raise CompanyError(f"Failed to update company: {str(e)}") from e

    def delete_company(self, company_id: int) -> None:
        """
        Delete a company record.

        Args:
            company_id: The ID of the company to delete

        Raises:
            CompanyNotFoundError: If the company is not found
        """
        # Check if the company exists
        self.get_company(company_id)

        try:
            self.db.execute("DELETE FROM companies WHERE id = ?", (company_id,))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise CompanyError(f"Failed to delete company: {str(e)}") from e