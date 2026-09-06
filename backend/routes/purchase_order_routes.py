from flask import Blueprint
from backend.controllers.purchase_order_controller import PurchaseOrderController
from backend.middlewares.auth import role_required

po_bp = Blueprint('purchase_orders', __name__)

# GET /api/purchase-orders - Fetch POs list (Admin, Officer, Manager)
po_bp.route('', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(PurchaseOrderController.get_orders)
)

# GET /api/purchase-orders/:id - Fetch single PO detail (Admin, Officer, Manager)
po_bp.route('/<int:po_id>', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(PurchaseOrderController.get_order)
)

# POST /api/purchase-orders - Create PO from approved PR (Admin, Officer)
po_bp.route('', methods=['POST'])(
    role_required('Admin', 'Procurement Officer')(PurchaseOrderController.create_po_from_request)
)

# PUT /api/purchase-orders/:id/status - Update PO status (Admin, Officer)
po_bp.route('/<int:po_id>/status', methods=['PUT'])(
    role_required('Admin', 'Procurement Officer')(PurchaseOrderController.update_po_status)
)
