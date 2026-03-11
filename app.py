from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'pms-dev-secret-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///property_management.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.context_processor
def inject_globals():
    from datetime import datetime
    return {'now': datetime.utcnow, 'today': date.today().isoformat()}


# ── Models ──────────────────────────────────────────────────────────────────

class Property(db.Model):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)   # Apartment / House / Commercial
    units = db.Column(db.Integer, default=1)
    rent_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Available')     # Available / Occupied / Maintenance
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    leases = db.relationship('Lease', backref='property', lazy=True, cascade='all, delete-orphan')
    maintenance_requests = db.relationship('MaintenanceRequest', backref='property', lazy=True, cascade='all, delete-orphan')


class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    id_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    leases = db.relationship('Lease', backref='tenant', lazy=True, cascade='all, delete-orphan')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Lease(db.Model):
    __tablename__ = 'leases'
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    rent_amount = db.Column(db.Float, nullable=False)
    security_deposit = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='Active')   # Active / Expired / Terminated
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    payments = db.relationship('Payment', backref='lease', lazy=True, cascade='all, delete-orphan')


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    lease_id = db.Column(db.Integer, db.ForeignKey('leases.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=date.today)
    payment_method = db.Column(db.String(50))   # Cash / Bank Transfer / Check / Online
    status = db.Column(db.String(20), default='Paid')   # Paid / Pending / Overdue
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_requests'
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='Medium')   # Low / Medium / High / Urgent
    status = db.Column(db.String(20), default='Open')       # Open / In Progress / Completed / Cancelled
    requested_by = db.Column(db.String(150))
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ── Dashboard ────────────────────────────────────────────────────────────────

@app.route('/')
def dashboard():
    total_properties = Property.query.count()
    available_properties = Property.query.filter_by(status='Available').count()
    occupied_properties = Property.query.filter_by(status='Occupied').count()
    total_tenants = Tenant.query.count()
    active_leases = Lease.query.filter_by(status='Active').count()
    open_maintenance = MaintenanceRequest.query.filter_by(status='Open').count()

    current_month_start = date.today().replace(day=1)
    monthly_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.status == 'Paid',
        Payment.payment_date >= current_month_start
    ).scalar() or 0

    recent_payments = Payment.query.order_by(Payment.created_at.desc()).limit(5).all()
    recent_requests = MaintenanceRequest.query.order_by(MaintenanceRequest.created_at.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        total_properties=total_properties,
        available_properties=available_properties,
        occupied_properties=occupied_properties,
        total_tenants=total_tenants,
        active_leases=active_leases,
        open_maintenance=open_maintenance,
        monthly_revenue=monthly_revenue,
        recent_payments=recent_payments,
        recent_requests=recent_requests,
    )


# ── Properties ───────────────────────────────────────────────────────────────

@app.route('/properties')
def properties():
    status_filter = request.args.get('status', '')
    query = Property.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    all_properties = query.order_by(Property.created_at.desc()).all()
    return render_template('properties/list.html', properties=all_properties, status_filter=status_filter)


@app.route('/properties/add', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        prop = Property(
            name=request.form['name'],
            address=request.form['address'],
            property_type=request.form['property_type'],
            units=int(request.form.get('units', 1)),
            rent_amount=float(request.form['rent_amount']),
            status=request.form.get('status', 'Available'),
            description=request.form.get('description', ''),
        )
        db.session.add(prop)
        db.session.commit()
        flash('Property added successfully!', 'success')
        return redirect(url_for('properties'))
    return render_template('properties/form.html', property=None, action='Add')


@app.route('/properties/<int:prop_id>/edit', methods=['GET', 'POST'])
def edit_property(prop_id):
    prop = Property.query.get_or_404(prop_id)
    if request.method == 'POST':
        prop.name = request.form['name']
        prop.address = request.form['address']
        prop.property_type = request.form['property_type']
        prop.units = int(request.form.get('units', 1))
        prop.rent_amount = float(request.form['rent_amount'])
        prop.status = request.form.get('status', 'Available')
        prop.description = request.form.get('description', '')
        db.session.commit()
        flash('Property updated successfully!', 'success')
        return redirect(url_for('properties'))
    return render_template('properties/form.html', property=prop, action='Edit')


@app.route('/properties/<int:prop_id>/delete', methods=['POST'])
def delete_property(prop_id):
    prop = Property.query.get_or_404(prop_id)
    db.session.delete(prop)
    db.session.commit()
    flash('Property deleted successfully!', 'success')
    return redirect(url_for('properties'))


@app.route('/properties/<int:prop_id>')
def property_detail(prop_id):
    prop = Property.query.get_or_404(prop_id)
    return render_template('properties/detail.html', property=prop)


# ── Tenants ──────────────────────────────────────────────────────────────────

@app.route('/tenants')
def tenants():
    all_tenants = Tenant.query.order_by(Tenant.created_at.desc()).all()
    return render_template('tenants/list.html', tenants=all_tenants)


@app.route('/tenants/add', methods=['GET', 'POST'])
def add_tenant():
    if request.method == 'POST':
        existing = Tenant.query.filter_by(email=request.form['email']).first()
        if existing:
            flash('A tenant with this email already exists.', 'danger')
            return render_template('tenants/form.html', tenant=None, action='Add')
        tenant = Tenant(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            phone=request.form.get('phone', ''),
            id_number=request.form.get('id_number', ''),
        )
        db.session.add(tenant)
        db.session.commit()
        flash('Tenant added successfully!', 'success')
        return redirect(url_for('tenants'))
    return render_template('tenants/form.html', tenant=None, action='Add')


@app.route('/tenants/<int:tenant_id>/edit', methods=['GET', 'POST'])
def edit_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    if request.method == 'POST':
        existing = Tenant.query.filter(
            Tenant.email == request.form['email'],
            Tenant.id != tenant_id
        ).first()
        if existing:
            flash('A tenant with this email already exists.', 'danger')
            return render_template('tenants/form.html', tenant=tenant, action='Edit')
        tenant.first_name = request.form['first_name']
        tenant.last_name = request.form['last_name']
        tenant.email = request.form['email']
        tenant.phone = request.form.get('phone', '')
        tenant.id_number = request.form.get('id_number', '')
        db.session.commit()
        flash('Tenant updated successfully!', 'success')
        return redirect(url_for('tenants'))
    return render_template('tenants/form.html', tenant=tenant, action='Edit')


@app.route('/tenants/<int:tenant_id>/delete', methods=['POST'])
def delete_tenant(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    db.session.delete(tenant)
    db.session.commit()
    flash('Tenant deleted successfully!', 'success')
    return redirect(url_for('tenants'))


@app.route('/tenants/<int:tenant_id>')
def tenant_detail(tenant_id):
    tenant = Tenant.query.get_or_404(tenant_id)
    return render_template('tenants/detail.html', tenant=tenant)


# ── Leases ───────────────────────────────────────────────────────────────────

@app.route('/leases')
def leases():
    status_filter = request.args.get('status', '')
    query = Lease.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    all_leases = query.order_by(Lease.created_at.desc()).all()
    return render_template('leases/list.html', leases=all_leases, status_filter=status_filter)


@app.route('/leases/add', methods=['GET', 'POST'])
def add_lease():
    if request.method == 'POST':
        start = date.fromisoformat(request.form['start_date'])
        end = date.fromisoformat(request.form['end_date'])
        if end <= start:
            flash('End date must be after start date.', 'danger')
            return render_template('leases/form.html', lease=None, action='Add',
                                   properties=Property.query.all(),
                                   tenants=Tenant.query.all())
        lease = Lease(
            property_id=int(request.form['property_id']),
            tenant_id=int(request.form['tenant_id']),
            start_date=start,
            end_date=end,
            rent_amount=float(request.form['rent_amount']),
            security_deposit=float(request.form.get('security_deposit', 0)),
            status=request.form.get('status', 'Active'),
            notes=request.form.get('notes', ''),
        )
        db.session.add(lease)
        # Update property status
        prop = Property.query.get(lease.property_id)
        if prop and lease.status == 'Active':
            prop.status = 'Occupied'
        db.session.commit()
        flash('Lease created successfully!', 'success')
        return redirect(url_for('leases'))
    return render_template('leases/form.html', lease=None, action='Add',
                           properties=Property.query.all(),
                           tenants=Tenant.query.all())


@app.route('/leases/<int:lease_id>/edit', methods=['GET', 'POST'])
def edit_lease(lease_id):
    lease = Lease.query.get_or_404(lease_id)
    if request.method == 'POST':
        start = date.fromisoformat(request.form['start_date'])
        end = date.fromisoformat(request.form['end_date'])
        if end <= start:
            flash('End date must be after start date.', 'danger')
            return render_template('leases/form.html', lease=lease, action='Edit',
                                   properties=Property.query.all(),
                                   tenants=Tenant.query.all())
        lease.property_id = int(request.form['property_id'])
        lease.tenant_id = int(request.form['tenant_id'])
        lease.start_date = start
        lease.end_date = end
        lease.rent_amount = float(request.form['rent_amount'])
        lease.security_deposit = float(request.form.get('security_deposit', 0))
        lease.status = request.form.get('status', 'Active')
        lease.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Lease updated successfully!', 'success')
        return redirect(url_for('leases'))
    return render_template('leases/form.html', lease=lease, action='Edit',
                           properties=Property.query.all(),
                           tenants=Tenant.query.all())


@app.route('/leases/<int:lease_id>/terminate', methods=['POST'])
def terminate_lease(lease_id):
    lease = Lease.query.get_or_404(lease_id)
    lease.status = 'Terminated'
    prop = Property.query.get(lease.property_id)
    if prop:
        prop.status = 'Available'
    db.session.commit()
    flash('Lease terminated successfully.', 'warning')
    return redirect(url_for('leases'))


@app.route('/leases/<int:lease_id>')
def lease_detail(lease_id):
    lease = Lease.query.get_or_404(lease_id)
    return render_template('leases/detail.html', lease=lease)


# ── Payments ─────────────────────────────────────────────────────────────────

@app.route('/payments')
def payments():
    status_filter = request.args.get('status', '')
    query = Payment.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    all_payments = query.order_by(Payment.created_at.desc()).all()
    return render_template('payments/list.html', payments=all_payments, status_filter=status_filter)


@app.route('/payments/add', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        payment = Payment(
            lease_id=int(request.form['lease_id']),
            amount=float(request.form['amount']),
            payment_date=date.fromisoformat(request.form['payment_date']),
            payment_method=request.form.get('payment_method', ''),
            status=request.form.get('status', 'Paid'),
            notes=request.form.get('notes', ''),
        )
        db.session.add(payment)
        db.session.commit()
        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('payments'))
    active_leases = Lease.query.filter_by(status='Active').all()
    return render_template('payments/form.html', payment=None, action='Add', leases=active_leases)


@app.route('/payments/<int:payment_id>/edit', methods=['GET', 'POST'])
def edit_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    if request.method == 'POST':
        payment.lease_id = int(request.form['lease_id'])
        payment.amount = float(request.form['amount'])
        payment.payment_date = date.fromisoformat(request.form['payment_date'])
        payment.payment_method = request.form.get('payment_method', '')
        payment.status = request.form.get('status', 'Paid')
        payment.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Payment updated successfully!', 'success')
        return redirect(url_for('payments'))
    active_leases = Lease.query.filter_by(status='Active').all()
    return render_template('payments/form.html', payment=payment, action='Edit', leases=active_leases)


@app.route('/payments/<int:payment_id>/delete', methods=['POST'])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    db.session.delete(payment)
    db.session.commit()
    flash('Payment deleted successfully!', 'success')
    return redirect(url_for('payments'))


# ── Maintenance ───────────────────────────────────────────────────────────────

@app.route('/maintenance')
def maintenance():
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    query = MaintenanceRequest.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    all_requests = query.order_by(MaintenanceRequest.created_at.desc()).all()
    return render_template('maintenance/list.html', requests=all_requests,
                           status_filter=status_filter, priority_filter=priority_filter)


@app.route('/maintenance/add', methods=['GET', 'POST'])
def add_maintenance():
    if request.method == 'POST':
        req = MaintenanceRequest(
            property_id=int(request.form['property_id']),
            title=request.form['title'],
            description=request.form['description'],
            priority=request.form.get('priority', 'Medium'),
            status=request.form.get('status', 'Open'),
            requested_by=request.form.get('requested_by', ''),
        )
        db.session.add(req)
        db.session.commit()
        flash('Maintenance request submitted!', 'success')
        return redirect(url_for('maintenance'))
    return render_template('maintenance/form.html', req=None, action='Add',
                           properties=Property.query.all())


@app.route('/maintenance/<int:req_id>/edit', methods=['GET', 'POST'])
def edit_maintenance(req_id):
    req = MaintenanceRequest.query.get_or_404(req_id)
    if request.method == 'POST':
        req.property_id = int(request.form['property_id'])
        req.title = request.form['title']
        req.description = request.form['description']
        req.priority = request.form.get('priority', 'Medium')
        old_status = req.status
        req.status = request.form.get('status', 'Open')
        req.requested_by = request.form.get('requested_by', '')
        if req.status == 'Completed' and old_status != 'Completed':
            req.resolved_at = datetime.utcnow()
        db.session.commit()
        flash('Maintenance request updated!', 'success')
        return redirect(url_for('maintenance'))
    return render_template('maintenance/form.html', req=req, action='Edit',
                           properties=Property.query.all())


@app.route('/maintenance/<int:req_id>/delete', methods=['POST'])
def delete_maintenance(req_id):
    req = MaintenanceRequest.query.get_or_404(req_id)
    db.session.delete(req)
    db.session.commit()
    flash('Maintenance request deleted!', 'success')
    return redirect(url_for('maintenance'))


# ── DB Init & Sample Data ────────────────────────────────────────────────────

def seed_data():
    if Property.query.count() > 0:
        return

    props = [
        Property(name='Sunset Apartments Unit 1A', address='123 Sunset Blvd, Los Angeles, CA 90001',
                 property_type='Apartment', units=1, rent_amount=1500, status='Occupied',
                 description='Cozy 1-bedroom apartment with great views.'),
        Property(name='Greenwood House', address='456 Elm Street, Austin, TX 78701',
                 property_type='House', units=3, rent_amount=2800, status='Available',
                 description='Spacious 3-bedroom house with a large backyard.'),
        Property(name='Downtown Office Suite', address='789 Main St, Suite 200, New York, NY 10001',
                 property_type='Commercial', units=1, rent_amount=5000, status='Occupied',
                 description='Prime commercial office space in the heart of downtown.'),
        Property(name='Lake View Condo', address='321 Lakeside Dr, Chicago, IL 60601',
                 property_type='Apartment', units=2, rent_amount=2200, status='Maintenance',
                 description='2-bedroom condo with stunning lake views.'),
    ]
    db.session.add_all(props)
    db.session.flush()

    tenants = [
        Tenant(first_name='Alice', last_name='Johnson', email='alice.johnson@email.com',
               phone='555-0101', id_number='ID001'),
        Tenant(first_name='Bob', last_name='Smith', email='bob.smith@email.com',
               phone='555-0102', id_number='ID002'),
        Tenant(first_name='Carol', last_name='Williams', email='carol.williams@email.com',
               phone='555-0103', id_number='ID003'),
    ]
    db.session.add_all(tenants)
    db.session.flush()

    leases = [
        Lease(property_id=props[0].id, tenant_id=tenants[0].id,
              start_date=date(2024, 1, 1), end_date=date(2024, 12, 31),
              rent_amount=1500, security_deposit=3000, status='Active',
              notes='Annual lease.'),
        Lease(property_id=props[2].id, tenant_id=tenants[1].id,
              start_date=date(2024, 3, 1), end_date=date(2025, 2, 28),
              rent_amount=5000, security_deposit=10000, status='Active',
              notes='Commercial lease for software company.'),
    ]
    db.session.add_all(leases)
    db.session.flush()

    payments = [
        Payment(lease_id=leases[0].id, amount=1500, payment_date=date(2024, 1, 1),
                payment_method='Bank Transfer', status='Paid'),
        Payment(lease_id=leases[0].id, amount=1500, payment_date=date(2024, 2, 1),
                payment_method='Bank Transfer', status='Paid'),
        Payment(lease_id=leases[0].id, amount=1500, payment_date=date(2024, 3, 1),
                payment_method='Bank Transfer', status='Paid'),
        Payment(lease_id=leases[1].id, amount=5000, payment_date=date(2024, 3, 1),
                payment_method='Check', status='Paid'),
    ]
    db.session.add_all(payments)

    maintenance = [
        MaintenanceRequest(property_id=props[3].id, title='HVAC Not Working',
                           description='The air conditioning unit stopped working.',
                           priority='High', status='Open', requested_by='Management'),
        MaintenanceRequest(property_id=props[0].id, title='Leaky Faucet',
                           description='The kitchen faucet is dripping continuously.',
                           priority='Medium', status='In Progress', requested_by='Alice Johnson'),
    ]
    db.session.add_all(maintenance)
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, port=5000)
