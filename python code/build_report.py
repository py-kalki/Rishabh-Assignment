"""Builds RetailMart_Sales_Report.pdf (run build_notebook.py first so charts/ exists)."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table,
                                TableStyle, PageBreak, ListFlowable, ListItem)
from insights import INSIGHTS, RECOMMENDATIONS

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=20, spaceAfter=4)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=colors.HexColor("#1F4E79"), spaceBefore=10)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10.5, leading=15)
CAP = ParagraphStyle("CAP", parent=B, fontSize=9, textColor=colors.grey, alignment=1)
SUB = ParagraphStyle("SUB", parent=B, alignment=1, textColor=colors.HexColor("#444444"))

def table(data, widths, header_color="#1F4E79"):
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_color)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FA")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t

def img(path, w):
    from PIL import Image as PI
    iw, ih = PI.open(path).size
    return Image(path, width=w, height=w * ih / iw)

def bullets(items):
    return ListFlowable([ListItem(Paragraph(f"<b>{t}.</b> {b}", B), leftIndent=12) for t, b in items],
                        bulletType="1", leftIndent=14)

s = []
s += [Paragraph("RetailMart Sales Analysis", H1),
      Paragraph("Python Mini Project – Short Report", SUB),
      Paragraph("BBA III Semester | Data Analysis using Python (BBADSE26303D) | IPS Academy, IBMR Indore", SUB),
      Spacer(1, 6),
      Paragraph("Submitted by: ____________________ &nbsp;&nbsp; Roll No: ________ &nbsp;&nbsp; Date: ________", SUB),
      Spacer(1, 10)]

s += [Paragraph("1. Objective", H2),
      Paragraph("This report analyses one year of RetailMart sales data (April 2025 – March 2026) using Python "
                "(pandas, matplotlib, seaborn). We want to know where sales come from, what customers buy, "
                "how sales change through the year and how satisfied customers are, and then give the owner "
                "practical advice.", B)]

s += [Paragraph("2. Data Cleaning", H2),
      Paragraph("The raw file had 510 rows and 11 columns. The steps below made it ready for analysis:", B),
      Spacer(1, 4),
      table([["Problem found", "Action taken", "Result"],
             ["10 duplicate rows", "Removed with drop_duplicates()", "500 rows"],
             ["8 rows with quantity = -1", "Kept only rows with quantity > 0", "492 rows"],
             ["City names in mixed case\n(indore, INDORE, Indore …)", "Converted to Title Case", "14 spellings → 5 cities"],
             ["20 missing customer ratings", "Filled with median rating (3.0)", "0 missing"],
             ["12 missing payment modes", "Filled with mode (UPI)", "0 missing"],
             ["order_date stored as text", "Converted with pd.to_datetime()", "Month column added"]],
            [5.6 * cm, 6.2 * cm, 4.4 * cm]),
      Spacer(1, 4),
      Paragraph("The final clean dataset has <b>492 valid orders</b> with no missing values.", B)]

s += [Paragraph("3. Key Metrics", H2),
      Paragraph("Net sales for each order = quantity × unit price × (1 − discount% / 100).", B),
      Spacer(1, 4),
      table([["Total Net Sales", "Total Orders", "Avg Order Value", "Unique Customers", "Avg Rating"],
             ["Rs 13,33,288", "492", "Rs 2,710", "168", "2.98 / 5"]],
            [3.4 * cm, 2.8 * cm, 3.3 * cm, 3.6 * cm, 3.1 * cm], "#2E86AB"),
      PageBreak()]

s += [Paragraph("4. Analysis by City, Category, Month & Product", H2),
      table([["City", "Net Sales (Rs)", "Orders", "Share", "Avg Rating"],
             ["Indore", "5,70,145", "214", "42.8%", "2.96"],
             ["Bhopal", "3,04,109", "111", "22.8%", "2.91"],
             ["Ujjain", "1,80,568", "61", "13.5%", "3.36"],
             ["Jabalpur", "1,57,077", "63", "11.8%", "2.79"],
             ["Dewas", "1,21,388", "43", "9.1%", "2.95"]],
            [3.5 * cm, 3.5 * cm, 2.5 * cm, 2.5 * cm, 2.8 * cm]),
      Spacer(1, 6),
      img("charts/1_city_sales.png", 13.5 * cm),
      Paragraph("Chart 1: Net sales by city", CAP), Spacer(1, 6),
      table([["Category", "Net Sales (Rs)", "Orders", "Share", "Avg Rating"],
             ["Electronics", "4,73,083", "111", "35.5%", "2.88"],
             ["Home & Kitchen", "3,59,182", "77", "26.9%", "3.38"],
             ["Clothing", "2,97,215", "102", "22.3%", "3.01"],
             ["Groceries", "1,21,991", "146", "9.1%", "2.80"],
             ["Beauty", "81,817", "56", "6.1%", "3.02"]],
            [3.5 * cm, 3.5 * cm, 2.5 * cm, 2.5 * cm, 2.8 * cm]),
      PageBreak()]

s += [img("charts/2_category_share.png", 8.5 * cm),
      Paragraph("Chart 2: Category share of net sales", CAP), Spacer(1, 6),
      img("charts/3_monthly_trend.png", 16 * cm),
      Paragraph("Chart 3: Monthly net sales trend – peak in September, lowest in January", CAP), Spacer(1, 8),
      Paragraph("<b>Top 5 products by net sales</b>", B), Spacer(1, 3),
      table([["#", "Product", "Category", "Net Sales (Rs)", "Units"],
             ["1", "Mixer Grinder", "Home & Kitchen", "1,89,438", "87"],
             ["2", "Smart Watch", "Electronics", "1,65,809", "72"],
             ["3", "Bluetooth Speaker", "Electronics", "1,45,989", "89"],
             ["4", "Dinner Set", "Home & Kitchen", "1,11,051", "76"],
             ["5", "Power Bank", "Electronics", "98,204", "82"]],
            [1 * cm, 4 * cm, 3.6 * cm, 3.2 * cm, 2 * cm]),
      PageBreak()]

s += [img("charts/4_ratings.png", 11.5 * cm),
      Paragraph("Chart 4: Customer rating distribution – 181 of 492 orders rated 1 or 2 stars", CAP), Spacer(1, 6),
      img("charts/5_heatmap.png", 15.5 * cm),
      Paragraph("Chart 5: City × Category heatmap (Rs '000)", CAP), Spacer(1, 6),
      img("charts/6_products_payment.png", 16 * cm),
      Paragraph("Chart 6: Top 5 products and payment mode usage", CAP),
      PageBreak()]

s += [Paragraph("5. Key Insights", H2), bullets(INSIGHTS),
      Paragraph("6. Recommendations for the Owner", H2), bullets(RECOMMENDATIONS),
      Paragraph("7. Conclusion", H2),
      Paragraph("RetailMart earned about <b>Rs 13.3 lakh</b> from 492 orders and 168 customers. Most of this "
                "came from Indore, from Electronics and Home & Kitchen, and from the June–October season. "
                "The biggest weakness is customer satisfaction, since more than one in three orders was "
                "rated poorly. If the owner improves service quality, prepares for peak months and uses "
                "smarter offers in slow months and smaller cities, RetailMart can grow both sales and "
                "customer loyalty next year.", B),
      Spacer(1, 8),
      Paragraph("<i>Tools used: Python 3, pandas, NumPy, matplotlib, seaborn, Jupyter Notebook.</i>", CAP)]

def footer(c, d):
    c.setFont("Helvetica", 8); c.setFillColor(colors.grey)
    c.drawString(2 * cm, 1.2 * cm, "RetailMart Sales Analysis – Python Mini Project")
    c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {d.page}")

SimpleDocTemplate("RetailMart_Sales_Report.pdf", pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                  topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                  title="RetailMart Sales Analysis").build(s, onFirstPage=footer, onLaterPages=footer)
print("PDF written")
