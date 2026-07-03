"""
utils.py
---------
Small reusable helper functions - currently just CSV export.
Kept separate so exporting logic doesn't clutter the manager classes.
"""

import csv
import os
from database import Database


EXPORT_DIR = "exports"


def _ensure_export_dir():
    os.makedirs(EXPORT_DIR, exist_ok=True)


def export_students_csv(db: Database, filename: str = "students.csv") -> tuple[bool, str]:
    _ensure_export_dir()
    path = os.path.join(EXPORT_DIR, filename)
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT roll_no, name, course, email, phone FROM students ORDER BY id")
            rows = cursor.fetchall()

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Roll No", "Name", "Course", "Email", "Phone"])
            for r in rows:
                writer.writerow([r["roll_no"], r["name"], r["course"], r["email"], r["phone"]])
        return True, f"Exported {len(rows)} students to {path}"
    except Exception as exc:
        return False, f"Export failed: {exc}"


def export_attendance_csv(db: Database, filename: str = "attendance.csv") -> tuple[bool, str]:
    _ensure_export_dir()
    path = os.path.join(EXPORT_DIR, filename)
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.roll_no, s.name, a.date, a.status
                FROM attendance a JOIN students s ON a.student_id = s.id
                ORDER BY s.roll_no, a.date
            """)
            rows = cursor.fetchall()

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Roll No", "Name", "Date", "Status"])
            for r in rows:
                writer.writerow([r["roll_no"], r["name"], r["date"], r["status"]])
        return True, f"Exported {len(rows)} attendance records to {path}"
    except Exception as exc:
        return False, f"Export failed: {exc}"


def export_marks_csv(db: Database, filename: str = "marks.csv") -> tuple[bool, str]:
    _ensure_export_dir()
    path = os.path.join(EXPORT_DIR, filename)
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.roll_no, s.name, m.subject, m.marks_obtained, m.max_marks
                FROM marks m JOIN students s ON m.student_id = s.id
                ORDER BY s.roll_no, m.subject
            """)
            rows = cursor.fetchall()

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Roll No", "Name", "Subject", "Marks Obtained", "Max Marks"])
            for r in rows:
                writer.writerow([r["roll_no"], r["name"], r["subject"], r["marks_obtained"], r["max_marks"]])
        return True, f"Exported {len(rows)} marks records to {path}"
    except Exception as exc:
        return False, f"Export failed: {exc}"
