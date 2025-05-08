"""
Tests for the CLI module.
"""

from click.testing import CliRunner
from facatura.cli import main


def test_main():
    """Test the main CLI entry point."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Facatura - Romanian invoicing application" in result.output


def test_version():
    """Test the version command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_create_invoice():
    """Test the create-invoice command."""
    runner = CliRunner()
    result = runner.invoke(main, ["create-invoice", "--client", "Test Client"])
    assert result.exit_code == 0
    assert "Creating invoice for client: Test Client" in result.output