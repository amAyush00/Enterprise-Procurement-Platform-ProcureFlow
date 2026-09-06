from sqlalchemy import or_
from backend.app import db
from backend.models.product import Product, Category
from backend.models.inventory import Inventory

class ProductService:
    @staticmethod
    def get_all_products(search=None, category_id=None, vendor_id=None, status=None, sort_by='name', sort_order='asc', page=1, per_page=10):
        """
        Retrieve products with filters, search, sorting, and pagination.
        """
        query = Product.query

        # Filters
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if vendor_id:
            query = query.filter(Product.vendor_id == vendor_id)
        if status:
            query = query.filter(Product.status == status)

        # Search
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.like(search_pattern),
                    Product.sku.like(search_pattern)
                )
            )

        # Sorting
        sort_attr = getattr(Product, sort_by, Product.name)
        if sort_order == 'desc':
            query = query.order_by(sort_attr.desc())
        else:
            query = query.order_by(sort_attr.asc())

        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'products': [product.to_dict() for product in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        }

    @staticmethod
    def get_product_by_id(product_id):
        """
        Fetch single product.
        """
        return Product.query.get(product_id)

    @staticmethod
    def create_product(data):
        """
        Create a new product catalog item and initialize an inventory record.
        """
        sku = data.get('sku')
        if Product.query.filter_by(sku=sku).first():
            raise ValueError(f"Product SKU '{sku}' already exists in catalog.")

        product = Product(
            name=data.get('name'),
            sku=sku,
            category_id=data.get('category_id'),
            unit_price=data.get('unit_price'),
            reorder_level=data.get('reorder_level', 10),
            vendor_id=data.get('vendor_id'),
            status=data.get('status', 'ACTIVE')
        )

        db.session.add(product)
        db.session.flush() # Secure product.id

        # Automate creation of inventory record
        inventory = Inventory(
            product_id=product.id,
            current_stock=0,
            incoming_stock=0,
            outgoing_stock=0
        )
        db.session.add(inventory)
        db.session.commit()

        return product

    @staticmethod
    def update_product(product_id, data):
        """
        Update catalog product fields.
        """
        product = Product.query.get(product_id)
        if not product:
            return None

        sku = data.get('sku')
        if sku and sku != product.sku:
            if Product.query.filter_by(sku=sku).first():
                raise ValueError(f"Product SKU '{sku}' already exists.")
            product.sku = sku

        product.name = data.get('name', product.name)
        product.category_id = data.get('category_id', product.category_id)
        product.unit_price = data.get('unit_price', product.unit_price)
        product.reorder_level = data.get('reorder_level', product.reorder_level)
        product.vendor_id = data.get('vendor_id', product.vendor_id)
        product.status = data.get('status', product.status)

        db.session.commit()
        return product

    @staticmethod
    def delete_product(product_id):
        """
        Delete a product and its associated inventory. Restricts if referenced.
        """
        product = Product.query.get(product_id)
        if not product:
            return False

        # Restrict if referenced in transactions, PRs, or POs
        if len(product.purchase_request_items) > 0 or len(product.purchase_order_items) > 0 or len(product.inventory_transactions) > 0:
            raise ValueError("Product is linked to active requests, orders, or transactions. Mark as DISCONTINUED instead.")

        db.session.delete(product)
        db.session.commit()
        return True

    @staticmethod
    def get_all_categories():
        """
        Retrieve all categories.
        """
        return Category.query.all()

    @staticmethod
    def create_category(data):
        """
        Create a new product category.
        """
        name = data.get('name')
        if Category.query.filter_by(name=name).first():
            raise ValueError(f"Category '{name}' already exists.")

        category = Category(
            name=name,
            description=data.get('description')
        )
        db.session.add(category)
        db.session.commit()
        return category
