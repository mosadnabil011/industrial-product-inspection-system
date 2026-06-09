from flask import Blueprint, request, send_file
from database.db import get_db
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
from datetime import datetime

report_bp = Blueprint("report", __name__)
colorGood = "#1abc9c";
colorBad = "#ffaf32";  

# ─── Brand Colors ──────────────────────────────────────────────────────────
DARK_BLUE = colors.HexColor("#0D1B2A")
MID_BLUE = colors.HexColor("#1B4F72")
ACCENT_BLUE = colors.HexColor("#2E86C1")
LIGHT_GRAY = colors.HexColor("#F2F4F7")
GREEN = colors.HexColor(colorGood)
RED = colors.HexColor(colorBad)
WHITE = colors.white
TEXT_DARK = colors.HexColor("#1A1A2E")


# ─── Branded Canvas (Header + Footer) ─────────────────────────────────────
class BrandedCanvas(canvas.Canvas):

    def __init__(self, *args, report_date=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.report_date = report_date or datetime.now().strftime("%Y-%m-%d")
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            self._draw_page_decorations(i + 1, num_pages)
            super().showPage()
        super().save()

    def _draw_page_decorations(self, page_num, total_pages):
        W, H = A4

        # Header
        self.setFillColor(DARK_BLUE)
        self.rect(0, H - 60, W, 60, fill=1, stroke=0)
        self.setFillColor(ACCENT_BLUE)
        self.rect(0, H - 64, W, 4, fill=1, stroke=0)

        self.setFillColor(WHITE)
        self.setFont("Helvetica-Bold", 18)
        self.drawString(30, H - 38, "FORCE")
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#A9CCE3"))
        self.drawString(30, H - 52, "Production Quality Control System")
        self.setFillColor(WHITE)
        self.setFont("Helvetica", 9)
        self.drawRightString(W - 30, H - 38, f"Report Date: {self.report_date}")
        self.drawRightString(W - 30, H - 52,
                             f"Generated: {datetime.now().strftime('%d %b %Y  %H:%M')}")

        # Footer
        self.setFillColor(DARK_BLUE)
        self.rect(0, 0, W, 38, fill=1, stroke=0)
        self.setFillColor(ACCENT_BLUE)
        self.rect(0, 38, W, 2, fill=1, stroke=0)
        self.setFillColor(WHITE)
        self.setFont("Helvetica-Bold", 9)
        self.drawString(30, 15, "FORCE - Confidential Internal Report")
        self.setFont("Helvetica", 9)
        self.drawRightString(W - 30, 15, f"Page {page_num} of {total_pages}")


# ─── Charts ────────────────────────────────────────────────────────────────
def make_pie(ok, not_ok, path):
    fig, ax = plt.subplots(figsize=(4.5, 4.5), facecolor="white")
    vals = [ok, not_ok] if (ok + not_ok) > 0 else [1, 0]
    wedge_props = dict(width=0.55, edgecolor="white", linewidth=2)
    wedges, texts, autotexts = ax.pie(
        vals, labels=None, autopct="%1.1f%%",
        startangle=90, wedgeprops=wedge_props,
        colors=[colorGood, colorBad], pctdistance=0.75,
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(11)
        at.set_fontweight("bold")
    ax.set_title("Quality Distribution", fontsize=13, fontweight="bold", pad=14)
    patches = [
        mpatches.Patch(color=colorGood, label=f"Valid  ({ok})"),
        mpatches.Patch(color=colorBad, label=f"Invalid ({not_ok})"),
    ]
    ax.legend(handles=patches, loc="lower center",
              bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False, fontsize=10)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


# def make_bar(ok, not_ok, path):
#     fig, ax = plt.subplots(figsize=(5, 3.5), facecolor="white")
#     bars = ax.bar(["Valid", "Invalid"], [ok, not_ok],
#                   color=[colorGood, colorBad], width=0.45,
#                   edgecolor="white", linewidth=1.2)
#     for bar, val in zip(bars, [ok, not_ok]):
#         ax.text(bar.get_x() + bar.get_width() / 2,
#                 bar.get_height() + 0.3, str(val),
#                 ha="center", va="bottom", fontweight="bold", fontsize=12)
#     ax.set_title("Box Status Count", fontsize=13, fontweight="bold", pad=10)
#     ax.set_ylabel("Units", fontsize=10)
#     ax.spines[["top", "right"]].set_visible(False)
#     ax.yaxis.grid(True, linestyle="--", alpha=0.4)
#     ax.set_axisbelow(True)
#     plt.tight_layout()
#     plt.savefig(path, dpi=150, bbox_inches="tight")
#     plt.close()

def make_bar(months, ok_data, not_ok_data, path):
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="white")

    x = range(len(months))
    width = 0.35

    bars1 = ax.bar(
        [i - width/2 for i in x],
        ok_data,
        width=width,
        label="Valid",
        color=colorGood
    )

    bars2 = ax.bar(
        [i + width/2 for i in x],
        not_ok_data,
        width=width,
        label="Invalid",
        color=colorBad
    )

    # كتابة الأرقام فوق الأعمدة
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2,
                height + 0.2,
                str(int(height)),
                ha='center',
                va='bottom',
                fontsize=9,
                fontweight='bold'
            )

    # أسماء الشهور
    month_names = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    labels = [month_names[int(m)-1] for m in months]

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)

    ax.set_title("Monthly Production Statistics",
                 fontsize=14,
                 fontweight="bold",
                 pad=12)

    ax.set_ylabel("Units")

    ax.legend()

    ax.spines[["top", "right"]].set_visible(False)

    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
# ─── Route ─────────────────────────────────────────────────────────────────
@report_bp.route("/report", methods=["GET"])
def generate_report():
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))

    db = get_db()
    cursor = db.cursor()

    # cursor.execute("""
    #     SELECT status, created_at
    #     FROM products
    #     WHERE created_at >= ?
    # """, (date,))

    # rows = cursor.fetchall()

    cursor.execute("""
        SELECT 
            strftime('%m', created_at) as month,
            COALESCE(SUM(CASE WHEN status='OK' THEN 1 ELSE 0 END), 0) as ok,
            COALESCE(SUM(CASE WHEN status='NOT_OK' THEN 1 ELSE 0 END), 0) as not_ok
        FROM products
        WHERE created_at >= ?
        GROUP BY month
        ORDER BY month
    """, (date,))

    rows = cursor.fetchall()

    months = []
    ok_data = []
    not_ok_data = []

    for row in rows:
        months.append(row[0])
        ok_data.append(row[1])
        not_ok_data.append(row[2])
        
    db.close()

    # ok = sum(1 for r in rows if r[0] == "OK")
    # not_ok = sum(1 for r in rows if r[0] == "NOT_OK")
    # total = len(rows)
    
    ok = sum(ok_data)
    not_ok = sum(not_ok_data)
    total = ok + not_ok
    
    defect_rate = (not_ok / total * 100) if total else 0
    pass_rate = (ok / total * 100) if total else 0

    # Charts
    pie_path = "/tmp/force_pie.png"
    bar_path = "/tmp/force_bar.png"
    make_pie(ok, not_ok, pie_path)
    # make_bar(ok, not_ok, bar_path)
    make_bar(months, ok_data, not_ok_data, bar_path)

    # PDF setup
    buffer = io.BytesIO()
    W, H = A4
    margin = 2 * cm

    def canvas_factory(*args, **kwargs):
        return BrandedCanvas(*args, report_date=date, **kwargs)

    pdf = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=80, bottomMargin=55,
    )

    styles = getSampleStyleSheet()

    style_section = ParagraphStyle(
        "SH", parent=styles["Heading2"],
        fontSize=13, textColor=MID_BLUE,
        spaceBefore=18, spaceAfter=6, leading=16,
    )
    style_body = ParagraphStyle(
        "BD", parent=styles["Normal"],
        fontSize=10, textColor=TEXT_DARK, leading=15,
    )
    style_small = ParagraphStyle(
        "SM", parent=styles["Normal"],
        fontSize=8.5, textColor=colors.HexColor("#6C6C6C"), leading=12,
    )
    style_sig_name = ParagraphStyle(
        "SN", parent=styles["Normal"],
        fontSize=14, textColor=DARK_BLUE, fontName="Helvetica-Bold",
    )
    style_sig_sub = ParagraphStyle(
        "SS", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#555555"),
    )

    content = []

    # ── Title ──
    content.append(Spacer(1, 6))
    content.append(Paragraph("Production Quality Report", ParagraphStyle(
        "BT", parent=styles["Title"],
        fontSize=22, textColor=DARK_BLUE, spaceAfter=4,
    )))
    content.append(Paragraph(
        f"Period starting: <b>{date}</b> &nbsp;|&nbsp; Total inspected units: <b>{total}</b>",
        style_body,
    ))
    content.append(HRFlowable(width="100%", thickness=2,
                               color=ACCENT_BLUE, spaceAfter=14))

    # ── KPI Cards ──

    content.append(Paragraph("Key Performance Indicators", style_section))

    kpi_items = [
        ("Total Units", str(total), "#0D1B2A"),
        ("Valid Units", str(ok), colorGood),
        ("Invalid Units", str(not_ok), colorBad),
        ("Pass Rate", f"{pass_rate:.1f}%", colorGood),
        ("Defect Rate", f"{defect_rate:.1f}%", colorBad),
    ]

    kpi_row = []
    for label, value, hex_color in kpi_items:
        cell_para = Paragraph(
            f'<para align="center">'
            f'<font name="Helvetica-Bold" size="20" color="{hex_color}">{value}</font>'
            f'<br/>'
            f'<font name="Helvetica" size="8" color="#666666">{label}</font>'
            f'</para>',
            styles["Normal"],
        )
        kpi_row.append(cell_para)

    kpi_table = Table([kpi_row], colWidths=[(W - 2 * margin) / 5] * 5)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5D8DC")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5D8DC")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))
    content.append(kpi_table)
    content.append(Spacer(1, 18))

    # ── Detailed Stats ──
    content.append(Paragraph("Detailed Statistics", style_section))

    detail_rows = [
        ["Metric", "Value", "Status"],
        ["Inspection Start Date", str(date), "-"],
        ["Total Boxes Scanned", str(total), "-"],
        ["Valid Boxes", str(ok), "Pass"],
        ["Invalid Boxes", str(not_ok), "Fail"],
        ["Pass Rate", f"{pass_rate:.2f}%", "Good" if pass_rate >= 90 else "Review"],
        ["Defect Rate", f"{defect_rate:.2f}%", "Good" if defect_rate < 10 else "High"],
    ]

    col_w = [(W - 2 * margin) * f for f in (0.45, 0.30, 0.25)]
    det_table = Table(detail_rows, colWidths=col_w)
    det_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("FONTSIZE", (0, 1), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 1), (-1, -1), TEXT_DARK),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFC9CA")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (2, 3), (2, 3), GREEN),
        ("TEXTCOLOR", (2, 4), (2, 4), RED),
        ("FONTNAME", (2, 3), (2, 4), "Helvetica-Bold"),
    ]))
    content.append(det_table)
    content.append(Spacer(1, 22))

    # ── Charts ──
    content.append(Paragraph("Visual Analysis", style_section))
    chart_table = Table(
        [[Image(pie_path, width=220, height=220),
          Image(bar_path, width=260, height=200)]],
        colWidths=[240, 270],
    )
    chart_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5D8DC")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    content.append(chart_table)
    content.append(Spacer(1, 30))

    # ── Signature ──
    content.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor("#BFC9CA"), spaceAfter=12))
    sig_data = [
        [Paragraph("Authorized By:", style_small), Paragraph("", style_small)],
        [Paragraph("FORCE", style_sig_name),
         Paragraph(
             f"<i>Production Quality Control Division</i><br/>"
             f"<i>Report ID: FORCE-{datetime.now().strftime('%Y%m%d-%H%M')}</i>",
             style_sig_sub,
         )],
        [Paragraph("_______________________________", style_small),
         Paragraph(f"Date: {datetime.now().strftime('%d %B %Y')}",
                   ParagraphStyle("DR", parent=style_small, alignment=2))],
    ]
    sig_table = Table(sig_data, colWidths=[(W - 2 * margin) * 0.5] * 2)
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    content.append(sig_table)

    # ── Build ──
    pdf.build(content, canvasmaker=canvas_factory)
    buffer.seek(0)

    os.remove(pie_path)
    os.remove(bar_path)

    return send_file(
        buffer,
        as_attachment=False,
        download_name=f"FORCE_Production_Report_{date}.pdf",
        mimetype="application/pdf",
    )
