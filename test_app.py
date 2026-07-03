"""
test_app.py
------------
Automated tests for the Student Management System.
Run with: python test_app.py

This is not pytest-based on purpose (keeps it dependency-free and easy
to read for a beginner project) - it just runs a series of checks and
prints PASS/FAIL for each, then exits with an error code if anything failed.
"""

import os
import sys

TEST_DB = "test_school.db"

# Clean slate before testing
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

from database import Database
from auth import AuthManager
from models import StudentManager
from attendance import AttendanceManager
from marks import MarksManager, calculate_grade
from utils import export_students_csv, export_attendance_csv, export_marks_csv

failures = []


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        failures.append(label)


# ---------------- SETUP ----------------
db = Database(TEST_DB)
auth = AuthManager(db)
sm = StudentManager(db)
am = AttendanceManager(db, sm)
mm = MarksManager(db, sm)

# ---------------- AUTH TESTS ----------------
ok, msg = auth.login("admin", "admin123")
check("Default admin login works", ok)

ok, msg = auth.login("admin", "wrongpassword")
check("Login fails with wrong password", not ok)

ok, msg = auth.login("nosuchuser", "whatever")
check("Login fails for nonexistent user", not ok)

ok, msg = auth.register_user("teacher1", "pass123")
check("New user registration works", ok)

ok, msg = auth.register_user("teacher1", "pass123")
check("Duplicate username registration fails", not ok)

ok, msg = auth.login("teacher1", "pass123")
check("New user can log in", ok)

ok, msg = auth.change_password("teacher1", "newpass1")
check("Password change works", ok)

ok, msg = auth.login("teacher1", "newpass1")
check("Login works with new password after change", ok)

# ---------------- STUDENT CRUD TESTS ----------------
ok, msg = sm.add_student("R001", "Itisha Rajput", "B.Sc CS", "itisha@example.com", "9999999999")
check("Add student works", ok)

ok, msg = sm.add_student("R001", "Duplicate Roll", "B.Sc CS")
check("Duplicate roll number is rejected", not ok)

ok, msg = sm.add_student("", "No Roll", "B.Sc CS")
check("Empty roll number is rejected", not ok)

sm.add_student("R002", "Rahul Sharma", "B.Sc CS", "rahul@example.com", "8888888888")
sm.add_student("R003", "Priya Verma", "BCA", "priya@example.com", "7777777777")

students = sm.get_all_students()
check("get_all_students returns 3 students", len(students) == 3)

student = sm.get_student_by_roll("R001")
check("get_student_by_roll finds correct student", student is not None and student.name == "Itisha Rajput")

missing = sm.get_student_by_roll("R999")
check("get_student_by_roll returns None for missing roll", missing is None)

results = sm.search_students(keyword="Rahul")
check("Search by name works", len(results) == 1 and results[0].roll_no == "R002")

results = sm.search_students(course="B.Sc CS")
check("Filter by course works", len(results) == 2)

results = sm.search_students(keyword="R00")
check("Search by partial roll number works", len(results) == 3)

ok, msg = sm.update_student("R001", name="Itisha R. Rajput")
check("Update student name works", ok)
updated = sm.get_student_by_roll("R001")
check("Updated name persisted correctly", updated.name == "Itisha R. Rajput")
check("Update did not wipe untouched fields (course)", updated.course == "B.Sc CS")

ok, msg = sm.update_student("R999", name="Ghost")
check("Updating nonexistent student fails cleanly", not ok)

ok, msg = sm.delete_student("R003")
check("Delete student works", ok)
check("Deleted student no longer in list", sm.get_student_by_roll("R003") is None)

ok, msg = sm.delete_student("R999")
check("Deleting nonexistent student fails cleanly", not ok)

# ---------------- ATTENDANCE TESTS ----------------
ok, msg = am.mark_attendance("R001", "2026-07-01", "Present")
check("Mark attendance works", ok)

ok, msg = am.mark_attendance("R001", "2026-07-02", "absent")  # lowercase on purpose
check("Mark attendance normalizes lowercase status", ok)

ok, msg = am.mark_attendance("R001", "2026-07-01", "Absent")  # same date, should overwrite
check("Re-marking same date updates instead of erroring", ok)

ok, msg = am.mark_attendance("R001", "2026-07-03", "Maybe")
check("Invalid attendance status is rejected", not ok)

ok, msg = am.mark_attendance("R999", "2026-07-01", "Present")
check("Marking attendance for nonexistent student fails cleanly", not ok)

report = am.get_attendance_report("R001")
check("Attendance report has 2 unique dates", report["total_days"] == 2)
check("Attendance report shows overwritten status as Absent", report["present"] == 0 and report["absent"] == 2)
check("Attendance percentage calculated correctly", report["percentage"] == 0.0)

am.mark_attendance("R002", "2026-07-01", "Present")
am.mark_attendance("R002", "2026-07-02", "Present")
am.mark_attendance("R002", "2026-07-03", "Absent")
report2 = am.get_attendance_report("R002")
check("Attendance percentage math correct (2/3 = 66.67%)", report2["percentage"] == 66.67)

# ---------------- MARKS & GRADE TESTS ----------------
check("Grade A+ for 95%", calculate_grade(95) == "A+")
check("Grade A for 85%", calculate_grade(85) == "A")
check("Grade B for 75%", calculate_grade(75) == "B")
check("Grade C for 65%", calculate_grade(65) == "C")
check("Grade D for 55%", calculate_grade(55) == "D")
check("Grade E for 45%", calculate_grade(45) == "E")
check("Grade F for 30%", calculate_grade(30) == "F")
check("Boundary: exactly 90% is A+", calculate_grade(90) == "A+")
check("Boundary: exactly 39.99% is F", calculate_grade(39.99) == "F")

ok, msg = mm.add_marks("R001", "Python", 85, 100)
check("Add marks works", ok)
mm.add_marks("R001", "Maths", 70, 100)

ok, msg = mm.add_marks("R001", "Physics", 150, 100)
check("Marks exceeding max is rejected", not ok)

ok, msg = mm.add_marks("R001", "Physics", -5, 100)
check("Negative marks is rejected", not ok)

ok, msg = mm.add_marks("R999", "Python", 50, 100)
check("Adding marks for nonexistent student fails cleanly", not ok)

report = mm.get_marks_report("R001")
check("Marks report shows 2 subjects", len(report["subjects"]) == 2)
check("Marks report total is correct (155/200)", report["total_obtained"] == 155 and report["total_max"] == 200)
check("Marks report percentage correct (77.5%)", report["percentage"] == 77.5)
check("Marks report grade correct (B)", report["grade"] == "B")

empty_report = mm.get_marks_report("R002")
check("Student with no marks shows grade N/A", empty_report["grade"] == "N/A")

# ---------------- CSV EXPORT TESTS ----------------
ok, msg = export_students_csv(db, "test_students.csv")
check("Export students CSV works", ok and os.path.exists("exports/test_students.csv"))

ok, msg = export_attendance_csv(db, "test_attendance.csv")
check("Export attendance CSV works", ok and os.path.exists("exports/test_attendance.csv"))

ok, msg = export_marks_csv(db, "test_marks.csv")
check("Export marks CSV works", ok and os.path.exists("exports/test_marks.csv"))

# Verify CSV content is actually correct, not just that the file exists
with open("exports/test_students.csv") as f:
    content = f.read()
check("Exported CSV contains student name", "Itisha R. Rajput" in content)

# ---------------- CLEANUP ----------------
for f in ["exports/test_students.csv", "exports/test_attendance.csv", "exports/test_marks.csv"]:
    if os.path.exists(f):
        os.remove(f)
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

# ---------------- SUMMARY ----------------
print("\n" + "=" * 50)
if failures:
    print(f"{len(failures)} TEST(S) FAILED:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED ✅")
    sys.exit(0)
