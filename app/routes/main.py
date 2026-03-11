from flask import Blueprint, render_template
from ..models import Property, Tenant, Lease, MaintenanceRequest, Payment

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    total_properties = Property.query.count()
    total_units = sum(p.num_units for p in Property.query.all())
    total_tenants = Tenant.query.count()
    active_leases = Lease.query.filter_by(status="active").count()
    open_maintenance = MaintenanceRequest.query.filter_by(status="open").count()

    recent_payments = (
        Payment.query.order_by(Payment.payment_date.desc()).limit(5).all()
    )
    recent_maintenance = (
        MaintenanceRequest.query.order_by(MaintenanceRequest.created_at.desc()).limit(5).all()
    )

    monthly_revenue = sum(
        p.amount
        for p in Payment.query.filter_by(status="paid").all()
    )

    return render_template(
        "index.html",
        total_properties=total_properties,
        total_units=total_units,
        total_tenants=total_tenants,
        active_leases=active_leases,
        open_maintenance=open_maintenance,
        recent_payments=recent_payments,
        recent_maintenance=recent_maintenance,
        monthly_revenue=monthly_revenue,
    )
