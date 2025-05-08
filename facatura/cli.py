"""
Command-line interface for facatura.
"""

import click
from . import __version__


@click.group()
@click.version_option(version=__version__)
def main():
    """Facatura - Romanian invoicing application."""
    pass


@main.command()
def init():
    """Initialize the database."""
    click.echo("Initializing database...")
    # Database initialization code would go here


@main.command()
@click.option("--client", help="Client name")
def create_invoice(client):
    """Create a new invoice."""
    click.echo(f"Creating invoice for client: {client}")
    # Invoice creation code would go here


if __name__ == "__main__":
    main()