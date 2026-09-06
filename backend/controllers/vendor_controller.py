from flask import request, jsonify
from backend.services.vendor_service import VendorService

class VendorController:
    @staticmethod
    def get_vendors():
        """
        Fetch filtered, searched, sorted, and paginated vendors.
        """
        search = request.args.get('search', None)
        status = request.args.get('status', None)
        sort_by = request.args.get('sort_by', 'name')
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

        result = VendorService.get_all_vendors(
            search=search,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=limit
        )

        return jsonify({
            "success": True,
            "message": "Vendors retrieved successfully.",
            "data": result
        }), 200

    @staticmethod
    def get_vendor(vendor_id):
        """
        Retrieve a single vendor by ID.
        """
        vendor = VendorService.get_vendor_by_id(vendor_id)
        if not vendor:
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Vendor with ID {vendor_id} does not exist."
            }), 404

        return jsonify({
            "success": True,
            "message": "Vendor details retrieved successfully.",
            "data": vendor.to_dict()
        }), 200

    @staticmethod
    def create_vendor():
        """
        Create a new vendor supplier.
        """
        data = request.get_json() or {}
        
        # Simple required check
        required_fields = ['name', 'company_name', 'gst_number', 'email', 'phone', 'address']
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": f"Missing required fields: {', '.join(missing)}"
            }), 400

        try:
            vendor = VendorService.create_vendor(data)
            return jsonify({
                "success": True,
                "message": "Vendor created successfully.",
                "data": vendor.to_dict()
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
                "message": "Failed to create vendor."
            }), 500

    @staticmethod
    def update_vendor(vendor_id):
        """
        Update fields of an existing vendor supplier.
        """
        data = request.get_json() or {}
        
        try:
            vendor = VendorService.update_vendor(vendor_id, data)
            if not vendor:
                return jsonify({
                    "success": False,
                    "error": "Not Found",
                    "message": f"Vendor with ID {vendor_id} does not exist."
                }), 404
                
            return jsonify({
                "success": True,
                "message": "Vendor updated successfully.",
                "data": vendor.to_dict()
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
                "message": "Failed to update vendor."
            }), 500

    @staticmethod
    def delete_vendor(vendor_id):
        """
        Delete a vendor from database if not referenced by active products.
        """
        try:
            success = VendorService.delete_vendor(vendor_id)
            if not success:
                return jsonify({
                    "success": False,
                    "error": "Not Found",
                    "message": f"Vendor with ID {vendor_id} does not exist."
                }), 404

            return jsonify({
                "success": True,
                "message": "Vendor deleted successfully."
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
                "message": "Failed to delete vendor due to foreign constraints."
            }), 500
