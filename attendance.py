"""
attendance.py
--------------
Handles marking and reporting attendance for students.
"""

from database import Database
from models import StudentManager


class AttendanceManager:
    def __init__(self, db: Database, student_manager: StudentManager):
        self.db = db
        self.student_manager = student_manager

    def mark_attendance(self, roll_no: str, date: str, status: str) -> tuple[bool, str]:
        """
        Marks a student Present or Absent on a given date (format: YYYY-MM-DD).
        If attendance for that student+date already exists, it gets updated
        instead of duplicated.
        """
        status = status.strip().capitalize()
        if status not in ("Present", "Absent"):
            return False, "Status must be 'Present' or 'Absent'."

        student = self.student_manager.get_student_by_roll(roll_no)
        if student is None:
            return False, f"No student found with roll number '{roll_no}'."

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO attendance (student_id, date, status)
                       VALUES (?, ?, ?)
                       ON CONFLICT(student_id, date)
                       DO UPDATE SET status = excluded.status""",
                    (student.id, date.strip(), status),
                )
            return True, f"Attendance for '{roll_no}' on {date} marked as {status}."
        except Exception as exc:
            return False, f"Could not mark attendance: {exc}"

    def get_attendance_report(self, roll_no: str) -> dict:
        """Returns a summary: total days, present count, absent count, percentage."""
        student = self.student_manager.get_student_by_roll(roll_no)
        if student is None:
            return {}

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT date, status FROM attendance WHERE student_id = ? ORDER BY date",
                (student.id,),
            )
            rows = cursor.fetchall()

        total = len(rows)
        present = sum(1 for r in rows if r["status"] == "Present")
        absent = total - present
        percentage = round((present / total) * 100, 2) if total > 0 else 0.0

        return {
            "roll_no": roll_no,
            "name": student.name,
            "total_days": total,
            "present": present,
            "absent": absent,
            "percentage": percentage,
            "records": [(r["date"], r["status"]) for r in rows],
        }
