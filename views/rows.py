"""
rows.py

Blueprint for row-related routes and logic in the SQLFlask application.

This module provides routes for listing, adding, editing, updating, and deleting rows
within the currently selected table of the SQLite database. It also includes
helper functions for retrieving row data.
"""

from flask import Blueprint, render_template, request, g
from views.utils import get_db
import sqlite3

rows_bp = Blueprint('rows', __name__)

@rows_bp.route("/", methods=["GET"])
def index():
    g.context = "Rows"
    db = get_db()
    current_table = g.get("current_table", "details")

    # Check if the table exists
    table_exists = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (current_table,)
    ).fetchone()

    if table_exists:
        rows = db.execute(f"SELECT id, name FROM {current_table} ORDER BY id DESC").fetchall()
    else:
        rows = []    
    
    return render_template(
        "index.html",
        context="Rows",
        current_database=g.get("current_database", "none"),
        current_table=current_table,
        item_list=rows
    )

@rows_bp.route("/add", methods=["POST"])
def add():
    db = get_db()
    current_table = g.get("current_table", "details")
    name = request.form["name"]
    db.execute(f"INSERT INTO {current_table} (name) VALUES (?)", (name,))
    db.commit()
    item_list = db.execute(f"SELECT id, name FROM {current_table} ORDER BY id DESC").fetchall()
    return render_template("_rows.html", item_list=item_list, context="Rows")

@rows_bp.route('/edit/<int:item_id>', methods=['GET'])
def edit_row(item_id):
    db = get_db()
    current_table = g.get("current_table", "details")
    row = db.execute(f"SELECT id, name FROM {current_table} WHERE id = ?", (item_id,)).fetchone()
    return render_template("_edit_form.html", person=row)

@rows_bp.route('/row/update/<int:item_id>', methods=['PUT'])
def update_row(item_id):
    db = get_db()
    current_table = g.get("current_table", "details")
    name = request.form["name"]
    db.execute(f"UPDATE {current_table} SET name = ? WHERE id = ?", (name, item_id))
    db.commit()
    item = db.execute(f"SELECT id, name FROM {current_table} WHERE id = ?", (item_id,)).fetchone()
    return render_template("_row.html", item=item)

@rows_bp.route('/row/delete/<int:item_id>', methods=['DELETE'])
def row_delete(item_id):
    db = get_db()
    current_table = g.get("current_table", "details")
    db.execute(f"DELETE FROM {current_table} WHERE id = ?", (item_id,))
    db.commit()
    item_list = db.execute(f"SELECT id, name FROM {current_table} ORDER BY id DESC").fetchall()
    return render_template("_rows.html", item_list=item_list, context="Rows")