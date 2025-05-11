# sqlflask.py
from flask import Flask, render_template, request, g, send_from_directory
import sqlite3
import os

if not os.path.exists("./data"):
    os.makedirs("./data")

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
    current_database = "current_database.sqlite"  # Replace with logic to get the current database
    current_table = "details"  # Replace with logic to get the current table
    details = db.execute("SELECT id, name FROM details ORDER BY id DESC").fetchall()
    return render_template(
        "index.html",
        context="Rows",
        current_database=current_database,
        current_table=current_table,
        details=details
)

@app.route("/databases", methods=["GET", "POST"])
def databases():
    if request.method == "POST":
        database_name = request.form.get("name")
        if not database_name:
            return "Database name is required.", 400
        
        # Logic to create a new database (e.g., create a new SQLite file)
        try:
            sqlite3.connect(f"./data/{database_name}.sqlite").close()
        except Exception as e:
            return f"Error: {e}", 400

    # Dynamically fetch the list of databases from the filesystem
    databases = [
        {"id": idx, "name": db} for idx, db in enumerate(os.listdir("./data")) if db.endswith(".sqlite")
    ]
    return render_template(
        "index.html",
        context="Databases",
        current_database=None,  # No database selected in this context
        current_table=None,  # No table selected in this context
        item_list=databases
    )

@app.route("/tables", methods=["GET", "POST"])
def tables():
    db = get_db()
    db_name = db.execute("PRAGMA database_list").fetchone()[2]
    if request.method == "POST":
        table_name = request.form["name"]
        # Create a new table in the current database
        db.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, name TEXT)")
        db.commit()
        g.current_table = table_name  # Set the current table in the request context
    else:
        g.current_table = request.args.get("current_table", "details")  # Default to "details"

    # Query to get all table names in the database
    tables = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
    ).fetchall()
    
    # Transform tables into a list of dictionaries with id and name
    item_list = [{"id": idx, "name": table["name"]} for idx, table in enumerate(tables)]
    return render_template(
        "index.html",
        context="Tables",
        current_database=db_name,
        current_table=None,  # No table selected in this context
        item_list=item_list
    )

@app.route("/columns", methods=["GET", "POST"])
def columns():
    db = get_db()
    g.current_table = request.args.get("current_table", "details")  # Default to "details"
    current_database = "current_database.sqlite"  # Replace with logic to get the current database

    if request.method == "POST":
        column_name = request.form.get("name")
        
        # Validate form data
        if not column_name:
            return "Column name is required.", 400
        
        # Add the column to the specified table
        try:
            db.execute(f"ALTER TABLE {g.current_table} ADD COLUMN {column_name} TEXT")
            db.commit()
        except sqlite3.OperationalError as e:
            return f"Error: {e}", 400

    # Fetch updated columns for the table
    columns = db.execute(f"PRAGMA table_info({g.current_table})").fetchall()
    # Transform columns into a list of dictionaries with id and name
    item_list = [{"id": column["cid"], "name": column["name"]} for column in columns]
    return render_template(
        "index.html",
        context="Columns",
        current_database=current_database,
        current_table=g.current_table,
        item_list=item_list,
    )

@app.route("/fields")
def fields():
    db = get_db()
    current_table = g.get("current_table", "details")
    if request.method == "POST":
        field_name = request.form.get("field_name")
        db.execute(f"ALTER TABLE {current_table} ADD COLUMN {field_name} TEXT")
        db.commit()
    fields = db.execute(f"PRAGMA table_info({current_table})").fetchall()
    return render_template(
        "index.html",
        context="Fields",
        item_list=[field["name"] for field in fields]
    )

@app.route("/tabulator")
def show_table():
    return render_template("tabulator.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    db = get_db()
    db.execute("INSERT INTO details (name) VALUES (?)", (name,))
    db.commit()
    item_list = db.execute("SELECT id, name FROM details ORDER BY id DESC").fetchall()
    return render_template("_rows.html", item_list=item_list)

@app.route('/edit/<int:person_id>', methods=['GET'])
def edit_person(person_id):
    db = get_db()
    person = db.execute("SELECT id, name FROM details WHERE id = ?", (person_id,)).fetchone()
    return render_template("_edit_form.html", person=person)

@app.route('/update/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    name = request.form["name"]
    db = get_db()
    db.execute("UPDATE details SET name = ? WHERE id = ?", (name, person_id))
    db.commit()

    # Fetch the updated record to replace the row
    person = db.execute("SELECT id, name FROM details WHERE id = ?", (person_id,)).fetchone()
    return render_template("_rows.html", item_list=[person])

@app.route("/row/<int:person_id>")
def row(person_id):
    db = get_db()
    person = db.execute("SELECT id, name FROM details WHERE id = ?", (person_id,)).fetchone()
    return render_template("_row.html", person=person)

@app.route('/delete/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    db = get_db()
    db.execute("DELETE FROM details WHERE id = ?", (person_id,))
    db.commit()

    # Fetch updated list of details
    item_list = db.execute("SELECT id, name FROM details ORDER BY id DESC").fetchall()
    return render_template('_rows.html', item_list=item_list)

if __name__ == "__main__":
    # Init DB if needed
    with sqlite3.connect(DATABASE) as db:
        db.execute("CREATE TABLE IF NOT EXISTS details (id INTEGER PRIMARY KEY, name TEXT)")
    app.run(debug=True)
