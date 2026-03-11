# Property Management Application

A full-stack Property Management System built with **React** (frontend) and **Node.js / Express** (backend).

## Features

- **Dashboard** – Overview of properties, tenants, leases, revenue and recent payments
- **Properties** – Add, edit, delete and view all properties (apartments, houses, condos, commercial)
- **Tenants** – Manage tenant records with search functionality
- **Leases** – Create and manage lease agreements linking tenants to properties
- **Payments** – Record and track rent payments

## Tech Stack

| Layer    | Technology                              |
|----------|-----------------------------------------|
| Frontend | React 19, Vite, React Router v7, Axios |
| Backend  | Node.js, Express 5, better-sqlite3     |
| Database | SQLite (via better-sqlite3)            |

## Getting Started

### Prerequisites

- Node.js 18+
- npm 9+

### 1. Start the Backend

```bash
cd server
npm install
npm start
```

The API server starts on **http://localhost:5000**.

### 2. Start the Frontend

```bash
cd client
npm install
npm run dev
```

The React app starts on **http://localhost:5173**.

## API Endpoints

| Method | Path                    | Description           |
|--------|-------------------------|-----------------------|
| GET    | /api/dashboard          | Dashboard statistics  |
| GET    | /api/properties         | List all properties   |
| POST   | /api/properties         | Create a property     |
| PUT    | /api/properties/:id     | Update a property     |
| DELETE | /api/properties/:id     | Delete a property     |
| GET    | /api/tenants            | List all tenants      |
| POST   | /api/tenants            | Create a tenant       |
| PUT    | /api/tenants/:id        | Update a tenant       |
| DELETE | /api/tenants/:id        | Delete a tenant       |
| GET    | /api/leases             | List all leases       |
| POST   | /api/leases             | Create a lease        |
| PUT    | /api/leases/:id         | Update a lease        |
| DELETE | /api/leases/:id         | Delete a lease        |
| GET    | /api/payments           | List all payments     |
| POST   | /api/payments           | Record a payment      |
