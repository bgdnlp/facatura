# Facatura

Small local invoicing application intended for use in Romania.

Written in Python, uses SQLite as a database. It has a CLI interface, but the core functions are kept in library and could also be used by a GUI.

Invoices will be output to HTML or PDF.

## Installation

Clone this repository and navigate to the project directory:

```bash
git clone https://github.com/yourusername/facatura.git
cd facatura
```

## Database Setup

Before using the application, you need to set up the database:

### Method 1: Using the setup script directly

```bash
# Make the script executable (MacOS/Linux)
chmod +x facatura/db/setup_db.py

# Run the script
./facatura/db/setup_db.py
```

### Method 2: Using the main application

```bash
python -m facatura setup-db
```

By default, this creates a SQLite database file named `facatura.db` in the current directory. You can specify a different path:

```bash
python -m facatura setup-db --db-path /path/to/custom/database.db
```

## Database Schema

The database includes the following tables:

1. **companies** - Stores information about companies that issue invoices
   - Company details (name, address, etc.)
   - Registration information
   - Banking details

2. **clients** - Stores information about clients who receive invoices
   - Similar fields to the companies table

3. **products** - Stores information about products and services
   - Product name
   - Measuring unit
   - Price per unit
   - VAT rate

4. **currency_exchange** - Stores currency exchange rates
   - Supports RON (default), EUR, USD, and GBP

## Running Tests

To run the tests:

```bash
python -m unittest discover tests
```
