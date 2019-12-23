from app import db


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.Text)
    amount = db.Column(db.Float)
    payment_sending_time = db.Column(db.DateTime)
    description = db.Column(db.Text)
    uid_code = db.Column(db.Text, unique=True)

    def __repr__(self):
        return str(self.id)
