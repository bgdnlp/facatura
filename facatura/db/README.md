# Database Setup for Facatura

This directory contains scripts for setting up and managing the SQLite database used by Facatura.

## Setup Script

The main script is `setup_db.py`, which creates the necessary tables in the SQLite database:

1. `companies` - Stores information about companies that issue invoices
2. `clients` - Stores information about clients who receive invoices
3. `products` - Stores information about products and services that can be invoiced
4. `currency_exchange` - Stores currency exchange rates for RON, EUR, USD, and GBP

## Usage

To set up the database:

```bash
# Make the script executable (MacOS/Linux)
chmod +x setup_db.py

# Run the script
./setup_db.py

# Alternatively, run with Python directly
python3 setup_db.py
```

By default, the script creates a database file named `facatura.db` in the current directory. You can specify a different path as an argument:

```bash
./setup_db.py /path/to/custom/database.db
```

## Database Schema

### Companies Table
Stores information about companies that issue invoices:
- Basic information (name, address, etc.)
- Registration details (registration number, fiscal code, VAT number)
- Banking information
- Contact information

### Clients Table
Similar to the companies table, but for clients who receive invoices.

### Products Table
Stores information about products and services:
- Name and description
- Measuring unit
- Price per unit
- VAT rate
- Flag to distinguish between products and services

### Currency Exchange Table
Stores exchange rates for different currencies:
- Currency code (RON, EUR, USD, GBP)
- Exchange rate (relative to RON)
- Date of the exchange rate