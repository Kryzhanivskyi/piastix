from app import db


class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(3), unique=True, nullable=False)

    def __repr__(self):
        return self.name


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    currency = db.relationship('Currency', backref=db.backref('posts'))
    amount = db.Column(db.Float)
    payment_sending_time = db.Column(db.DateTime)
    description = db.Column(db.Text)
    uid_code = db.Column(db.SmallInteger, unique=True)
