from flask import jsonify
from backend.services.analytics_service import AnalyticsService

class AnalyticsController:
    @staticmethod
    def get_summary():
        """
        Fetch general dashboard statistics and recent activities.
        """
        try:
            summary = AnalyticsService.get_dashboard_summary()
            return jsonify({
                "success": True,
                "message": "Dashboard KPI summary retrieved successfully.",
                "data": summary
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "message": f"Failed to load dashboard KPIs. {str(e)}"
            }), 500

    @staticmethod
    def get_charts():
        """
        Fetch aggregated chart trends data.
        """
        try:
            charts_data = AnalyticsService.get_charts_data()
            return jsonify({
                "success": True,
                "message": "Analytics charts data retrieved successfully.",
                "data": charts_data
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "message": f"Failed to load analytics trends. {str(e)}"
            }), 500
