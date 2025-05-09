#!/usr/bin/env python3
"""
Main entry point for the Facatura application.
"""

import os
import sys
import argparse

from facatura.db.setup_db import setup_database
from facatura.core.company import Company
from facatura.core.client import Client
from facatura.core.bank_account import BankAccount
from facatura.cli import main as cli_main


def main():
    """Main entry point for the application."""
    # Use the Click-based CLI
    cli_main(obj={})


if __name__ == '__main__':
    main()