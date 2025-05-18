"""
utils.py

Utility functions for the SQLFlask application.

This module provides shared helper functions, such as get_db(),
which manages the SQLite database connection for use throughout
the application and its blueprints.
"""

from flask import g
import sqlite3

def get_db():
    # You may want to import this from a shared utils.py
    db = getattr(g, "_database", None)
    if db is None:
        from sqlflask import DATABASE  # or set DATABASE in config
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db
