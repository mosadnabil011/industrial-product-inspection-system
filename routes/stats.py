from flask import Blueprint, jsonify
from database.db import get_db

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/summary")
def summary():
    db = get_db()
    cursor = db.cursor()

    # عدد المنتجات السليمة
    cursor.execute("SELECT COUNT(*) FROM products WHERE status='OK'")
    ok_count = cursor.fetchone()[0]

    # عدد المنتجات التالفة
    cursor.execute("SELECT COUNT(*) FROM products WHERE status='NOT_OK'")
    not_ok_count = cursor.fetchone()[0]

    # عدد المنتجات لكل لون
    cursor.execute("SELECT color, COUNT(*) FROM products GROUP BY color")
    color_counts = cursor.fetchall()

    # تحويل النتيجة لقاموس {color: count}
    colors = {color: count for color, count in color_counts}

    db.close()

    # JSON النهائي
    return jsonify({
        "ok": ok_count,
        "not_ok": not_ok_count,
        "colors": colors
    })