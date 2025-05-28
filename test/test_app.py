import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlflask import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_favicon(client):
    response = client.get("/favicon.ico")
    assert response.status_code in (200, 404)  # 200 if favicon exists, 404 if not

def test_homepage_no_details_table(client):
    # Use a temp db
    with client.session_transaction() as sess:
        sess["current_database"] = "temp_db.sqlite"
    # Ensure the db file exists but no details table
    import os, sqlite3
    db_path = os.path.join("data", "temp_db.sqlite")
    if os.path.exists(db_path):
        os.remove(db_path)
    sqlite3.connect(db_path).close()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Rows" in response.data

def test_session_context(client):
    with client.session_transaction() as sess:
        sess["current_database"] = "db.sqlite"
    response = client.get("/")
    assert b"Rows" in response.data
    # After request, session should still have current_database
    with client.session_transaction() as sess:
        assert sess["current_database"] == "db.sqlite"

def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Rows" in response.data  # Adjust if your homepage uses a different context/title

def test_add_database(client):
    response = client.post("/databases/add", data={"name": "pytest_db"})
    assert response.status_code == 200
    assert b"pytest_db.sqlite" in response.data  # Adjust if your template displays just "pytest_db"

def test_delete_database(client):
    # Add a database first
    client.post("/databases/add", data={"name": "delete_me"})
    # Find its id
    response = client.get("/databases/")
    assert b"delete_me.sqlite" in response.data
    # Assuming it's the last in the list
    from sqlflask import app
    with app.app_context():
        from views.databases import get_all_databases
        dbs = get_all_databases()
        db_id = next((d["id"] for d in dbs if d["name"] == "delete_me.sqlite"), None)
    response = client.delete(f"/databases/delete/{db_id}")
    assert response.status_code == 200
    assert b"delete_me.sqlite" not in response.data

def test_tables_view_loads(client):
    response = client.get("/tables/")
    assert response.status_code == 200
    assert b"Tables" in response.data  # Adjust if your template uses a different heading

def test_edit_nonexistent_database(client):
    response = client.get("/databases/edit/9999")
    assert response.status_code == 404
    assert b"Database not found" in response.data

def test_add_table(client):
    # First, select a database (simulate session)
    with client.session_transaction() as sess:
        sess["current_database"] = "db.sqlite"
    response = client.post("/tables/add", data={"name": "pytest_table"})
    assert response.status_code == 200
    assert b"pytest_table" in response.data

def test_edit_table(client):
    with client.session_transaction() as sess:
        sess["current_database"] = "db.sqlite"
    # Add a table to edit
    client.post("/tables/add", data={"name": "old_table"})
    # Edit the table (id 0, since it's the first)
    response = client.put("/tables/update/0", data={"name": "new_table"})
    assert response.status_code == 200
    assert b"new_table" in response.data

def test_delete_table(client):
    with client.session_transaction() as sess:
        sess["current_database"] = "db.sqlite"
    client.post("/tables/add", data={"name": "pytest_table"})
    response = client.delete("/tables/delete/0")
    assert response.status_code == 200
    assert b"table_to_delete" not in response.data

def test_add_column(client):
    with client.session_transaction() as sess:
        sess["current_database"] = "db.sqlite"
        sess["current_table"] = "pytest_table"
    # Ensure table exists
    client.post("/tables/add", data={"name": "pytest_table"})
    response = client.post("/columns/add", data={"name": "pytest_column"})
    assert response.status_code == 200
    assert b"pytest_column" in response.data

def test_rename_column(client):
    with client.session_transaction() as sess:
        sess["current_database"] = "db.sqlite"
        sess["current_table"] = "pytest_table"
    client.post("/tables/add", data={"name": "pytest_table"})
    client.post("/columns/add", data={"name": "old_column"})
    response = client.put("/columns/update/1", data={"name": "new_column"})
    assert response.status_code == 200
    assert b"new_column" in response.data

#relationships zijn er nog niet, maar later wel nodig
#def test_add_row(client):
#    with client.session_transaction() as sess:
#        sess["current_database"] = "db.sqlite"
#        sess["current_table"] = "pytest_table"
    # Ensure table exists
#    client.post("/tables/add", data={"name": "pytest_table"})
#    response = client.post("/relationships/add", data={"name": "pytest_row"})
#    assert response.status_code == 200
#    assert b"pytest_row" in response.data
