import pandas as pd

from models import Order


def order_statistics():
    orders = Order.query.all()
    df = pd.DataFrame([order.serialize() for order in orders])
    status_counts = df["status"].value_counts().to_dict()
    return status_counts
