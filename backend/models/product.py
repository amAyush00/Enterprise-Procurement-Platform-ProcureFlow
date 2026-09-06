from backend.app import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    products = db.relationship('Product', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(50), nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    reorder_level = db.Column(db.Integer, default=10, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id', ondelete='RESTRICT'), nullable=False)
    status = db.Column(db.Enum('ACTIVE', 'INACTIVE', 'DISCONTINUED'), default='ACTIVE')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    inventory = db.relationship('Inventory', backref='product', uselist=False, cascade='all, delete-orphan')
    purchase_request_items = db.relationship('PurchaseRequestItem', backref='product', lazy=True)
    purchase_order_items = db.relationship('PurchaseOrderItem', backref='product', lazy=True)
    inventory_transactions = db.relationship('InventoryTransaction', backref='product', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'unit_price': float(self.unit_price),
            'reorder_level': self.reorder_level,
            'vendor_id': self.vendor_id,
            'vendor_name': self.vendor.name if self.vendor else None,
            'status': self.status,
            'available_quantity': self.inventory.current_stock if self.inventory else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
