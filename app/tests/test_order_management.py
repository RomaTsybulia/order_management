import pytest
from flask import Flask
from database import db
from models import Order
from routes import order_bp


@pytest.fixture(scope="module")
def test_client():
    flask_app = Flask(__name__)
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test_orders.db"
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with flask_app.app_context():
        db.init_app(flask_app)
        db.create_all()
        flask_app.register_blueprint(order_bp, url_prefix="/api/orders")

        for i in range(1, 11):
            db.session.add(
                Order(
                    name=f"Test Order {i}",
                    description=f"This is test order {i}",
                    status="New",
                )
            )
        db.session.commit()

        yield flask_app.test_client()

        db.drop_all()


def test_get_order(test_client):
    response = test_client.get("/api/orders/1")
    assert response.status_code == 200
    assert b"Test Order 1" in response.data


def test_add_order(test_client):
    response = test_client.post(
        "/api/orders/",
        json={
            "name": "Test Order 11",
            "description": "This is test order 11",
            "status": "New",
        },
    )
    assert response.status_code == 201
    assert b"Order added successfully" in response.data

    with db.session.begin():
        order = db.session.query(Order).filter_by(name="Test Order 11").first()
        assert order


def test_update_order(test_client):
    response = test_client.put(
        "/api/orders/1", json={"name": "Updated Test Order 1", "status": "In Progress"}
    )
    assert response.status_code == 200
    assert b"Order updated successfully" in response.data

    with db.session.begin():
        updated_order = db.session.query(Order).filter_by(id=1).first()
        assert updated_order.name == "Updated Test Order 1"
        assert updated_order.status == "In Progress"


def test_delete_order(test_client):
    response = test_client.delete("/api/orders/1")
    assert response.status_code == 200
    assert b"Order deleted successfully" in response.data

    with db.session.begin():
        order = db.session.query(Order).filter_by(id=1).first()
        assert not order


def test_generate_report(test_client):
    response = test_client.get("/api/orders/report")
    assert response.status_code == 200
    assert b"file_path" in response.data


def test_order_statistics(test_client):
    response = test_client.get("/api/orders/statistics")
    assert response.status_code == 200
    assert response.json == {"New": 10}


def test_export_import_hdf5(test_client):
    response = test_client.get("/api/orders/export/hdf5")
    assert response.status_code == 200
    file_path = response.json["file_path"]

    response = test_client.post(
        "/api/orders/import/hdf5", json={"file_path": file_path}
    )
    assert response.status_code == 200
    assert b"Data imported from HDF5 successfully" in response.data


def test_export_import_xml(test_client):
    response = test_client.get("/api/orders/export/xml")
    assert response.status_code == 200
    file_path = response.json["file_path"]

    response = test_client.post("/api/orders/import/xml", json={"file_path": file_path})
    assert response.status_code == 200
    assert b"Data imported from XML successfully" in response.data


def test_bulk_update(test_client):
    response = test_client.put(
        "/api/orders/bulk_update", json={"order_ids": [1, 2], "status": "Completed"}
    )
    assert response.status_code == 200
    print(response.data)
    assert b"Order ID 1 does not exist." in response.data

    with db.session.begin():
        orders = db.session.query(Order).filter(Order.id.in_([1, 2])).all()
        for order in orders:
            assert order.status == "Completed"
