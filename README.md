# Property Management Application

A full-featured Property Management System (PMS) built with **Python Flask** and **SQLite**, featuring a clean Bootstrap 5 UI.

![Dashboard](https://github.com/user-attachments/assets/988bdbb4-0169-44f3-9f71-bb3093bf46f0)

## Features

- 🏢 **Properties** — Add, edit, and manage properties with multiple units
- 🚪 **Units** — Track unit details (beds/baths, rent, status, square footage)
- 👥 **Tenants** — Manage tenant profiles and emergency contacts
- 📄 **Leases** — Create and track lease agreements with start/end dates and deposit info
- 💰 **Payments** — Record rent payments, deposits, and fees with full history
- 🔧 **Maintenance** — Submit and track maintenance requests with priority levels
- 📊 **Dashboard** — Overview of properties, tenants, active leases, open maintenance, and revenue

## Tech Stack

- **Backend**: Python 3, Flask, Flask-SQLAlchemy
- **Database**: SQLite (easily swappable to PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5, Bootstrap Icons

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Seed with sample data
python seed.py

# 3. Run the app
python run.py
```

Then open http://127.0.0.1:5000 in your browser.

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Project Structure

```
├── app/
│   ├── __init__.py        # App factory & DB init
│   ├── models.py          # SQLAlchemy models
│   ├── routes/            # Blueprint route handlers
│   │   ├── main.py        # Dashboard
│   │   ├── properties.py
│   │   ├── tenants.py
│   │   ├── leases.py
│   │   ├── maintenance.py
│   │   └── payments.py
│   ├── templates/         # Jinja2 HTML templates
│   └── static/            # CSS & JS assets
├── tests/
│   └── test_app.py
├── run.py                 # Entry point
├── seed.py                # Sample data seeder
└── requirements.txt
```
