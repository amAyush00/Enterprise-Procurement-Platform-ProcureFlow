import datetime
from sqlalchemy import func, desc
from backend.app import db
from backend.models.vendor import Vendor
from backend.models.product import Product, Category
from backend.models.inventory import Inventory, InventoryTransaction
from backend.models.purchase_request import PurchaseRequest
from backend.models.purchase_order import PurchaseOrder, PurchaseOrderItem

class AnalyticsService:
    @staticmethod
    def get_dashboard_summary():
        """
        Compile high-level KPIs and recent activities for the admin dashboard.
        """
        # KPIs
        total_vendors = Vendor.query.count()
        active_vendors = Vendor.query.filter_by(status='ACTIVE').count()
        total_products = Product.query.count()
        
        # Current Inventory Value (SUM of current_stock * unit_price)
        inv_value_query = db.session.query(
            func.sum(Inventory.current_stock * Product.unit_price)
        ).join(Product, Inventory.product_id == Product.id).scalar()
        inventory_value = float(inv_value_query) if inv_value_query else 0.0

        pending_requests = PurchaseRequest.query.filter_by(status='PENDING').count()
        
        # Pending POs are those not Delivered or Cancelled
        pending_orders = PurchaseOrder.query.filter(
            PurchaseOrder.status.in_(['PENDING', 'APPROVED', 'ORDERED'])
        ).count()

        # Low Stock Alerts (current_stock <= reorder_level)
        low_stock_alerts = Inventory.query.join(Product).filter(
            Inventory.current_stock <= Product.reorder_level
        ).count()

        # Monthly Spending (Sum of POs for current calendar month that are not cancelled)
        today = datetime.date.today()
        first_day_of_month = datetime.date(today.year, today.month, 1)
        monthly_spend_query = db.session.query(
            func.sum(PurchaseOrder.total_amount)
        ).filter(
            PurchaseOrder.created_at >= first_day_of_month,
            PurchaseOrder.status != 'CANCELLED'
        ).scalar()
        monthly_spending = float(monthly_spend_query) if monthly_spend_query else 0.0

        # Recent activities (newest 5 PRs and 5 Inventory Transactions)
        recent_prs = PurchaseRequest.query.order_by(PurchaseRequest.created_at.desc()).limit(5).all()
        recent_txs = InventoryTransaction.query.order_by(InventoryTransaction.transaction_date.desc()).limit(5).all()

        activities = []
        for pr in recent_prs:
            activities.append({
                'type': 'PURCHASE_REQUEST',
                'description': f"Purchase request #{pr.id} submitted by {pr.employee.first_name if pr.employee else 'User'} for Rs. {float(pr.total_amount):,.2f}",
                'status': pr.status,
                'timestamp': pr.created_at.isoformat() if pr.created_at else None
            })
        for tx in recent_txs:
            activities.append({
                'type': 'INVENTORY_TX',
                'description': f"Stock {tx.transaction_type} of {abs(tx.quantity)} units for product {tx.product.name if tx.product else 'Unknown'} ({tx.notes})",
                'status': 'COMPLETED',
                'timestamp': tx.transaction_date.isoformat() if tx.transaction_date else None
            })
            
        # Sort activities by timestamp desc
        activities.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        activities = activities[:7] # Return top 7 overall

        return {
            'total_vendors': total_vendors,
            'active_vendors': active_vendors,
            'total_products': total_products,
            'inventory_value': inventory_value,
            'pending_purchase_requests': pending_requests,
            'pending_purchase_orders': pending_orders,
            'low_stock_alerts': low_stock_alerts,
            'monthly_spending': monthly_spending,
            'recent_activities': activities
        }

    @staticmethod
    def get_charts_data():
        """
        Compile charts analytics.
        """
        # 1. Monthly Spend Trend (Last 6 months)
        six_months_ago = datetime.datetime.now() - datetime.timedelta(days=180)
        
        # Dialect-aware date formatting
        is_sqlite = db.engine.name == 'sqlite'
        date_format_func = func.strftime('%Y-%m', PurchaseOrder.created_at) if is_sqlite else func.date_format(PurchaseOrder.created_at, '%Y-%m')

        monthly_spend_trend = db.session.query(
            date_format_func.label('month'),
            func.sum(PurchaseOrder.total_amount).label('total')
        ).filter(
            PurchaseOrder.created_at >= six_months_ago,
            PurchaseOrder.status != 'CANCELLED'
        ).group_by('month').order_by('month').all()

        monthly_spend_data = [
            {'month': row.month, 'amount': float(row.total)} for row in monthly_spend_trend
        ]

        # 2. Vendor Performance (Top 5 vendors by spend + their ratings)
        vendor_spend = db.session.query(
            Vendor.name.label('name'),
            Vendor.rating.label('rating'),
            func.sum(PurchaseOrder.total_amount).label('spend')
        ).join(PurchaseOrder, PurchaseOrder.vendor_id == Vendor.id).filter(
            PurchaseOrder.status != 'CANCELLED'
        ).group_by(Vendor.id).order_by(desc('spend')).limit(5).all()

        vendor_performance_data = [
            {'name': row.name, 'rating': float(row.rating), 'spend': float(row.spend)} for row in vendor_spend
        ]

        # 3. Inventory Value by Category
        category_inventory = db.session.query(
            Category.name.label('name'),
            func.sum(Inventory.current_stock * Product.unit_price).label('value')
        ).join(Product, Product.category_id == Category.id).join(Inventory, Inventory.product_id == Product.id).group_by(Category.id).all()

        inventory_category_data = [
            {'name': row.name, 'value': float(row.value) if row.value else 0.0} for row in category_inventory
        ]

        # 4. Purchase Order Status Split
        po_status_split = db.session.query(
            PurchaseOrder.status.label('status'),
            func.count(PurchaseOrder.id).label('count')
        ).group_by(PurchaseOrder.status).all()

        po_status_data = [
            {'status': row.status, 'count': row.count} for row in po_status_split
        ]

        # 5. Top Purchased Products (Top 5 by quantity ordered)
        top_products = db.session.query(
            Product.name.label('name'),
            func.sum(PurchaseOrderItem.quantity).label('quantity')
        ).join(PurchaseOrderItem, PurchaseOrderItem.product_id == Product.id).join(PurchaseOrder, PurchaseOrderItem.purchase_order_id == PurchaseOrder.id).filter(
            PurchaseOrder.status == 'DELIVERED'
        ).group_by(Product.id).order_by(desc('quantity')).limit(5).all()

        top_products_data = [
            {'name': row.name, 'quantity': int(row.quantity)} for row in top_products
        ]

        return {
            'monthly_spend_trend': monthly_spend_data,
            'vendor_performance': vendor_performance_data,
            'inventory_by_category': inventory_category_data,
            'purchase_order_status_split': po_status_data,
            'top_purchased_products': top_products_data
        }
