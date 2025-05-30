"""
sqlflask.py

Main application entry point for the SQLFlask project.

This module initializes the Flask app, configures global settings,
registers blueprints for modular route handling, and manages
application-wide context and session logic.
"""

import sentry_sdk
from flask import Flask, session, render_template, request, g, send_from_directory, Blueprint
from .views.databases import database_bp
from .views.tables import tables_bp
from .views.columns import columns_bp
from .views.relationships import relationships_bp
from .views.data_entry import data_entry_bp
from .views.utils import get_db
from .config import DB_PATH, EXCEL_DIR
import sqlite3
import tomllib
import os


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    traces_sample_rate=0.1,
    environment="production",
)

app = Flask(__name__)
app.config["DB_PATH"] = str(DB_PATH)  # <-- including db (file) name 
app.config["DATA_DIR"] = str(DB_PATH.parent)  # <-- excluding db (file) name
app.secret_key = os.urandom(24)

app.register_blueprint(database_bp)
app.register_blueprint(tables_bp)
app.register_blueprint(columns_bp)
app.register_blueprint(relationships_bp)
app.register_blueprint(data_entry_bp)


def get_project_metadata():
    pyproject_path = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    project = data.get("project", {})
    return {
        "project_name": project.get("name", ""),
        "project_version": project.get("version", ""),
    }

@app.context_processor
def inject_project_metadata():
    return get_project_metadata()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.before_request
def set_initial_context():
    if not hasattr(g, "context"):
        g.context = "None"  # Default context
    g.current_database = session.get("current_database", "none")  # Load from session
    g.current_table = "None"  # Default table

@app.after_request
def save_context(response):
    session["current_database"] = g.get("current_database", "None")  # Save to session
    return response

@app.route("/")
def index():
    db = get_db()
    current_database = g.current_database
    current_table = g.current_table

    # Check if the 'details' table exists
    table_exists = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='details';"
    ).fetchone()

    # Check if the 'name' column exists in the 'details' table
    name_column_exists = False
    if table_exists:
        columns = db.execute("PRAGMA table_info(details)").fetchall()
        name_column_exists = any(col["name"] == "name" for col in columns)

    if table_exists and name_column_exists:
        details = db.execute("SELECT id, name FROM details ORDER BY id DESC").fetchall()
    else:
        details = []

    return render_template(
        "index.html",
        context="Rows",
        current_database=current_database,
        current_table=current_table,
        details=details
)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

if __name__ == "__main__":
    
    with sqlite3.connect(app.config["DB_PATH"]) as db:
        db.execute("CREATE TABLE IF NOT EXISTS details (id INTEGER PRIMARY KEY, name TEXT)")
    # Get port number from environment variable or use default
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
