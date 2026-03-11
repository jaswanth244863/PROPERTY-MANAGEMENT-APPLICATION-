from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import date
from ..models import Tenant
from .. import db

bp = Blueprint("tenants", __name__, url_prefix="/tenants")


@bp.route("/")
def list_tenants():
    tenants = Tenant.query.order_by(Tenant.last_name).all()
    return render_template("tenants/list.html", tenants=tenants)


@bp.route("/<int:id>")
def detail(id):
    tenant = Tenant.query.get_or_404(id)
    return render_template("tenants/detail.html", tenant=tenant)


@bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        dob_str = request.form.get("date_of_birth", "")
        dob = date.fromisoformat(dob_str) if dob_str else None
        tenant = Tenant(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            email=request.form["email"],
            phone=request.form["phone"],
            date_of_birth=dob,
            emergency_contact_name=request.form.get("emergency_contact_name", ""),
            emergency_contact_phone=request.form.get("emergency_contact_phone", ""),
        )
        db.session.add(tenant)
        db.session.commit()
        flash(f"Tenant {tenant.full_name} added successfully.", "success")
        return redirect(url_for("tenants.detail", id=tenant.id))
    return render_template("tenants/form.html", tenant=None)


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    tenant = Tenant.query.get_or_404(id)
    if request.method == "POST":
        dob_str = request.form.get("date_of_birth", "")
        tenant.first_name = request.form["first_name"]
        tenant.last_name = request.form["last_name"]
        tenant.email = request.form["email"]
        tenant.phone = request.form["phone"]
        tenant.date_of_birth = date.fromisoformat(dob_str) if dob_str else None
        tenant.emergency_contact_name = request.form.get("emergency_contact_name", "")
        tenant.emergency_contact_phone = request.form.get("emergency_contact_phone", "")
        db.session.commit()
        flash(f"Tenant {tenant.full_name} updated.", "success")
        return redirect(url_for("tenants.detail", id=tenant.id))
    return render_template("tenants/form.html", tenant=tenant)


@bp.route("/<int:id>/delete", methods=["POST"])
def delete(id):
    tenant = Tenant.query.get_or_404(id)
    name = tenant.full_name
    db.session.delete(tenant)
    db.session.commit()
    flash(f"Tenant {name} deleted.", "info")
    return redirect(url_for("tenants.list_tenants"))
