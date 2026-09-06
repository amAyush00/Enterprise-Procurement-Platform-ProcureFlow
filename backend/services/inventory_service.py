from sqlalchemy import or_
from backend.app import db
from backend.models.inventory import Inventory, InventoryTransaction
from backend.models.product import Product

class InventoryService:
    @staticmethod
    def get_all_inventory(search=None, low_stock=False, sort_by='product_name', sort_order='asc', page=1, per_page=10):
        """
        List inventory items with search, filters (like low stock alert), sorting, and pagination.
        """
        # Join with Product table to query reorder level and name/sku
        query = Inventory.query.join(Product)

        # Filter by Low Stock alert (current_stock <= reorder_level)
        if low_stock:
            query = query.filter(Inventory.current_stock <= Product.reorder_level)

        # Search matching name or SKU
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.like(search_pattern),
                    Product.sku.like(search_pattern)
                )
            )

        # Sort logic
        if sort_by == 'product_name':
            sort_attr = Product.name
        elif sort_by == 'current_stock':
            sort_attr = Inventory.current_stock
        elif sort_by == 'inventory_value':
            sort_attr = Product.unit_price * Inventory.current_stock
        else:
            sort_attr = Inventory.last_updated

        if sort_order == 'desc':
            query = query.order_by(sort_attr.desc())
        else:
            query = query.order_by(sort_attr.asc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'inventory': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        }

    @staticmethod
    def adjust_stock(product_id, quantity, notes, reference_id=None, transaction_type='ADJUSTMENT'):
        """
        Adjust stock levels manually or programmatically.
        Inserts an InventoryTransaction log and updates the Inventory table.
        """
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        if not inventory:
            raise ValueError(f"Inventory record for product ID {product_id} does not exist.")

        # Prevent negative inventory
        if inventory.current_stock + quantity < 0:
            raise ValueError(f"Insufficient stock. Current inventory level is {inventory.current_stock}, tried to deduct {abs(quantity)}.")

        # Update values
        inventory.current_stock += quantity
        
        # Adjust incoming / outgoing stocks conditionally if driven by PO/PR workflows
        if transaction_type == 'IN':
            # Decrement incoming stock since it is now in current stock
            inventory.incoming_stock = max(0, inventory.incoming_stock - abs(quantity))
        elif transaction_type == 'OUT':
            # Decrement outgoing stock
            inventory.outgoing_stock = max(0, inventory.outgoing_stock - abs(quantity))

        # Log transaction record
        transaction = InventoryTransaction(
            product_id=product_id,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_id=reference_id,
            notes=notes
        )

        db.session.add(transaction)
        db.session.commit()
        return inventory

    @staticmethod
    def get_transaction_history(product_id=None, transaction_type=None, page=1, per_page=10):
        """
        Retrieve paginated inventory logs.
        """
        query = InventoryTransaction.query

        if product_id:
            query = query.filter(InventoryTransaction.product_id == product_id)
        if transaction_type:
            query = query.filter(InventoryTransaction.transaction_type == transaction_type)

        # Order by newest transactions
        query = query.order_by(InventoryTransaction.transaction_date.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'transactions': [tx.to_dict() for tx in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        }
