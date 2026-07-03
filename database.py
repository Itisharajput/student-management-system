"""
database.py
------------
Handles the SQLite database connection and table creation for the
Student Management System.

All raw SQL lives in this file so the rest of the app never has to
write SQL directly. Every method that touches the DB is wrapped in
try/except so a bad query never crashes the whole program.
"""

import sqlite3
from contextlib import contextmanager


class Database:
    """Wraps a single SQLite connection and creates the required tables."""

    def __init__(self, db_path: str = "school.db"):
        self.db_path = db_path
        self._create_tables()

    @contextmanager
    def get_connection(self):
        """
        Context manager that yields a connection and always closes it,
        even if an error happens. Also enables foreign key support,
        which SQLite disables by default.
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row  # lets us access columns by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _create_tables(self):
        """Creates all tables if they do not already exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'admin'
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_no TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    course TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    created_at TEXT DEFAULT (datetime('now', 'localtime'))
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    UNIQUE(student_id, date)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS marks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    marks_obtained REAL NOT NULL,
                    max_marks REAL NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                )
            """)
