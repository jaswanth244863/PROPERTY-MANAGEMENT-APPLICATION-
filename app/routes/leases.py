from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import date
from ..models import Lease, Unit, Tenant
from .. import db

bp = Blueprint("leases", __name__, url_prefix="/leases")


@bp.route("/")
def list_leases():
    leases = Lease.query.order_by(Lease.start_date.desc()).all()
    return render_template("leases/list.html", leases=leases)


@bp.route("/<int:id>")
def detail(id):
    lease = Lease.query.get_or_404(id)
    return render_template("leases/detail.html", lease=lease)


@bp.route("/new", methods=["GET", "POST"])
def new():
    units = Unit.query.filter_by(status="available").all()
    tenants = Tenant.query.order_by(Tenant.last_name).all()
    if request.method == "POST":
        lease = Lease(
            unit_id=int(request.form["unit_id"]),
            tenant_id=int(request.form["tenant_id"]),
            start_date=date.fromisoformat(request.form["start_date"]),
            end_date=date.fromisoformat(request.form["end_date"]),
            rent_amount=float(request.form["rent_amount"]),
            security_deposit=float(request.form.get("security_deposit", 0)),
            status="active",
            notes=request.form.get("notes", ""),
        )
        db.session.add(lease)
        unit = db.session.get(Unit, lease.unit_id)
        if unit:
            unit.status = "occupied"
        db.session.commit()
        flash("Lease created successfully.", "success")
        return redirect(url_for("leases.detail", id=lease.id))
    return render_template("leases/form.html", lease=None, units=units, tenants=tenants)


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    lease = Lease.query.get_or_404(id)
    units = Unit.query.all()
    tenants = Tenant.query.order_by(Tenant.last_name).all()
    if request.method == "POST":
        old_unit_id = lease.unit_id
        lease.unit_id = int(request.form["unit_id"])
        lease.tenant_id = int(request.form["tenant_id"])
        lease.start_date = date.fromisoformat(request.form["start_date"])
        lease.end_date = date.fromisoformat(request.form["end_date"])
        lease.rent_amount = float(request.form["rent_amount"])
        lease.security_deposit = float(request.form.get("security_deposit", lease.security_deposit))
        lease.status = request.form.get("status", lease.status)
        lease.notes = request.form.get("notes", lease.notes)
        if old_unit_id != lease.unit_id:
            old_unit = db.session.get(Unit, old_unit_id)
            if old_unit:
                old_unit.status = "available"
            new_unit = db.session.get(Unit, lease.unit_id)
            if new_unit and lease.status == "active":
                new_unit.status = "occupied"
        if lease.status in ("expired", "terminated"):
            unit = db.session.get(Unit, lease.unit_id)
            if unit:
                unit.status = "available"
        db.session.commit()
        flash("Lease updated successfully.", "success")
        return redirect(url_for("leases.detail", id=lease.id))
    return render_template("leases/form.html", lease=lease, units=units, tenants=tenants)


@bp.route("/<int:id>/terminate", methods=["POST"])
def terminate(id):
    lease = Lease.query.get_or_404(id)
    lease.status = "terminated"
    unit = db.session.get(Unit, lease.unit_id)
    if unit:
        unit.status = "available"
    db.session.commit()
    flash("Lease terminated.", "warning")
    return redirect(url_for("leases.list_leases"))
