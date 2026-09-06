from flask import request, jsonify
from backend.services.purchase_order_service import PurchaseOrderService

class PurchaseOrderController:
    @staticmethod
    def get_orders():
        """
        List purchase orders (supports search, vendor filters, pagination).
        """
        search = request.args.get('search', None)
        status = request.args.get('status', None)
        
        try:
            vendor_id = request.args.get('vendor_id')
            vendor_id = int(vendor_id) if vendor_id else None
            
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Numeric query parameters must be integers."
            }), 400

        result = PurchaseOrderService.get_all_orders(
            search=search,
            status=status,
            vendor_id=vendor_id,
            page=page,
            per_page=limit
        )

        return jsonify({
            "success": True,
            "message": "Purchase orders retrieved successfully.",
            "data": result
        }), 200

    @staticmethod
    def get_order(po_id):
        """
        Retrieve single purchase order details.
        """
        po = PurchaseOrderService.get_order_by_id(po_id)
        if not po:
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Purchase order with ID {po_id} does not exist."
            }), 404

        return jsonify({
            "success": True,
            "message": "Purchase order retrieved successfully.",
            "data": po.to_dict()
        }), 200

    @staticmethod
    def create_po_from_request():
        """
        Generate vendor purchase orders from an approved purchase request.
        """
        data = request.get_json() or {}
        pr_id = data.get('purchase_request_id')
        expected_delivery_date = data.get('expected_delivery_date')

        if not pr_id or not expected_delivery_date:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Purchase request ID and expected delivery date are required."
            }), 400

        try:
            pr_id = int(pr_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Purchase request ID must be a valid integer."
            }), 400

        try:
            pos = PurchaseOrderService.create_po_from_request(pr_id, expected_delivery_date)
            return jsonify({
                "success": True,
                "message": f"Successfully generated {len(pos)} purchase order(s) from request.",
                "data": pos
            }), 201
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": str(e)
            }), 400
        except Exception:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "message": "Failed to create purchase order from request."
            }), 500

    @staticmethod
    def update_po_status(po_id):
        """
        Update the status of a purchase order (triggers stock adjustments).
        """
        data = request.get_json() or {}
        status = data.get('status')

        if not status:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Status field is required."
            }), 400

        try:
            po = PurchaseOrderService.update_po_status(po_id, status)
            if not po:
                return jsonify({
                    "success": False,
                    "error": "Not Found",
                    "message": f"Purchase order with ID {po_id} does not exist."
                }), 404

            return jsonify({
                "success": True,
                "message": f"Purchase order status updated to '{status}' successfully.",
                "data": po.to_dict()
            }), 200
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": str(e)
            }), 400
        except Exception:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "message": "Failed to update purchase order status."
            }), 500
