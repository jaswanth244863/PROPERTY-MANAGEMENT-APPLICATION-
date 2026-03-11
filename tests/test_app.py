import pytest
from app import create_app, db


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        WTF_CSRF_ENABLED=False,
    )
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_dashboard(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_properties_list_empty(client):
    response = client.get("/properties/")
    assert response.status_code == 200
    assert b"Properties" in response.data


def test_add_property(client):
    response = client.post(
        "/properties/new",
        data={
            "name": "Test Apartments",
            "address": "100 Test St",
            "city": "Testville",
            "state": "TX",
            "zip_code": "78000",
            "property_type": "apartment",
            "num_units": "5",
            "description": "A test property",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Test Apartments" in response.data


def test_tenants_list_empty(client):
    response = client.get("/tenants/")
    assert response.status_code == 200
    assert b"Tenants" in response.data


def test_add_tenant(client):
    response = client.post(
        "/tenants/new",
        data={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "phone": "555-000-1111",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Jane" in response.data


def test_leases_list_empty(client):
    response = client.get("/leases/")
    assert response.status_code == 200
    assert b"Leases" in response.data


def test_maintenance_list_empty(client):
    response = client.get("/maintenance/")
    assert response.status_code == 200
    assert b"Maintenance" in response.data


def test_payments_list_empty(client):
    response = client.get("/payments/")
    assert response.status_code == 200
    assert b"Payments" in response.data


def test_property_not_found(client):
    response = client.get("/properties/999")
    assert response.status_code == 404
