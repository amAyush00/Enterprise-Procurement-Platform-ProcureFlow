from flask import Blueprint
from backend.controllers.analytics_controller import AnalyticsController
from backend.middlewares.auth import role_required

analytics_bp = Blueprint('analytics', __name__)

# GET /api/analytics/summary - High-level KPIs and recent activity (Admin, Officer, Manager)
analytics_bp.route('/summary', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(AnalyticsController.get_summary)
)

# GET /api/analytics/charts - Aggregated spend, vendor performance, category inventory charts (Admin, Officer, Manager)
analytics_bp.route('/charts', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager')(AnalyticsController.get_charts)
)
