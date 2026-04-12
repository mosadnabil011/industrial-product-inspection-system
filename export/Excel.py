from flask import send_file
import io
import pandas as pd

@stats_bp.route("/export/excel")
def export_excel():
    db = get_db()
    df = pd.read_sql_query("SELECT * FROM products", db)
    db.close()

    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="production_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )