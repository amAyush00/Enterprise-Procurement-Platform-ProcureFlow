from backend.app import db

class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, unique=True)
    current_stock = db.Column(db.Integer, default=0, nullable=False)
    incoming_stock = db.Column(db.Integer, default=0, nullable=False)
    outgoing_stock = db.Column(db.Integer, default=0, nullable=False)
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'product_sku': self.product.sku if self.product else None,
            'product_category': self.product.category.name if self.product and self.product.category else None,
            'current_stock': self.current_stock,
            'incoming_stock': self.incoming_stock,
            'outgoing_stock': self.outgoing_stock,
            'reorder_level': self.product.reorder_level if self.product else 0,
            'unit_price': float(self.product.unit_price) if self.product else 0.0,
            'inventory_value': float(self.product.unit_price * self.current_stock) if self.product else 0.0,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class InventoryTransaction(db.Model):
    __tablename__ = 'inventory_transactions'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    transaction_type = db.Column(db.Enum('IN', 'OUT', 'ADJUSTMENT'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reference_id = db.Column(db.Integer)  # PO ID, PR ID, etc.
    transaction_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    notes = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'product_sku': self.product.sku if self.product else None,
            'transaction_type': self.transaction_type,
            'quantity': self.quantity,
            'reference_id': self.reference_id,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'notes': self.notes
        }
