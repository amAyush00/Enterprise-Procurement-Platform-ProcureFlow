from flask import Blueprint
from backend.controllers.product_controller import ProductController
from backend.middlewares.auth import role_required

product_bp = Blueprint('products', __name__)

# Category Routes (Must be declared before general ID routes to avoid matching "categories" as a product_id)
product_bp.route('/categories', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager', 'Employee')(ProductController.get_categories)
)

product_bp.route('/categories', methods=['POST'])(
    role_required('Admin', 'Procurement Officer')(ProductController.create_category)
)

# Product Routes
product_bp.route('', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager', 'Employee')(ProductController.get_products)
)

product_bp.route('/<int:product_id>', methods=['GET'])(
    role_required('Admin', 'Procurement Officer', 'Manager', 'Employee')(ProductController.get_product)
)

product_bp.route('', methods=['POST'])(
    role_required('Admin', 'Procurement Officer')(ProductController.create_product)
)

product_bp.route('/<int:product_id>', methods=['PUT'])(
    role_required('Admin', 'Procurement Officer')(ProductController.update_product)
)

product_bp.route('/<int:product_id>', methods=['DELETE'])(
    role_required('Admin', 'Procurement Officer')(ProductController.delete_product)
)
