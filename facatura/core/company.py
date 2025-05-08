"""
Company management module for facatura.

This module provides the CompanyManager class for managing company records in the database.
"""

import sqlite3
from typing import Dict, List, Optional, Tuple, Union


class CompanyManager:
    """
    Class for managing company records in the database.
    
    This class provides methods for creating, retrieving, updating, and deleting
    company records in the database.
    """
    
    def __init__(self, db_path: str = 'facatura.db'):
        """
        Initialize the CompanyManager with a database connection.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a connection to the database.
        
        Returns:
            sqlite3.Connection: A connection to the database
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    
    def create_company(self, company_data: Dict[str, any]) -> Tuple[bool, Union[int, str]]:
        """
        Create a new company record in the database.
        
        Args:
            company_data (Dict[str, any]): Dictionary containing company data with the following keys:
                - name: Company name (required)
                - address: Company address (required)
                - city: Company city (required)
                - county: Company county (optional)
                - postal_code: Company postal code (optional)
                - country: Company country (default: Romania)
                - registration_number: Company registration number (required)
                - fiscal_code: Company fiscal code (required)
                - vat_payer: Whether the company is a VAT payer (default: True)
                - phone: Company phone number (optional)
                - email: Company email (optional)
                - website: Company website (optional)
                - logo_path: Path to company logo (optional)
        
        Returns:
            Tuple[bool, Union[int, str]]: A tuple containing:
                - bool: True if successful, False otherwise
                - Union[int, str]: If successful, the ID of the new company; otherwise, an error message
        """
        # Validate required fields
        required_fields = ['name', 'address', 'city', 'registration_number', 'fiscal_code']
        for field in required_fields:
            if field not in company_data or not company_data[field]:
                return False, f"Missing required field: {field}"
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Prepare the SQL query
            fields = []
            placeholders = []
            values = []
            
            for key, value in company_data.items():
                fields.append(key)
                placeholders.append('?')
                values.append(value)
            
            query = f'''
            INSERT INTO companies ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
            '''
            
            cursor.execute(query, values)
            company_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return True, company_id
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: companies.fiscal_code" in str(e):
                return False, "A company with this fiscal code already exists"
            return False, str(e)
        except Exception as e:
            return False, str(e)
    
    def get_company_by_id(self, company_id: int) -> Tuple[bool, Union[Dict[str, any], str]]:
        """
        Get a company by its ID.
        
        Args:
            company_id (int): The ID of the company to retrieve
        
        Returns:
            Tuple[bool, Union[Dict[str, any], str]]: A tuple containing:
                - bool: True if successful, False otherwise
                - Union[Dict[str, any], str]: If successful, a dictionary containing the company data;
                  otherwise, an error message
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM companies WHERE id = ?', (company_id,))
            company = cursor.fetchone()
            conn.close()
            
            if company:
                return True, dict(company)
            else:
                return False, f"No company found with ID {company_id}"
            
        except Exception as e:
            return False, str(e)
    
    def get_company_by_fiscal_code(self, fiscal_code: str) -> Tuple[bool, Union[Dict[str, any], str]]:
        """
        Get a company by its fiscal code.
        
        Args:
            fiscal_code (str): The fiscal code of the company to retrieve
        
        Returns:
            Tuple[bool, Union[Dict[str, any], str]]: A tuple containing:
                - bool: True if successful, False otherwise
                - Union[Dict[str, any], str]: If successful, a dictionary containing the company data;
                  otherwise, an error message
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM companies WHERE fiscal_code = ?', (fiscal_code,))
            company = cursor.fetchone()
            conn.close()
            
            if company:
                return True, dict(company)
            else:
                return False, f"No company found with fiscal code {fiscal_code}"
            
        except Exception as e:
            return False, str(e)
    
    def update_company(self, company_id: int, company_data: Dict[str, any]) -> Tuple[bool, str]:
        """
        Update a company record in the database.
        
        Args:
            company_id (int): The ID of the company to update
            company_data (Dict[str, any]): Dictionary containing the company data to update
        
        Returns:
            Tuple[bool, str]: A tuple containing:
                - bool: True if successful, False otherwise
                - str: A success or error message
        """
        if not company_data:
            return False, "No data provided for update"
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if the company exists
            cursor.execute('SELECT id FROM companies WHERE id = ?', (company_id,))
            if not cursor.fetchone():
                conn.close()
                return False, f"No company found with ID {company_id}"
            
            # Prepare the SQL query
            set_clause = []
            values = []
            
            for key, value in company_data.items():
                set_clause.append(f"{key} = ?")
                values.append(value)
            
            # Add the company_id to the values
            values.append(company_id)
            
            query = f'''
            UPDATE companies
            SET {', '.join(set_clause)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            '''
            
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount > 0:
                conn.close()
                return True, f"Company with ID {company_id} updated successfully"
            else:
                conn.close()
                return False, f"No changes made to company with ID {company_id}"
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: companies.fiscal_code" in str(e):
                return False, "A company with this fiscal code already exists"
            return False, str(e)
        except Exception as e:
            return False, str(e)
    
    def delete_company(self, company_id: int) -> Tuple[bool, str]:
        """
        Delete a company record from the database.
        
        Args:
            company_id (int): The ID of the company to delete
        
        Returns:
            Tuple[bool, str]: A tuple containing:
                - bool: True if successful, False otherwise
                - str: A success or error message
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if the company exists
            cursor.execute('SELECT id FROM companies WHERE id = ?', (company_id,))
            if not cursor.fetchone():
                conn.close()
                return False, f"No company found with ID {company_id}"
            
            # Delete the company
            cursor.execute('DELETE FROM companies WHERE id = ?', (company_id,))
            conn.commit()
            conn.close()
            
            return True, f"Company with ID {company_id} deleted successfully"
            
        except Exception as e:
            return False, str(e)
    
    def list_companies(self, filters: Optional[Dict[str, any]] = None) -> Tuple[bool, Union[List[Dict[str, any]], str]]:
        """
        List all companies in the database, optionally filtered.
        
        Args:
            filters (Optional[Dict[str, any]]): Optional dictionary of filters to apply
        
        Returns:
            Tuple[bool, Union[List[Dict[str, any]], str]]: A tuple containing:
                - bool: True if successful, False otherwise
                - Union[List[Dict[str, any]], str]: If successful, a list of dictionaries containing company data;
                  otherwise, an error message
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = 'SELECT * FROM companies'
            values = []
            
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    where_clauses.append(f"{key} = ?")
                    values.append(value)
                
                if where_clauses:
                    query += f" WHERE {' AND '.join(where_clauses)}"
            
            cursor.execute(query, values)
            companies = [dict(company) for company in cursor.fetchall()]
            conn.close()
            
            return True, companies
            
        except Exception as e:
            return False, str(e)