import os
from backend.app import create_app, db
from backend.models.user import Role, User
from backend.models.vendor import Vendor
from backend.models.product import Category, Product
from backend.models.inventory import Inventory, InventoryTransaction
from backend.models.purchase_request import PurchaseRequest, PurchaseRequestItem, Approval
from backend.models.purchase_order import PurchaseOrder, PurchaseOrderItem
import datetime

app = create_app()

with app.app_context():
    print("--------------------------------------------------")
    print("ProcureFlow Database Initializer - Enterprise Mode")
    print("--------------------------------------------------")
    
    # 1. Reset and create tables
    print("Recreating database tables...")
    db.drop_all()
    db.create_all()
    print("Tables created successfully.")
    
    print("Seeding lookups and rich enterprise multi-vendor dataset...")
    
    # 2a. Seed Roles
    roles = [
        Role(id=1, name='Admin', description='Platform administration, user management, full access to analytics and settings'),
        Role(id=2, name='Procurement Officer', description='Manage vendor catalog, products, inventory, create purchase orders, receive deliveries'),
        Role(id=3, name='Manager', description='Review and approve/reject purchase requests, monitor procurement spend, view analytics'),
        Role(id=4, name='Employee', description='Create purchase requests, view self purchase request history and tracking')
    ]
    db.session.add_all(roles)
    
    # 2b. Seed Categories
    categories = [
        Category(id=1, name='Laptops & Workstations', description='High-performance developer laptops, ultrabooks, and enterprise mobile workstations'),
        Category(id=2, name='Displays & Conference Hubs', description='4K UHD monitors, smart interactive displays, and video conferencing systems'),
        Category(id=3, name='Networking & Server Infrastructure', description='Rack servers, enterprise managed PoE+ switches, and Wi-Fi 6 access points'),
        Category(id=4, name='Office Ergonomics & Furniture', description='Ergonomic mesh chairs, dual-motor standing desks, and physical workspace assets'),
        Category(id=5, name='Peripherals & Accessories', description='Thunderbolt 4 docking stations, precision input devices, and active noise-canceling headsets'),
        Category(id=6, name='IT Consumables', description='Structured Cat6 cabling spools, high-yield toner cartridges, and maintenance supplies')
    ]
    db.session.add_all(categories)
    
    # 2c. Seed Users (Bcrypt Hash for 'Password123')
    pw_hash = '$2b$12$AG2BcKDp/o4e9Cift42LwuxHUQZuUPCsHB6RNI3/6CHk64E35dQIO'
    users = [
        # Management Team
        User(id=1, role_id=1, username='admin', email='admin@enterprise.com', password_hash=pw_hash, first_name='Raghav', last_name='Sharma', status='ACTIVE'),
        User(id=2, role_id=2, username='officer', email='officer@enterprise.com', password_hash=pw_hash, first_name='Rajesh', last_name='Verma', status='ACTIVE'),
        User(id=3, role_id=3, username='manager', email='manager@enterprise.com', password_hash=pw_hash, first_name='Priyanka', last_name='Joshi', status='ACTIVE'),
        
        # 5 Department Employee Leads
        User(id=4, role_id=4, username='employee', email='employee@enterprise.com', password_hash=pw_hash, first_name='Amit', last_name='Patil', status='ACTIVE'),
        User(id=5, role_id=4, username='sneha', email='sneha@enterprise.com', password_hash=pw_hash, first_name='Sneha', last_name='Kulkarni', status='ACTIVE'),
        User(id=6, role_id=4, username='vikram', email='vikram@enterprise.com', password_hash=pw_hash, first_name='Vikram', last_name='Malhotra', status='ACTIVE'),
        User(id=7, role_id=4, username='ananya', email='ananya@enterprise.com', password_hash=pw_hash, first_name='Ananya', last_name='Roy', status='ACTIVE'),
        User(id=8, role_id=4, username='rohit', email='rohit@enterprise.com', password_hash=pw_hash, first_name='Rohit', last_name='Sen', status='ACTIVE')
    ]
    db.session.add_all(users)
    
    # 2d. Seed 5 Real Enterprise Vendors
    vendors = [
        Vendor(
            id=1,
            name='Apple Enterprise Solutions (India)',
            company_name='Apple India Private Limited',
            gst_number='29AABCA1234F1Z5',
            email='b2b.india@apple.com',
            phone='+91-80-40455000',
            address='19th Floor, Concorde Tower C, UB City, Vittal Mallya Road, Bengaluru, Karnataka 560001',
            rating=4.90,
            status='ACTIVE'
        ),
        Vendor(
            id=2,
            name='Dell Technologies Commercial India',
            company_name='Dell International Services India Pvt Ltd',
            gst_number='29AABCD5678G1Z2',
            email='commercial.sales@dell.com',
            phone='+91-80-66882000',
            address='Divyasree Greens, Ground Floor, Challaghatta Village, Varthur Hobli, Bengaluru, Karnataka 560071',
            rating=4.80,
            status='ACTIVE'
        ),
        Vendor(
            id=3,
            name='Lenovo Enterprise Partner Network',
            company_name='Lenovo (India) Private Limited',
            gst_number='29AABCL9012H1Z8',
            email='enterprise.india@lenovo.com',
            phone='+91-80-30533000',
            address='Ferns Icon, Level 2, Marathahalli Outer Ring Road, Doddanekundi, Bengaluru, Karnataka 560037',
            rating=4.70,
            status='ACTIVE'
        ),
        Vendor(
            id=4,
            name='Redington IT Distribution Ltd',
            company_name='Redington India Limited (IT Supply Chain Division)',
            gst_number='33AABCR3456J1Z1',
            email='enterprise.supply@redington.co.in',
            phone='+91-44-42243353',
            address='SPL Guindy House, 95 Mount Road, Guindy, Chennai, Tamil Nadu 600032',
            rating=4.60,
            status='ACTIVE'
        ),
        Vendor(
            id=5,
            name='Featherlite Workspace Ergonomics',
            company_name='Featherlite Products Private Limited',
            gst_number='29AABCF7890K1Z4',
            email='corporate.solutions@featherlite.com',
            phone='+91-80-40474047',
            address='16/A Millers Road, Vasanthnagar, Bengaluru, Karnataka 560052',
            rating=4.75,
            status='ACTIVE'
        )
    ]
    db.session.add_all(vendors)
    
    # 2e. Seed 18 Enterprise Products (in INR)
    products = [
        # Laptops & Workstations (Category 1)
        Product(id=1, name='MacBook Pro 16" (M3 Max, 36GB, 1TB SSD)', sku='APP-MBP-16M3', category_id=1, unit_price=249900.00, reorder_level=5, vendor_id=1, status='ACTIVE'),
        Product(id=2, name='MacBook Air 15" (M3, 16GB, 512GB SSD)', sku='APP-MBA-15M3', category_id=1, unit_price=134900.00, reorder_level=8, vendor_id=1, status='ACTIVE'),
        Product(id=3, name='Dell XPS 15 9530 (i9-13900H, 32GB, RTX 4060)', sku='DELL-XPS-15', category_id=1, unit_price=189990.00, reorder_level=6, vendor_id=2, status='ACTIVE'),
        Product(id=4, name='Lenovo ThinkPad X1 Carbon Gen 11 (i7, 32GB, 1TB)', sku='LEN-TP-X1C11', category_id=1, unit_price=165000.00, reorder_level=8, vendor_id=3, status='ACTIVE'),
        
        # Displays & Conference Hubs (Category 2)
        Product(id=5, name='Dell UltraSharp 32" 4K USB-C Hub Monitor (U3223QE)', sku='DELL-MON-U32', category_id=2, unit_price=68500.00, reorder_level=10, vendor_id=2, status='ACTIVE'),
        Product(id=6, name='Logitech Rally Bar 4K All-In-One Conference Bar', sku='LOG-CONF-RALLY', category_id=2, unit_price=295000.00, reorder_level=2, vendor_id=4, status='ACTIVE'),
        Product(id=18, name='Lenovo ThinkVision 27" QHD Ergonomic Monitor (T27h-30)', sku='LEN-MON-T27H', category_id=2, unit_price=24500.00, reorder_level=10, vendor_id=3, status='ACTIVE'),

        # Networking & Server Infrastructure (Category 3)
        Product(id=7, name='Dell PowerEdge R760 Rack Server (Dual Xeon, 128GB)', sku='DELL-SRV-R760', category_id=3, unit_price=485000.00, reorder_level=2, vendor_id=2, status='ACTIVE'),
        Product(id=8, name='Cisco Catalyst 1000 24-Port Gigabit PoE+ Switch', sku='CIS-SW-1000-24P', category_id=3, unit_price=72000.00, reorder_level=5, vendor_id=4, status='ACTIVE'),
        Product(id=9, name='Aruba Instant On AP22 Wi-Fi 6 Access Point', sku='ARU-WIFI-AP22', category_id=3, unit_price=14500.00, reorder_level=12, vendor_id=4, status='ACTIVE'),
        
        # Office Ergonomics & Furniture (Category 4)
        Product(id=10, name='Featherlite Optima High-Back Mesh Ergonomic Chair', sku='FL-CHR-OPTIMA', category_id=4, unit_price=18500.00, reorder_level=15, vendor_id=5, status='ACTIVE'),
        Product(id=11, name='Featherlite Motorized Dual-Motor Standing Desk (1500x750)', sku='FL-DSK-ELEC15', category_id=4, unit_price=36000.00, reorder_level=6, vendor_id=5, status='ACTIVE'),
        
        # Peripherals & Accessories (Category 5)
        Product(id=12, name='CalDigit TS4 Thunderbolt 4 Docking Station (18 Ports)', sku='CAL-DCK-TS4', category_id=5, unit_price=38990.00, reorder_level=15, vendor_id=4, status='ACTIVE'),
        Product(id=13, name='Logitech MX Master 3S Performance Wireless Mouse', sku='LOG-ACC-MXM3S', category_id=5, unit_price=8995.00, reorder_level=25, vendor_id=4, status='ACTIVE'),
        Product(id=14, name='Jabra Evolve2 75 Wireless ANC Headset', sku='JAB-AUD-EV75', category_id=5, unit_price=26500.00, reorder_level=10, vendor_id=4, status='ACTIVE'),
        Product(id=17, name='Dell Pro Wireless Keyboard and Mouse Combo (KM5221W)', sku='DELL-ACC-KM522', category_id=5, unit_price=3200.00, reorder_level=20, vendor_id=2, status='ACTIVE'),

        # IT Consumables (Category 6)
        Product(id=15, name='Schneider Electric Cat6 UTP 305m Cable Drum', sku='SCH-CAB-CAT6-305', category_id=6, unit_price=9800.00, reorder_level=10, vendor_id=4, status='ACTIVE'),
        Product(id=16, name='HP LaserJet High Yield Black Toner Pack (W1330X)', sku='HP-SUP-TONER-1330', category_id=6, unit_price=11200.00, reorder_level=20, vendor_id=4, status='ACTIVE')
    ]
    db.session.add_all(products)
    db.session.flush()
    
    # 2f. Seed Inventory slots for the 18 products
    inventory_items = [
        Inventory(product_id=1, current_stock=15, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=2, current_stock=20, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=3, current_stock=12, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=4, current_stock=18, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=5, current_stock=25, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=6, current_stock=4, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=7, current_stock=3, incoming_stock=1, outgoing_stock=0),
        Inventory(product_id=8, current_stock=8, incoming_stock=2, outgoing_stock=0),
        Inventory(product_id=9, current_stock=30, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=10, current_stock=45, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=11, current_stock=14, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=12, current_stock=35, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=13, current_stock=60, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=14, current_stock=22, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=15, current_stock=18, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=16, current_stock=50, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=17, current_stock=40, incoming_stock=0, outgoing_stock=0),
        Inventory(product_id=18, current_stock=28, incoming_stock=0, outgoing_stock=0)
    ]
    db.session.add_all(inventory_items)
    
    # 2g. Log initial stock transactions
    initial_txs = [
        InventoryTransaction(product_id=1, transaction_type='IN', quantity=13, notes='Initial setup stock'),
        InventoryTransaction(product_id=2, transaction_type='IN', quantity=20, notes='Initial setup stock'),
        InventoryTransaction(product_id=3, transaction_type='IN', quantity=12, notes='Initial setup stock'),
        InventoryTransaction(product_id=4, transaction_type='IN', quantity=18, notes='Initial setup stock'),
        InventoryTransaction(product_id=5, transaction_type='IN', quantity=22, notes='Initial setup stock'),
        InventoryTransaction(product_id=6, transaction_type='IN', quantity=4, notes='Initial setup stock'),
        InventoryTransaction(product_id=7, transaction_type='IN', quantity=3, notes='Initial setup stock'),
        InventoryTransaction(product_id=8, transaction_type='IN', quantity=8, notes='Initial setup stock'),
        InventoryTransaction(product_id=9, transaction_type='IN', quantity=30, notes='Initial setup stock'),
        InventoryTransaction(product_id=10, transaction_type='IN', quantity=45, notes='Initial setup stock'),
        InventoryTransaction(product_id=11, transaction_type='IN', quantity=14, notes='Initial setup stock'),
        InventoryTransaction(product_id=12, transaction_type='IN', quantity=33, notes='Initial setup stock'),
        InventoryTransaction(product_id=13, transaction_type='IN', quantity=55, notes='Initial setup stock'),
        InventoryTransaction(product_id=14, transaction_type='IN', quantity=22, notes='Initial setup stock'),
        InventoryTransaction(product_id=15, transaction_type='IN', quantity=14, notes='Initial setup stock'),
        InventoryTransaction(product_id=16, transaction_type='IN', quantity=44, notes='Initial setup stock'),
        InventoryTransaction(product_id=17, transaction_type='IN', quantity=40, notes='Initial setup stock'),
        InventoryTransaction(product_id=18, transaction_type='IN', quantity=28, notes='Initial setup stock')
    ]
    db.session.add_all(initial_txs)
    
    # 3. Rich Requisitions Operational History Distributed Across All 5 Department Employees
    # Employee 1: Amit Patil (user_id=4, Engineering Lead)
    # Employee 2: Sneha Kulkarni (user_id=5, UI/UX Lead)
    # Employee 3: Vikram Malhotra (user_id=6, Cloud/Infra Lead)
    # Employee 4: Ananya Roy (user_id=7, Finance Analyst)
    # Employee 5: Rohit Sen (user_id=8, Facilities Lead)
    
    reqs = [
        # PR 1: Amit Patil (Engineering) -> High-end Dev MacBook Pros & CalDigit TS4 Docks (Converted to PO 1)
        PurchaseRequest(id=1, employee_id=4, status='CONVERTED', total_amount=577780.00, comments='High-performance compute machines and Thunderbolt 4 docks for Core AI & Systems Engineering team.', created_at=datetime.datetime.now() - datetime.timedelta(days=18)),
        
        # PR 2: Sneha Kulkarni (UI/UX) -> Dell UltraSharp 32" 4K Displays & MX Master 3S mice (Converted to PO 2)
        PurchaseRequest(id=2, employee_id=5, status='CONVERTED', total_amount=232485.00, comments='Color-accurate 4K displays and ergonomic precision mice for Design Sprint Studio.', created_at=datetime.datetime.now() - datetime.timedelta(days=14)),
        
        # PR 3: Vikram Malhotra (Cloud/Infra) -> Dell PowerEdge R760 Rack Server + Cisco PoE+ Switches (Converted to PO 3)
        PurchaseRequest(id=3, employee_id=6, status='CONVERTED', total_amount=629000.00, comments='Private cloud on-prem virtualization expansion and core network switch upgrades.', created_at=datetime.datetime.now() - datetime.timedelta(days=10)),
        
        # PR 4: Rohit Sen (Facilities) -> Featherlite Optima Ergonomic Chairs & Motorized Standing Desks (Approved)
        PurchaseRequest(id=4, employee_id=8, status='APPROVED', total_amount=329000.00, comments='Ergonomic seating and height-adjustable desks for newly renovated 4th Floor Tech Wing.', created_at=datetime.datetime.now() - datetime.timedelta(days=5)),
        
        # PR 5: Ananya Roy (Finance) -> ThinkPad X1 Carbon Gen 11 laptops for executive financial modeling (Pending Review)
        PurchaseRequest(id=5, employee_id=7, status='PENDING', total_amount=330000.00, comments='Secure, lightweight executive laptops for Q3 M&A audit and financial forecasting team.', created_at=datetime.datetime.now() - datetime.timedelta(days=2)),
        
        # PR 6: Rohit Sen (Facilities) -> Schneider Cat6 Structured Cables + High-yield Toner Cartridges (Converted to PO 4)
        PurchaseRequest(id=6, employee_id=8, status='CONVERTED', total_amount=116200.00, comments='Structured Cat6 cabling drums and floor printer high-yield toner cartridge restock.', created_at=datetime.datetime.now() - datetime.timedelta(days=12)),
        
        # PR 7: Sneha Kulkarni (UI/UX) -> MacBook Air 15" for design research interns (Pending Review)
        PurchaseRequest(id=7, employee_id=5, status='PENDING', total_amount=269800.00, comments='Ultrabooks for incoming UX Research interns and interaction prototypes.', created_at=datetime.datetime.now() - datetime.timedelta(days=1)),
        
        # PR 8: Vikram Malhotra (Cloud/Infra) -> Informal huddle space video bar (Rejected)
        PurchaseRequest(id=8, employee_id=6, status='REJECTED', total_amount=295000.00, comments='Stand-alone conference bar for informal dev huddle space.', created_at=datetime.datetime.now() - datetime.timedelta(days=8))
    ]
    db.session.add_all(reqs)
    db.session.flush()
    
    # 3a. Requisition items
    req_items = [
        # PR 1: Amit Patil (2x MacBook Pro 16", 2x CalDigit TS4)
        PurchaseRequestItem(purchase_request_id=1, product_id=1, quantity=2, unit_price=249900.00),
        PurchaseRequestItem(purchase_request_id=1, product_id=12, quantity=2, unit_price=38990.00),
        
        # PR 2: Sneha Kulkarni (3x Dell 32" 4K, 3x MX Master 3S)
        PurchaseRequestItem(purchase_request_id=2, product_id=5, quantity=3, unit_price=68500.00),
        PurchaseRequestItem(purchase_request_id=2, product_id=13, quantity=3, unit_price=8995.00),
        
        # PR 3: Vikram Malhotra (1x PowerEdge R760, 2x Cisco PoE+ Switch)
        PurchaseRequestItem(purchase_request_id=3, product_id=7, quantity=1, unit_price=485000.00),
        PurchaseRequestItem(purchase_request_id=3, product_id=8, quantity=2, unit_price=72000.00),
        
        # PR 4: Rohit Sen (10x Featherlite Chairs, 4x Standing Desks)
        PurchaseRequestItem(purchase_request_id=4, product_id=10, quantity=10, unit_price=18500.00),
        PurchaseRequestItem(purchase_request_id=4, product_id=11, quantity=4, unit_price=36000.00),
        
        # PR 5: Ananya Roy (2x Lenovo ThinkPad X1 Carbon)
        PurchaseRequestItem(purchase_request_id=5, product_id=4, quantity=2, unit_price=165000.00),
        
        # PR 6: Rohit Sen (5x Cat6 Cable Drums, 6x Toner Packs)
        PurchaseRequestItem(purchase_request_id=6, product_id=15, quantity=5, unit_price=9800.00),
        PurchaseRequestItem(purchase_request_id=6, product_id=16, quantity=6, unit_price=11200.00),
        
        # PR 7: Sneha Kulkarni (2x MacBook Air 15")
        PurchaseRequestItem(purchase_request_id=7, product_id=2, quantity=2, unit_price=134900.00),
        
        # PR 8: Vikram Malhotra (1x Logitech Rally Bar)
        PurchaseRequestItem(purchase_request_id=8, product_id=6, quantity=1, unit_price=295000.00)
    ]
    db.session.add_all(req_items)
    
    # 3b. Reviews/Approvals logs (Manager Priyanka Joshi, user_id=3)
    approvals_log = [
        Approval(purchase_request_id=1, reviewer_id=3, status='APPROVED', review_comments='Approved for Core Engineering infrastructure onboarding. Budget cleared under CapEx 2026.', reviewed_at=datetime.datetime.now() - datetime.timedelta(days=17)),
        Approval(purchase_request_id=2, reviewer_id=3, status='APPROVED', review_comments='Approved. Design lab color-accuracy requirements validated.', reviewed_at=datetime.datetime.now() - datetime.timedelta(days=13)),
        Approval(purchase_request_id=3, reviewer_id=3, status='APPROVED', review_comments='Approved. Infrastructure expansion justified for private cloud virtualization.', reviewed_at=datetime.datetime.now() - datetime.timedelta(days=9)),
        Approval(purchase_request_id=4, reviewer_id=3, status='APPROVED', review_comments='Approved. Facilities ergonomics refresh endorsed by HR & Operations committee.', reviewed_at=datetime.datetime.now() - datetime.timedelta(days=4)),
        Approval(purchase_request_id=6, reviewer_id=3, status='APPROVED', review_comments='Approved. Standard infrastructure and consumable replenishment.', reviewed_at=datetime.datetime.now() - datetime.timedelta(days=11)),
        Approval(purchase_request_id=8, reviewer_id=3, status='REJECTED', review_comments='Non-standard allocation for dev huddle space. Please utilize existing meeting room conference hardware.', reviewed_at=datetime.datetime.now() - datetime.timedelta(days=7))
    ]
    db.session.add_all(approvals_log)
    
    # 4. Rich Purchase Orders Operational History
    orders = [
        # PO 1: Apple Enterprise Solutions (PR 1: MacBook Pros + TS4 Docks) -> Delivered
        PurchaseOrder(id=1, purchase_request_id=1, vendor_id=1, po_number='PO-2026-0001', status='DELIVERED', total_amount=577780.00, expected_delivery_date=datetime.datetime.now() - datetime.timedelta(days=14), actual_delivery_date=datetime.datetime.now() - datetime.timedelta(days=12), created_at=datetime.datetime.now() - datetime.timedelta(days=17)),
        
        # PO 2: Dell Technologies (PR 2: 4K Monitors + MX Master 3S) -> Delivered
        PurchaseOrder(id=2, purchase_request_id=2, vendor_id=2, po_number='PO-2026-0002', status='DELIVERED', total_amount=232485.00, expected_delivery_date=datetime.datetime.now() - datetime.timedelta(days=8), actual_delivery_date=datetime.datetime.now() - datetime.timedelta(days=7), created_at=datetime.datetime.now() - datetime.timedelta(days=13)),
        
        # PO 3: Dell Technologies (PR 3: PowerEdge R760 Server + Cisco Switches) -> Ordered / Shipped
        PurchaseOrder(id=3, purchase_request_id=3, vendor_id=2, po_number='PO-2026-0003', status='ORDERED', total_amount=629000.00, expected_delivery_date=datetime.datetime.now() + datetime.timedelta(days=5), actual_delivery_date=None, created_at=datetime.datetime.now() - datetime.timedelta(days=9)),
        
        # PO 4: Redington IT Distribution (PR 6: Cat6 Cable Drums + Toner Packs) -> Delivered
        PurchaseOrder(id=4, purchase_request_id=6, vendor_id=4, po_number='PO-2026-0004', status='DELIVERED', total_amount=116200.00, expected_delivery_date=datetime.datetime.now() - datetime.timedelta(days=7), actual_delivery_date=datetime.datetime.now() - datetime.timedelta(days=6), created_at=datetime.datetime.now() - datetime.timedelta(days=11)),
        
        # PO 5: Direct Lenovo Ad-hoc PO -> Cancelled due to vendor quotation expiration
        PurchaseOrder(id=5, purchase_request_id=None, vendor_id=3, po_number='PO-2026-0005', status='CANCELLED', total_amount=165000.00, expected_delivery_date=datetime.datetime.now() - datetime.timedelta(days=3), actual_delivery_date=None, created_at=datetime.datetime.now() - datetime.timedelta(days=10))
    ]
    db.session.add_all(orders)
    db.session.flush()
    
    # 4a. Purchase Order Items
    order_items = [
        # PO 1
        PurchaseOrderItem(purchase_order_id=1, product_id=1, quantity=2, unit_price=249900.00),
        PurchaseOrderItem(purchase_order_id=1, product_id=12, quantity=2, unit_price=38990.00),
        
        # PO 2
        PurchaseOrderItem(purchase_order_id=2, product_id=5, quantity=3, unit_price=68500.00),
        PurchaseOrderItem(purchase_order_id=2, product_id=13, quantity=3, unit_price=8995.00),
        
        # PO 3
        PurchaseOrderItem(purchase_order_id=3, product_id=7, quantity=1, unit_price=485000.00),
        PurchaseOrderItem(purchase_order_id=3, product_id=8, quantity=2, unit_price=72000.00),
        
        # PO 4
        PurchaseOrderItem(purchase_order_id=4, product_id=15, quantity=5, unit_price=9800.00),
        PurchaseOrderItem(purchase_order_id=4, product_id=16, quantity=6, unit_price=11200.00),
        
        # PO 5
        PurchaseOrderItem(purchase_order_id=5, product_id=4, quantity=1, unit_price=165000.00)
    ]
    db.session.add_all(order_items)
    
    # 4b. Log transaction records for DELIVERED POs (PO 1, PO 2, PO 4)
    # PO 1 Delivery: +2 MacBook Pro 16", +2 CalDigit TS4 Docks
    db.session.add(InventoryTransaction(product_id=1, transaction_type='IN', quantity=2, reference_id=1, notes='PO-2026-0001 delivery receipt (Apple)'))
    db.session.add(InventoryTransaction(product_id=12, transaction_type='IN', quantity=2, reference_id=1, notes='PO-2026-0001 delivery receipt (Apple Partner)'))
    
    # PO 2 Delivery: +3 Dell 4K Monitors, +3 MX Master 3S
    db.session.add(InventoryTransaction(product_id=5, transaction_type='IN', quantity=3, reference_id=2, notes='PO-2026-0002 delivery receipt (Dell Technologies)'))
    db.session.add(InventoryTransaction(product_id=13, transaction_type='IN', quantity=3, reference_id=2, notes='PO-2026-0002 delivery receipt (Dell Technologies)'))
    
    # PO 4 Delivery: +5 Cat6 Cable Drums, +6 Toner Packs
    db.session.add(InventoryTransaction(product_id=15, transaction_type='IN', quantity=5, reference_id=4, notes='PO-2026-0004 delivery receipt (Redington)'))
    db.session.add(InventoryTransaction(product_id=16, transaction_type='IN', quantity=6, reference_id=4, notes='PO-2026-0004 delivery receipt (Redington)'))
    
    # 5. Miscellaneous Manual Adjustments for Realism
    # Damaged Cat6 cable drum disposal during warehouse re-rack
    db.session.add(InventoryTransaction(product_id=15, transaction_type='OUT', quantity=-1, reference_id=None, notes='Damaged transit Cat6 cable drum discarded'))
    # Annual stock audit verification: +2 MX Master 3S surplus found
    db.session.add(InventoryTransaction(product_id=13, transaction_type='IN', quantity=2, reference_id=None, notes='Quarterly warehouse physical count reconciliation'))
    
    db.session.commit()
    print("Database successfully seeded with multi-vendor enterprise dataset.")
    print("--------------------------------------------------")
    print("Initialization finished successfully.")
    print("--------------------------------------------------")
