const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const Database = require('better-sqlite3');
const { v4: uuidv4 } = require('uuid');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Apply rate limiting to all API routes
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 200,
  standardHeaders: true,
  legacyHeaders: false,
});
app.use('/api', apiLimiter);

// Initialize SQLite database
const db = new Database(path.join(__dirname, 'property_management.db'));

// Create tables
db.exec(`
  CREATE TABLE IF NOT EXISTS properties (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip TEXT NOT NULL,
    type TEXT NOT NULL,
    units INTEGER DEFAULT 1,
    rent REAL NOT NULL,
    status TEXT DEFAULT 'available',
    description TEXT,
    created_at TEXT DEFAULT (datetime('now'))
  );

  CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    created_at TEXT DEFAULT (datetime('now'))
  );

  CREATE TABLE IF NOT EXISTS leases (
    id TEXT PRIMARY KEY,
    property_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    monthly_rent REAL NOT NULL,
    deposit REAL,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (property_id) REFERENCES properties(id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
  );

  CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY,
    lease_id TEXT NOT NULL,
    amount REAL NOT NULL,
    payment_date TEXT NOT NULL,
    payment_method TEXT DEFAULT 'bank_transfer',
    status TEXT DEFAULT 'paid',
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (lease_id) REFERENCES leases(id)
  );
`);

// Seed sample data if tables are empty
const propertyCount = db.prepare('SELECT COUNT(*) as count FROM properties').get();
if (propertyCount.count === 0) {
  const insertProperty = db.prepare(`
    INSERT INTO properties (id, name, address, city, state, zip, type, units, rent, status, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  insertProperty.run(uuidv4(), 'Sunset Apartments', '123 Sunset Blvd', 'Los Angeles', 'CA', '90001', 'apartment', 12, 1500, 'available', 'Modern apartment complex with pool and gym');
  insertProperty.run(uuidv4(), 'Oak Street House', '456 Oak Street', 'Austin', 'TX', '78701', 'house', 1, 2200, 'occupied', 'Spacious 3-bedroom house with backyard');
  insertProperty.run(uuidv4(), 'Downtown Loft', '789 Main Ave', 'Chicago', 'IL', '60601', 'condo', 4, 1800, 'available', 'Stylish loft in downtown area');
}

// ─── Properties ──────────────────────────────────────────────────────────────

app.get('/api/properties', (req, res) => {
  const properties = db.prepare('SELECT * FROM properties ORDER BY created_at DESC').all();
  res.json(properties);
});

app.get('/api/properties/:id', (req, res) => {
  const property = db.prepare('SELECT * FROM properties WHERE id = ?').get(req.params.id);
  if (!property) return res.status(404).json({ error: 'Property not found' });
  res.json(property);
});

app.post('/api/properties', (req, res) => {
  const { name, address, city, state, zip, type, units, rent, status, description } = req.body;
  if (!name || !address || !city || !state || !zip || !type || !rent) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  const id = uuidv4();
  db.prepare(`
    INSERT INTO properties (id, name, address, city, state, zip, type, units, rent, status, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(id, name, address, city, state, zip, type, units || 1, rent, status || 'available', description || '');
  const property = db.prepare('SELECT * FROM properties WHERE id = ?').get(id);
  res.status(201).json(property);
});

app.put('/api/properties/:id', (req, res) => {
  const { name, address, city, state, zip, type, units, rent, status, description } = req.body;
  const existing = db.prepare('SELECT * FROM properties WHERE id = ?').get(req.params.id);
  if (!existing) return res.status(404).json({ error: 'Property not found' });
  db.prepare(`
    UPDATE properties SET name=?, address=?, city=?, state=?, zip=?, type=?, units=?, rent=?, status=?, description=?
    WHERE id=?
  `).run(
    name || existing.name,
    address || existing.address,
    city || existing.city,
    state || existing.state,
    zip || existing.zip,
    type || existing.type,
    units !== undefined ? units : existing.units,
    rent !== undefined ? rent : existing.rent,
    status || existing.status,
    description !== undefined ? description : existing.description,
    req.params.id
  );
  res.json(db.prepare('SELECT * FROM properties WHERE id = ?').get(req.params.id));
});

app.delete('/api/properties/:id', (req, res) => {
  const existing = db.prepare('SELECT * FROM properties WHERE id = ?').get(req.params.id);
  if (!existing) return res.status(404).json({ error: 'Property not found' });
  db.prepare('DELETE FROM properties WHERE id = ?').run(req.params.id);
  res.json({ message: 'Property deleted' });
});

// ─── Tenants ─────────────────────────────────────────────────────────────────

app.get('/api/tenants', (req, res) => {
  const tenants = db.prepare('SELECT * FROM tenants ORDER BY created_at DESC').all();
  res.json(tenants);
});

app.get('/api/tenants/:id', (req, res) => {
  const tenant = db.prepare('SELECT * FROM tenants WHERE id = ?').get(req.params.id);
  if (!tenant) return res.status(404).json({ error: 'Tenant not found' });
  res.json(tenant);
});

app.post('/api/tenants', (req, res) => {
  const { first_name, last_name, email, phone } = req.body;
  if (!first_name || !last_name || !email) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  const id = uuidv4();
  try {
    db.prepare('INSERT INTO tenants (id, first_name, last_name, email, phone) VALUES (?, ?, ?, ?, ?)').run(id, first_name, last_name, email, phone || '');
    res.status(201).json(db.prepare('SELECT * FROM tenants WHERE id = ?').get(id));
  } catch (e) {
    if (e.message.includes('UNIQUE')) return res.status(400).json({ error: 'Email already exists' });
    throw e;
  }
});

app.put('/api/tenants/:id', (req, res) => {
  const { first_name, last_name, email, phone } = req.body;
  const existing = db.prepare('SELECT * FROM tenants WHERE id = ?').get(req.params.id);
  if (!existing) return res.status(404).json({ error: 'Tenant not found' });
  try {
    db.prepare('UPDATE tenants SET first_name=?, last_name=?, email=?, phone=? WHERE id=?').run(
      first_name || existing.first_name,
      last_name || existing.last_name,
      email || existing.email,
      phone !== undefined ? phone : existing.phone,
      req.params.id
    );
    res.json(db.prepare('SELECT * FROM tenants WHERE id = ?').get(req.params.id));
  } catch (e) {
    if (e.message.includes('UNIQUE')) return res.status(400).json({ error: 'Email already exists' });
    throw e;
  }
});

app.delete('/api/tenants/:id', (req, res) => {
  const existing = db.prepare('SELECT * FROM tenants WHERE id = ?').get(req.params.id);
  if (!existing) return res.status(404).json({ error: 'Tenant not found' });
  db.prepare('DELETE FROM tenants WHERE id = ?').run(req.params.id);
  res.json({ message: 'Tenant deleted' });
});

// ─── Leases ──────────────────────────────────────────────────────────────────

app.get('/api/leases', (req, res) => {
  const leases = db.prepare(`
    SELECT l.*, 
      p.name as property_name, p.address as property_address,
      t.first_name, t.last_name, t.email as tenant_email
    FROM leases l
    JOIN properties p ON l.property_id = p.id
    JOIN tenants t ON l.tenant_id = t.id
    ORDER BY l.created_at DESC
  `).all();
  res.json(leases);
});

app.post('/api/leases', (req, res) => {
  const { property_id, tenant_id, start_date, end_date, monthly_rent, deposit, status } = req.body;
  if (!property_id || !tenant_id || !start_date || !end_date || !monthly_rent) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  const id = uuidv4();
  db.prepare(`
    INSERT INTO leases (id, property_id, tenant_id, start_date, end_date, monthly_rent, deposit, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).run(id, property_id, tenant_id, start_date, end_date, monthly_rent, deposit || 0, status || 'active');
  // Update property status to occupied
  db.prepare("UPDATE properties SET status='occupied' WHERE id=?").run(property_id);
  res.status(201).json(db.prepare('SELECT * FROM leases WHERE id = ?').get(id));
});

app.put('/api/leases/:id', (req, res) => {
  const { start_date, end_date, monthly_rent, deposit, status } = req.body;
  const existing = db.prepare('SELECT * FROM leases WHERE id = ?').get(req.params.id);
  if (!existing) return res.status(404).json({ error: 'Lease not found' });
  db.prepare(`
    UPDATE leases SET start_date=?, end_date=?, monthly_rent=?, deposit=?, status=? WHERE id=?
  `).run(
    start_date || existing.start_date,
    end_date || existing.end_date,
    monthly_rent !== undefined ? monthly_rent : existing.monthly_rent,
    deposit !== undefined ? deposit : existing.deposit,
    status || existing.status,
    req.params.id
  );
  if (status === 'terminated' || status === 'expired') {
    db.prepare("UPDATE properties SET status='available' WHERE id=?").run(existing.property_id);
  }
  res.json(db.prepare('SELECT * FROM leases WHERE id = ?').get(req.params.id));
});

app.delete('/api/leases/:id', (req, res) => {
  const existing = db.prepare('SELECT * FROM leases WHERE id = ?').get(req.params.id);
  if (!existing) return res.status(404).json({ error: 'Lease not found' });
  db.prepare('DELETE FROM leases WHERE id = ?').run(req.params.id);
  res.json({ message: 'Lease deleted' });
});

// ─── Payments ────────────────────────────────────────────────────────────────

app.get('/api/payments', (req, res) => {
  const payments = db.prepare(`
    SELECT pay.*, 
      t.first_name, t.last_name,
      p.name as property_name
    FROM payments pay
    JOIN leases l ON pay.lease_id = l.id
    JOIN tenants t ON l.tenant_id = t.id
    JOIN properties p ON l.property_id = p.id
    ORDER BY pay.created_at DESC
  `).all();
  res.json(payments);
});

app.post('/api/payments', (req, res) => {
  const { lease_id, amount, payment_date, payment_method, status, notes } = req.body;
  if (!lease_id || !amount || !payment_date) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  const id = uuidv4();
  db.prepare(`
    INSERT INTO payments (id, lease_id, amount, payment_date, payment_method, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).run(id, lease_id, amount, payment_date, payment_method || 'bank_transfer', status || 'paid', notes || '');
  res.status(201).json(db.prepare('SELECT * FROM payments WHERE id = ?').get(id));
});

// ─── Dashboard Stats ─────────────────────────────────────────────────────────

app.get('/api/dashboard', (req, res) => {
  const totalProperties = db.prepare('SELECT COUNT(*) as count FROM properties').get().count;
  const availableProperties = db.prepare("SELECT COUNT(*) as count FROM properties WHERE status='available'").get().count;
  const occupiedProperties = db.prepare("SELECT COUNT(*) as count FROM properties WHERE status='occupied'").get().count;
  const totalTenants = db.prepare('SELECT COUNT(*) as count FROM tenants').get().count;
  const activeLeases = db.prepare("SELECT COUNT(*) as count FROM leases WHERE status='active'").get().count;
  const monthlyRevenue = db.prepare("SELECT COALESCE(SUM(monthly_rent), 0) as total FROM leases WHERE status='active'").get().total;
  const recentPayments = db.prepare(`
    SELECT pay.*, t.first_name, t.last_name, p.name as property_name
    FROM payments pay
    JOIN leases l ON pay.lease_id = l.id
    JOIN tenants t ON l.tenant_id = t.id
    JOIN properties p ON l.property_id = p.id
    ORDER BY pay.created_at DESC LIMIT 5
  `).all();
  res.json({
    totalProperties,
    availableProperties,
    occupiedProperties,
    totalTenants,
    activeLeases,
    monthlyRevenue,
    recentPayments
  });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
