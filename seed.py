"""Seed the database with sample data for demonstration."""
from datetime import date, timedelta
from app import create_app, db
from app.models import Property, Unit, Tenant, Lease, MaintenanceRequest, Payment


def seed():
    app = create_app()
    with app.app_context():
        # Clear existing data
        Payment.query.delete()
        MaintenanceRequest.query.delete()
        Lease.query.delete()
        Unit.query.delete()
        Tenant.query.delete()
        Property.query.delete()
        db.session.commit()

        # Properties
        prop1 = Property(
            name="Sunset Apartments",
            address="123 Sunset Blvd",
            city="Los Angeles",
            state="CA",
            zip_code="90028",
            property_type="apartment",
            num_units=3,
            description="Modern apartment complex with pool and gym.",
        )
        prop2 = Property(
            name="Maple Street House",
            address="456 Maple St",
            city="Chicago",
            state="IL",
            zip_code="60614",
            property_type="house",
            num_units=1,
            description="Single-family home with a large backyard.",
        )
        db.session.add_all([prop1, prop2])
        db.session.commit()

        # Units
        u1 = Unit(property_id=prop1.id, unit_number="101", bedrooms=2, bathrooms=1.0,
                  rent_amount=1800.0, square_feet=850, status="occupied")
        u2 = Unit(property_id=prop1.id, unit_number="102", bedrooms=1, bathrooms=1.0,
                  rent_amount=1400.0, square_feet=620, status="available")
        u3 = Unit(property_id=prop1.id, unit_number="201", bedrooms=3, bathrooms=2.0,
                  rent_amount=2500.0, square_feet=1100, status="occupied")
        u4 = Unit(property_id=prop2.id, unit_number="Main", bedrooms=4, bathrooms=2.5,
                  rent_amount=3200.0, square_feet=2100, status="occupied")
        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        # Tenants
        t1 = Tenant(first_name="Alice", last_name="Johnson", email="alice@example.com",
                    phone="555-101-2020", emergency_contact_name="Bob Johnson",
                    emergency_contact_phone="555-101-3030")
        t2 = Tenant(first_name="Carlos", last_name="Rivera", email="carlos@example.com",
                    phone="555-202-3030")
        t3 = Tenant(first_name="Diana", last_name="Smith", email="diana@example.com",
                    phone="555-303-4040", emergency_contact_name="John Smith",
                    emergency_contact_phone="555-303-5050")
        db.session.add_all([t1, t2, t3])
        db.session.commit()

        # Leases
        today = date.today()
        l1 = Lease(unit_id=u1.id, tenant_id=t1.id,
                   start_date=today - timedelta(days=180),
                   end_date=today + timedelta(days=185),
                   rent_amount=1800.0, security_deposit=3600.0, status="active")
        l2 = Lease(unit_id=u3.id, tenant_id=t2.id,
                   start_date=today - timedelta(days=90),
                   end_date=today + timedelta(days=275),
                   rent_amount=2500.0, security_deposit=5000.0, status="active")
        l3 = Lease(unit_id=u4.id, tenant_id=t3.id,
                   start_date=today - timedelta(days=30),
                   end_date=today + timedelta(days=335),
                   rent_amount=3200.0, security_deposit=6400.0, status="active")
        db.session.add_all([l1, l2, l3])
        db.session.commit()

        # Payments
        p1 = Payment(lease_id=l1.id, amount=1800.0,
                     payment_date=today - timedelta(days=150),
                     due_date=today - timedelta(days=150),
                     payment_method="online", payment_type="rent", status="paid")
        p2 = Payment(lease_id=l1.id, amount=1800.0,
                     payment_date=today - timedelta(days=120),
                     due_date=today - timedelta(days=120),
                     payment_method="online", payment_type="rent", status="paid")
        p3 = Payment(lease_id=l2.id, amount=2500.0,
                     payment_date=today - timedelta(days=60),
                     due_date=today - timedelta(days=60),
                     payment_method="bank_transfer", payment_type="rent", status="paid")
        p4 = Payment(lease_id=l3.id, amount=6400.0,
                     payment_date=today - timedelta(days=30),
                     due_date=today - timedelta(days=30),
                     payment_method="check", payment_type="deposit", status="paid")
        db.session.add_all([p1, p2, p3, p4])

        # Maintenance requests
        m1 = MaintenanceRequest(unit_id=u1.id, title="Leaking faucet in bathroom",
                                description="The bathroom faucet has been dripping non-stop.",
                                priority="medium", status="open", reported_by="Alice Johnson",
                                estimated_cost=150.0)
        m2 = MaintenanceRequest(unit_id=u3.id, title="HVAC not cooling properly",
                                description="The air conditioning unit is not reaching set temperature.",
                                priority="high", status="in_progress",
                                reported_by="Carlos Rivera", assigned_to="Mike's HVAC Services",
                                estimated_cost=400.0)
        m3 = MaintenanceRequest(unit_id=u4.id, title="Broken window latch",
                                description="Master bedroom window latch is broken.",
                                priority="low", status="completed",
                                reported_by="Diana Smith", actual_cost=75.0,
                                completed_at=today - timedelta(days=5))
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        print("✅ Database seeded successfully!")
        print(f"   Properties: {Property.query.count()}")
        print(f"   Units: {Unit.query.count()}")
        print(f"   Tenants: {Tenant.query.count()}")
        print(f"   Leases: {Lease.query.count()}")
        print(f"   Payments: {Payment.query.count()}")
        print(f"   Maintenance: {MaintenanceRequest.query.count()}")


if __name__ == "__main__":
    seed()
