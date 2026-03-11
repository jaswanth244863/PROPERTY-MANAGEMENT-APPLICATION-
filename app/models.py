from datetime import date
from . import db


class Property(db.Model):
    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)  # apartment, house, condo, commercial, townhouse, duplex
    num_units = db.Column(db.Integer, default=1)
    description = db.Column(db.Text, default="")
    created_at = db.Column(db.Date, default=date.today)

    units = db.relationship("Unit", backref="property", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Property {self.name}>"

    @property
    def available_units(self):
        return sum(1 for u in self.units if u.status == "available")

    @property
    def occupied_units(self):
        return sum(1 for u in self.units if u.status == "occupied")


class Unit(db.Model):
    __tablename__ = "units"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)
    unit_number = db.Column(db.String(20), nullable=False)
    bedrooms = db.Column(db.Integer, default=1)
    bathrooms = db.Column(db.Float, default=1.0)
    rent_amount = db.Column(db.Float, nullable=False)
    square_feet = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="available")  # available, occupied, maintenance

    leases = db.relationship("Lease", backref="unit", lazy=True)
    maintenance_requests = db.relationship("MaintenanceRequest", backref="unit", lazy=True)

    def __repr__(self):
        return f"<Unit {self.unit_number}>"

    @property
    def active_lease(self):
        return next(
            (l for l in self.leases if l.status == "active"),
            None,
        )


class Tenant(db.Model):
    __tablename__ = "tenants"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    emergency_contact_name = db.Column(db.String(160), default="")
    emergency_contact_phone = db.Column(db.String(20), default="")
    created_at = db.Column(db.Date, default=date.today)

    leases = db.relationship("Lease", backref="tenant", lazy=True)

    def __repr__(self):
        return f"<Tenant {self.first_name} {self.last_name}>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def active_lease(self):
        return next(
            (l for l in self.leases if l.status == "active"),
            None,
        )


class Lease(db.Model):
    __tablename__ = "leases"

    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey("units.id"), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    rent_amount = db.Column(db.Float, nullable=False)
    security_deposit = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="active")  # active, expired, terminated
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.Date, default=date.today)

    payments = db.relationship("Payment", backref="lease", lazy=True)

    def __repr__(self):
        return f"<Lease {self.id}>"


class MaintenanceRequest(db.Model):
    __tablename__ = "maintenance_requests"

    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey("units.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default="medium")  # low, medium, high, urgent
    status = db.Column(db.String(20), default="open")  # open, in_progress, completed, cancelled
    reported_by = db.Column(db.String(120), default="")
    assigned_to = db.Column(db.String(120), default="")
    estimated_cost = db.Column(db.Float, default=0.0)
    actual_cost = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.Date, default=date.today)
    completed_at = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"<MaintenanceRequest {self.title}>"


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    lease_id = db.Column(db.Integer, db.ForeignKey("leases.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50), default="")  # cash, check, online, bank transfer
    payment_type = db.Column(db.String(50), default="rent")  # rent, deposit, late_fee, other
    status = db.Column(db.String(20), default="paid")  # paid, pending, late, partial
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.Date, default=date.today)

    def __repr__(self):
        return f"<Payment {self.id}>"
