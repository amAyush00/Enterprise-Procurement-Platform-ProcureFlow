import datetime
from backend.app import db
from backend.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from backend.models.purchase_request import PurchaseRequest
from backend.models.inventory import Inventory
from backend.services.inventory_service import InventoryService

class PurchaseOrderService:
    @staticmethod
    def get_all_orders(search=None, status=None, vendor_id=None, page=1, per_page=10):
        """
        List purchase orders using search, filter, and pagination.
        """
        query = PurchaseOrder.query

        if status:
            query = query.filter(PurchaseOrder.status == status)
        if vendor_id:
            query = query.filter(PurchaseOrder.vendor_id == vendor_id)
        if search:
            query = query.filter(PurchaseOrder.po_number.like(f"%{search}%"))

        # Order by newest orders first
        query = query.order_by(PurchaseOrder.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'purchase_orders': [po.to_dict() for po in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        }

    @staticmethod
    def get_order_by_id(po_id):
        """
        Retrieve details of a single PO.
        """
        return PurchaseOrder.query.get(po_id)

    @staticmethod
    def generate_po_number():
        """
        Generate a unique corporate purchase order number.
        Format: PO-YYYYMMDD-XXXX
        """
        today_str = datetime.date.today().strftime('%Y%m%d')
        # Count POs created today to calculate the sequence suffix
        count = PurchaseOrder.query.filter(
            PurchaseOrder.po_number.like(f"PO-{today_str}-%")
        ).count()
        return f"PO-{today_str}-{count + 1:04d}"

    @staticmethod
    def create_po_from_request(pr_id, expected_delivery_date):
        """
        Generate vendor-specific Purchase Orders from an Approved Purchase Request.
        Groups items by supplier and creates a distinct PO for each vendor.
        """
        pr = PurchaseRequest.query.get(pr_id)
        if not pr:
            raise ValueError(f"Purchase Request with ID {pr_id} does not exist.")

        if pr.status != 'APPROVED':
            raise ValueError(f"Only APPROVED purchase requests can be converted. Current request status is {pr.status}.")

        # Group items by Vendor ID
        vendor_items = {}
        for item in pr.items:
            vendor_id = item.product.vendor_id
            if vendor_id not in vendor_items:
                vendor_items[vendor_id] = []
            vendor_items[vendor_id].append(item)

        created_pos = []

        try:
            # Parse delivery date
            delivery_date = datetime.datetime.strptime(expected_delivery_date, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Expected delivery date must be in YYYY-MM-DD format.")

        # Create a PO for each vendor
        for vendor_id, items in vendor_items.items():
            po_number = PurchaseOrderService.generate_po_number()
            total_amount = sum(item.unit_price * item.quantity for item in items)

            po = PurchaseOrder(
                purchase_request_id=pr_id,
                vendor_id=vendor_id,
                po_number=po_number,
                status='PENDING',
                total_amount=total_amount,
                expected_delivery_date=delivery_date
            )
            db.session.add(po)
            db.session.flush() # Secure po.id

            # Add PO items
            for item in items:
                po_item = PurchaseOrderItem(
                    purchase_order_id=po.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
                db.session.add(po_item)

            created_pos.append(po)

        # Mark request as converted
        pr.status = 'CONVERTED'
        db.session.commit()

        return [po.to_dict() for po in created_pos]

    @staticmethod
    def update_po_status(po_id, new_status):
        """
        Apply status changes and update stocks.
        """
        valid_statuses = ['PENDING', 'APPROVED', 'ORDERED', 'DELIVERED', 'CANCELLED']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status '{new_status}'.")

        po = PurchaseOrder.query.get(po_id)
        if not po:
            return None

        old_status = po.status
        if old_status == new_status:
            return po

        # Restrict invalid state transitions
        if old_status == 'DELIVERED':
            raise ValueError("Delivered purchase orders cannot be modified or cancelled.")
        if old_status == 'CANCELLED':
            raise ValueError("Cancelled purchase orders cannot be reopened.")

        # 1. Move to ORDERED (Deducted from budget / Sent to supplier): Update incoming inventory stock levels
        if new_status == 'ORDERED':
            for item in po.items:
                inv = Inventory.query.filter_by(product_id=item.product_id).first()
                if inv:
                    inv.incoming_stock += item.quantity

        # 2. Move to DELIVERED (Received in warehouse): Deduct incoming, Add to current stock, write ledger log
        elif new_status == 'DELIVERED':
            for item in po.items:
                InventoryService.adjust_stock(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    notes=f"Stock received from Purchase Order {po.po_number}",
                    reference_id=po.id,
                    transaction_type='IN'
                )
            po.actual_delivery_date = datetime.date.today()

        # 3. Move to CANCELLED: Deduct incoming stock counts if previously ordered
        elif new_status == 'CANCELLED':
            if old_status == 'ORDERED':
                for item in po.items:
                    inv = Inventory.query.filter_by(product_id=item.product_id).first()
                    if inv:
                        inv.incoming_stock = max(0, inv.incoming_stock - item.quantity)

        po.status = new_status
        db.session.commit()
        return po
