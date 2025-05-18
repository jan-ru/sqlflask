"""
columns.py

Blueprint for column-related routes and logic in the SQLFlask application.

This module provides routes for listing, adding, renaming, and deleting columns
within the currently selected table of the SQLite database. It also includes
helper functions for retrieving column metadata.
"""

from flask import Blueprint, render_template, request, g
from views.utils import get_db
import sqlite3

columns_bp = Blueprint('columns', __name__, url_prefix="/columns")

def get_all_columns(db, table):
    columns = db.execute(f"PRAGMA table_info({table})").fetchall()
    return [{"id": col["cid"], "name": col["name"]} for col in columns]

@columns_bp.route("/", methods=["GET", "POST"])
def index():
    g.context = "Columns"
    db = get_db()
    current_table = g.get("current_table", "details")

    if request.method == "POST":
        column_name = request.form.get("name")
        if not column_name:
            return "Column name is required.", 400
        try:
            db.execute(f'ALTER TABLE {current_table} ADD COLUMN "{column_name}" TEXT')
            db.commit()
        except sqlite3.OperationalError as e:
            return f"Error: {e}", 400

    columns = get_all_columns(db, current_table)
    item_list = columns
    return render_template(
        "index.html",
        context="Columns",
        current_database=g.get("current_database", "none"),
        current_table=current_table,
        item_list=item_list
    )

@columns_bp.route('/update/<int:column_id>', methods=['PUT'])
def update_column(column_id):
    db = get_db()
    current_table = g.get("current_table", "details")
    new_name = request.form["name"]
    columns = db.execute(f"PRAGMA table_info({current_table})").fetchall()
    column = next((col for col in columns if col["cid"] == column_id), None)
    if not column:
        return "Column not found", 404
    old_name = column["name"]
    try:
        db.execute(f'ALTER TABLE {current_table} RENAME COLUMN "{old_name}" TO "{new_name}"')
        db.commit()
    except sqlite3.OperationalError as e:
        return f"Error: {e}", 400
    columns = get_all_columns(db, current_table)
    item_list = columns
    return render_template("_rows.html", item_list=item_list, context="Columns")

@columns_bp.route('/delete/<int:column_id>', methods=['DELETE'])
def column_delete(column_id):
    db = get_db()
    current_table = g.get("current_table", "details")
    columns = db.execute(f"PRAGMA table_info({current_table})").fetchall()
    column = next((col for col in columns if col["cid"] == column_id), None)
    if not column:
        return "Column not found", 404
    column_name = column["name"]
    try:
        db.execute(f'ALTER TABLE {current_table} DROP COLUMN "{column_name}"')
        db.commit()
    except sqlite3.OperationalError as e:
        return f"Error: {e}", 400
    columns = get_all_columns(db, current_table)
    item_list = columns
    return render_template("_rows.html", item_list=item_list, context="Columns")