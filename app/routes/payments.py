from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import date
from ..models import Payment, Lease
from .. import db

bp = Blueprint("payments", __name__, url_prefix="/payments")


@bp.route("/")
def list_payments():
    payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    return render_template("payments/list.html", payments=payments)


@bp.route("/<int:id>")
def detail(id):
    payment = Payment.query.get_or_404(id)
    return render_template("payments/detail.html", payment=payment)


@bp.route("/new", methods=["GET", "POST"])
def new():
    leases = Lease.query.filter_by(status="active").all()
    if request.method == "POST":
        payment = Payment(
            lease_id=int(request.form["lease_id"]),
            amount=float(request.form["amount"]),
            payment_date=date.fromisoformat(request.form["payment_date"]),
            due_date=date.fromisoformat(request.form["due_date"]),
            payment_method=request.form.get("payment_method", ""),
            payment_type=request.form.get("payment_type", "rent"),
            status=request.form.get("status", "paid"),
            notes=request.form.get("notes", ""),
        )
        db.session.add(payment)
        db.session.commit()
        flash("Payment recorded successfully.", "success")
        return redirect(url_for("payments.list_payments"))
    return render_template("payments/form.html", payment=None, leases=leases)


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit(id):
    payment = Payment.query.get_or_404(id)
    leases = Lease.query.all()
    if request.method == "POST":
        payment.lease_id = int(request.form["lease_id"])
        payment.amount = float(request.form["amount"])
        payment.payment_date = date.fromisoformat(request.form["payment_date"])
        payment.due_date = date.fromisoformat(request.form["due_date"])
        payment.payment_method = request.form.get("payment_method", payment.payment_method)
        payment.payment_type = request.form.get("payment_type", payment.payment_type)
        payment.status = request.form.get("status", payment.status)
        payment.notes = request.form.get("notes", payment.notes)
        db.session.commit()
        flash("Payment updated.", "success")
        return redirect(url_for("payments.list_payments"))
    return render_template("payments/form.html", payment=payment, leases=leases)


@bp.route("/<int:id>/delete", methods=["POST"])
def delete(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    flash("Payment record deleted.", "info")
    return redirect(url_for("payments.list_payments"))
