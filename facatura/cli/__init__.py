"""
Command-line interface for facatura.
"""

import argparse
import sys
from typing import List, Optional

from facatura.core.company import CompanyManager, CompanyError, CompanyNotFoundError


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code
    """
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Facatura - Romanian invoicing application")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Company commands
    company_parser = subparsers.add_parser("company", help="Company management")
    company_subparsers = company_parser.add_subparsers(dest="subcommand", help="Company subcommand")

    # Company list
    company_list_parser = company_subparsers.add_parser("list", help="List companies")
    company_list_parser.add_argument("--name", help="Filter by name")
    company_list_parser.add_argument("--city", help="Filter by city")
    company_list_parser.add_argument("--county", help="Filter by county")

    # Company show
    company_show_parser = company_subparsers.add_parser("show", help="Show company details")
    company_show_parser.add_argument("id", type=int, help="Company ID")

    # Company create
    company_create_parser = company_subparsers.add_parser("create", help="Create a new company")
    company_create_parser.add_argument("--name", required=True, help="Company name")
    company_create_parser.add_argument("--registration-number", required=True, help="Registration number (CUI)")
    company_create_parser.add_argument("--vat-number", help="VAT number")
    company_create_parser.add_argument("--address", required=True, help="Address")
    company_create_parser.add_argument("--city", required=True, help="City")
    company_create_parser.add_argument("--county", required=True, help="County")
    company_create_parser.add_argument("--postal-code", help="Postal code")
    company_create_parser.add_argument("--country", default="Romania", help="Country")
    company_create_parser.add_argument("--bank-name", help="Bank name")
    company_create_parser.add_argument("--bank-account", help="Bank account")
    company_create_parser.add_argument("--email", help="Email")
    company_create_parser.add_argument("--phone", help="Phone")
    company_create_parser.add_argument("--website", help="Website")
    company_create_parser.add_argument("--notes", help="Notes")

    # Company update
    company_update_parser = company_subparsers.add_parser("update", help="Update a company")
    company_update_parser.add_argument("id", type=int, help="Company ID")
    company_update_parser.add_argument("--name", help="Company name")
    company_update_parser.add_argument("--registration-number", help="Registration number (CUI)")
    company_update_parser.add_argument("--vat-number", help="VAT number")
    company_update_parser.add_argument("--address", help="Address")
    company_update_parser.add_argument("--city", help="City")
    company_update_parser.add_argument("--county", help="County")
    company_update_parser.add_argument("--postal-code", help="Postal code")
    company_update_parser.add_argument("--country", help="Country")
    company_update_parser.add_argument("--bank-name", help="Bank name")
    company_update_parser.add_argument("--bank-account", help="Bank account")
    company_update_parser.add_argument("--email", help="Email")
    company_update_parser.add_argument("--phone", help="Phone")
    company_update_parser.add_argument("--website", help="Website")
    company_update_parser.add_argument("--notes", help="Notes")

    # Company delete
    company_delete_parser = company_subparsers.add_parser("delete", help="Delete a company")
    company_delete_parser.add_argument("id", type=int, help="Company ID")

    # Parse arguments
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 1

    # Handle company commands
    if parsed_args.command == "company":
        return handle_company_command(parsed_args)

    return 0


def handle_company_command(args) -> int:
    """
    Handle company commands.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code
    """
    if not args.subcommand:
        print("Error: No subcommand specified")
        return 1

    company_manager = CompanyManager()

    try:
        if args.subcommand == "list":
            # Build filters
            filters = {}
            if args.name:
                filters["name"] = args.name
            if args.city:
                filters["city"] = args.city
            if args.county:
                filters["county"] = args.county

            # List companies
            companies = company_manager.list_companies(filters)
            
            if not companies:
                print("No companies found")
                return 0
            
            # Print companies
            print(f"Found {len(companies)} companies:")
            for company in companies:
                print(f"{company['id']}: {company['name']} ({company['registration_number']})")
            
            return 0

        elif args.subcommand == "show":
            # Show company details
            company = company_manager.get_company(args.id)
            
            print(f"Company: {company['name']}")
            print(f"Registration number: {company['registration_number']}")
            print(f"VAT number: {company['vat_number'] or 'N/A'}")
            print(f"Address: {company['address']}")
            print(f"City: {company['city']}")
            print(f"County: {company['county']}")
            print(f"Postal code: {company['postal_code'] or 'N/A'}")
            print(f"Country: {company['country']}")
            print(f"Bank: {company['bank_name'] or 'N/A'}")
            print(f"Bank account: {company['bank_account'] or 'N/A'}")
            print(f"Email: {company['email'] or 'N/A'}")
            print(f"Phone: {company['phone'] or 'N/A'}")
            print(f"Website: {company['website'] or 'N/A'}")
            print(f"Notes: {company['notes'] or 'N/A'}")
            
            return 0

        elif args.subcommand == "create":
            # Build company data
            company_data = {
                "name": args.name,
                "registration_number": args.registration_number,
                "address": args.address,
                "city": args.city,
                "county": args.county,
                "country": args.country,
            }
            
            # Add optional fields
            if args.vat_number:
                company_data["vat_number"] = args.vat_number
            if args.postal_code:
                company_data["postal_code"] = args.postal_code
            if args.bank_name:
                company_data["bank_name"] = args.bank_name
            if args.bank_account:
                company_data["bank_account"] = args.bank_account
            if args.email:
                company_data["email"] = args.email
            if args.phone:
                company_data["phone"] = args.phone
            if args.website:
                company_data["website"] = args.website
            if args.notes:
                company_data["notes"] = args.notes
            
            # Create company
            company_id = company_manager.create_company(company_data)
            print(f"Company created with ID: {company_id}")
            
            return 0

        elif args.subcommand == "update":
            # Build company data
            company_data = {}
            
            # Add fields that were provided
            if args.name:
                company_data["name"] = args.name
            if args.registration_number:
                company_data["registration_number"] = args.registration_number
            if args.vat_number:
                company_data["vat_number"] = args.vat_number
            if args.address:
                company_data["address"] = args.address
            if args.city:
                company_data["city"] = args.city
            if args.county:
                company_data["county"] = args.county
            if args.postal_code:
                company_data["postal_code"] = args.postal_code
            if args.country:
                company_data["country"] = args.country
            if args.bank_name:
                company_data["bank_name"] = args.bank_name
            if args.bank_account:
                company_data["bank_account"] = args.bank_account
            if args.email:
                company_data["email"] = args.email
            if args.phone:
                company_data["phone"] = args.phone
            if args.website:
                company_data["website"] = args.website
            if args.notes:
                company_data["notes"] = args.notes
            
            # Check if any fields were provided
            if not company_data:
                print("Error: No fields to update")
                return 1
            
            # Update company
            company_manager.update_company(args.id, company_data)
            print(f"Company with ID {args.id} updated")
            
            return 0

        elif args.subcommand == "delete":
            # Delete company
            company_manager.delete_company(args.id)
            print(f"Company with ID {args.id} deleted")
            
            return 0

        else:
            print(f"Error: Unknown subcommand: {args.subcommand}")
            return 1

    except CompanyNotFoundError as e:
        print(f"Error: {str(e)}")
        return 1
    except CompanyError as e:
        print(f"Error: {str(e)}")
        return 1
    finally:
        company_manager.close()


if __name__ == "__main__":
    sys.exit(main())