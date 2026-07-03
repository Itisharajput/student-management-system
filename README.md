# 🎓 Student Management System

A command-line Student Management System built in **Python** with a **SQLite** database.
Built as a resume project to demonstrate practical skills in OOP, database design (CRUD),
authentication, and clean project structure.

## ✨ Features

- 🔐 **Login System** — password-hashed authentication (default admin account created automatically)
- 👨‍🎓 **Student CRUD** — Add, View, Update, Delete student records
- 🔍 **Search & Filter** — search by name/roll number, filter by course
- 📅 **Attendance Tracking** — mark daily attendance and view per-student attendance % reports
- 📊 **Marks & Grade Calculation** — record subject-wise marks, auto-calculate percentage and letter grade
- 📁 **Export to CSV** — export students, attendance, or marks data for use in Excel/Sheets
- ⚠️ **Robust Error Handling** — every operation validates input and fails gracefully with a clear message instead of crashing

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.10+ |
| Database | SQLite3 (built into Python, no setup needed) |
| Interface | Command-Line Interface (CLI) |
| Dependencies | None — standard library only |

## 📂 Project Structure

```
student_management_system/
├── main.py            # Entry point — CLI menus and program flow
├── database.py         # SQLite connection handling & table creation
├── auth.py             # Login, registration, password hashing
├── models.py            # Student data model + CRUD operations
├── attendance.py        # Attendance marking & reporting
├── marks.py             # Marks entry & grade calculation
├── utils.py              # CSV export helpers
├── test_app.py           # Automated test suite (51 checks)
├── requirements.txt
├── .gitignore
└── README.md
```

Each file has a single responsibility — this is a deliberate design choice (separation of concerns)
rather than putting everything in one script.

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher installed ([download here](https://www.python.org/downloads/))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Itisharajput/student-management-system.git
cd student-management-system

# 2. (No external packages needed, but this is here for completeness)
pip install -r requirements.txt

# 3. Run the application
python main.py
```

### Default Login

On first run, a default admin account is created automatically:

```
Username: admin
Password: admin123
```

You can change this password from the main menu after logging in (Option 5).

## 📖 Usage Example

```
==================================================
 STUDENT MANAGEMENT SYSTEM - LOGIN
==================================================
Username: admin
Password: admin123
Welcome, admin!

1. Student Records (Add/View/Search/Update/Delete)
2. Attendance
3. Marks & Grades
4. Export Data to CSV
5. Change Password
0. Exit
```

## 🧪 Testing

This project includes an automated test suite covering authentication, all CRUD operations,
search/filter, attendance edge cases (duplicate dates, invalid status), marks validation
(negative/over-max marks), grade boundaries, and CSV export correctness.

```bash
python test_app.py
```

Expected output ends with:
```
ALL TESTS PASSED ✅
```

## 🗺️ Roadmap / Future Improvements

- [ ] Web version using Flask
- [ ] Export reports as PDF (in addition to CSV)
- [ ] Attendance summary charts using Matplotlib
- [ ] Multi-role support (Admin vs Teacher vs Student view)
- [ ] Bulk import students from a CSV file

## 👩‍💻 Author

**Itisha Rajput**
B.Sc. Computer Science, DAVV Indore
[GitHub](https://github.com/Itisharajput) • [LinkedIn](https://linkedin.com/in/itisha-rajput-24303532a)

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
