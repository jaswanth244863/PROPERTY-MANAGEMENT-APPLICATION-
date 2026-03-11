# 🏠 Property Management System

A complete Property Management System (PMS) web application built with **Flask** and **SQLite**.

## Features

- **Dashboard** – Overview of key metrics: total properties, occupancy, active leases, monthly revenue, and maintenance alerts
- **Properties** – Full CRUD management with status filtering (Available / Occupied / Maintenance)
- **Tenants** – Manage tenant profiles including contact and ID information
- **Leases** – Create, edit, and terminate lease agreements; link properties and tenants
- **Payments** – Record and track rent payments (Paid / Pending / Overdue)
- **Maintenance Requests** – Submit and track maintenance issues with priority levels (Low / Medium / High / Urgent)

## Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Backend    | Python 3 / Flask        |
| Database   | SQLite (via SQLAlchemy) |
| Frontend   | HTML / CSS / Jinja2     |

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/jaswanth244863/PROPERTY-MANAGEMENT-APPLICATION-.git
cd PROPERTY-MANAGEMENT-APPLICATION-

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Open your browser and navigate to **http://localhost:5000**

The application will automatically create the SQLite database and seed it with sample data on first run.

## Project Structure

```
├── app.py                  # Main Flask application (models + routes)
├── requirements.txt        # Python dependencies
├── static/
│   └── css/
│       └── style.css       # Application stylesheet
└── templates/
    ├── base.html           # Base layout with sidebar navigation
    ├── dashboard.html      # Dashboard overview
    ├── properties/         # Property list, form, detail templates
    ├── tenants/            # Tenant list, form, detail templates
    ├── leases/             # Lease list, form, detail templates
    ├── payments/           # Payment list, form templates
    └── maintenance/        # Maintenance request list, form templates
```

## Sample Data

On first launch, the app seeds the database with:
- 4 sample properties (different types and statuses)
- 3 tenants
- 2 active leases
- 4 payment records
- 2 maintenance requests
