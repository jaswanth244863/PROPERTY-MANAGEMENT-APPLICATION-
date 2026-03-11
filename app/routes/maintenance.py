from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import date
from ..models import MaintenanceRequest, Unit
from .. import db

bp = Blueprint("maintenance", __name__, url_prefix="/maintenance")


@bp.route("/")
def list_requests():
    status_filter = request.args.get("status", "")
    query = MaintenanceRequest.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    requests = query.order_by(MaintenanceRequest.created_at.desc()).all()
    return render_template("maintenance/list.html", requests=requests, status_filter=status_filter)


@bp.route("/<int:id>")
def detail(id):
    req = MaintenanceRequest.query.get_or_404(id)
    return render_template("maintenance/detail.html", request=req)


@bp.route("/new", methods=["GET", "POST"])
def new():
    units = Unit.query.all()
    if request.method == "POST":
        req = MaintenanceRequest(
            unit_id=int(request.form["unit_id"]),
            title=request.form["title"],
            description=request.form["description"],
            priority=request.form.get("priority", "medium"),
            status="open",
            reported_by=request.form.get("reported_by", ""),
            assigned_to=request.form.get("assigned_to", ""),
            estimated_cost=float(request.form.get("estimated_cost", 0)),
        )
        db.session.add(req)
        db.session.commit()
        flash("Maintenance request submitted.", "success")
        return redirect(url_for("maintenance.detail", id=req.id))
    return render_template("maintenance/form.html", request=None, units=units)


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    req = MaintenanceRequest.query.get_or_404(id)
    units = Unit.query.all()
    if request.method == "POST":
        req.unit_id = int(request.form["unit_id"])
        req.title = request.form["title"]
        req.description = request.form["description"]
        req.priority = request.form.get("priority", req.priority)
        req.status = request.form.get("status", req.status)
        req.reported_by = request.form.get("reported_by", req.reported_by)
        req.assigned_to = request.form.get("assigned_to", req.assigned_to)
        req.estimated_cost = float(request.form.get("estimated_cost", req.estimated_cost))
        req.actual_cost = float(request.form.get("actual_cost", req.actual_cost))
        if req.status == "completed" and not req.completed_at:
            req.completed_at = date.today()
        db.session.commit()
        flash("Maintenance request updated.", "success")
        return redirect(url_for("maintenance.detail", id=req.id))
    return render_template("maintenance/form.html", request=req, units=units)


@bp.route("/<int:id>/complete", methods=["POST"])
def complete(id):
    req = MaintenanceRequest.query.get_or_404(id)
    req.status = "completed"
    req.completed_at = date.today()
    actual_cost = request.form.get("actual_cost")
    if actual_cost:
        req.actual_cost = float(actual_cost)
    db.session.commit()
    flash("Maintenance request marked as completed.", "success")
    return redirect(url_for("maintenance.list_requests"))
