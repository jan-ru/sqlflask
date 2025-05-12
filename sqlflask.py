# sqlflask.py
from flask import Flask, session, render_template, request, g, send_from_directory
import sqlite3
import os


if not os.path.exists("./data"):
    os.makedirs("./data")

app = Flask(__name__)
DATABASE = "./data/db.sqlite"

app.secret_key = os.urandom(24)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        g.current_database = os.path.basename(DATABASE)  # Set the current database name
        session["current_database"] = g.current_database  # Update the session
    db.row_factory = sqlite3.Row
    return db

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

@app.route("/databases", methods=["GET", "POST"])
def databases():
    g.context = "Databases"  # Update context to "Databases"
    if request.method == "POST":
        database_name = request.form.get("name")
        if not database_name:
            return "Database name is required.", 400
        
        # Logic to create a new database (e.g., create a new SQLite file)
        try:
            sqlite3.connect(f"./data/{database_name}.sqlite").close()
        except Exception as e:
            return f"Error: {e}", 400

    # Handle switching the current database
    selected_database = request.args.get("db")
    if selected_database:
        DATABASE = f"./data/{selected_database}"  # Update the global DATABASE variable
        g.current_database = selected_database
        session["current_database"] = selected_database

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
    g.context = "Tables"  # Update context to "Tables"
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
    g.context = "Columns"  # Set the context to "Columns"
    current_database = g.current_database
    current_table = g.current_table
    db = get_db()

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
    item_list = [{"id": column["cid"], "name": column["name"]} for column in columns]
    return render_template(
        "index.html",
        context="Columns",
        current_database=current_database,
        current_table=g.current_table,
        item_list=item_list,
    )

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

@app.route('/edit/<int:item_id>', methods=['GET'])
def edit_person(item_id):
    db = get_db()
    person = db.execute("SELECT id, name FROM details WHERE id = ?", (item_id,)).fetchone()
    return render_template("_edit_form.html", person=person)

@app.route('/update/<int:item_id>', methods=['PUT'])
def update_person(item_id):
    name = request.form["name"]
    db = get_db()
    db.execute("UPDATE details SET name = ? WHERE id = ?", (name, item_id))
    db.commit()

    # Fetch the updated record to replace the row
    person = db.execute("SELECT id, name FROM details WHERE id = ?", (item_id,)).fetchone()
    return render_template("_rows.html", item_list=[person])

@app.route("/row/<int:item_id>")
def row(item_id):
    db = get_db()

    if g.context == "Databases":
        # Fetch the list of databases
        databases = [
            {"id": idx, "name": db} for idx, db in enumerate(os.listdir("./data")) if db.endswith(".sqlite")
        ]

        # Find the database by ID
        item = next((db for db in databases if db["id"] == item_id), None)
        if not item:
            return "Database not found", 404

    elif g.context == "Tables":
        # Fetch the list of tables
        tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        ).fetchall()
        item = {"id": item_id, "name": tables[item_id]["name"]} if item_id < len(tables) else None
        if not item:
            return "Table not found", 404

    elif g.context == "Columns":
        # Fetch the list of columns for the current table
        columns = db.execute(f"PRAGMA table_info({g.current_table})").fetchall()
        item = {"id": columns[item_id]["cid"], "name": columns[item_id]["name"]} if item_id < len(columns) else None
        if not item:
            return "Column not found", 404

    elif g.context == "Rows":
        # Fetch the row from the current table
        item = db.execute("SELECT id, name FROM details WHERE id = ?", (item_id,)).fetchone()
        if not item:
            return "Row not found", 404

    else:
        return "Invalid context", 400

    # Render the appropriate row template
    return render_template("_row.html", item=item)

@app.route('/delete/<int:item_id>', methods=['DELETE'])
def delete_person(item_id):
    db = get_db()

    # Handle deletion based on the current context
    if g.context == "Rows":
        db.execute("DELETE FROM details WHERE id = ?", (item_id,))
        db.commit()
        item_list = db.execute("SELECT id, name FROM details ORDER BY id DESC").fetchall()
        return render_template("_rows.html", item_list=item_list)

    elif g.context == "Columns":
        db.execute(f"ALTER TABLE {g.current_table} DROP COLUMN {item_id}")  # Example logic
        db.commit()
        columns = db.execute(f"PRAGMA table_info({g.current_table})").fetchall()
        item_list = [{"id": column["cid"], "name": column["name"]} for column in columns]
        return render_template("_columns.html", item_list=item_list)

    elif g.context == "Tables":
        db.execute(f"DROP TABLE {item_id}")  # Example logic
        db.commit()
        tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        ).fetchall()
        item_list = [{"id": idx, "name": table["name"]} for idx, table in enumerate(tables)]
        return render_template("_tables.html", item_list=item_list)

    elif g.context == "Databases":
        # Fetch the list of databases
        databases = [
            {"id": idx, "name": db} for idx, db in enumerate(os.listdir("./data")) if db.endswith(".sqlite")
        ]

        # Find the database name by id
        database_to_delete = next((db for db in databases if db["id"] == item_id), None)
        if not database_to_delete:
            return f"Database with id {item_id} not found.", 404

        # Delete the database file
        db_path = f"./data/{database_to_delete['name']}"
        if os.path.exists(db_path):
            os.remove(db_path)
        else:
            return f"Database {database_to_delete['name']} does not exist.", 404

        # Fetch the updated list of databases
        updated_databases = [
            {"id": idx, "name": db} for idx, db in enumerate(os.listdir("./data")) if db.endswith(".sqlite")
        ]
        return render_template("_databases.html", item_list=updated_databases)

    return "Invalid context", 400

if __name__ == "__main__":
    # Init DB if needed
    with sqlite3.connect(DATABASE) as db:
        db.execute("CREATE TABLE IF NOT EXISTS details (id INTEGER PRIMARY KEY, name TEXT)")
    app.run(debug=True)
