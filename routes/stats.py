from flask import Blueprint, jsonify
from database.db import get_db
import logging

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/summary", methods=["GET"])
def summary():
    db = None
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

        return jsonify({
            "ok": ok_count,
            "not_ok": not_ok_count,
            "colors": colors
        }), 200

    except Exception as e:
        logging.exception(f"Stats Error: {e}")
        return jsonify({
            "error": "Failed to fetch statistics"
        }), 500
    finally:
        if db:
            db.close()

        
@stats_bp.route("/monthly", methods=["GET"])
def monthly_stats():
    db = None
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT 
    strftime('%Y-%m', created_at) as month,
    SUM(CASE WHEN status='OK' THEN 1 ELSE 0 END) as ok,
    SUM(CASE WHEN status='NOT_OK' THEN 1 ELSE 0 END) as not_ok
FROM products
WHERE created_at IS NOT NULL
GROUP BY month
ORDER BY month ASC
        """)

        rows = cursor.fetchall()

        months = []
        ok_data = []
        not_ok_data = []

        for row in rows:
            months.append(row[0])
            ok_data.append(row[1] or 0)
            not_ok_data.append(row[2] or 0)

        return jsonify({
            "months": months,
            "valid": ok_data,
            "invalid": not_ok_data
        })

    except Exception as e:
        logging.exception(f"Monthly Stats Error: {e}")
        return jsonify({"error": "failed"}), 500
    finally:
        if db:
            db.close()
    

@stats_bp.route("/weekly", methods=["GET"])
def weekly_stats():
    db = None
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT 
                strftime('%Y', created_at) || '-W' || 
                printf('%02d', CAST(strftime('%W', created_at) AS INTEGER)) as week,

                SUM(CASE WHEN status='OK' THEN 1 ELSE 0 END) as valid,
                SUM(CASE WHEN status='NOT_OK' THEN 1 ELSE 0 END) as invalid

            FROM products

            WHERE created_at IS NOT NULL

            GROUP BY week
            ORDER BY week ASC
        """)

        rows = cursor.fetchall()

        weeks = []
        valid = []
        invalid = []

        for row in rows:
            # weeks.append(f"Week {row[0]}")
            weeks.append(row[0])
            valid.append(row[1] or 0)
            invalid.append(row[2] or 0)

        return jsonify({
            "weeks": weeks,
            "valid": valid,
            "invalid": invalid
        })

    except Exception as e:
        logging.exception(f"Weekly Stats Error: {e}")
        return jsonify({
            "error": "failed"
        }), 500
    finally:
        if db:
            db.close()
    
