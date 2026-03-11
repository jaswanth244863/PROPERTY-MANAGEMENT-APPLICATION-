from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import Property, Unit
from .. import db

bp = Blueprint("properties", __name__, url_prefix="/properties")


@bp.route("/")
def list_properties():
    properties = Property.query.order_by(Property.name).all()
    return render_template("properties/list.html", properties=properties)


@bp.route("/<int:id>")
def detail(id):
    prop = Property.query.get_or_404(id)
    return render_template("properties/detail.html", property=prop)


@bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        prop = Property(
            name=request.form["name"],
            address=request.form["address"],
            city=request.form["city"],
            state=request.form["state"],
            zip_code=request.form["zip_code"],
            property_type=request.form["property_type"],
            num_units=int(request.form.get("num_units", 1)),
            description=request.form.get("description", ""),
        )
        db.session.add(prop)
        db.session.commit()
        flash(f'Property "{prop.name}" added successfully.', "success")
        return redirect(url_for("properties.detail", id=prop.id))
    return render_template("properties/form.html", property=None)


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    prop = Property.query.get_or_404(id)
    if request.method == "POST":
        prop.name = request.form["name"]
        prop.address = request.form["address"]
        prop.city = request.form["city"]
        prop.state = request.form["state"]
        prop.zip_code = request.form["zip_code"]
        prop.property_type = request.form["property_type"]
        prop.num_units = int(request.form.get("num_units", prop.num_units))
        prop.description = request.form.get("description", prop.description)
        db.session.commit()
        flash(f'Property "{prop.name}" updated successfully.', "success")
        return redirect(url_for("properties.detail", id=prop.id))
    return render_template("properties/form.html", property=prop)


@bp.route("/<int:id>/delete", methods=["POST"])
def delete(id):
    prop = Property.query.get_or_404(id)
    name = prop.name
    db.session.delete(prop)
    db.session.commit()
    flash(f'Property "{name}" deleted.', "info")
    return redirect(url_for("properties.list_properties"))


@bp.route("/<int:property_id>/units/new", methods=["GET", "POST"])
def new_unit(property_id):
    prop = Property.query.get_or_404(property_id)
    if request.method == "POST":
        unit = Unit(
            property_id=property_id,
            unit_number=request.form["unit_number"],
            bedrooms=int(request.form.get("bedrooms", 1)),
            bathrooms=float(request.form.get("bathrooms", 1.0)),
            rent_amount=float(request.form["rent_amount"]),
            square_feet=int(request.form.get("square_feet", 0)),
            status=request.form.get("status", "available"),
        )
        db.session.add(unit)
        db.session.commit()
        flash(f"Unit {unit.unit_number} added to {prop.name}.", "success")
        return redirect(url_for("properties.detail", id=property_id))
    return render_template("properties/unit_form.html", property=prop, unit=None)


@bp.route("/<int:property_id>/units/<int:unit_id>/edit", methods=["GET", "POST"])
def edit_unit(property_id, unit_id):
    prop = Property.query.get_or_404(property_id)
    unit = Unit.query.get_or_404(unit_id)
    if request.method == "POST":
        unit.unit_number = request.form["unit_number"]
        unit.bedrooms = int(request.form.get("bedrooms", unit.bedrooms))
        unit.bathrooms = float(request.form.get("bathrooms", unit.bathrooms))
        unit.rent_amount = float(request.form["rent_amount"])
        unit.square_feet = int(request.form.get("square_feet", unit.square_feet))
        unit.status = request.form.get("status", unit.status)
        db.session.commit()
        flash(f"Unit {unit.unit_number} updated.", "success")
        return redirect(url_for("properties.detail", id=property_id))
    return render_template("properties/unit_form.html", property=prop, unit=unit)


@bp.route("/<int:property_id>/units/<int:unit_id>/delete", methods=["POST"])
def delete_unit(property_id, unit_id):
    unit = Unit.query.get_or_404(unit_id)
    db.session.delete(unit)
    db.session.commit()
    flash(f"Unit {unit.unit_number} deleted.", "info")
    return redirect(url_for("properties.detail", id=property_id))
