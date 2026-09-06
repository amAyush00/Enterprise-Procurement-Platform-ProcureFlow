import io
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from backend.models.vendor import Vendor
from backend.models.product import Product
from backend.models.inventory import Inventory
from backend.models.purchase_order import PurchaseOrder

# Define standard enterprise style helpers for Excel
EXCEL_HEADER_FILL = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
EXCEL_HEADER_FONT = Font(name="Arial", size=11, bold=True, color="FFFFFF")
EXCEL_TEXT_FONT = Font(name="Arial", size=10)
EXCEL_BOLD_FONT = Font(name="Arial", size=10, bold=True)
EXCEL_ALIGN_LEFT = Alignment(horizontal="left", vertical="center")
EXCEL_ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")
EXCEL_ALIGN_CENTER = Alignment(horizontal="center", vertical="center")
EXCEL_THIN_BORDER = Border(
    left=Side(style='thin', color='E5E7EB'),
    right=Side(style='thin', color='E5E7EB'),
    top=Side(style='thin', color='E5E7EB'),
    bottom=Side(style='thin', color='E5E7EB')
)

class ReportService:
    @staticmethod
    def _auto_fit_excel_columns(ws):
        """
        Adjust column widths to fit cell contents cleanly.
        """
        for col in ws.columns:
            max_len = 0
            col_letter = col[0].column_letter
            for cell in col:
                if cell.value is not None:
                    max_len = max(max_len, len(str(cell.value)))
            # Add padding
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    @staticmethod
    def generate_vendors_excel(search=None, status=None):
        wb = Workbook()
        ws = wb.active
        ws.title = "Vendors Catalog"

        # Set title block
        ws.merge_cells("A1:H1")
        ws["A1"] = "ENTERPRISE PROCUREMENT PLATFORM - VENDOR REPORT"
        ws["A1"].font = Font(name="Arial", size=14, bold=True, color="1E293B")
        ws["A1"].alignment = EXCEL_ALIGN_LEFT
        ws.row_dimensions[1].height = 30

        ws["A2"] = f"Generated On: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ws["A2"].font = Font(name="Arial", size=9, italic=True)
        ws.row_dimensions[2].height = 20

        # Headers
        headers = ["ID", "Vendor Name", "Company Name", "GST Number", "Email", "Phone", "Rating", "Status"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col_idx, value=header)
            cell.fill = EXCEL_HEADER_FILL
            cell.font = EXCEL_HEADER_FONT
            cell.alignment = EXCEL_ALIGN_CENTER
            cell.border = EXCEL_THIN_BORDER
        ws.row_dimensions[4].height = 25

        # Query data
        query = Vendor.query
        if status:
            query = query.filter(Vendor.status == status)
        vendors = query.all()

        # Add data rows
        row_idx = 5
        for vendor in vendors:
            ws.cell(row=row_idx, column=1, value=vendor.id).alignment = EXCEL_ALIGN_CENTER
            ws.cell(row=row_idx, column=2, value=vendor.name).alignment = EXCEL_ALIGN_LEFT
            ws.cell(row=row_idx, column=3, value=vendor.company_name).alignment = EXCEL_ALIGN_LEFT
            ws.cell(row=row_idx, column=4, value=vendor.gst_number).alignment = EXCEL_ALIGN_CENTER
            ws.cell(row=row_idx, column=5, value=vendor.email).alignment = EXCEL_ALIGN_LEFT
            ws.cell(row=row_idx, column=6, value=vendor.phone).alignment = EXCEL_ALIGN_CENTER
            ws.cell(row=row_idx, column=7, value=float(vendor.rating)).alignment = EXCEL_ALIGN_RIGHT
            ws.cell(row=row_idx, column=8, value=vendor.status).alignment = EXCEL_ALIGN_CENTER

            # Format fonts and borders
            for col_idx in range(1, 9):
                c = ws.cell(row=row_idx, column=col_idx)
                c.font = EXCEL_TEXT_FONT
                c.border = EXCEL_THIN_BORDER
            ws.row_dimensions[row_idx].height = 20
            row_idx += 1

        ReportService._auto_fit_excel_columns(ws)
        
        # Save to stream
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def generate_inventory_excel(low_stock=False):
        wb = Workbook()
        ws = wb.active
        ws.title = "Inventory Report"

        ws.merge_cells("A1:I1")
        ws["A1"] = "ENTERPRISE PROCUREMENT PLATFORM - INVENTORY STATUS REPORT"
        ws["A1"].font = Font(name="Arial", size=14, bold=True, color="1E293B")
        ws["A1"].alignment = EXCEL_ALIGN_LEFT
        ws.row_dimensions[1].height = 30

        ws["A2"] = f"Generated On: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ws["A2"].font = Font(name="Arial", size=9, italic=True)
        ws.row_dimensions[2].height = 20

        # Headers
        headers = ["Product SKU", "Product Name", "Category", "Current Stock", "Incoming", "Outgoing", "Reorder Level", "Unit Price", "Total Value"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col_idx, value=header)
            cell.fill = EXCEL_HEADER_FILL
            cell.font = EXCEL_HEADER_FONT
            cell.alignment = EXCEL_ALIGN_CENTER
            cell.border = EXCEL_THIN_BORDER
        ws.row_dimensions[4].height = 25

        query = Inventory.query.join(Product)
        if low_stock:
            query = query.filter(Inventory.current_stock <= Product.reorder_level)
        items = query.all()

        row_idx = 5
        for item in items:
            p = item.product
            value = float(p.unit_price * item.current_stock)
            ws.cell(row=row_idx, column=1, value=p.sku).alignment = EXCEL_ALIGN_CENTER
            ws.cell(row=row_idx, column=2, value=p.name).alignment = EXCEL_ALIGN_LEFT
            ws.cell(row=row_idx, column=3, value=p.category.name if p.category else '').alignment = EXCEL_ALIGN_LEFT
            ws.cell(row=row_idx, column=4, value=item.current_stock).alignment = EXCEL_ALIGN_RIGHT
            ws.cell(row=row_idx, column=5, value=item.incoming_stock).alignment = EXCEL_ALIGN_RIGHT
            ws.cell(row=row_idx, column=6, value=item.outgoing_stock).alignment = EXCEL_ALIGN_RIGHT
            ws.cell(row=row_idx, column=7, value=p.reorder_level).alignment = EXCEL_ALIGN_RIGHT
            ws.cell(row=row_idx, column=8, value=float(p.unit_price)).alignment = EXCEL_ALIGN_RIGHT
            ws.cell(row=row_idx, column=9, value=value).alignment = EXCEL_ALIGN_RIGHT

            for col_idx in range(1, 10):
                c = ws.cell(row=row_idx, column=col_idx)
                c.font = EXCEL_TEXT_FONT
                c.border = EXCEL_THIN_BORDER
            ws.row_dimensions[row_idx].height = 20
            row_idx += 1

        # Total summary row
        ws.cell(row=row_idx, column=3, value="Total Inventory Value:").font = EXCEL_BOLD_FONT
        ws.cell(row=row_idx, column=3).alignment = EXCEL_ALIGN_RIGHT
        total_cell = ws.cell(row=row_idx, column=9, value=f"=SUM(I5:I{row_idx-1})")
        total_cell.font = EXCEL_BOLD_FONT
        total_cell.alignment = EXCEL_ALIGN_RIGHT
        total_cell.border = Border(bottom=Side(style='double', color='1E293B'))

        ReportService._auto_fit_excel_columns(ws)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def generate_purchase_orders_excel(status=None):
        wb = Workbook()
        ws = wb.active
        ws.title = "Purchase Orders"

        ws.merge_cells("A1:G1")
        ws["A1"] = "ENTERPRISE PROCUREMENT PLATFORM - PURCHASE ORDERS"
        ws["A1"].font = Font(name="Arial", size=14, bold=True, color="1E293B")
        ws["A1"].alignment = EXCEL_ALIGN_LEFT
        ws.row_dimensions[1].height = 30

        ws["A2"] = f"Generated On: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ws["A2"].font = Font(name="Arial", size=9, italic=True)
        ws.row_dimensions[2].height = 20

        # Headers
        headers = ["PO Number", "Vendor Name", "Status", "Total Amount", "Expected Date", "Actual Date", "Created Date"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col_idx, value=header)
            cell.fill = EXCEL_HEADER_FILL
            cell.font = EXCEL_HEADER_FONT
            cell.alignment = EXCEL_ALIGN_CENTER
            cell.border = EXCEL_THIN_BORDER
        ws.row_dimensions[4].height = 25

        query = PurchaseOrder.query
        if status:
            query = query.filter(PurchaseOrder.status == status)
        orders = query.all()

        row_idx = 5
        for po in orders:
            ws.cell(row=row_idx, column=1, value=po.po_number).alignment = EXCEL_ALIGN_CENTER
            ws.cell(row=row_idx, column=2, value=po.vendor.name).alignment = EXCEL_ALIGN_LEFT
            ws.cell(row=row_idx, column=3, value=po.status).alignment = EXCEL_ALIGN_CENTER
            ws.cell(row=row_idx, column=4, value=float(po.total_amount)).alignment = EXCEL_ALIGN_RIGHT
            ws.cell(row=row_idx, column=5, value=po.expected_delivery_date.strftime('%Y-%m-%d')).alignment = EXCEL_ALIGN_CENTER
            ws.cell(row=row_idx, column=6, value=po.actual_delivery_date.strftime('%Y-%m-%d') if po.actual_delivery_date else '-').alignment = EXCEL_ALIGN_CENTER
            ws.cell(row=row_idx, column=7, value=po.created_at.strftime('%Y-%m-%d')).alignment = EXCEL_ALIGN_CENTER

            for col_idx in range(1, 8):
                c = ws.cell(row=row_idx, column=col_idx)
                c.font = EXCEL_TEXT_FONT
                c.border = EXCEL_THIN_BORDER
            ws.row_dimensions[row_idx].height = 20
            row_idx += 1

        ReportService._auto_fit_excel_columns(ws)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def generate_procurement_report_pdf():
        """
        Generate global procurement status PDF with corporate branding.
        """
        output = io.BytesIO()
        doc = SimpleDocTemplate(
            output, 
            pagesize=letter, 
            rightMargin=40, 
            leftMargin=40, 
            topMargin=40, 
            bottomMargin=40
        )
        story = []

        styles = getSampleStyleSheet()
        
        # Corporate Color Palette styles
        title_style = ParagraphStyle(
            'CorporateTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'CorporateSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#6B7280'),
            spaceAfter=15
        )
        section_heading = ParagraphStyle(
            'CorporateSection',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#2563EB'),
            spaceBefore=12,
            spaceAfter=8
        )
        body_style = ParagraphStyle(
            'CorporateBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#374151')
        )
        
        # Branding Header Bar
        story.append(Paragraph("ENTERPRISE PROCUREMENT PLATFORM", ParagraphStyle('SubBranding', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#2563EB'), spaceAfter=2)))
        story.append(Paragraph("Procurement Operations & Spending Report", title_style))
        story.append(Paragraph(f"Generated On: {datetime.datetime.now().strftime('%B %d, %Y %I:%M %p')} | Scope: Complete Dataset", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563EB'), spaceAfter=15))

        # Recent Purchase Orders Section
        story.append(Paragraph("Recent Purchase Orders", section_heading))
        
        # Build PO table data
        table_data = [["PO Number", "Vendor Name", "Order Date", "Amount", "Status"]]
        orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).limit(15).all()
        for po in orders:
            table_data.append([
                po.po_number,
                po.vendor.name[:25],
                po.created_at.strftime('%Y-%m-%d'),
                f"Rs. {float(po.total_amount):,.2f}",
                po.status
            ])

        # Style Table
        t = Table(table_data, colWidths=[100, 180, 80, 90, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'), # Left align vendor name
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'), # Right align amount
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
        ]))
        story.append(t)

        # Build PDF Document
        doc.build(story)
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def generate_purchase_order_pdf(po_id):
        """
        Generate detailed invoice-quality PDF for a single Purchase Order.
        """
        po = PurchaseOrder.query.get(po_id)
        if not po:
            raise ValueError(f"Purchase Order with ID {po_id} not found.")

        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('POTitle', fontName='Helvetica-Bold', fontSize=24, textColor=colors.HexColor('#1E293B'), spaceAfter=4)
        po_number_style = ParagraphStyle('PONum', fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor('#2563EB'), spaceAfter=15)
        label_bold = ParagraphStyle('LabelBold', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor('#1E293B'))
        label_val = ParagraphStyle('LabelVal', fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#4B5563'))
        
        # 1. Header Block (Company logo/Branding on left, title on right)
        story.append(Paragraph("PURCHASE ORDER", title_style))
        story.append(Paragraph(f"ORDER NO: {po.po_number}", po_number_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E5E7EB'), spaceAfter=15))

        # 2. Metadata Columns (PO Date, Expected Delivery Date, Status)
        meta_table_data = [
            [Paragraph("Order Date:", label_bold), Paragraph(po.created_at.strftime('%B %d, %Y'), label_val),
             Paragraph("Vendor:", label_bold), Paragraph(po.vendor.company_name, label_val)],
            [Paragraph("Expected Date:", label_bold), Paragraph(po.expected_delivery_date.strftime('%B %d, %Y'), label_val),
             Paragraph("Supplier GST:", label_bold), Paragraph(po.vendor.gst_number, label_val)],
            [Paragraph("Status:", label_bold), Paragraph(po.status, label_val),
             Paragraph("Email:", label_bold), Paragraph(po.vendor.email, label_val)]
        ]
        meta_table = Table(meta_table_data, colWidths=[90, 160, 90, 200])
        meta_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 20))

        # 3. Items Table
        items_header_style = ParagraphStyle('ColH', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)
        item_text_style = ParagraphStyle('ColT', fontName='Helvetica', fontSize=9, leading=11, textColor=colors.HexColor('#1E293B'))
        item_num_style = ParagraphStyle('ColN', fontName='Helvetica', fontSize=9, alignment=2, textColor=colors.HexColor('#1E293B')) # Right align
        
        items_table_data = [[
            Paragraph("Item Description", items_header_style),
            Paragraph("SKU", items_header_style),
            Paragraph("Unit Price", items_header_style),
            Paragraph("Qty", items_header_style),
            Paragraph("Total", items_header_style)
        ]]

        for item in po.items:
            items_table_data.append([
                Paragraph(item.product.name, item_text_style),
                Paragraph(item.product.sku, item_text_style),
                Paragraph(f"Rs. {float(item.unit_price):,.2f}", item_num_style),
                Paragraph(str(item.quantity), item_num_style),
                Paragraph(f"Rs. {float(item.unit_price * item.quantity):,.2f}", item_num_style)
            ])

        # Add total row
        items_table_data.append([
            Paragraph("<b>TOTAL AMOUNT (INR):</b>", ParagraphStyle('TotLabel', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#1E293B'))),
            "", "", "",
            Paragraph(f"<b>Rs. {float(po.total_amount):,.2f}</b>", ParagraphStyle('TotVal', fontName='Helvetica-Bold', fontSize=10, alignment=2, textColor=colors.HexColor('#2563EB')))
        ])

        items_table = Table(items_table_data, colWidths=[200, 110, 80, 50, 100])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#E5E7EB')),
            ('SPAN', (0, -1), (3, -1)), # Span total label
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor('#1E293B')), # Bold line above totals
        ]))
        story.append(items_table)
        story.append(Spacer(1, 40))

        # 4. Signature block
        sig_data = [
            [Paragraph("Prepared By", label_bold), Paragraph("Authorized Approval", label_bold)],
            [Spacer(1, 30), Spacer(1, 30)],
            [Paragraph("____________________________", label_val), Paragraph("____________________________", label_val)],
            [Paragraph("Procurement Department", label_val), Paragraph("Finance Director / Manager", label_val)]
        ]
        sig_table = Table(sig_data, colWidths=[270, 270])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ]))
        story.append(sig_table)

        doc.build(story)
        output.seek(0)
        return output.getvalue()
