from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
import io

@stats_bp.route("/export/pdf")
def export_pdf():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT status, color FROM products")
    rows = cursor.fetchall()
    db.close()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Production Report", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    data = [["Status", "Color"]] + rows
    table = Table(data)
    table.setStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ])

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="production_report.pdf",
        mimetype="application/pdf"
    )