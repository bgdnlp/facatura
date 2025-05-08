"""
Command-line interface for facatura.
"""

import os
import click
from . import __version__
from .db.setup_db import setup_database


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


if __name__ == "__main__":
    main()