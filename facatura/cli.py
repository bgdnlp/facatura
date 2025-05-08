"""
Command-line interface for facatura.
"""

import click
import pathlib
from . import __version__
from .db.setup_db import create_tables, DEFAULT_DB_PATH


@click.group()
@click.version_option(version=__version__)
def main():
    """Facatura - Romanian invoicing application."""
    pass


@main.command()
@click.option("--db-path", help="Path to the database file", default=None)
def init(db_path):
    """Initialize the database."""
    if db_path is None:
        db_path = DEFAULT_DB_PATH
        
    click.echo(f"Initializing database at: {db_path}")
    
    # Create the directory if it doesn't exist
    db_dir = pathlib.Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize the database
    if create_tables(db_path):
        click.echo("Database initialized successfully.")
    else:
        click.echo("Failed to initialize database.", err=True)
        exit(1)


@main.command()
@click.option("--client", help="Client name")
def create_invoice(client):
    """Create a new invoice."""
    click.echo(f"Creating invoice for client: {client}")
    # Invoice creation code would go here


if __name__ == "__main__":
    main()