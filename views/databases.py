"""
databases.py

Blueprint for database-related routes and logic in the SQLFlask application.

This module provides routes for listing, creating, renaming, and deleting SQLite database files.
It also includes helper functions for retrieving database metadata.
"""
from flask import Blueprint, render_template, request, g, session
import os
import sqlite3

database_bp = Blueprint('database', __name__, url_prefix="/databases")

def get_all_databases():
    return [
        {"id": idx, "name": db}
        for idx, db in enumerate(os.listdir("./data"))
        if db.endswith(".sqlite")
    ]

@database_bp.route("/", methods=["GET", "POST"])
def index():
    g.context = "Databases"
    if request.method == "POST":
        database_name = request.form.get("name")
        if not database_name:
            return "Database name is required.", 400
        try:
            sqlite3.connect(f"./data/{database_name}.sqlite").close()
        except Exception as e:
            return f"Error: {e}", 400

    selected_database = request.args.get("db")
    if selected_database:
        g.current_database = selected_database
        session["current_database"] = selected_database

    databases = get_all_databases()
    return render_template(
        "index.html",
        context="Databases",
        current_database=g.get("current_database", "none"),
        current_table=g.get("current_table", "None"),
        item_list=databases
    )

@database_bp.route('/delete/<db_name>', methods=['DELETE'])
def database_delete(db_name):
    db_path = os.path.join("./data", db_name)
    print("Trying to delete:", db_path)
    print("Exists?", os.path.exists(db_path))
    if os.path.exists(db_path):
        os.remove(db_path)
    else:
        return f"Database {db_name} does not exist.", 404
    updated_databases = get_all_databases()
    return render_template(
        "_rows.html",
        item_list=updated_databases,
        context="Databases"
    )

@database_bp.route('/update/<db_name>', methods=['PUT'])
def update_database(db_name):
    new_name = request.form["name"]
    old_path = os.path.join("./data", db_name)
    new_path = os.path.join("./data", new_name)
    if not os.path.exists(old_path):
        return f"Database {db_name} does not exist.", 404
    if os.path.exists(new_path):
        return f"Database {new_name} already exists.", 400
    os.rename(old_path, new_path)
    updated_databases = get_all_databases()
    return render_template(
        "_rows.html", 
        item_list=updated_databases, 
        context="Databases")