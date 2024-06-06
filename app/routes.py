from flask import Blueprint, request, jsonify
from models import Order
from database import db
from report import generate_report
from analysis import order_statistics
from file_handlers import export_hdf5, import_hdf5, export_xml, import_xml

order_bp = Blueprint("order_bp", __name__)


@order_bp.route("/", methods=["POST"])
def add_order():
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 415
    data = request.get_json()

    try:
        new_order = Order(
            name=data["name"],
            description=data.get("description", ""),
            status=data["status"],
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({"message": "Order added successfully"}), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


@order_bp.route("/", methods=["GET"])
def get_orders():
    orders = Order.query.all()
    return jsonify([order.serialize() for order in orders])


@order_bp.route("/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.serialize())


@order_bp.route("/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    try:
        if "status" in data:
            Order.validate_status(data["status"])
        order.name = data.get("name", order.name)
        order.description = data.get("description", order.description)
        order.status = data.get("status", order.status)
        db.session.commit()
        return jsonify({"message": "Order updated successfully"}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400


@order_bp.route("/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order deleted successfully"}), 200


@order_bp.route("/report", methods=["GET"])
def get_report():
    file_path = generate_report()
    return jsonify({"file_path": file_path}), 200


@order_bp.route("/statistics", methods=["GET"])
def get_statistics():
    stats = order_statistics()
    return jsonify(stats), 200


@order_bp.route("/export/hdf5", methods=["GET"])
def export_orders_hdf5():
    file_path = export_hdf5()
    return jsonify({"file_path": file_path}), 200


@order_bp.route("/import/hdf5", methods=["POST"])
def import_orders_hdf5():
    file_path = request.json.get("file_path")
    if not file_path:
        return jsonify({"message": "file_path is required"}), 400
    try:
        import_hdf5(file_path)
        return jsonify({"message": "Data imported from HDF5 successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error importing data from HDF5: {e}"}), 400


@order_bp.route("/export/xml", methods=["GET"])
def export_orders_xml():
    file_path = export_xml()
    return jsonify({"file_path": file_path}), 200


@order_bp.route("/import/xml", methods=["POST"])
def import_orders_xml():
    file_path = request.json.get("file_path")
    if not file_path:
        return jsonify({"message": "file_path is required"}), 400
    try:
        import_xml(file_path)
        return jsonify({"message": "Data imported from XML successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error importing data from XML: {e}"}), 400


@order_bp.route("/bulk_update", methods=["PUT"])
def bulk_update_orders():
    data = request.get_json()
    order_ids = data.get("order_ids", [])
    new_status = data.get("status")
    messages = []

    try:
        Order.validate_status(new_status)
        for order_id in order_ids:
            try:
                order = Order.query.get(order_id)
                if order:
                    order.status = new_status
                    db.session.commit()
                else:
                    messages.append(f"Order ID {order_id} does not exist.")
            except Exception as e:
                messages.append(f"Error updating Order ID {order_id}: {str(e)}")
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    if not messages:
        return jsonify({"result": "Statuses were updated"}), 200

    return jsonify({"result": messages}), 200
