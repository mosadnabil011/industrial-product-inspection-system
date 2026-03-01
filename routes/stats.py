from flask import Blueprint, jsonify
from database.db import get_db
import logging

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/summary", methods=["GET"])
def summary():
    try:
        db = get_db()
        cursor = db.cursor()

        # ========================
        # Count OK / NOT_OK
        # ========================
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN status='OK' THEN 1 ELSE 0 END) as ok_count,
                SUM(CASE WHEN status='NOT_OK' THEN 1 ELSE 0 END) as not_ok_count
            FROM products
        """)

        result = cursor.fetchone()
        ok_count = result[0] or 0
        not_ok_count = result[1] or 0

        # ========================
        # Count per Color
        # ========================
        cursor.execute("""
            SELECT color, COUNT(*) 
            FROM products 
            GROUP BY color
        """)

        color_counts = cursor.fetchall()
        colors = {color: count for color, count in color_counts}

        db.close()

        return jsonify({
            "ok": ok_count,
            "not_ok": not_ok_count,
            "colors": colors
        }), 200

    except Exception as e:
        logging.error(f"Stats Error: {e}")
        return jsonify({
            "error": "Failed to fetch statistics"
        }), 500