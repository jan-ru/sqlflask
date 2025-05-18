"""
databases.py

Blueprint for database-related routes and logic in the SQLFlask application.

This module provides routes for listing, creating, editing, updating, and deleting SQLite database files.
It also includes helper functions for retrieving database metadata.
"""

from flask import Blueprint, render_template, request, g, session, redirect, url_for
import os
import sqlite3

database_bp = Blueprint('database', __name__, url_prefix="/databases")

def get_all_databases():
    return [
        {"id": idx, "name": db}
        for idx, db in enumerate(os.listdir("./data"))
        if db.endswith(".sqlite")
    ]

@database_bp.route("/", methods=["GET"])
def index():
    g.context = "Databases"
    databases = get_all_databases()
    if request.headers.get("HX-Request") == "true":
        # HTMX request: return only the rows partial
        return render_template(
            "_rows.html",
            item_list=databases,
            context="Databases"
        )
    return render_template(
        "index.html",
        context="Databases",
        current_database=g.get("current_database", "none"),
        current_table=g.get("current_table", "None"),
        item_list=databases
    )

@database_bp.route("/add", methods=["POST"])
def add():
    database_name = request.form.get("name")
    if not database_name:
        return "Database name is required.", 400
    try:
        sqlite3.connect(f"./data/{database_name}.sqlite").close()
    except Exception as e:
        return f"Error: {e}", 400
    databases = get_all_databases()
    return render_template(
        "_rows.html",
        item_list=databases,
        context="Databases"
    )

@database_bp.route('/select/<db_name>', methods=['GET'])
def select_database(db_name):
    session["current_database"] = db_name
    g.current_database = db_name
    # Redirect to the appropriate view, e.g., tables
    return redirect(url_for('tables.index'))

@database_bp.route('/edit/<int:db_id>', methods=['GET'])
def edit(db_id):
    databases = get_all_databases()
    db = next((d for d in databases if d["id"] == db_id), None)
    if not db:
        return "Database not found", 404
    return render_template("_edit_form.html", item=db, context="Databases")

@database_bp.route('/update/<int:db_id>', methods=['PUT'])
def update(db_id):
    databases = get_all_databases()
    db = next((d for d in databases if d["id"] == db_id), None)
    if not db:
        return "Database not found", 404
    old_name = db["name"]
    new_name = request.form["name"]
    old_path = os.path.join("./data", old_name)
    new_path = os.path.join("./data", new_name)
    if not os.path.exists(old_path):
        return f"Database {old_name} does not exist.", 404
    if os.path.exists(new_path):
        return f"Database {new_name} already exists.", 400
    os.rename(old_path, new_path)
    databases = get_all_databases()
    return render_template(
        "_rows.html",
        item_list=databases,
        context="Databases"
    )

@database_bp.route('/delete/<int:db_id>', methods=['DELETE'])
def delete(db_id):
    databases = get_all_databases()
    db = next((d for d in databases if d["id"] == db_id), None)
    if not db:
        return f"Database with id {db_id} does not exist.", 404
    db_path = os.path.join("./data", db["name"])
    if os.path.exists(db_path):
        os.remove(db_path)
    else:
        return f"Database {db['name']} does not exist.", 404
    databases = get_all_databases()
    return render_template(
        "_rows.html",
        item_list=databases,
        context="Databases"
    )