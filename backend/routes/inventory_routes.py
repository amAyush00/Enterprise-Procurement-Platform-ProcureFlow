from flask import Blueprint
from backend.controllers.inventory_controller import InventoryController
from backend.middlewares.auth import role_required

inventory_bp = Blueprint('inventory', __name__)

# GET /api/inventory - Retrieve inventory stock levels (Admin, Officer, Manager)
inventory_bp.route('', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(InventoryController.get_inventory)
)

# GET /api/inventory/transactions - Retrieve ledger history logs (Admin, Officer, Manager)
inventory_bp.route('/transactions', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(InventoryController.get_transactions)
)

# POST /api/inventory/adjust - Adjust stock level manually (Admin, Officer)
inventory_bp.route('/adjust', methods=['POST'])(
    role_required('Admin', 'Procurement Officer')(InventoryController.adjust_stock)
)
