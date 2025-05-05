# app.py
from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)
DATABASE = "./data/db.sqlite"

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
    people = db.execute("SELECT id, name FROM people ORDER BY id DESC").fetchall()
    return render_template("index.html", people=people)

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    db = get_db()
    db.execute("INSERT INTO people (name) VALUES (?)", (name,))
    db.commit()
    people = db.execute("SELECT id, name FROM people ORDER BY id DESC").fetchall()
    return render_template("_rows.html", people=people)

@app.route('/edit/<int:person_id>', methods=['GET'])
def edit_person(person_id):
    db = get_db()
    person = db.execute("SELECT id, name FROM people WHERE id = ?", (person_id,)).fetchone()
    return render_template("_edit_form.html", person=person)

@app.route('/update/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    name = request.form["name"]
    db = get_db()
    db.execute("UPDATE people SET name = ? WHERE id = ?", (name, person_id))
    db.commit()

    # Fetch the updated record to replace the row
    person = db.execute("SELECT id, name FROM people WHERE id = ?", (person_id,)).fetchone()
    return render_template("_rows.html", people=[person])

@app.route("/row/<int:person_id>")
def row(person_id):
    db = get_db()
    person = db.execute("SELECT id, name FROM people WHERE id = ?", (person_id,)).fetchone()
    return render_template("_row.html", person=person)

@app.route('/delete/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    db = get_db()
    db.execute("DELETE FROM people WHERE id = ?", (person_id,))
    db.commit()

    # Fetch updated list of people
    people = db.execute("SELECT id, name FROM people ORDER BY id DESC").fetchall()
    return render_template('_rows.html', people=people)

if __name__ == "__main__":
    # Init DB if needed
    with sqlite3.connect(DATABASE) as db:
        db.execute("CREATE TABLE IF NOT EXISTS people (id INTEGER PRIMARY KEY, name TEXT)")
    app.run(debug=True)
