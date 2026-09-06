import io
import datetime
from flask import send_file, jsonify, request
from backend.services.report_service import ReportService

class ReportController:
    @staticmethod
    def download_vendors_excel():
        """
        Download Vendor list as formatted Excel.
        """
        try:
            status = request.args.get('status', None)
            excel_data = ReportService.generate_vendors_excel(status=status)
            
            return send_file(
                io.BytesIO(excel_data),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f"Vendor_Report_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
            )
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "message": f"Failed to generate Excel report. {str(e)}"
            }), 500

    @staticmethod
    def download_inventory_excel():
        """
        Download inventory levels as formatted Excel.
        """
        try:
            low_stock_raw = request.args.get('low_stock', 'false')
            low_stock = low_stock_raw.lower() == 'true'
            excel_data = ReportService.generate_inventory_excel(low_stock=low_stock)
            
            return send_file(
                io.BytesIO(excel_data),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f"Inventory_Report_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
            )
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "message": f"Failed to generate Excel report. {str(e)}"
            }), 500

    @staticmethod
    def download_purchase_orders_excel():
        """
        Download PO records as formatted Excel.
        """
        try:
            status = request.args.get('status', None)
            excel_data = ReportService.generate_purchase_orders_excel(status=status)
            
            return send_file(
                io.BytesIO(excel_data),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f"Purchase_Orders_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
            )
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "message": f"Failed to generate Excel report. {str(e)}"
            }), 500

    @staticmethod
    def download_procurement_pdf():
        """
        Download consolidated procurement status PDF report.
        """
        try:
            pdf_data = ReportService.generate_procurement_report_pdf()
            
            return send_file(
                io.BytesIO(pdf_data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"Procurement_Report_{datetime.date.today().strftime('%Y%m%d')}.pdf"
            )
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "message": f"Failed to generate PDF report. {str(e)}"
            }), 500

    @staticmethod
    def download_purchase_order_pdf(po_id):
        """
        Download single PO PDF (invoice style).
        """
        try:
            pdf_data = ReportService.generate_purchase_order_pdf(po_id)
            
            return send_file(
                io.BytesIO(pdf_data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"Purchase_Order_PO_{po_id}.pdf"
            )
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": str(e)
            }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "message": f"Failed to generate PO PDF document. {str(e)}"
            }), 500
