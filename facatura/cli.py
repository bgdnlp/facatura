"""
Command-line interface for facatura.
"""

import os
import click
from . import __version__
from .db.setup_db import setup_database
from .core.company import Company
from .core.client import Client
from .core.bank_account import BankAccount


@click.group()
@click.version_option(version=__version__)
@click.option("--db-path", default="facatura.db", help="Path to the database file", envvar="FACATURA_DB")
@click.pass_context
def main(ctx, db_path):
    """Facatura - Romanian invoicing application."""
    ctx.ensure_object(dict)
    ctx.obj['DB_PATH'] = db_path


@main.command()
@click.pass_context
def init(ctx):
    """Initialize the database."""
    db_path = ctx.obj['DB_PATH']
    click.echo(f"Initializing database at {db_path}...")
    if setup_database(db_path):
        click.echo("Database initialization completed successfully.")
    else:
        click.echo("Database initialization failed.", err=True)
        exit(1)


@main.command()
@click.option("--client", help="Client name")
@click.pass_context
def create_invoice(ctx, client):
    """Create a new invoice."""
    click.echo(f"Creating invoice for client: {client}")
    # Invoice creation code would go here


# Company management commands
@main.group()
def company():
    """Manage companies."""
    pass


@company.command("list")
@click.pass_context
def list_companies(ctx):
    """List all companies."""
    db_path = ctx.obj['DB_PATH']
    company_manager = Company(db_path)
    companies = company_manager.get_all()
    
    if not companies:
        click.echo("No companies found.")
        return
    
    click.echo("Companies:")
    for c in companies:
        click.echo(f"{c['id']}: {c['name']} (Fiscal code: {c['fiscal_code']})")


@company.command("add")
@click.option("--name", required=True, help="Company name")
@click.option("--address", required=True, help="Company address")
@click.option("--city", required=True, help="Company city")
@click.option("--registration-number", required=True, help="Company registration number")
@click.option("--fiscal-code", required=True, help="Company fiscal code")
@click.option("--county", help="Company county")
@click.option("--postal-code", help="Company postal code")
@click.option("--country", default="Romania", help="Company country")
@click.option("--vat-payer/--no-vat-payer", default=True, help="Whether the company is a VAT payer")
@click.option("--phone", help="Company phone")
@click.option("--email", help="Company email")
@click.option("--website", help="Company website")
@click.option("--logo-path", help="Path to company logo")
@click.pass_context
def add_company(ctx, name, address, city, registration_number, fiscal_code, county, postal_code,
                country, vat_payer, phone, email, website, logo_path):
    """Add a new company."""
    db_path = ctx.obj['DB_PATH']
    company_manager = Company(db_path)
    
    try:
        company_id = company_manager.create(
            name, address, city, registration_number, fiscal_code,
            county, postal_code, country, vat_payer, phone, email, website, logo_path
        )
        click.echo(f"Company added successfully with ID: {company_id}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)


@company.command("show")
@click.argument("company_id", type=int)
@click.pass_context
def show_company(ctx, company_id):
    """Show company details."""
    db_path = ctx.obj['DB_PATH']
    company_manager = Company(db_path)
    
    try:
        company_data = company_manager.get(company_id)
        if not company_data:
            click.echo(f"Company with ID {company_id} not found.", err=True)
            exit(1)
        
        click.echo(f"Company ID: {company_data['id']}")
        click.echo(f"Name: {company_data['name']}")
        click.echo(f"Address: {company_data['address']}")
        click.echo(f"City: {company_data['city']}")
        click.echo(f"County: {company_data['county'] or 'N/A'}")
        click.echo(f"Postal Code: {company_data['postal_code'] or 'N/A'}")
        click.echo(f"Country: {company_data['country']}")
        click.echo(f"Registration Number: {company_data['registration_number']}")
        click.echo(f"Fiscal Code: {company_data['fiscal_code']}")
        click.echo(f"VAT Payer: {'Yes' if company_data['vat_payer'] else 'No'}")
        click.echo(f"Phone: {company_data['phone'] or 'N/A'}")
        click.echo(f"Email: {company_data['email'] or 'N/A'}")
        click.echo(f"Website: {company_data['website'] or 'N/A'}")
        
        # Show bank accounts
        bank_accounts = company_manager.get_bank_accounts(company_id)
        if bank_accounts:
            click.echo("\nBank Accounts:")
            for account in bank_accounts:
                default_mark = " (Default)" if account['is_default'] else ""
                click.echo(f"  {account['id']}: {account['bank_name']} - {account['account_number']}{default_mark}")
        else:
            click.echo("\nNo bank accounts found for this company.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)


@company.command("delete")
@click.argument("company_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this company?")
@click.pass_context
def delete_company(ctx, company_id):
    """Delete a company."""
    db_path = ctx.obj['DB_PATH']
    company_manager = Company(db_path)
    
    try:
        # Check if the company exists
        company_data = company_manager.get(company_id)
        if not company_data:
            click.echo(f"Company with ID {company_id} not found.", err=True)
            exit(1)
        
        # Delete the company
        if company_manager.delete(company_id):
            click.echo(f"Company '{company_data['name']}' deleted successfully.")
        else:
            click.echo("Failed to delete the company.", err=True)
            exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)


@company.command("add-bank-account")
@click.argument("company_id", type=int)
@click.option("--bank-name", required=True, help="Bank name")
@click.option("--account-number", required=True, help="Account number")
@click.option("--swift-code", help="SWIFT code")
@click.option("--iban", help="IBAN")
@click.option("--currency", default="RON", help="Currency")
@click.option("--default/--no-default", default=False, help="Set as default account")
@click.pass_context
def add_company_bank_account(ctx, company_id, bank_name, account_number, swift_code, iban, currency, default):
    """Add a bank account to a company."""
    db_path = ctx.obj['DB_PATH']
    company_manager = Company(db_path)
    
    try:
        account_id = company_manager.add_bank_account(
            company_id, bank_name, account_number, swift_code, iban, currency, default
        )
        click.echo(f"Bank account added successfully with ID: {account_id}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)


# Client management commands
@main.group()
def client():
    """Manage clients."""
    pass


@client.command("list")
@click.pass_context
def list_clients(ctx):
    """List all clients."""
    db_path = ctx.obj['DB_PATH']
    client_manager = Client(db_path)
    clients = client_manager.get_all()
    
    if not clients:
        click.echo("No clients found.")
        return
    
    click.echo("Clients:")
    for c in clients:
        click.echo(f"{c['id']}: {c['name']} (Fiscal code: {c['fiscal_code']})")


@client.command("add")
@click.option("--name", required=True, help="Client name")
@click.option("--address", required=True, help="Client address")
@click.option("--city", required=True, help="Client city")
@click.option("--fiscal-code", required=True, help="Client fiscal code")
@click.option("--registration-number", help="Client registration number")
@click.option("--county", help="Client county")
@click.option("--postal-code", help="Client postal code")
@click.option("--country", default="Romania", help="Client country")
@click.option("--vat-payer/--no-vat-payer", default=True, help="Whether the client is a VAT payer")
@click.option("--phone", help="Client phone")
@click.option("--email", help="Client email")
@click.option("--website", help="Client website")
@click.pass_context
def add_client(ctx, name, address, city, fiscal_code, registration_number, county, postal_code,
               country, vat_payer, phone, email, website):
    """Add a new client."""
    db_path = ctx.obj['DB_PATH']
    client_manager = Client(db_path)
    
    try:
        client_id = client_manager.create(
            name, address, city, fiscal_code, registration_number,
            county, postal_code, country, vat_payer, phone, email, website
        )
        click.echo(f"Client added successfully with ID: {client_id}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)


@client.command("show")
@click.argument("client_id", type=int)
@click.pass_context
def show_client(ctx, client_id):
    """Show client details."""
    db_path = ctx.obj['DB_PATH']
    client_manager = Client(db_path)
    
    try:
        client_data = client_manager.get(client_id)
        if not client_data:
            click.echo(f"Client with ID {client_id} not found.", err=True)
            exit(1)
        
        click.echo(f"Client ID: {client_data['id']}")
        click.echo(f"Name: {client_data['name']}")
        click.echo(f"Address: {client_data['address']}")
        click.echo(f"City: {client_data['city']}")
        click.echo(f"County: {client_data['county'] or 'N/A'}")
        click.echo(f"Postal Code: {client_data['postal_code'] or 'N/A'}")
        click.echo(f"Country: {client_data['country']}")
        click.echo(f"Registration Number: {client_data['registration_number'] or 'N/A'}")
        click.echo(f"Fiscal Code: {client_data['fiscal_code']}")
        click.echo(f"VAT Payer: {'Yes' if client_data['vat_payer'] else 'No'}")
        click.echo(f"Phone: {client_data['phone'] or 'N/A'}")
        click.echo(f"Email: {client_data['email'] or 'N/A'}")
        click.echo(f"Website: {client_data['website'] or 'N/A'}")
        
        # Show bank accounts
        bank_accounts = client_manager.get_bank_accounts(client_id)
        if bank_accounts:
            click.echo("\nBank Accounts:")
            for account in bank_accounts:
                default_mark = " (Default)" if account['is_default'] else ""
                click.echo(f"  {account['id']}: {account['bank_name']} - {account['account_number']}{default_mark}")
        else:
            click.echo("\nNo bank accounts found for this client.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)


@client.command("delete")
@click.argument("client_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this client?")
@click.pass_context
def delete_client(ctx, client_id):
    """Delete a client."""
    db_path = ctx.obj['DB_PATH']
    client_manager = Client(db_path)
    
    try:
        # Check if the client exists
        client_data = client_manager.get(client_id)
        if not client_data:
            click.echo(f"Client with ID {client_id} not found.", err=True)
            exit(1)
        
        # Delete the client
        if client_manager.delete(client_id):
            click.echo(f"Client '{client_data['name']}' deleted successfully.")
        else:
            click.echo("Failed to delete the client.", err=True)
            exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)


@client.command("add-bank-account")
@click.argument("client_id", type=int)
@click.option("--bank-name", required=True, help="Bank name")
@click.option("--account-number", required=True, help="Account number")
@click.option("--swift-code", help="SWIFT code")
@click.option("--iban", help="IBAN")
@click.option("--currency", default="RON", help="Currency")
@click.option("--default/--no-default", default=False, help="Set as default account")
@click.pass_context
def add_client_bank_account(ctx, client_id, bank_name, account_number, swift_code, iban, currency, default):
    """Add a bank account to a client."""
    db_path = ctx.obj['DB_PATH']
    client_manager = Client(db_path)
    
    try:
        account_id = client_manager.add_bank_account(
            client_id, bank_name, account_number, swift_code, iban, currency, default
        )
        click.echo(f"Bank account added successfully with ID: {account_id}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)


if __name__ == "__main__":
    main()