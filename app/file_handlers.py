import xmltodict
import pandas as pd
import xmltodict

from database import db
from models import Order


def export_hdf5():
    orders = Order.query.all()
    df = pd.DataFrame([order.serialize() for order in orders])
    file_path = "orders.h5"
    df.to_hdf(file_path, key="orders", mode="w")
    return file_path


def import_hdf5(file_path):
    try:
        df = pd.read_hdf(file_path, key="orders")
        for _, row in df.iterrows():
            order = Order.query.get(row["id"])
            if not order:
                new_order = Order(
                    name=row["name"],
                    description=row["description"],
                    status=row["status"],
                )
                db.session.add(new_order)
            else:
                order.name = row["name"]
                order.description = row["description"]
                order.status = row["status"]
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error importing HDF5 file: {e}")
        raise


def export_xml():
    orders = Order.query.all()
    orders_dict = [order.serialize() for order in orders]
    file_path = "orders.xml"
    with open(file_path, "w") as file:
        file.write(xmltodict.unparse({"orders": {"order": orders_dict}}, pretty=True))
    return file_path


def import_xml(file_path):
    try:
        with open(file_path, "r") as file:
            orders_dict = xmltodict.parse(file.read())["orders"]["order"]
            if isinstance(orders_dict, dict):  # Single order case
                orders_dict = [orders_dict]
            for order_data in orders_dict:
                order = Order.query.get(order_data["id"])
                if not order:
                    new_order = Order(
                        name=order_data["name"],
                        description=order_data["description"],
                        status=order_data["status"],
                    )
                    db.session.add(new_order)
                else:
                    order.name = order_data["name"]
                    order.description = order_data["description"]
                    order.status = order_data["status"]
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error importing XML file: {e}")
        raise
