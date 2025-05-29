"""
columns.py

Blueprint for column-related routes and logic in the SQLFlask application.

This module provides routes for listing, adding, renaming, and deleting columns
within the currently selected table of the SQLite database. It also includes
helper functions for retrieving column metadata.
"""

from flask import Blueprint, render_template, request, g, session, redirect, url_for
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
    # Restore current_database and current_table from session if present
    g.current_database = session.get("current_database", "none")
    g.current_table = session.get("current_table", "details")
    current_table = g.current_table

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

    # HTMX partial rendering
    if request.headers.get("HX-Request") == "true":
        return render_template(
            "_rows.html",
            item_list=item_list,
            context="Columns",
            current_database=g.current_database,
            current_table=current_table,
        )

    # Full page rendering
    return render_template(
        "index.html",
        context="Columns",
        current_database=g.current_database,
        current_table=current_table,
        item_list=item_list
    )

@columns_bp.route("/add", methods=["POST"])
def add():
    db = get_db()
    g.current_database = session.get("current_database", "none")
    g.current_table = session.get("current_table", "details")
    current_table = g.current_table
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
        "_rows.html",
        item_list=item_list,
        context="Columns",
        current_database=g.current_database,
        current_table=current_table
    )

@columns_bp.route('/select/<column_name>', methods=['GET'])
def select_column(column_name):
    session["current_column"] = column_name
    g.current_column = column_name
    return redirect(url_for('rows.index'))

@columns_bp.route('/edit/<int:column_id>', methods=['GET'])
def edit_column(column_id):
    db = get_db()
    g.current_database = session.get("current_database", "none")
    g.current_table = session.get("current_table", "details")
    current_table = g.current_table
    columns = db.execute(f"PRAGMA table_info({current_table})").fetchall()
    column = next((col for col in columns if col["cid"] == column_id), None)
    if not column:
        return "Column not found", 404
    item = {"id": column["cid"], "name": column["name"]}
    return render_template("_edit_form.html", item=item, context="Columns")

@columns_bp.route('/update/<int:column_id>', methods=['PUT'])
def update_column(column_id):
    db = get_db()
    g.current_database = session.get("current_database", "none")
    g.current_table = session.get("current_table", "details")
    current_table = g.current_table
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
    g.current_database = session.get("current_database", "none")
    g.current_table = session.get("current_table", "details")
    current_table = g.current_table
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