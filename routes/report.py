from flask import Blueprint, request, send_file
from database.db import get_db
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io
import matplotlib
matplotlib.use('Agg')  # 👈 ده أهم سطر
import matplotlib.pyplot as plt
import os

report_bp = Blueprint("report", __name__)


@report_bp.route("/report", methods=["GET"])
def generate_report():
    date = request.args.get("date")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT status, created_at
        FROM products
        WHERE DATE(created_at) >= DATE(?)
    """, (date,))

    rows = cursor.fetchall()
    db.close()

    ok = sum(1 for r in rows if r[0] == "OK")
    not_ok = sum(1 for r in rows if r[0] == "NOT_OK")
    total = len(rows)
    defect_rate = (not_ok / total * 100) if total else 0

    # ================== CHART (PIE) ==================
    pie_path = "/tmp/pie.png"

    plt.figure(figsize=(4, 4))
    plt.pie(
        [ok, not_ok],
        labels=["Valid", "Invalid"],
        autopct="%1.1f%%",
        colors=["green", "red"]
    )
    plt.title("Production Distribution")
    plt.savefig(pie_path)
    plt.close()

    # ================== CHART (BAR) ==================
    bar_path = "/tmp/bar.png"

    plt.figure(figsize=(4, 3))
    plt.bar(["Valid", "Invalid"], [ok, not_ok], color=["green", "red"])
    plt.title("Box Status Count")
    plt.savefig(bar_path)
    plt.close()

    # ================== PDF ==================
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    content = []

    # Title
    content.append(Paragraph("Production Report", styles["Title"]))
    content.append(Spacer(1, 12))

    # Info Table
    data = [
        ["Metric", "Value"],
        ["Date From", str(date)],
        ["Total Boxes", total],
        ["Valid", ok],
        ["Invalid", not_ok],
        ["Defect Rate", f"{defect_rate:.2f}%"]
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    content.append(table)
    content.append(Spacer(1, 20))

    # Charts inside PDF
    content.append(Paragraph("Production Charts", styles["Heading2"]))
    content.append(Spacer(1, 10))

    content.append(Image(pie_path, width=250, height=250))
    content.append(Spacer(1, 10))
    content.append(Image(bar_path, width=250, height=200))

    pdf.build(content)

    buffer.seek(0)

    # cleanup images
    os.remove(pie_path)
    os.remove(bar_path)

    return send_file(
        buffer,
        as_attachment=False,
        download_name="production_report.pdf",
        mimetype="application/pdf"
    )
