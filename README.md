# facatura

Small local invoicing application intended for use in Romania.

Written in Python, uses SQLite as a database. It has a CLI interface, but the core functions are kept in library and could also be used by a GUI.

Invoices will be output to HTML or PDF.

## Features

- Company management (create, read, update, delete)
- More features coming soon...

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/facatura.git
cd facatura

# Install the package
pip install -e .
```

## Usage

### Command Line Interface

```bash
# List all companies
facatura company list

# Show company details
facatura company show 1

# Create a new company
facatura company create --name "My Company SRL" --registration-number "RO12345678" --address "123 Main St" --city "Bucharest" --county "Bucharest"

# Update a company
facatura company update 1 --name "Updated Company Name"

# Delete a company
facatura company delete 1
```

### Python API

```python
from facatura.core.company import CompanyManager

# Create a company manager
company_manager = CompanyManager()

# Create a new company
company_data = {
    "name": "My Company SRL",
    "registration_number": "RO12345678",
    "address": "123 Main St",
    "city": "Bucharest",
    "county": "Bucharest",
    "country": "Romania"
}
company_id = company_manager.create_company(company_data)

# Get company details
company = company_manager.get_company(company_id)
print(f"Company: {company['name']}")

# List companies
companies = company_manager.list_companies()
for company in companies:
    print(f"{company['id']}: {company['name']}")

# Update a company
company_manager.update_company(company_id, {"name": "Updated Company Name"})

# Delete a company
company_manager.delete_company(company_id)

# Close the connection when done
company_manager.close()
```

## Development

### Running Tests

```bash
python -m unittest discover tests
```
