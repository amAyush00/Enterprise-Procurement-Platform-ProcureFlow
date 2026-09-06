from flask import request, jsonify
from backend.services.product_service import ProductService

class ProductController:
    @staticmethod
    def get_products():
        """
        List all products in catalog (supports sorting, filter, search, paging).
        """
        search = request.args.get('search', None)
        status = request.args.get('status', None)
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')

        try:
            category_id = request.args.get('category_id')
            category_id = int(category_id) if category_id else None
            
            vendor_id = request.args.get('vendor_id')
            vendor_id = int(vendor_id) if vendor_id else None
            
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Numeric query parameters must be valid integers."
            }), 400

        result = ProductService.get_all_products(
            search=search,
            category_id=category_id,
            vendor_id=vendor_id,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=limit
        )

        return jsonify({
            "success": True,
            "message": "Products retrieved successfully.",
            "data": result
        }), 200

    @staticmethod
    def get_product(product_id):
        """
        Retrieve single product.
        """
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Product with ID {product_id} does not exist."
            }), 404

        return jsonify({
            "success": True,
            "message": "Product retrieved successfully.",
            "data": product.to_dict()
        }), 200

    @staticmethod
    def create_product():
        """
        Create new product catalog item.
        """
        data = request.get_json() or {}

        # Validate mandatory properties
        required = ['name', 'sku', 'category_id', 'unit_price', 'vendor_id']
        missing = [f for f in required if data.get(f) is None]
        if missing:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": f"Missing required fields: {', '.join(missing)}"
            }), 400

        try:
            product = ProductService.create_product(data)
            return jsonify({
                "success": True,
                "message": "Product created successfully.",
                "data": product.to_dict()
            }), 201
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": "Conflict",
                "message": str(e)
            }), 409
        except Exception:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "message": "Failed to create catalog product."
            }), 500

    @staticmethod
    def update_product(product_id):
        """
        Update catalog product item.
        """
        data = request.get_json() or {}

        try:
            product = ProductService.update_product(product_id, data)
            if not product:
                return jsonify({
                    "success": False,
                    "error": "Not Found",
                    "message": f"Product with ID {product_id} does not exist."
                }), 404

            return jsonify({
                "success": True,
                "message": "Product updated successfully.",
                "data": product.to_dict()
            }), 200
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": "Conflict",
                "message": str(e)
            }), 409
        except Exception:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "message": "Failed to update product."
            }), 500

    @staticmethod
    def delete_product(product_id):
        """
        Remove product from catalog.
        """
        try:
            success = ProductService.delete_product(product_id)
            if not success:
                return jsonify({
                    "success": False,
                    "error": "Not Found",
                    "message": f"Product with ID {product_id} does not exist."
                }), 404

            return jsonify({
                "success": True,
                "message": "Product deleted successfully from catalog."
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
                "message": "Failed to delete product."
            }), 500

    @staticmethod
    def get_categories():
        """
        Get all product categories.
        """
        categories = ProductService.get_all_categories()
        return jsonify({
            "success": True,
            "message": "Categories retrieved successfully.",
            "data": [category.to_dict() for category in categories]
        }), 200

    @staticmethod
    def create_category():
        """
        Add a new product category.
        """
        data = request.get_json() or {}
        name = data.get('name')
        if not name:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Category name is required."
            }), 400

        try:
            category = ProductService.create_category(data)
            return jsonify({
                "success": True,
                "message": "Category created successfully.",
                "data": category.to_dict()
            }), 201
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": "Conflict",
                "message": str(e)
            }), 409
        except Exception:
            return jsonify({
                "success": False,
                "error": "Internal Server Error",
                "message": "Failed to create category."
            }), 500
