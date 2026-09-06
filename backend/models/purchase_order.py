from backend.app import db

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True)
    purchase_request_id = db.Column(db.Integer, db.ForeignKey('purchase_requests.id', ondelete='SET NULL'), nullable=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id', ondelete='RESTRICT'), nullable=False)
    po_number = db.Column(db.String(50), nullable=False, unique=True)
    status = db.Column(db.Enum('PENDING', 'APPROVED', 'ORDERED', 'DELIVERED', 'CANCELLED'), default='PENDING')
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    expected_delivery_date = db.Column(db.Date, nullable=False)
    actual_delivery_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    items = db.relationship('PurchaseOrderItem', backref='purchase_order', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'purchase_request_id': self.purchase_request_id,
            'vendor_id': self.vendor_id,
            'vendor_name': self.vendor.name if self.vendor else None,
            'po_number': self.po_number,
            'status': self.status,
            'total_amount': float(self.total_amount),
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'actual_delivery_date': self.actual_delivery_date.isoformat() if self.actual_delivery_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }


class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'

    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'purchase_order_id': self.purchase_order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'product_sku': self.product.sku if self.product else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.unit_price * self.quantity)
        }
