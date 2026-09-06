from sqlalchemy import or_
from backend.app import db
from backend.models.vendor import Vendor

class VendorService:
    @staticmethod
    def get_all_vendors(search=None, status=None, sort_by='name', sort_order='asc', page=1, per_page=10):
        """
        Fetch vendors using filtering, search, sorting, and pagination.
        """
        query = Vendor.query

        # 1. Filtering by Status
        if status:
            query = query.filter(Vendor.status == status)

        # 2. Searching across fields
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Vendor.name.like(search_pattern),
                    Vendor.company_name.like(search_pattern),
                    Vendor.email.like(search_pattern)
                )
            )

        # 3. Sorting
        sort_attr = getattr(Vendor, sort_by, Vendor.name)
        if sort_order == 'desc':
            query = query.order_by(sort_attr.desc())
        else:
            query = query.order_by(sort_attr.asc())

        # 4. Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'vendors': [vendor.to_dict() for vendor in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        }

    @staticmethod
    def get_vendor_by_id(vendor_id):
        """
        Fetch single vendor by ID.
        """
        return Vendor.query.get(vendor_id)

    @staticmethod
    def create_vendor(data):
        """
        Create a new vendor. Performs unique constraints validations.
        """
        gst = data.get('gst_number')
        email = data.get('email')

        # Check unique constraint violations
        if Vendor.query.filter_by(gst_number=gst).first():
            raise ValueError(f"GST Number '{gst}' is already registered to another vendor.")
        
        if Vendor.query.filter_by(email=email).first():
            raise ValueError(f"Email '{email}' is already in use by another vendor.")

        vendor = Vendor(
            name=data.get('name'),
            company_name=data.get('company_name'),
            gst_number=gst,
            email=email,
            phone=data.get('phone'),
            address=data.get('address'),
            rating=data.get('rating', 5.00),
            status=data.get('status', 'ACTIVE')
        )

        db.session.add(vendor)
        db.session.commit()
        return vendor

    @staticmethod
    def update_vendor(vendor_id, data):
        """
        Update an existing vendor.
        """
        vendor = Vendor.query.get(vendor_id)
        if not vendor:
            return None

        # Check unique constraints if values are changing
        gst = data.get('gst_number')
        if gst and gst != vendor.gst_number:
            if Vendor.query.filter_by(gst_number=gst).first():
                raise ValueError(f"GST Number '{gst}' is already registered to another vendor.")
            vendor.gst_number = gst

        email = data.get('email')
        if email and email != vendor.email:
            if Vendor.query.filter_by(email=email).first():
                raise ValueError(f"Email '{email}' is already in use by another vendor.")
            vendor.email = email

        vendor.name = data.get('name', vendor.name)
        vendor.company_name = data.get('company_name', vendor.company_name)
        vendor.phone = data.get('phone', vendor.phone)
        vendor.address = data.get('address', vendor.address)
        vendor.rating = data.get('rating', vendor.rating)
        vendor.status = data.get('status', vendor.status)

        db.session.commit()
        return vendor

    @staticmethod
    def delete_vendor(vendor_id):
        """
        Delete a vendor from database, or raise violation error if products are linked.
        """
        vendor = Vendor.query.get(vendor_id)
        if not vendor:
            return False

        # Restrict deletion if vendor has products
        if len(vendor.products) > 0:
            raise ValueError("Cannot delete vendor: active products are linked to this supplier. Mark as INACTIVE instead.")

        db.session.delete(vendor)
        db.session.commit()
        return True
