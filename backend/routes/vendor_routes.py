from flask import Blueprint
from backend.controllers.vendor_controller import VendorController
from backend.middlewares.auth import role_required

vendor_bp = Blueprint('vendors', __name__)

# GET /api/vendors - List vendors (Accessible by Admin, Officer, Manager)
vendor_bp.route('', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(VendorController.get_vendors)
)

# GET /api/vendors/:id - Fetch single vendor (Accessible by Admin, Officer, Manager)
vendor_bp.route('/<int:vendor_id>', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(VendorController.get_vendor)
)

# POST /api/vendors - Create vendor (Accessible by Admin and Procurement Officer)
vendor_bp.route('', methods=['POST'])(
    role_required('Admin', 'Procurement Officer')(VendorController.create_vendor)
)

# PUT /api/vendors/:id - Update vendor (Accessible by Admin and Procurement Officer)
vendor_bp.route('/<int:vendor_id>', methods=['PUT'])(
    role_required('Admin', 'Procurement Officer')(VendorController.update_vendor)
)

# DELETE /api/vendors/:id - Delete vendor (Accessible by Admin and Procurement Officer)
vendor_bp.route('/<int:vendor_id>', methods=['DELETE'])(
    role_required('Admin', 'Procurement Officer')(VendorController.delete_vendor)
)
