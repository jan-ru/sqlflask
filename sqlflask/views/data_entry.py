from flask import Blueprint, render_template, request, redirect, url_for
from .utils import get_db

data_entry_bp = Blueprint('data_entry', __name__)

@data_entry_bp.route("/data-entry/<table_name>", methods=["GET", "POST"])
def data_entry(table_name):
    """
    Render a data entry form for a given table and handle form submission.

    GET: Fetches table schema and renders an HTML form with input fields
         corresponding to the table's columns (excluding 'id').
    POST: Accepts form data and inserts it into the specified table in the database.

    Args:
        table_name (str): The name of the table to insert data into.

    Returns:
        Rendered HTML template for GET request.
        Redirect to the same page after successful form submission (POST).
    """
    db = get_db()
    if not table_name or table_name.lower() == "none":
        return "No table selected. Please select a table first.", 400

    cursor = db.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    if not columns:
        return f"Table '{table_name}' does not exist.", 400

    if request.method == "POST":
        fields = [col[1] for col in columns if col[1] != 'id']  # skip 'id' if it's auto-increment
        values = [request.form.get(col) for col in fields]
        placeholders = ','.join('?' * len(fields))
        db.execute(f"INSERT INTO {table_name} ({','.join(fields)}) VALUES ({placeholders})", values)
        db.commit()
        return redirect(url_for("data_entry.data_list", table_name=table_name))

    return render_template("_data_entry.html", table_name=table_name, columns=columns)

@data_entry_bp.route("/data-list/<table_name>")
def data_list(table_name):
    db = get_db()
    cursor = db.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    rows = db.execute(f"SELECT * FROM {table_name}").fetchall()
    return render_template("_data_list.html", table_name=table_name, columns=columns, rows=rows)

@data_entry_bp.route("/data-edit/<table_name>/<int:record_id>", methods=["GET", "POST"])
def edit_record(table_name, record_id):
    # Implement edit logic here
    return f"Edit form for {table_name} record {record_id}"

@data_entry_bp.route("/data-delete/<table_name>/<int:record_id>", methods=["POST"])
def delete_record(table_name, record_id):
    db = get_db()
    db.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
    db.commit()
    return redirect(url_for("data_entry.data_list", table_name=table_name))