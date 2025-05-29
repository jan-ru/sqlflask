from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime

from sqlflask.config import DB_PATH, EXCEL_DIR

EXCEL_DIR.mkdir(exist_ok=True)
EXCEL_LATEST = EXCEL_DIR / "latest.xlsx"
TABLE_NAME = "your_table"  # Replace with actual table name from sqlflask

# Function to read from the sqlflask DB
def read_from_db():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    conn.close()
    return df

# Function to write to the DB (overwrite existing data)
def write_to_db(df: pd.DataFrame):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()

# Export current DB table to Excel and archive with timestamp
def export_to_excel(df: pd.DataFrame):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    versioned_path = EXCEL_DIR / f"export_{timestamp}.xlsx"
    df.to_excel(EXCEL_LATEST, index=False)
    df.to_excel(versioned_path, index=False)

# Import Excel file into a DataFrame
def import_from_excel(file_path: Path = EXCEL_LATEST) -> pd.DataFrame:
    return pd.read_excel(file_path)

# List available versioned Excel files
def list_excel_versions():
    return sorted(EXCEL_DIR.glob("export_*.xlsx"), reverse=True)

app_ui = ui.page_fluid(
    ui.h2("SQLFlask: Database + Excel Reporting with Versioning"),
    ui.output_table("data_view"),
    ui.row(
        ui.action_button("refresh", "🔁 Refresh from DB"),
        ui.action_button("export", "📤 Export to Excel (Versioned)")
    ),
    ui.input_select("version_select", "📂 Load Excel Version", choices=[]),
    ui.action_button("import_version", "📥 Import Selected Version")
)

def server(input: Inputs, output: Outputs, session: Session):
    data = reactive.Value(read_from_db())

    @reactive.Effect
    @reactive.event(input.refresh)
    def _():
        data.set(read_from_db())

    @reactive.Effect
    @reactive.event(input.export)
    def _():
        export_to_excel(data.get())
        session.send_input("version_select", [f.name for f in list_excel_versions()])

    @reactive.Effect
    def update_dropdown():
        session.send_input("version_select", [f.name for f in list_excel_versions()])

    @reactive.Effect
    @reactive.event(input.import_version)
    def _():
        selected_file = input.version_select()
        if selected_file:
            file_path = EXCEL_DIR / selected_file
            df = import_from_excel(file_path)
            write_to_db(df)
            data.set(df)

    @output
    @render.table
    def data_view():
        return data.get()

app = App(app_ui, server)
if __name__ == "__main__":
    app.run()
# To run the app, use the command: `python shiny_excel_sync.py`
# Ensure you have the required packages installed:
# pip install shiny pandas openpyxl sqlite3
