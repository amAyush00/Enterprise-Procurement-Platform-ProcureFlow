from backend.app import db

class PurchaseRequest(db.Model):
    __tablename__ = 'purchase_requests'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    status = db.Column(db.Enum('PENDING', 'APPROVED', 'REJECTED', 'CONVERTED'), default='PENDING')
    total_amount = db.Column(db.Numeric(15, 2), default=0.00, nullable=False)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    items = db.relationship('PurchaseRequestItem', backref='purchase_request', cascade='all, delete-orphan', lazy=True)
    approvals = db.relationship('Approval', backref='purchase_request', cascade='all, delete-orphan', lazy=True)
    purchase_orders = db.relationship('PurchaseOrder', backref='purchase_request', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': f"{self.employee.first_name} {self.employee.last_name}" if self.employee else None,
            'status': self.status,
            'total_amount': float(self.total_amount),
            'comments': self.comments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }


class PurchaseRequestItem(db.Model):
    __tablename__ = 'purchase_request_items'

    id = db.Column(db.Integer, primary_key=True)
    purchase_request_id = db.Column(db.Integer, db.ForeignKey('purchase_requests.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'purchase_request_id': self.purchase_request_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'product_sku': self.product.sku if self.product else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.unit_price * self.quantity)
        }


class Approval(db.Model):
    __tablename__ = 'approvals'

    id = db.Column(db.Integer, primary_key=True)
    purchase_request_id = db.Column(db.Integer, db.ForeignKey('purchase_requests.id', ondelete='CASCADE'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    status = db.Column(db.Enum('APPROVED', 'REJECTED'), nullable=False)
    review_comments = db.Column(db.Text)
    reviewed_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'purchase_request_id': self.purchase_request_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': f"{self.reviewer.first_name} {self.reviewer.last_name}" if self.reviewer else None,
            'status': self.status,
            'review_comments': self.review_comments,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }
