#!/usr/bin/env python3
"""
Main entry point for the Facatura application.
"""

import os
import sys
import argparse

from facatura.db.setup_db import setup_database


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Facatura - Romanian invoicing application')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Setup database command
    setup_parser = subparsers.add_parser('setup-db', help='Set up the database')
    setup_parser.add_argument('--db-path', default='facatura.db', 
                             help='Path to the database file (default: facatura.db)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'setup-db':
        setup_database(args.db_path)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()