-- =====================================================================
-- Enterprise Procurement & Vendor Analytics Platform (ProcureFlow)
-- MySQL Database Definition & Seeding Script (Multi-Vendor Enterprise Mode)
-- Standard 3NF Relational Database Design for MySQL (InnoDB)
-- =====================================================================

-- Disable foreign keys temporarily to allow drops and clean inserts
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS inventory_transactions;
DROP TABLE IF EXISTS purchase_order_items;
DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS approvals;
DROP TABLE IF EXISTS purchase_request_items;
DROP TABLE IF EXISTS purchase_requests;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS vendors;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------
-- 1. Table `roles`
-- -----------------------------------------------------
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 2. Table `users`
-- -----------------------------------------------------
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    status ENUM('ACTIVE', 'INACTIVE') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT,
    INDEX idx_user_username (username),
    INDEX idx_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 3. Table `vendors`
-- -----------------------------------------------------
CREATE TABLE vendors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    gst_number VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    rating DECIMAL(3, 2) DEFAULT 5.00,
    status ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_vendor_rating CHECK (rating >= 0.00 AND rating <= 5.00),
    INDEX idx_vendor_status (status),
    INDEX idx_vendor_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 4. Table `categories`
-- -----------------------------------------------------
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 5. Table `products`
-- -----------------------------------------------------
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    category_id INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    reorder_level INT NOT NULL DEFAULT 10,
    vendor_id INT NOT NULL,
    status ENUM('ACTIVE', 'INACTIVE', 'DISCONTINUED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE RESTRICT,
    CONSTRAINT chk_product_price CHECK (unit_price >= 0),
    CONSTRAINT chk_product_reorder CHECK (reorder_level >= 0),
    INDEX idx_product_sku (sku),
    INDEX idx_product_vendor (vendor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 6. Table `inventory`
-- -----------------------------------------------------
CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL UNIQUE,
    current_stock INT NOT NULL DEFAULT 0,
    incoming_stock INT NOT NULL DEFAULT 0,
    outgoing_stock INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT chk_inventory_current CHECK (current_stock >= 0),
    CONSTRAINT chk_inventory_incoming CHECK (incoming_stock >= 0),
    CONSTRAINT chk_inventory_outgoing CHECK (outgoing_stock >= 0),
    INDEX idx_inventory_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 7. Table `purchase_requests`
-- -----------------------------------------------------
CREATE TABLE purchase_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'CONVERTED') DEFAULT 'PENDING',
    total_amount DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT chk_pr_total CHECK (total_amount >= 0),
    INDEX idx_pr_employee (employee_id),
    INDEX idx_pr_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 8. Table `purchase_request_items`
-- -----------------------------------------------------
CREATE TABLE purchase_request_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_request_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (purchase_request_id) REFERENCES purchase_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    CONSTRAINT chk_pri_quantity CHECK (quantity > 0),
    CONSTRAINT chk_pri_price CHECK (unit_price >= 0),
    INDEX idx_pri_request (purchase_request_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 9. Table `approvals`
-- -----------------------------------------------------
CREATE TABLE approvals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_request_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    status ENUM('APPROVED', 'REJECTED') NOT NULL,
    review_comments TEXT,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (purchase_request_id) REFERENCES purchase_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_approval_request (purchase_request_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 10. Table `purchase_orders`
-- -----------------------------------------------------
CREATE TABLE purchase_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_request_id INT DEFAULT NULL,
    vendor_id INT NOT NULL,
    po_number VARCHAR(50) NOT NULL UNIQUE,
    status ENUM('PENDING', 'APPROVED', 'ORDERED', 'DELIVERED', 'CANCELLED') DEFAULT 'PENDING',
    total_amount DECIMAL(15, 2) NOT NULL,
    expected_delivery_date DATE NOT NULL,
    actual_delivery_date DATE DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (purchase_request_id) REFERENCES purchase_requests(id) ON DELETE SET NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE RESTRICT,
    CONSTRAINT chk_po_total CHECK (total_amount >= 0),
    INDEX idx_po_number (po_number),
    INDEX idx_po_status (status),
    INDEX idx_po_vendor (vendor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 11. Table `purchase_order_items`
-- -----------------------------------------------------
CREATE TABLE purchase_order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    CONSTRAINT chk_poi_quantity CHECK (quantity > 0),
    CONSTRAINT chk_poi_price CHECK (unit_price >= 0),
    INDEX idx_poi_order (purchase_order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- 12. Table `inventory_transactions`
-- -----------------------------------------------------
CREATE TABLE inventory_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    transaction_type ENUM('IN', 'OUT', 'ADJUSTMENT') NOT NULL,
    quantity INT NOT NULL,
    reference_id INT DEFAULT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes VARCHAR(255),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    CONSTRAINT chk_inv_tx_quantity CHECK (quantity <> 0),
    INDEX idx_inv_tx_product (product_id),
    INDEX idx_inv_tx_type (transaction_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =====================================================================
-- DATA SEEDING (Multi-Vendor Enterprise Procurement)
-- =====================================================================

-- 1. Seed Roles
INSERT INTO roles (id, name, description) VALUES
(1, 'Admin', 'Platform administration, user management, full access to analytics and settings'),
(2, 'Procurement Officer', 'Manage vendor catalog, products, inventory, create purchase orders, receive deliveries'),
(3, 'Manager', 'Review and approve/reject purchase requests, monitor procurement spend, view analytics'),
(4, 'Employee', 'Create purchase requests, view self purchase request history and tracking');

-- 2. Seed Users (Bcrypt Hash for 'Password123')
-- Hash: $2b$12$AG2BcKDp/o4e9Cift42LwuxHUQZuUPCsHB6RNI3/6CHk64E35dQIO
INSERT INTO users (id, role_id, username, email, password_hash, first_name, last_name, status) VALUES
(1, 1, 'admin', 'admin@enterprise.com', '$2b$12$AG2BcKDp/o4e9Cift42LwuxHUQZuUPCsHB6RNI3/6CHk64E35dQIO', 'Raghav', 'Sharma', 'ACTIVE'),
(2, 2, 'officer', 'officer@enterprise.com', '$2b$12$AG2BcKDp/o4e9Cift42LwuxHUQZuUPCsHB6RNI3/6CHk64E35dQIO', 'Rajesh', 'Verma', 'ACTIVE'),
(3, 3, 'manager', 'manager@enterprise.com', '$2b$12$AG2BcKDp/o4e9Cift42LwuxHUQZuUPCsHB6RNI3/6CHk64E35dQIO', 'Priyanka', 'Joshi', 'ACTIVE'),
(4, 4, 'employee', 'employee@enterprise.com', '$2b$12$AG2BcKDp/o4e9Cift42LwuxHUQZuUPCsHB6RNI3/6CHk64E35dQIO', 'Amit', 'Patil', 'ACTIVE'),
(5, 4, 'sneha', 'sneha@enterprise.com', '$2b$12$AG2BcKDp/o4e9Cift42LwuxHUQZuUPCsHB6RNI3/6CHk64E35dQIO', 'Sneha', 'Kulkarni', 'ACTIVE'),
(6, 4, 'vikram', 'vikram@enterprise.com', '$2b$12$AG2BcKDp/o4e9Cift42LwuxHUQZuUPCsHB6RNI3/6CHk64E35dQIO', 'Vikram', 'Malhotra', 'ACTIVE'),
(7, 4, 'ananya', 'ananya@enterprise.com', '$2b$12$AG2BcKDp/o4e9Cift42LwuxHUQZuUPCsHB6RNI3/6CHk64E35dQIO', 'Ananya', 'Roy', 'ACTIVE'),
(8, 4, 'rohit', 'rohit@enterprise.com', '$2b$12$AG2BcKDp/o4e9Cift42LwuxHUQZuUPCsHB6RNI3/6CHk64E35dQIO', 'Rohit', 'Sen', 'ACTIVE');

-- 3. Seed Categories
INSERT INTO categories (id, name, description) VALUES
(1, 'Laptops & Workstations', 'High-performance developer laptops, ultrabooks, and enterprise mobile workstations'),
(2, 'Displays & Conference Hubs', '4K UHD monitors, smart interactive displays, and video conferencing systems'),
(3, 'Networking & Server Infrastructure', 'Rack servers, enterprise managed PoE+ switches, and Wi-Fi 6 access points'),
(4, 'Office Ergonomics & Furniture', 'Ergonomic mesh chairs, dual-motor standing desks, and physical workspace assets'),
(5, 'Peripherals & Accessories', 'Thunderbolt 4 docking stations, precision input devices, and active noise-canceling headsets'),
(6, 'IT Consumables', 'Structured Cat6 cabling spools, high-yield toner cartridges, and maintenance supplies');

-- 4. Seed 5 Real Enterprise Vendors
INSERT INTO vendors (id, name, company_name, gst_number, email, phone, address, rating, status) VALUES
(1, 'Apple Enterprise Solutions (India)', 'Apple India Private Limited', '29AABCA1234F1Z5', 'b2b.india@apple.com', '+91-80-40455000', '19th Floor, Concorde Tower C, UB City, Vittal Mallya Road, Bengaluru, Karnataka 560001', 4.90, 'ACTIVE'),
(2, 'Dell Technologies Commercial India', 'Dell International Services India Pvt Ltd', '29AABCD5678G1Z2', 'commercial.sales@dell.com', '+91-80-66882000', 'Divyasree Greens, Ground Floor, Challaghatta Village, Varthur Hobli, Bengaluru, Karnataka 560071', 4.80, 'ACTIVE'),
(3, 'Lenovo Enterprise Partner Network', 'Lenovo (India) Private Limited', '29AABCL9012H1Z8', 'enterprise.india@lenovo.com', '+91-80-30533000', 'Ferns Icon, Level 2, Marathahalli Outer Ring Road, Doddanekundi, Bengaluru, Karnataka 560037', 4.70, 'ACTIVE'),
(4, 'Redington IT Distribution Ltd', 'Redington India Limited (IT Supply Chain Division)', '33AABCR3456J1Z1', 'enterprise.supply@redington.co.in', '+91-44-42243353', 'SPL Guindy House, 95 Mount Road, Guindy, Chennai, Tamil Nadu 600032', 4.60, 'ACTIVE'),
(5, 'Featherlite Workspace Ergonomics', 'Featherlite Products Private Limited', '29AABCF7890K1Z4', 'corporate.solutions@featherlite.com', '+91-80-40474047', '16/A Millers Road, Vasanthnagar, Bengaluru, Karnataka 560052', 4.75, 'ACTIVE');

-- 5. Seed 18 Enterprise Products (in INR)
INSERT INTO products (id, name, sku, category_id, unit_price, reorder_level, vendor_id, status) VALUES
(1, 'MacBook Pro 16" (M3 Max, 36GB, 1TB SSD)', 'APP-MBP-16M3', 1, 249900.00, 5, 1, 'ACTIVE'),
(2, 'MacBook Air 15" (M3, 16GB, 512GB SSD)', 'APP-MBA-15M3', 1, 134900.00, 8, 1, 'ACTIVE'),
(3, 'Dell XPS 15 9530 (i9-13900H, 32GB, RTX 4060)', 'DELL-XPS-15', 1, 189990.00, 6, 2, 'ACTIVE'),
(4, 'Lenovo ThinkPad X1 Carbon Gen 11 (i7, 32GB, 1TB)', 'LEN-TP-X1C11', 1, 165000.00, 8, 3, 'ACTIVE'),
(5, 'Dell UltraSharp 32" 4K USB-C Hub Monitor (U3223QE)', 'DELL-MON-U32', 2, 68500.00, 10, 2, 'ACTIVE'),
(6, 'Logitech Rally Bar 4K All-In-One Conference Bar', 'LOG-CONF-RALLY', 2, 295000.00, 2, 4, 'ACTIVE'),
(7, 'Dell PowerEdge R760 Rack Server (Dual Xeon, 128GB)', 'DELL-SRV-R760', 3, 485000.00, 2, 2, 'ACTIVE'),
(8, 'Cisco Catalyst 1000 24-Port Gigabit PoE+ Switch', 'CIS-SW-1000-24P', 3, 72000.00, 5, 4, 'ACTIVE'),
(9, 'Aruba Instant On AP22 Wi-Fi 6 Access Point', 'ARU-WIFI-AP22', 3, 14500.00, 12, 4, 'ACTIVE'),
(10, 'Featherlite Optima High-Back Mesh Ergonomic Chair', 'FL-CHR-OPTIMA', 4, 18500.00, 15, 5, 'ACTIVE'),
(11, 'Featherlite Motorized Dual-Motor Standing Desk (1500x750)', 'FL-DSK-ELEC15', 4, 36000.00, 6, 5, 'ACTIVE'),
(12, 'CalDigit TS4 Thunderbolt 4 Docking Station (18 Ports)', 'CAL-DCK-TS4', 5, 38990.00, 15, 4, 'ACTIVE'),
(13, 'Logitech MX Master 3S Performance Wireless Mouse', 'LOG-ACC-MXM3S', 5, 8995.00, 25, 4, 'ACTIVE'),
(14, 'Jabra Evolve2 75 Wireless ANC Headset', 'JAB-AUD-EV75', 5, 26500.00, 10, 4, 'ACTIVE'),
(15, 'Schneider Electric Cat6 UTP 305m Cable Drum', 'SCH-CAB-CAT6-305', 6, 9800.00, 10, 4, 'ACTIVE'),
(16, 'HP LaserJet High Yield Black Toner Pack (W1330X)', 'HP-SUP-TONER-1330', 6, 11200.00, 20, 4, 'ACTIVE'),
(17, 'Dell Pro Wireless Keyboard and Mouse Combo (KM5221W)', 'DELL-ACC-KM522', 5, 3200.00, 20, 2, 'ACTIVE'),
(18, 'Lenovo ThinkVision 27" QHD Ergonomic Monitor (T27h-30)', 'LEN-MON-T27H', 2, 24500.00, 10, 3, 'ACTIVE');

-- 6. Seed Inventory slots for the 18 products
INSERT INTO inventory (product_id, current_stock, incoming_stock, outgoing_stock) VALUES
(1, 15, 0, 0),
(2, 20, 0, 0),
(3, 12, 0, 0),
(4, 18, 0, 0),
(5, 25, 0, 0),
(6, 4, 0, 0),
(7, 3, 1, 0),
(8, 8, 2, 0),
(9, 30, 0, 0),
(10, 45, 0, 0),
(11, 14, 0, 0),
(12, 35, 0, 0),
(13, 60, 0, 0),
(14, 22, 0, 0),
(15, 18, 0, 0),
(16, 50, 0, 0),
(17, 40, 0, 0),
(18, 28, 0, 0);

-- 7. Seed Initial Inventory setup transactions
INSERT INTO inventory_transactions (product_id, transaction_type, quantity, reference_id, notes) VALUES
(1, 'IN', 13, NULL, 'Initial setup stock'),
(2, 'IN', 20, NULL, 'Initial setup stock'),
(3, 'IN', 12, NULL, 'Initial setup stock'),
(4, 'IN', 18, NULL, 'Initial setup stock'),
(5, 'IN', 22, NULL, 'Initial setup stock'),
(6, 'IN', 4, NULL, 'Initial setup stock'),
(7, 'IN', 3, NULL, 'Initial setup stock'),
(8, 'IN', 8, NULL, 'Initial setup stock'),
(9, 'IN', 30, NULL, 'Initial setup stock'),
(10, 'IN', 45, NULL, 'Initial setup stock'),
(11, 'IN', 14, NULL, 'Initial setup stock'),
(12, 'IN', 33, NULL, 'Initial setup stock'),
(13, 'IN', 55, NULL, 'Initial setup stock'),
(14, 'IN', 22, NULL, 'Initial setup stock'),
(15, 'IN', 14, NULL, 'Initial setup stock'),
(16, 'IN', 44, NULL, 'Initial setup stock'),
(17, 'IN', 40, NULL, 'Initial setup stock'),
(18, 'IN', 28, NULL, 'Initial setup stock');

-- 8. Seed Sample Purchase Requests Distributed Across 5 Department Leads
INSERT INTO purchase_requests (id, employee_id, status, total_amount, comments, created_at) VALUES
(1, 4, 'CONVERTED', 577780.00, 'High-performance compute machines and Thunderbolt 4 docks for Core AI & Systems Engineering team.', DATE_SUB(NOW(), INTERVAL 18 DAY)),
(2, 5, 'CONVERTED', 232485.00, 'Color-accurate 4K displays and ergonomic precision mice for Design Sprint Studio.', DATE_SUB(NOW(), INTERVAL 14 DAY)),
(3, 6, 'CONVERTED', 629000.00, 'Private cloud on-prem virtualization expansion and core network switch upgrades.', DATE_SUB(NOW(), INTERVAL 10 DAY)),
(4, 8, 'APPROVED', 329000.00, 'Ergonomic seating and height-adjustable desks for newly renovated 4th Floor Tech Wing.', DATE_SUB(NOW(), INTERVAL 5 DAY)),
(5, 7, 'PENDING', 330000.00, 'Secure, lightweight executive laptops for Q3 M&A audit and financial forecasting team.', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(6, 8, 'CONVERTED', 116200.00, 'Structured Cat6 cabling drums and floor printer high-yield toner cartridge restock.', DATE_SUB(NOW(), INTERVAL 12 DAY)),
(7, 5, 'PENDING', 269800.00, 'Ultrabooks for incoming UX Research interns and interaction prototypes.', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(8, 6, 'REJECTED', 295000.00, 'Stand-alone conference bar for informal dev huddle space.', DATE_SUB(NOW(), INTERVAL 8 DAY));

-- 9. Seed Purchase Request Items
INSERT INTO purchase_request_items (purchase_request_id, product_id, quantity, unit_price) VALUES
(1, 1, 2, 249900.00),
(1, 12, 2, 38990.00),
(2, 5, 3, 68500.00),
(2, 13, 3, 8995.00),
(3, 7, 1, 485000.00),
(3, 8, 2, 72000.00),
(4, 10, 10, 18500.00),
(4, 11, 4, 36000.00),
(5, 4, 2, 165000.00),
(6, 15, 5, 9800.00),
(6, 16, 6, 11200.00),
(7, 2, 2, 134900.00),
(8, 6, 1, 295000.00);

-- 10. Seed Approvals / Reviews (Manager Priyanka Joshi, user_id=3)
INSERT INTO approvals (purchase_request_id, reviewer_id, status, review_comments, reviewed_at) VALUES
(1, 3, 'APPROVED', 'Approved for Core Engineering infrastructure onboarding. Budget cleared under CapEx 2026.', DATE_SUB(NOW(), INTERVAL 17 DAY)),
(2, 3, 'APPROVED', 'Approved. Design lab color-accuracy requirements validated.', DATE_SUB(NOW(), INTERVAL 13 DAY)),
(3, 3, 'APPROVED', 'Approved. Infrastructure expansion justified for private cloud virtualization.', DATE_SUB(NOW(), INTERVAL 9 DAY)),
(4, 3, 'APPROVED', 'Approved. Facilities ergonomics refresh endorsed by HR & Operations committee.', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(6, 3, 'APPROVED', 'Approved. Standard infrastructure and consumable replenishment.', DATE_SUB(NOW(), INTERVAL 11 DAY)),
(8, 3, 'REJECTED', 'Non-standard allocation for dev huddle space. Please utilize existing meeting room conference hardware.', DATE_SUB(NOW(), INTERVAL 7 DAY));

-- 11. Seed Purchase Orders
INSERT INTO purchase_orders (id, purchase_request_id, vendor_id, po_number, status, total_amount, expected_delivery_date, actual_delivery_date, created_at) VALUES
(1, 1, 1, 'PO-2026-0001', 'DELIVERED', 577780.00, DATE_SUB(NOW(), INTERVAL 14 DAY), DATE_SUB(NOW(), INTERVAL 12 DAY), DATE_SUB(NOW(), INTERVAL 17 DAY)),
(2, 2, 2, 'PO-2026-0002', 'DELIVERED', 232485.00, DATE_SUB(NOW(), INTERVAL 8 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 13 DAY)),
(3, 3, 2, 'PO-2026-0003', 'ORDERED', 629000.00, DATE_ADD(NOW(), INTERVAL 5 DAY), NULL, DATE_SUB(NOW(), INTERVAL 9 DAY)),
(4, 6, 4, 'PO-2026-0004', 'DELIVERED', 116200.00, DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 11 DAY)),
(5, NULL, 3, 'PO-2026-0005', 'CANCELLED', 165000.00, DATE_SUB(NOW(), INTERVAL 3 DAY), NULL, DATE_SUB(NOW(), INTERVAL 10 DAY));

-- 12. Seed Purchase Order Items
INSERT INTO purchase_order_items (purchase_order_id, product_id, quantity, unit_price) VALUES
(1, 1, 2, 249900.00),
(1, 12, 2, 38990.00),
(2, 5, 3, 68500.00),
(2, 13, 3, 8995.00),
(3, 7, 1, 485000.00),
(3, 8, 2, 72000.00),
(4, 15, 5, 9800.00),
(4, 16, 6, 11200.00),
(5, 4, 1, 165000.00);

-- 13. Seed Transaction Ledger Entries for Delivered POs & Adjustments
INSERT INTO inventory_transactions (product_id, transaction_type, quantity, reference_id, notes) VALUES
(1, 'IN', 2, 1, 'PO-2026-0001 delivery receipt (Apple)'),
(12, 'IN', 2, 1, 'PO-2026-0001 delivery receipt (Apple Partner)'),
(5, 'IN', 3, 2, 'PO-2026-0002 delivery receipt (Dell Technologies)'),
(13, 'IN', 3, 2, 'PO-2026-0002 delivery receipt (Dell Technologies)'),
(15, 'IN', 5, 4, 'PO-2026-0004 delivery receipt (Redington)'),
(16, 'IN', 6, 4, 'PO-2026-0004 delivery receipt (Redington)'),
(15, 'OUT', -1, NULL, 'Damaged transit Cat6 cable drum discarded'),
(13, 'IN', 2, NULL, 'Quarterly warehouse physical count reconciliation');

COMMIT;
