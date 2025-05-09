# Facatura

Small local invoicing application intended for use in Romania.

Written in Python, uses SQLite as a database. It has a CLI interface, but the core functions are kept in library and could also be used by a GUI.

Invoices will be output to HTML or PDF.

## Setup

### Prerequisites

- Python 3.6 or higher

### Setting up the development environment

#### On Linux/macOS

```bash
# Clone the repository
git clone https://github.com/yourusername/facatura.git
cd facatura

# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh

# Activate the virtual environment
source venv/bin/activate
```

#### On Windows

```cmd
# Clone the repository
git clone https://github.com/yourusername/facatura.git
cd facatura

# Run the setup script
setup.bat

# Activate the virtual environment
venv\Scripts\activate.bat
```

### Manual setup (alternative)

If you prefer to set up the environment manually:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
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

## Running tests

```bash
# Make sure the virtual environment is activated
pytest
```
Or
```bash
python -m unittest discover tests
```

## Usage

After activating the virtual environment, you can use the CLI:

```bash
# Show help
facatura --help

# Create an invoice
facatura create-invoice --client "Client Name"
```
