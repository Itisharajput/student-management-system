"""
marks.py
---------
Handles storing subject-wise marks and calculating grades.
"""

from database import Database
from models import StudentManager


def calculate_grade(percentage: float) -> str:
    """Converts a percentage score into a letter grade."""
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    elif percentage >= 40:
        return "E"
    else:
        return "F"


class MarksManager:
    def __init__(self, db: Database, student_manager: StudentManager):
        self.db = db
        self.student_manager = student_manager

    def add_marks(self, roll_no: str, subject: str,
                   marks_obtained: float, max_marks: float) -> tuple[bool, str]:
        student = self.student_manager.get_student_by_roll(roll_no)
        if student is None:
            return False, f"No student found with roll number '{roll_no}'."

        if max_marks <= 0:
            return False, "Maximum marks must be greater than zero."
        if marks_obtained < 0 or marks_obtained > max_marks:
            return False, f"Marks obtained must be between 0 and {max_marks}."

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO marks (student_id, subject, marks_obtained, max_marks)
                   VALUES (?, ?, ?, ?)""",
                (student.id, subject.strip(), marks_obtained, max_marks),
            )
        return True, f"Marks for '{subject}' added for student '{roll_no}'."

    def get_marks_report(self, roll_no: str) -> dict:
        """Returns subject-wise marks plus an overall percentage and grade."""
        student = self.student_manager.get_student_by_roll(roll_no)
        if student is None:
            return {}

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT subject, marks_obtained, max_marks FROM marks WHERE student_id = ?",
                (student.id,),
            )
            rows = cursor.fetchall()

        total_obtained = sum(r["marks_obtained"] for r in rows)
        total_max = sum(r["max_marks"] for r in rows)
        percentage = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0.0

        return {
            "roll_no": roll_no,
            "name": student.name,
            "subjects": [
                (r["subject"], r["marks_obtained"], r["max_marks"]) for r in rows
            ],
            "total_obtained": total_obtained,
            "total_max": total_max,
            "percentage": percentage,
            "grade": calculate_grade(percentage) if rows else "N/A",
        }
