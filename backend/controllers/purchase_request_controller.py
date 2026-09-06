from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.purchase_request_service import PurchaseRequestService
import json

def _get_identity_dict():
    identity = get_jwt_identity()
    if isinstance(identity, str):
        try:
            return json.loads(identity)
        except Exception:
            pass
    return identity or {}

class PurchaseRequestController:
    @staticmethod
    @jwt_required()
    def get_requests():
        """
        List purchase requests. Automatically extracts user ID and role from JWT 
        to enforce data access isolation (employees see only their own).
        """
        identity = _get_identity_dict()
        user_id = identity.get('id')
        role = identity.get('role')
        status = request.args.get('status', None)

        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Page and limit parameters must be integers."
            }), 400

        result = PurchaseRequestService.get_all_requests(
            user_id=user_id,
            role=role,
            status=status,
            page=page,
            per_page=limit
        )

        return jsonify({
            "success": True,
            "message": "Purchase requests retrieved successfully.",
            "data": result
        }), 200

    @staticmethod
    @jwt_required()
    def get_request(request_id):
        """
        Fetch single purchase request detail.
        """
        identity = _get_identity_dict()
        user_id = identity.get('id')
        role = identity.get('role')

        req = PurchaseRequestService.get_request_by_id(request_id, user_id, role)
        if not req:
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Purchase request with ID {request_id} does not exist or you lack permission to view it."
            }), 404

        return jsonify({
            "success": True,
            "message": "Purchase request retrieved successfully.",
            "data": req.to_dict()
        }), 200

    @staticmethod
    @jwt_required()
    def create_request():
        """
        Create a new purchase request.
        """
        identity = _get_identity_dict()
        employee_id = identity.get('id')
        data = request.get_json() or {}

        try:
            req = PurchaseRequestService.create_request(employee_id, data)
            return jsonify({
                "success": True,
                "message": "Purchase request submitted successfully.",
                "data": req.to_dict()
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
                "message": "Failed to create purchase request."
            }), 500

    @staticmethod
    @jwt_required()
    def review_request(request_id):
        """
        Approve or Reject a pending request (Manager/Admin action).
        """
        identity = _get_identity_dict()
        reviewer_id = identity.get('id')
        data = request.get_json() or {}
        
        status = data.get('status')
        comments = data.get('comments', '')

        if not status:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Review status (APPROVED or REJECTED) is required."
            }), 400

        try:
            req = PurchaseRequestService.review_request(
                request_id=request_id,
                reviewer_id=reviewer_id,
                status=status,
                comments=comments
            )
            if not req:
                return jsonify({
                    "success": False,
                    "error": "Not Found",
                    "message": f"Purchase request with ID {request_id} does not exist."
                }), 404

            return jsonify({
                "success": True,
                "message": f"Purchase request has been {status.lower()} successfully.",
                "data": req.to_dict()
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
                "message": "Failed to review purchase request."
            }), 500
