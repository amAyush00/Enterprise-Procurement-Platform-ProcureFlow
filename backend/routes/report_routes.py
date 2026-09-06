from flask import Blueprint
from backend.controllers.report_controller import ReportController
from backend.middlewares.auth import role_required

report_bp = Blueprint('reports', __name__)

# GET /api/reports/vendors/excel (Admin, Officer, Manager)
report_bp.route('/vendors/excel', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(ReportController.download_vendors_excel)
)

# GET /api/reports/inventory/excel (Admin, Officer, Manager)
report_bp.route('/inventory/excel', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(ReportController.download_inventory_excel)
)

# GET /api/reports/purchase-orders/excel (Admin, Officer, Manager)
report_bp.route('/purchase-orders/excel', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(ReportController.download_purchase_orders_excel)
)

# GET /api/reports/procurement/pdf (Admin, Officer, Manager)
report_bp.route('/procurement/pdf', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(ReportController.download_procurement_pdf)
)

# GET /api/reports/purchase-orders/:id/pdf - Invoice style download for a single PO (Admin, Officer, Manager)
report_bp.route('/purchase-orders/<int:po_id>/pdf', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(ReportController.download_purchase_order_pdf)
)
