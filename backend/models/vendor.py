from backend.app import db

class Vendor(db.Model):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    gst_number = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Numeric(3, 2), default=5.00)
    status = db.Column(db.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED'), default='ACTIVE')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    products = db.relationship('Product', backref='vendor', lazy=True)
    purchase_orders = db.relationship('PurchaseOrder', backref='vendor', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company_name': self.company_name,
            'gst_number': self.gst_number,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'rating': float(self.rating) if self.rating else 0.0,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
