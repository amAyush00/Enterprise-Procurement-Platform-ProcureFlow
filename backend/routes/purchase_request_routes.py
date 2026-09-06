from flask import Blueprint
from backend.controllers.purchase_request_controller import PurchaseRequestController
from backend.middlewares.auth import role_required

pr_bp = Blueprint('purchase_requests', __name__)

# GET /api/purchase-requests - Fetch requests list (Admin, Officer, Manager, Employee)
pr_bp.route('', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager', 'Employee')(PurchaseRequestController.get_requests)
)

# GET /api/purchase-requests/:id - Fetch single request detail (Admin, Officer, Manager, Employee)
pr_bp.route('/<int:request_id>', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager', 'Employee')(PurchaseRequestController.get_request)
)

# POST /api/purchase-requests - Submit new request (Admin, Manager, Employee)
pr_bp.route('', methods=['POST'])(
    role_required('Admin', 'Manager', 'Employee')(PurchaseRequestController.create_request)
)

# POST /api/purchase-requests/:id/review - Review pending request (Admin, Manager)
pr_bp.route('/<int:request_id>/review', methods=['POST'])(
    role_required('Admin', 'Manager')(PurchaseRequestController.review_request)
)
