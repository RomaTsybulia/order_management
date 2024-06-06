from datetime import datetime
from database import db


class Order(db.Model):
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    creation_date = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.String(20), nullable=False)

    VALID_STATUSES = ["New", "In Progress", "Completed"]

    @staticmethod
    def validate_status(status):
        if status not in Order.VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of {Order.VALID_STATUSES}."
            )

    def __init__(self, name, description, status):
        self.name = name
        self.description = description
        self.creation_date = datetime.now()
        self.validate_status(status)
        self.status = status

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "creation_date": self.creation_date.isoformat(),
            "status": self.status,
        }
