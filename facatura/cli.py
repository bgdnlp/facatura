"""
Command-line interface for facatura.
"""

import os
import click
from . import __version__
from .db.setup_db import setup_database
from .core.company import CompanyManager


@click.group()
@click.version_option(version=__version__)
def main():
    """Facatura - Romanian invoicing application."""
    pass


@main.command()
@click.option("--db-path", default="facatura.db", help="Path to the database file")
def init(db_path):
    """Initialize the database."""
    click.echo(f"Initializing database at {db_path}...")
    if setup_database(db_path):
        click.echo("Database initialization completed successfully.")
    else:
        click.echo("Database initialization failed.", err=True)
        exit(1)


@main.command()
@click.option("--client", help="Client name")
def create_invoice(client):
    """Create a new invoice."""
    click.echo(f"Creating invoice for client: {client}")
    # Invoice creation code would go here


# Company management commands
@main.group()
def company():
    """Manage company records."""
    pass


@company.command()
@click.option("--db-path", default="facatura.db", help="Path to the database file")
@click.option("--name", required=True, help="Company name")
@click.option("--address", required=True, help="Company address")
@click.option("--city", required=True, help="Company city")
@click.option("--county", help="Company county")
@click.option("--postal-code", help="Company postal code")
@click.option("--country", default="Romania", help="Company country")
@click.option("--registration-number", required=True, help="Company registration number")
@click.option("--fiscal-code", required=True, help="Company fiscal code")
@click.option("--vat-payer/--no-vat-payer", default=True, help="Whether the company is a VAT payer")
@click.option("--phone", help="Company phone number")
@click.option("--email", help="Company email")
@click.option("--website", help="Company website")
@click.option("--logo-path", help="Path to company logo")
def create(db_path, **kwargs):
    """Create a new company record."""
    company_manager = CompanyManager(db_path)
    
    # Convert kebab-case to snake_case for keys
    company_data = {k.replace('-', '_'): v for k, v in kwargs.items() if k != 'db_path' and v is not None}
    
    success, result = company_manager.create_company(company_data)
    
    if success:
        click.echo(f"Company created successfully with ID: {result}")
    else:
        click.echo(f"Failed to create company: {result}", err=True)
        exit(1)


@company.command()
@click.option("--db-path", default="facatura.db", help="Path to the database file")
@click.option("--id", type=int, help="Company ID")
@click.option("--fiscal-code", help="Company fiscal code")
def get(db_path, id, fiscal_code):
    """Get a company record by ID or fiscal code."""
    if not id and not fiscal_code:
        click.echo("Either --id or --fiscal-code must be provided", err=True)
        exit(1)
    
    company_manager = CompanyManager(db_path)
    
    if id:
        success, result = company_manager.get_company_by_id(id)
    else:
        success, result = company_manager.get_company_by_fiscal_code(fiscal_code)
    
    if success:
        click.echo("Company details:")
        for key, value in result.items():
            click.echo(f"{key}: {value}")
    else:
        click.echo(f"Failed to retrieve company: {result}", err=True)
        exit(1)


@company.command()
@click.option("--db-path", default="facatura.db", help="Path to the database file")
@click.option("--id", required=True, type=int, help="Company ID")
@click.option("--name", help="Company name")
@click.option("--address", help="Company address")
@click.option("--city", help="Company city")
@click.option("--county", help="Company county")
@click.option("--postal-code", help="Company postal code")
@click.option("--country", help="Company country")
@click.option("--registration-number", help="Company registration number")
@click.option("--fiscal-code", help="Company fiscal code")
@click.option("--vat-payer/--no-vat-payer", help="Whether the company is a VAT payer")
@click.option("--phone", help="Company phone number")
@click.option("--email", help="Company email")
@click.option("--website", help="Company website")
@click.option("--logo-path", help="Path to company logo")
def update(db_path, id, **kwargs):
    """Update a company record."""
    company_manager = CompanyManager(db_path)
    
    # Convert kebab-case to snake_case for keys and filter out None values
    company_data = {k.replace('-', '_'): v for k, v in kwargs.items() 
                   if k not in ('db_path', 'id') and v is not None}
    
    if not company_data:
        click.echo("No update data provided", err=True)
        exit(1)
    
    success, result = company_manager.update_company(id, company_data)
    
    if success:
        click.echo(result)
    else:
        click.echo(f"Failed to update company: {result}", err=True)
        exit(1)


@company.command()
@click.option("--db-path", default="facatura.db", help="Path to the database file")
@click.option("--id", required=True, type=int, help="Company ID")
@click.confirmation_option(prompt="Are you sure you want to delete this company?")
def delete(db_path, id):
    """Delete a company record."""
    company_manager = CompanyManager(db_path)
    
    success, result = company_manager.delete_company(id)
    
    if success:
        click.echo(result)
    else:
        click.echo(f"Failed to delete company: {result}", err=True)
        exit(1)


@company.command()
@click.option("--db-path", default="facatura.db", help="Path to the database file")
@click.option("--city", help="Filter by city")
@click.option("--county", help="Filter by county")
@click.option("--country", help="Filter by country")
@click.option("--vat-payer/--no-vat-payer", help="Filter by VAT payer status")
def list(db_path, **kwargs):
    """List company records."""
    company_manager = CompanyManager(db_path)
    
    # Convert kebab-case to snake_case for keys and filter out None values
    filters = {k.replace('-', '_'): v for k, v in kwargs.items() 
              if k != 'db_path' and v is not None}
    
    success, result = company_manager.list_companies(filters if filters else None)
    
    if success:
        if not result:
            click.echo("No companies found")
        else:
            click.echo(f"Found {len(result)} companies:")
            for company in result:
                click.echo(f"ID: {company['id']}, Name: {company['name']}, Fiscal Code: {company['fiscal_code']}")
    else:
        click.echo(f"Failed to list companies: {result}", err=True)
        exit(1)


if __name__ == "__main__":
    main()