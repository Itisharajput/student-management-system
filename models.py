"""
models.py
----------
Defines the Student data class and the StudentManager, which handles
all CRUD (Create, Read, Update, Delete) operations plus search/filter
for students.
"""

from dataclasses import dataclass
from typing import Optional
from database import Database


@dataclass
class Student:
    """A simple data container representing one student record."""
    id: Optional[int]
    roll_no: str
    name: str
    course: str
    email: str = ""
    phone: str = ""

    def __str__(self):
        return (f"[{self.roll_no}] {self.name} | Course: {self.course} | "
                f"Email: {self.email or '-'} | Phone: {self.phone or '-'}")


class StudentManager:
    """Handles all database operations related to students."""

    def __init__(self, db: Database):
        self.db = db

    # ---------- CREATE ----------
    def add_student(self, roll_no: str, name: str, course: str,
                     email: str = "", phone: str = "") -> tuple[bool, str]:
        roll_no, name, course = roll_no.strip(), name.strip(), course.strip()

        if not roll_no or not name or not course:
            return False, "Roll number, name, and course are required."

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO students (roll_no, name, course, email, phone)
                       VALUES (?, ?, ?, ?, ?)""",
                    (roll_no, name, course, email.strip(), phone.strip()),
                )
            return True, f"Student '{name}' added successfully."
        except Exception as exc:
            if "UNIQUE" in str(exc):
                return False, f"Roll number '{roll_no}' already exists."
            return False, f"Could not add student: {exc}"

    # ---------- READ ----------
    def get_all_students(self) -> list[Student]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY id")
            rows = cursor.fetchall()
        return [self._row_to_student(r) for r in rows]

    def get_student_by_roll(self, roll_no: str) -> Optional[Student]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no.strip(),))
            row = cursor.fetchone()
        return self._row_to_student(row) if row else None

    def search_students(self, keyword: str = "", course: str = "") -> list[Student]:
        """
        Search/filter students by a keyword (matches name or roll number)
        and/or an exact course filter. Either argument can be left blank.
        """
        query = "SELECT * FROM students WHERE 1=1"
        params = []

        if keyword.strip():
            query += " AND (name LIKE ? OR roll_no LIKE ?)"
            like_term = f"%{keyword.strip()}%"
            params.extend([like_term, like_term])

        if course.strip():
            query += " AND course LIKE ?"
            params.append(f"%{course.strip()}%")

        query += " ORDER BY id"

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
        return [self._row_to_student(r) for r in rows]

    # ---------- UPDATE ----------
    def update_student(self, roll_no: str, name: str = None, course: str = None,
                        email: str = None, phone: str = None) -> tuple[bool, str]:
        student = self.get_student_by_roll(roll_no)
        if student is None:
            return False, f"No student found with roll number '{roll_no}'."

        # Only overwrite fields that were actually passed in.
        new_name = name.strip() if name else student.name
        new_course = course.strip() if course else student.course
        new_email = email.strip() if email is not None else student.email
        new_phone = phone.strip() if phone is not None else student.phone

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE students SET name=?, course=?, email=?, phone=?
                   WHERE roll_no=?""",
                (new_name, new_course, new_email, new_phone, roll_no.strip()),
            )
        return True, f"Student '{roll_no}' updated successfully."

    # ---------- DELETE ----------
    def delete_student(self, roll_no: str) -> tuple[bool, str]:
        student = self.get_student_by_roll(roll_no)
        if student is None:
            return False, f"No student found with roll number '{roll_no}'."

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE roll_no = ?", (roll_no.strip(),))
        return True, f"Student '{roll_no}' deleted successfully."

    # ---------- HELPERS ----------
    @staticmethod
    def _row_to_student(row) -> Student:
        return Student(
            id=row["id"], roll_no=row["roll_no"], name=row["name"],
            course=row["course"], email=row["email"] or "", phone=row["phone"] or "",
        )
