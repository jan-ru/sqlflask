"""
sqlflask.py

Main application entry point for the SQLFlask project.

This module initializes the Flask app, configures global settings,
registers blueprints for modular route handling, and manages
application-wide context and session logic.
"""

from flask import Flask, session, render_template, request, g, send_from_directory, Blueprint
from views.databases import database_bp
from views.tables import tables_bp
from views.columns import columns_bp
from views.rows import rows_bp
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = "./data/db.sqlite"

# Ensure the data directory exists
if not os.path.exists("./data"):
    os.makedirs("./data")

app.register_blueprint(database_bp)
app.register_blueprint(tables_bp)
app.register_blueprint(columns_bp)
app.register_blueprint(rows_bp)

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
    current_table = "details"  # Replace with logic to get the current table
    details = db.execute("SELECT id, name FROM details ORDER BY id DESC").fetchall()
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
    
    # Init DB if needed
    with sqlite3.connect(DATABASE) as db:
        db.execute("CREATE TABLE IF NOT EXISTS details (id INTEGER PRIMARY KEY, name TEXT)")
    # Get port number from environment variable or use default
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)