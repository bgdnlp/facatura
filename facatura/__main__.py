#!/usr/bin/env python3
"""
Main entry point for the Facatura application.
"""

import os
import sys
import argparse

from facatura.db.setup_db import setup_database
from facatura.core.company import CompanyManager


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Facatura - Romanian invoicing application')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Setup database command
    setup_parser = subparsers.add_parser('setup-db', help='Set up the database')
    setup_parser.add_argument('--db-path', default='facatura.db', 
                             help='Path to the database file (default: facatura.db)')
    
    # Company management commands
    company_parser = subparsers.add_parser('company', help='Manage company records')
    company_subparsers = company_parser.add_subparsers(dest='company_command', help='Company command to run')
    
    # Create company command
    create_company_parser = company_subparsers.add_parser('create', help='Create a new company record')
    create_company_parser.add_argument('--db-path', default='facatura.db', help='Path to the database file')
    create_company_parser.add_argument('--name', required=True, help='Company name')
    create_company_parser.add_argument('--address', required=True, help='Company address')
    create_company_parser.add_argument('--city', required=True, help='Company city')
    create_company_parser.add_argument('--county', help='Company county')
    create_company_parser.add_argument('--postal-code', help='Company postal code')
    create_company_parser.add_argument('--country', default='Romania', help='Company country')
    create_company_parser.add_argument('--registration-number', required=True, help='Company registration number')
    create_company_parser.add_argument('--fiscal-code', required=True, help='Company fiscal code')
    create_company_parser.add_argument('--vat-payer', action='store_true', default=True, help='Company is a VAT payer')
    create_company_parser.add_argument('--no-vat-payer', action='store_false', dest='vat_payer', help='Company is not a VAT payer')
    create_company_parser.add_argument('--phone', help='Company phone number')
    create_company_parser.add_argument('--email', help='Company email')
    create_company_parser.add_argument('--website', help='Company website')
    create_company_parser.add_argument('--logo-path', help='Path to company logo')
    
    # Get company command
    get_company_parser = company_subparsers.add_parser('get', help='Get a company record')
    get_company_parser.add_argument('--db-path', default='facatura.db', help='Path to the database file')
    get_company_parser.add_argument('--id', type=int, help='Company ID')
    get_company_parser.add_argument('--fiscal-code', help='Company fiscal code')
    
    # Update company command
    update_company_parser = company_subparsers.add_parser('update', help='Update a company record')
    update_company_parser.add_argument('--db-path', default='facatura.db', help='Path to the database file')
    update_company_parser.add_argument('--id', required=True, type=int, help='Company ID')
    update_company_parser.add_argument('--name', help='Company name')
    update_company_parser.add_argument('--address', help='Company address')
    update_company_parser.add_argument('--city', help='Company city')
    update_company_parser.add_argument('--county', help='Company county')
    update_company_parser.add_argument('--postal-code', help='Company postal code')
    update_company_parser.add_argument('--country', help='Company country')
    update_company_parser.add_argument('--registration-number', help='Company registration number')
    update_company_parser.add_argument('--fiscal-code', help='Company fiscal code')
    update_company_parser.add_argument('--vat-payer', action='store_true', dest='vat_payer', help='Company is a VAT payer')
    update_company_parser.add_argument('--no-vat-payer', action='store_false', dest='vat_payer', help='Company is not a VAT payer')
    update_company_parser.add_argument('--phone', help='Company phone number')
    update_company_parser.add_argument('--email', help='Company email')
    update_company_parser.add_argument('--website', help='Company website')
    update_company_parser.add_argument('--logo-path', help='Path to company logo')
    
    # Delete company command
    delete_company_parser = company_subparsers.add_parser('delete', help='Delete a company record')
    delete_company_parser.add_argument('--db-path', default='facatura.db', help='Path to the database file')
    delete_company_parser.add_argument('--id', required=True, type=int, help='Company ID')
    
    # List companies command
    list_companies_parser = company_subparsers.add_parser('list', help='List company records')
    list_companies_parser.add_argument('--db-path', default='facatura.db', help='Path to the database file')
    list_companies_parser.add_argument('--city', help='Filter by city')
    list_companies_parser.add_argument('--county', help='Filter by county')
    list_companies_parser.add_argument('--country', help='Filter by country')
    list_companies_parser.add_argument('--vat-payer', action='store_true', dest='vat_payer', help='Filter by VAT payer status')
    list_companies_parser.add_argument('--no-vat-payer', action='store_false', dest='vat_payer', help='Filter by non-VAT payer status')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'setup-db':
        setup_database(args.db_path)
    elif args.command == 'company':
        handle_company_command(args)
    else:
        parser.print_help()


def handle_company_command(args):
    """Handle company management commands."""
    if not args.company_command:
        print("Please specify a company command. Use 'facatura company --help' for more information.")
        sys.exit(1)
    
    company_manager = CompanyManager(args.db_path)
    
    if args.company_command == 'create':
        # Convert arguments to a dictionary and filter out None values and special keys
        company_data = {k: v for k, v in vars(args).items() 
                       if k not in ('command', 'company_command', 'db_path') and v is not None}
        
        success, result = company_manager.create_company(company_data)
        
        if success:
            print(f"Company created successfully with ID: {result}")
        else:
            print(f"Failed to create company: {result}")
            sys.exit(1)
    
    elif args.company_command == 'get':
        if not args.id and not args.fiscal_code:
            print("Either --id or --fiscal-code must be provided")
            sys.exit(1)
        
        if args.id:
            success, result = company_manager.get_company_by_id(args.id)
        else:
            success, result = company_manager.get_company_by_fiscal_code(args.fiscal_code)
        
        if success:
            print("Company details:")
            for key, value in result.items():
                print(f"{key}: {value}")
        else:
            print(f"Failed to retrieve company: {result}")
            sys.exit(1)
    
    elif args.company_command == 'update':
        # Convert arguments to a dictionary and filter out None values and special keys
        company_data = {k: v for k, v in vars(args).items() 
                       if k not in ('command', 'company_command', 'db_path', 'id') and v is not None}
        
        if not company_data:
            print("No update data provided")
            sys.exit(1)
        
        success, result = company_manager.update_company(args.id, company_data)
        
        if success:
            print(result)
        else:
            print(f"Failed to update company: {result}")
            sys.exit(1)
    
    elif args.company_command == 'delete':
        # Ask for confirmation
        confirm = input(f"Are you sure you want to delete company with ID {args.id}? (y/N): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
        
        success, result = company_manager.delete_company(args.id)
        
        if success:
            print(result)
        else:
            print(f"Failed to delete company: {result}")
            sys.exit(1)
    
    elif args.company_command == 'list':
        # Convert arguments to a dictionary and filter out None values and special keys
        filters = {k: v for k, v in vars(args).items() 
                  if k not in ('command', 'company_command', 'db_path') and v is not None}
        
        success, result = company_manager.list_companies(filters if filters else None)
        
        if success:
            if not result:
                print("No companies found")
            else:
                print(f"Found {len(result)} companies:")
                for company in result:
                    print(f"ID: {company['id']}, Name: {company['name']}, Fiscal Code: {company['fiscal_code']}")
        else:
            print(f"Failed to list companies: {result}")
            sys.exit(1)


if __name__ == '__main__':
    main()