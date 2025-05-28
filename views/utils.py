"""
utils.py

Utility functions for the SQLFlask application.

This module provides shared helper functions, such as get_db(),
which manages the SQLite database connection for use throughout
the application and its blueprints.
"""

from flask import g, session, current_app
import sqlite3
import os

def get_db():
    db = getattr(g, "_database", None)
    db_name = session.get("current_database", "db.sqlite")
    db_path = os.path.join(current_app.config["DATA_DIR"], db_name)
    try:
        # Ensure the data directory exists
        data_dir = current_app.config["DATA_DIR"]
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        # Try to connect to the database
        if db is None or getattr(g, "_db_path", None) != db_path:
            if db is not None:
                db.close()
            if not os.path.exists(db_path):
                # Optionally, create the database file if it doesn't exist
                open(db_path, "a").close()
            db = sqlite3.connect(db_path)
            db.row_factory = sqlite3.Row
            g._database = db
            g._db_path = db_path
        return db
    except sqlite3.OperationalError as e:
        # Handle database connection errors gracefully
        raise RuntimeError(f"Unable to open database file '{db_path}': {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error opening database file '{db_path}': {e}")