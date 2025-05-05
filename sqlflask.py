# app.py
from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)
DATABASE = "db.sqlite"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    db = get_db()
    rows = db.execute("SELECT id, name FROM people ORDER BY id DESC").fetchall()
    return render_template("index.html", rows=rows)

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    db = get_db()
    db.execute("INSERT INTO people (name) VALUES (?)", (name,))
    db.commit()
    rows = db.execute("SELECT id, name FROM people ORDER BY id DESC").fetchall()
    return render_template("_rows.html", rows=rows)

if __name__ == "__main__":
    # Init DB if needed
    with sqlite3.connect(DATABASE) as db:
        db.execute("CREATE TABLE IF NOT EXISTS people (id INTEGER PRIMARY KEY, name TEXT)")
    app.run(debug=True)
