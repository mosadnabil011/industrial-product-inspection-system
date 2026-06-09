from flask import Blueprint, request, send_file
from database.db import get_db

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable,
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

import io
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

VALID_COLOR = "#001A2B"
INVALID_COLOR = "#FF5A2A"

# =========================================================
# Blueprint
# =========================================================

report_bp = Blueprint("report", __name__)

# =========================================================
# COLORS
# =========================================================

PRIMARY = colors.HexColor("#061826")
ACCENT = colors.HexColor("#E94E2E")

LIGHT_BG = colors.HexColor("#F4F6F7")

TEXT = colors.HexColor("#1F2933")

GREEN = colors.HexColor("#1abc9c")
ORANGE = colors.HexColor("#ffaf32")

WHITE = colors.white

# =========================================================
# HEADER / FOOTER
# =========================================================


class DashboardCanvas(canvas.Canvas):

    def __init__(self, *args, report_date=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.report_date = report_date

        self.pages = []

    def showPage(self):

        self.pages.append(dict(self.__dict__))

        self._startPage()

    def save(self):

        total_pages = len(self.pages)

        for page_num, state in enumerate(self.pages, start=1):

            self.__dict__.update(state)

            self.draw_layout(page_num, total_pages)

            super().showPage()

        super().save()

    def draw_layout(self, page_num, total_pages):

        W, H = A4

        # ================= HEADER =================

        self.setFillColor(PRIMARY)

        self.rect(0, H - 75, W, 75, fill=1, stroke=0)

        self.setFillColor(ACCENT)

        self.rect(0, H - 80, W, 5, fill=1, stroke=0)

        self.setFillColor(WHITE)

        self.setFont("Helvetica-Bold", 20)

        self.drawString(30, H - 40, "FORCE")

        self.setFont("Helvetica-Bold", 16)

        self.drawString(120, H - 40, "Monthly Production Report")

        self.setFont("Helvetica", 9)

        self.drawString(
            120,
            H - 55,
            "Production Monitoring & Quality Dashboard"
        )

        self.drawRightString(
            W - 30,
            H - 40,
            f"Date : {self.report_date}"
        )

        self.drawRightString(
            W - 30,
            H - 55,
            datetime.now().strftime("%d %b %Y  %H:%M")
        )

        # ================= FOOTER =================

        self.setFillColor(PRIMARY)

        self.rect(0, 0, W, 28, fill=1, stroke=0)

        self.setFillColor(ACCENT)

        self.rect(0, 28, W, 2, fill=1, stroke=0)

        self.setFillColor(WHITE)

        self.setFont("Helvetica", 8)

        self.drawString(
            25,
            10,
            "FORCE - Production Quality Control System"
        )

        self.drawRightString(
            W - 25,
            10,
            f"Page {page_num}/{total_pages}"
        )

# =========================================================
# KPI CARD
# =========================================================


def create_card(title, value, color):

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title",
        parent=styles["Normal"],
        fontSize=7,
        textColor=colors.gray,
        alignment=TA_CENTER,
    )

    value_style = ParagraphStyle(
        "value",
        parent=styles["Normal"],
        fontSize=16,
        textColor=color,
        alignment=TA_CENTER,
        leading=18,
    )

    card = Table(
        [
            [Paragraph(f"<b>{value}</b>", value_style)],
            [Paragraph(title, title_style)],
        ],
        colWidths=3.1 * cm,
        rowHeights=[0.8 * cm, 0.6 * cm],
    )

    card.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, -1), WHITE),

        ("BOX", (0, 0), (-1, -1), 1,
         colors.HexColor("#D6DBDF")),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("TOPPADDING", (0, 0), (-1, -1), 4),

        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),

    ]))

    return card

# =========================================================
# SECTION TITLE
# =========================================================


def section_title(text):

    styles = getSampleStyleSheet()

    style = ParagraphStyle(
        "section",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=PRIMARY,
        spaceBefore=6,
        spaceAfter=6,
    )

    return Paragraph(f"<b>{text}</b>", style)

# =========================================================
# PIE CHART
# =========================================================


def make_pie(ok, not_ok, path, defect_rate):

    fig, ax = plt.subplots(figsize=(3.5, 3.5))

    values = [ok, not_ok] if (ok + not_ok) > 0 else [1, 0]

    ax.pie(
        values,

        startangle=90,

        colors=[VALID_COLOR, INVALID_COLOR ],

        wedgeprops={
            "width": 0.35,
            "edgecolor": "white",
            "linewidth": 2,
        },
    )

    ax.text(
        0,
        0,
        f"{defect_rate:.1f}%\nDefect",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
    )

    ax.legend(
        [
            mpatches.Patch(color=VALID_COLOR),
            mpatches.Patch(color=INVALID_COLOR),
        ],
        [
            f"Valid ({ok})",
            f"Invalid ({not_ok})",
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.1),
        ncol=2,
        frameon=False,
        fontsize=8,
    )

    ax.set_title(
        "Quality Distribution",
        fontsize=11,
        fontweight="bold",
    )

    plt.tight_layout()

    plt.savefig(path, dpi=300, bbox_inches="tight")

    plt.close()

# =========================================================
# BAR CHART
# =========================================================


def make_bar(months, ok_data, not_ok_data, path):

    fig, ax = plt.subplots(figsize=(8, 4))

    x = range(len(months))

    width = 0.5

    bars1 = ax.bar(
        [i - width / 2 for i in x],
        ok_data,
        width=width,
        label="Valid",
        color=VALID_COLOR ,
    )

    bars2 = ax.bar(
        [i + width / 2 for i in x],
        not_ok_data,
        width=width,
        label="Invalid",
        color=INVALID_COLOR ,
    )

    month_names = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    labels = [month_names[int(m) - 1] for m in months]

    ax.set_xticks(list(x))

    ax.set_xticklabels(labels, fontsize=8)

    for bars in [bars1, bars2]:

        for bar in bars:

            h = bar.get_height()

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + 0.2,
                str(int(h)),
                ha="center",
                fontsize=7,
                fontweight="bold",
            )

    ax.set_title(
        "Monthly Statistics",
        fontsize=11,
        fontweight="bold",
    )

    ax.spines[["top", "right"]].set_visible(False)

    ax.yaxis.grid(True, linestyle="--", alpha=0.3)

    ax.legend(fontsize=7)

    plt.tight_layout()

    plt.savefig(path, dpi=300, bbox_inches="tight")

    plt.close()

# =========================================================
# REPORT ROUTE
# =========================================================


@report_bp.route("/report", methods=["GET"])
def generate_report():

    date = request.args.get(
        "date",
        datetime.now().strftime("%Y-%m-%d")
    )

    db = get_db()

    cursor = db.cursor()

    cursor.execute("""

        SELECT

            strftime('%m', created_at) as month,

            COALESCE(
                SUM(CASE WHEN status='OK' THEN 1 ELSE 0 END),
                0
            ) as ok,

            COALESCE(
                SUM(CASE WHEN status='NOT_OK' THEN 1 ELSE 0 END),
                0
            ) as not_ok

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

    ok = sum(ok_data)

    not_ok = sum(not_ok_data)

    total = ok + not_ok

    pass_rate = (ok / total * 100) if total else 0

    defect_rate = (not_ok / total * 100) if total else 0

    # =====================================================
    # CHARTS
    # =====================================================

    pie_path = "/tmp/force_pie.png"

    bar_path = "/tmp/force_bar.png"

    make_pie(ok, not_ok, pie_path, defect_rate)

    make_bar(months, ok_data, not_ok_data, bar_path)

    # =====================================================
    # PDF
    # =====================================================

    buffer = io.BytesIO()

    margin = 1.2 * cm

    def canvas_factory(*args, **kwargs):

        return DashboardCanvas(
            *args,
            report_date=date,
            **kwargs
        )

    pdf = SimpleDocTemplate(
        buffer,

        pagesize=A4,

        leftMargin=margin,
        rightMargin=margin,

        topMargin=80,
        bottomMargin=35,
    )

    styles = getSampleStyleSheet()

    body_style = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        fontSize=9,
        textColor=TEXT,
        leading=13,
    )

    content = []

    # =====================================================
    # TITLE
    # =====================================================

    content.append(
        Paragraph(
            "<b>Production Summary Dashboard</b>",
            ParagraphStyle(
                "title",
                parent=styles["Title"],
                fontSize=18,
                textColor=PRIMARY,
            )
        )
    )

    content.append(Spacer(1, 0.15 * cm))

    content.append(
        Paragraph(
            f"""
            Production quality analysis and inspection statistics
            generated automatically from the FORCE system.

            <br/><br/>

            <b>Start Date:</b> {date}
            """,
            body_style
        )
    )

    content.append(Spacer(1, 0.25 * cm))

    # =====================================================
    # KPI
    # =====================================================

    content.append(section_title("Production KPIs"))

    kpi_table = Table([
        [
            create_card("Total", total, PRIMARY),

            create_card("Valid", ok, GREEN),

            create_card("Invalid", not_ok, ORANGE),

            create_card("Pass Rate", f"{pass_rate:.1f}%", GREEN),

            create_card("Defect", f"{defect_rate:.1f}%", ORANGE),
        ]
    ])

    content.append(kpi_table)

    content.append(Spacer(1, 0.2 * cm))

    # =====================================================
    # DETAILS TABLE
    # =====================================================

    content.append(section_title("Monthly Production Sheet"))

    details = [

        ["Metric", "Value", "Status"],

        ["Total Units", str(total), "Completed"],

        ["Valid Units", str(ok), "PASS"],

        ["Invalid Units", str(not_ok), "FAIL"],

        [
            "Quality Rate",
            f"{pass_rate:.1f}%",
            "GOOD" if pass_rate >= 90 else "REVIEW",
        ],
    ]

    table = Table(
        details,
        colWidths=[6.5 * cm, 4 * cm, 4 * cm],
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),

        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            WHITE,
            LIGHT_BG
        ]),

        ("GRID", (0, 0), (-1, -1), 0.5,
         colors.HexColor("#D5D8DC")),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),

        ("TOPPADDING", (0, 0), (-1, 0), 6),

        ("FONTSIZE", (0, 0), (-1, -1), 8),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

    ]))

    content.append(table)

    content.append(Spacer(1, 0.25 * cm))

    # =====================================================
    # CHARTS
    # =====================================================

    content.append(section_title("Visual Analysis"))

    chart_table = Table(

        [[
            Image(pie_path, width=180, height=180),

            Image(bar_path, width=240, height=170),
        ]],

        colWidths=[8 * cm, 9 * cm]
    )

    chart_table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),

        ("BOX", (0, 0), (-1, -1), 0.5,
         colors.HexColor("#D5D8DC")),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("TOPPADDING", (0, 0), (-1, -1), 6),

        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),

        ("LEFTPADDING", (0, 0), (-1, -1), 10),

        ("RIGHTPADDING", (0, 0), (-1, -1), 10),

    ]))

    content.append(chart_table)

    content.append(Spacer(1, 0.35 * cm))

    # =====================================================
    # FOOTER SIGN
    # =====================================================

    content.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor("#D6DBDF")
    ))

    content.append(Spacer(1, 0.15 * cm))

    content.append(
        Paragraph(
            f"""
            <b>FORCE Production Quality Control Division</b>

            <br/><br/>

            Generated Automatically :
            {datetime.now().strftime("%d %B %Y - %H:%M")}
            """,
            body_style
        )
    )

    # =====================================================
    # BUILD PDF
    # =====================================================

    pdf.build(
        content,
        canvasmaker=canvas_factory
    )

    buffer.seek(0)

    # =====================================================
    # REMOVE TEMP FILES
    # =====================================================

    os.remove(pie_path)

    os.remove(bar_path)

    # =====================================================
    # RETURN PDF
    # =====================================================

    return send_file(
        buffer,

        as_attachment=False,

        download_name=f"FORCE_Report_{date}.pdf",

        mimetype="application/pdf",
    )
