import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from pdf_generator import generate_pdf

app = FastAPI(title="PDF Report Generator")

DB_NAME = "report.db"
REPORTS_DIR = Path("reports")


def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_reports_table():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/reports")
def create_report():
    initialize_reports_table()

    connection = get_connection()
    cursor = connection.cursor()

    # Reuse an existing report generated today.
    cursor.execute("""
        SELECT id, path
        FROM reports
        WHERE DATE(created_at) = DATE('now', 'localtime')
        ORDER BY id DESC
        LIMIT 1
    """)

    existing_report = cursor.fetchone()

    if existing_report:
        report_id = existing_report["id"]
        file_path = Path(existing_report["path"])

        # Reuse the report only if its PDF still exists.
        if file_path.is_file():
            connection.close()

            return {
                "id": report_id,
                "file": f"/reports/{report_id}/file",
            }

        # If the PDF is missing, remove the stale record.
        cursor.execute(
            "DELETE FROM reports WHERE id = ?",
            (report_id,),
        )
        connection.commit()

    # Create a new report record.
    cursor.execute("""
        INSERT INTO reports (path, created_at)
        VALUES (?, datetime('now', 'localtime'))
    """, ("",))

    report_id = cursor.lastrowid
    connection.commit()

    output_path = REPORTS_DIR / f"{report_id}.pdf"

    try:
        # Generate the PDF.
        generate_pdf(str(output_path))

        # Save its path in the database.
        cursor.execute("""
            UPDATE reports
            SET path = ?
            WHERE id = ?
        """, (str(output_path), report_id))

        connection.commit()

    except Exception as error:
        # Remove the incomplete record if generation fails.
        cursor.execute(
            "DELETE FROM reports WHERE id = ?",
            (report_id,),
        )
        connection.commit()
        connection.close()

        raise HTTPException(
            status_code=500,
            detail="Failed to generate PDF report",
        ) from error

    connection.close()

    return {
        "id": report_id,
        "file": f"/reports/{report_id}/file",
    }


@app.get("/reports/{report_id}")
def get_report(report_id: int):
    connection = get_connection()

    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, path, created_at
        FROM reports
        WHERE id = ?
    """, (report_id,))

    report = cursor.fetchone()
    connection.close()

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return {
        "id": report["id"],
        "path": report["path"],
        "created_at": report["created_at"],
        "file": f"/reports/{report_id}/file",
    }


@app.get("/reports/{report_id}/file")
def download_report(report_id: int):
    connection = get_connection()

    cursor = connection.cursor()
    cursor.execute("""
        SELECT path
        FROM reports
        WHERE id = ?
    """, (report_id,))

    report = cursor.fetchone()
    connection.close()

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    file_path = Path(report["path"])

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="PDF file not found",
        )

    return FileResponse(
        path=str(file_path.resolve()),
        media_type="application/pdf",
        filename=f"report-{report_id}.pdf",
    )