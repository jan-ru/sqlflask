"""
tables.py

Blueprint for table-related routes and logic in the SQLFlask application.

This module provides routes for listing, creating, renaming, and deleting tables
within the currently selected SQLite database. It also includes helper functions
for retrieving table metadata.
"""

from flask import Blueprint, render_template, request, g, session, redirect, url_for
from views.utils import get_db
import sqlite3

tables_bp = Blueprint('tables', __name__, url_prefix="/tables")

def get_all_tables(db):
    tables = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    ).fetchall()
    return [{"id": idx, "name": table["name"]} for idx, table in enumerate(tables)]

@tables_bp.route("/", methods=["GET", "POST"])
def index():
    g.context = "Tables"
    db = get_db()
    # Always get current_database from session if available
    g.current_database = session.get("current_database", "none")

    # Handle switching the current table
    selected_table = request.args.get("current_table")
    if selected_table:
        g.current_table = selected_table
        session["current_table"] = selected_table
    else:
        g.current_table = session.get("current_table", "details")

    if request.method == "POST":
        table_name = request.form["name"]
        db.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, name TEXT)")
        db.commit()
        g.current_table = table_name
        session["current_table"] = table_name

    tables = get_all_tables(db)
    item_list = tables

    # HTMX partial rendering
    if request.headers.get("HX-Request") == "true":
        return render_template(
            "_rows.html",
            item_list=item_list,
            context="Tables",
            current_database=g.current_database,
            current_table=g.get("current_table", "details"),
        )

    # Full page rendering
    return render_template(
        "index.html",
        context="Tables",
        current_database=g.current_database,
        current_table=g.get("current_table", "details"),
        item_list=item_list
    )

@tables_bp.route("/add", methods=["POST"])
def add():
    db = get_db()
    g.current_database = session.get("current_database", "none")
    table_name = request.form.get("name")
    if not table_name:
        return "Table name is required.", 400
    try:
        db.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, name TEXT)')
        db.commit()
        g.current_table = table_name
        session["current_table"] = table_name
    except sqlite3.OperationalError as e:
        return f"Error: {e}", 400

    tables = get_all_tables(db)
    item_list = tables
    return render_template(
        "_rows.html",
        item_list=item_list,
        context="Tables",
        current_database=g.current_database,
        current_table=g.current_table
    )

tables_bp.route('/select/<table_name>', methods=['GET'])
def select_table(table_name):
    session["current_table"] = table_name
    g.current_table = table_name
    return redirect(url_for('columns.index'))

@tables_bp.route('/edit/<int:table_id>', methods=['GET'])
def edit_table(table_id):
    db = get_db()
    tables = get_all_tables(db)
    if table_id < 0 or table_id >= len(tables):
        return "Table not found", 404
    table = tables[table_id]
    return render_template("_edit_form.html", item=table, context="Tables")

@tables_bp.route('/update/<int:table_id>', methods=['PUT'])
def update_table(table_id):
    db = get_db()
    tables = get_all_tables(db)
    if table_id < 0 or table_id >= len(tables):
        return "Table not found", 404
    old_table_name = tables[table_id]["name"]
    new_table_name = request.form["name"]
    try:
        db.execute(f"ALTER TABLE {old_table_name} RENAME TO {new_table_name}")
        db.commit()
    except sqlite3.OperationalError as e:
        return f"Error: {e}", 400
    tables = get_all_tables(db)
    item_list = tables
    return render_template("_rows.html", item_list=item_list, context="Tables")

@tables_bp.route('/delete/<int:table_id>', methods=['DELETE'])
def table_delete(table_id):
    db = get_db()
    tables = get_all_tables(db)
    if table_id < 0 or table_id >= len(tables):
        return "Table not found", 404
    table_name = tables[table_id]["name"]
    db.execute(f"DROP TABLE IF EXISTS {table_name}")
    db.commit()
    tables = get_all_tables(db)
    item_list = tables
    return render_template("_rows.html", item_list=item_list, context="Tables")