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

        
@stats_bp.route("/monthly", methods=["GET"])
def monthly_stats():
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT 
    strftime('%m', created_at) as month,
    COALESCE(SUM(CASE WHEN status='OK' THEN 1 ELSE 0 END), 0) as ok,
    COALESCE(SUM(CASE WHEN status='NOT_OK' THEN 1 ELSE 0 END), 0) as not_ok
FROM products
GROUP BY month
ORDER BY month
        """)

        rows = cursor.fetchall()

        months = []
        ok_data = []
        not_ok_data = []

        for row in rows:
            months.append(row[0])
            ok_data.append(row[1])
            not_ok_data.append(row[2])

        db.close()

        return jsonify({
            "months": months,
            "valid": ok_data,
            "invalid": not_ok_data
        })

    except Exception as e:
        logging.error(f"Monthly Stats Error: {e}")
        return jsonify({"error": "failed"}), 500


@stats_bp.route("/weekly", methods=["GET"])
def weekly_stats():

    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT 
                strftime('%W', created_at) as week,

                COALESCE(SUM(
                    CASE WHEN status='OK' THEN 1 ELSE 0 END
                ),0) as valid,

                COALESCE(SUM(
                    CASE WHEN status='NOT_OK' THEN 1 ELSE 0 END
                ),0) as invalid

            FROM products
            GROUP BY week
            ORDER BY week
        """)

        rows = cursor.fetchall()

        weeks = []
        valid = []
        invalid = []

        for row in rows:
            weeks.append(f"Week {row[0]}")
            valid.append(row[1])
            invalid.append(row[2])

        db.close()

        return jsonify({
            "weeks": weeks,
            "valid": valid,
            "invalid": invalid
        })

    except Exception as e:
        logging.error(f"Weekly Stats Error: {e}")
        return jsonify({
            "error": "failed"
        }), 500
