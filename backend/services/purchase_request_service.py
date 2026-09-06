from backend.app import db
from backend.models.purchase_request import PurchaseRequest, PurchaseRequestItem, Approval
from backend.models.product import Product

class PurchaseRequestService:
    @staticmethod
    def get_all_requests(user_id=None, role=None, status=None, page=1, per_page=10):
        """
        List purchase requests. Employees are limited to their own history.
        Admins, Officers, and Managers can query all requests.
        """
        query = PurchaseRequest.query

        # Enforce security boundary: Employees see only their own requests
        if role == 'Employee':
            query = query.filter(PurchaseRequest.employee_id == user_id)

        # Filter by request status (PENDING, APPROVED, REJECTED, CONVERTED)
        if status:
            query = query.filter(PurchaseRequest.status == status)

        # Order by newest request
        query = query.order_by(PurchaseRequest.created_at.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'requests': [req.to_dict() for req in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        }

    @staticmethod
    def get_request_by_id(request_id, user_id=None, role=None):
        """
        Fetch single purchase request. Restricts Employee access if it isn't theirs.
        """
        req = PurchaseRequest.query.get(request_id)
        if not req:
            return None

        # Verify ownership
        if role == 'Employee' and req.employee_id != user_id:
            return None

        return req

    @staticmethod
    def create_request(employee_id, data):
        """
        Create a purchase request with items. Look up unit prices, calculate totals,
        and write records inside a transaction.
        """
        items_data = data.get('items', [])
        if not items_data:
            raise ValueError("A purchase request must contain at least one item.")

        # Create parent purchase request row
        req = PurchaseRequest(
            employee_id=employee_id,
            status='PENDING',
            comments=data.get('comments'),
            total_amount=0.00
        )
        db.session.add(req)
        db.session.flush() # Retrieve req.id

        total_amount = 0.00
        for item in items_data:
            product_id = item.get('product_id')
            qty = item.get('quantity')

            if not product_id or qty is None or int(qty) <= 0:
                raise ValueError("Each item requires a valid product ID and a quantity greater than zero.")

            # Verify product is active
            product = Product.query.get(product_id)
            if not product or product.status != 'ACTIVE':
                raise ValueError(f"Product with ID {product_id} is either unavailable or discontinued.")

            # Calculate prices
            unit_price = product.unit_price
            item_total = unit_price * int(qty)
            total_amount += item_total

            # Create request item row
            req_item = PurchaseRequestItem(
                purchase_request_id=req.id,
                product_id=product_id,
                quantity=int(qty),
                unit_price=unit_price
            )
            db.session.add(req_item)

        # Update aggregated request amount
        req.total_amount = total_amount
        db.session.commit()

        return req

    @staticmethod
    def review_request(request_id, reviewer_id, status, comments):
        """
        Approve or Reject a pending request. Adds an audit approval log.
        """
        if status not in ['APPROVED', 'REJECTED']:
            raise ValueError("Review status must be either APPROVED or REJECTED.")

        req = PurchaseRequest.query.get(request_id)
        if not req:
            return None

        if req.status != 'PENDING':
            raise ValueError(f"Purchase request is already reviewed (current status: {req.status}).")

        # Update status
        req.status = status

        # Log approval audit record
        approval = Approval(
            purchase_request_id=req.id,
            reviewer_id=reviewer_id,
            status=status,
            review_comments=comments
        )
        db.session.add(approval)
        db.session.commit()

        return req
