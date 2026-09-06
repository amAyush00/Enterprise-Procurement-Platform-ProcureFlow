from flask import request, jsonify
from backend.services.inventory_service import InventoryService

class InventoryController:
    @staticmethod
    def get_inventory():
        """
        List inventory levels (supports pagination, search, low stock alert filter).
        """
        search = request.args.get('search', None)
        low_stock_raw = request.args.get('low_stock', 'false')
        low_stock = low_stock_raw.lower() == 'true'
        sort_by = request.args.get('sort_by', 'product_name')
        sort_order = request.args.get('sort_order', 'asc')

        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Page and limit parameters must be integers."
            }), 400

        result = InventoryService.get_all_inventory(
            search=search,
            low_stock=low_stock,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=limit
        )

        return jsonify({
            "success": True,
            "message": "Inventory records retrieved successfully.",
            "data": result
        }), 200

    @staticmethod
    def adjust_stock():
        """
        Adjust stock levels of a product manually.
        """
        data = request.get_json() or {}
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        notes = data.get('notes')

        if not product_id or quantity is None or not notes:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Product ID, quantity, and notes are required fields."
            }), 400

        try:
            quantity = int(quantity)
            product_id = int(product_id)
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Product ID and quantity must be valid numeric values."
            }), 400

        if quantity == 0:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Adjustment quantity cannot be zero."
            }), 400

        try:
            inventory = InventoryService.adjust_stock(
                product_id=product_id,
                quantity=quantity,
                notes=notes,
                transaction_type='ADJUSTMENT'
            )
            return jsonify({
                "success": True,
                "message": "Stock adjusted successfully.",
                "data": inventory.to_dict()
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
                "message": "Failed to adjust stock."
            }), 500

    @staticmethod
    def get_transactions():
        """
        Fetch historical inventory ledger transactions.
        """
        try:
            product_id = request.args.get('product_id')
            product_id = int(product_id) if product_id else None
            
            transaction_type = request.args.get('transaction_type')
            
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Numeric query parameters must be integers."
            }), 400

        result = InventoryService.get_transaction_history(
            product_id=product_id,
            transaction_type=transaction_type,
            page=page,
            per_page=limit
        )

        return jsonify({
            "success": True,
            "message": "Inventory ledger logs retrieved successfully.",
            "data": result
        }), 200
