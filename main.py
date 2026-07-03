"""
main.py
--------
Entry point for the Student Management System (CLI).

Run with:  python main.py

Default login (created automatically on first run):
    username: admin
    password: admin123
(Change it after logging in via the "Change Password" option.)
"""

from database import Database
from auth import AuthManager
from models import StudentManager
from attendance import AttendanceManager
from marks import MarksManager
from utils import export_students_csv, export_attendance_csv, export_marks_csv


def pause():
    input("\nPress Enter to continue...")


def login_screen(auth: AuthManager) -> str:
    """Loops until the user logs in successfully. Returns the username."""
    print("=" * 50)
    print(" STUDENT MANAGEMENT SYSTEM - LOGIN")
    print("=" * 50)
    while True:
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        success, message = auth.login(username, password)
        print(message)
        if success:
            return username
        print("Try again.\n")


def student_menu(sm: StudentManager):
    while True:
        print("""
--- Student Records ---
1. Add Student
2. View All Students
3. Search / Filter Students
4. Update Student
5. Delete Student
0. Back to Main Menu
""")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            roll_no = input("Roll No: ")
            name = input("Name: ")
            course = input("Course: ")
            email = input("Email (optional): ")
            phone = input("Phone (optional): ")
            ok, msg = sm.add_student(roll_no, name, course, email, phone)
            print(msg)

        elif choice == "2":
            students = sm.get_all_students()
            if not students:
                print("No students found.")
            for s in students:
                print(s)

        elif choice == "3":
            keyword = input("Search by name or roll no (leave blank to skip): ")
            course = input("Filter by course (leave blank to skip): ")
            results = sm.search_students(keyword, course)
            if not results:
                print("No matching students found.")
            for s in results:
                print(s)

        elif choice == "4":
            roll_no = input("Roll No of student to update: ")
            print("Leave a field blank to keep it unchanged.")
            name = input("New Name: ") or None
            course = input("New Course: ") or None
            email = input("New Email: ") or None
            phone = input("New Phone: ") or None
            ok, msg = sm.update_student(roll_no, name, course, email, phone)
            print(msg)

        elif choice == "5":
            roll_no = input("Roll No of student to delete: ")
            confirm = input(f"Type YES to confirm deleting '{roll_no}': ")
            if confirm == "YES":
                ok, msg = sm.delete_student(roll_no)
                print(msg)
            else:
                print("Deletion cancelled.")

        elif choice == "0":
            break
        else:
            print("Invalid option, please try again.")
        pause()


def attendance_menu(am: AttendanceManager):
    while True:
        print("""
--- Attendance ---
1. Mark Attendance
2. View Attendance Report
0. Back to Main Menu
""")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            roll_no = input("Roll No: ")
            date = input("Date (YYYY-MM-DD): ")
            status = input("Status (Present/Absent): ")
            ok, msg = am.mark_attendance(roll_no, date, status)
            print(msg)

        elif choice == "2":
            roll_no = input("Roll No: ")
            report = am.get_attendance_report(roll_no)
            if not report:
                print("No student found with that roll number.")
            else:
                print(f"\nAttendance report for {report['name']} ({report['roll_no']})")
                print(f"Total days marked: {report['total_days']}")
                print(f"Present: {report['present']}  Absent: {report['absent']}")
                print(f"Attendance %: {report['percentage']}%")
                for date, status in report["records"]:
                    print(f"  {date} - {status}")

        elif choice == "0":
            break
        else:
            print("Invalid option, please try again.")
        pause()


def marks_menu(mm: MarksManager):
    while True:
        print("""
--- Marks & Grades ---
1. Add Marks for a Subject
2. View Marks Report & Grade
0. Back to Main Menu
""")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            roll_no = input("Roll No: ")
            subject = input("Subject: ")
            try:
                obtained = float(input("Marks Obtained: "))
                maximum = float(input("Maximum Marks: "))
            except ValueError:
                print("Marks must be numbers.")
                pause()
                continue
            ok, msg = mm.add_marks(roll_no, subject, obtained, maximum)
            print(msg)

        elif choice == "2":
            roll_no = input("Roll No: ")
            report = mm.get_marks_report(roll_no)
            if not report:
                print("No student found with that roll number.")
            else:
                print(f"\nMarks report for {report['name']} ({report['roll_no']})")
                for subject, obtained, maximum in report["subjects"]:
                    print(f"  {subject}: {obtained}/{maximum}")
                print(f"Total: {report['total_obtained']}/{report['total_max']}")
                print(f"Percentage: {report['percentage']}%")
                print(f"Grade: {report['grade']}")

        elif choice == "0":
            break
        else:
            print("Invalid option, please try again.")
        pause()


def export_menu(db: Database):
    while True:
        print("""
--- Export to CSV ---
1. Export Students
2. Export Attendance
3. Export Marks
4. Export All
0. Back to Main Menu
""")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            print(export_students_csv(db)[1])
        elif choice == "2":
            print(export_attendance_csv(db)[1])
        elif choice == "3":
            print(export_marks_csv(db)[1])
        elif choice == "4":
            print(export_students_csv(db)[1])
            print(export_attendance_csv(db)[1])
            print(export_marks_csv(db)[1])
        elif choice == "0":
            break
        else:
            print("Invalid option, please try again.")
        pause()


def main():
    db = Database()
    auth = AuthManager(db)
    sm = StudentManager(db)
    am = AttendanceManager(db, sm)
    mm = MarksManager(db, sm)

    username = login_screen(auth)

    while True:
        print(f"""
{"=" * 50}
 STUDENT MANAGEMENT SYSTEM - Logged in as {username}
{"=" * 50}
1. Student Records (Add/View/Search/Update/Delete)
2. Attendance
3. Marks & Grades
4. Export Data to CSV
5. Change Password
0. Exit
""")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            student_menu(sm)
        elif choice == "2":
            attendance_menu(am)
        elif choice == "3":
            marks_menu(mm)
        elif choice == "4":
            export_menu(db)
        elif choice == "5":
            new_pw = input("Enter new password: ")
            ok, msg = auth.change_password(username, new_pw)
            print(msg)
            pause()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again.")


if __name__ == "__main__":
    main()
