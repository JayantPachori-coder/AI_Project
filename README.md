## Smart Schedule — AI-Powered Student Scheduling System

An intelligent academic scheduling platform that uses Machine Learning to generate personalized study timetables for students and teachers.


# 🌐 Live Preview
PortalDescription🎓 Student PortalRegister, login, input subjects & get AI-generated schedules👨‍🏫 Teacher PortalView student schedules, manage sessions

# 📌 Table of Contents

About the Project
Tech Stack
System Architecture
Methodology
Features
Database Schema
Project Structure
Setup & Installation
How It Works
ML Model
Screenshots
Future Scope


# 🧠 About the Project
Smart Schedule is a full-stack AI-driven web application that automates academic schedule generation for students. Instead of manually planning study hours, students input their subjects, difficulty levels, current performance, and available hours — and the system uses a Random Forest ML model to predict the ideal time block (Morning / Afternoon / Evening) for each subject.
The schedule is then saved to a MySQL database and can be downloaded as a PDF.

# 🛠 Tech Stack
LayerTechnologyFrontendHTML5, CSS3, JavaScript, Bootstrap 5BackendPython, FlaskDatabaseMySQL (via mysql-connector-python)ML ModelScikit-learn — Random Forest ClassifierPDF ExportReportLabAuthFlask Sessions + OTP via EmailDataPandas, CSV Training Data

# 🏗 System Architecture
User Browser
    │
    ▼
Flask Web Server (apppp.py)
    │
    ├──► MySQL Database (smart_schedule)
    │         ├── student_login
    │         ├── teacher_login
    │         └── timetable
    │
    └──► ML Engine (schedule_model.py)
              ├── Train_Data.csv  ──► RandomForestClassifier
              └── Predict: Morning / Afternoon / Evening

## 📖 Methodology
# Phase 1 — User Onboarding
Student/Teacher
     │
     ├── Register (First Name, Last Name, Username, Email, Phone, Password)
     │         └── Stored in MySQL → student_login / teacher_login
     │
     ├── Login (Username + Password)
     │         └── Session created with student_id / teacher_id
     │
     └── Forgot Password → OTP via Email → Reset Password

# Phase 2 — Schedule Generation (Student Flow)
Student enters subjects
     │
     ├── Subject Name
     ├── Difficulty (1–100)
     ├── Performance Score (1–100)
     └── Study Hours Available
          │
          ▼
   ML Model (Random Forest)
   Trained on Train_Data.csv
   [difficulty, performance, hours] → predicted_slot
          │
          ▼

   Time Block Assignment
   ┌──────────────────────────┐
   │ High Risk   → Morning    │
   │ Medium Risk → Afternoon  │
   │ Low Risk    → Evening    │
   └──────────────────────────┘
          │
          ▼
   Scheduled Time (2-hour slots from 8:00 AM)
          │
          ▼
   Saved to MySQL timetable table
          │
          ▼
   Rendered to Student + PDF Download Available


# Phase -3 — PDF Export
Student clicks "Download Schedule"
     │
     ▼
Flask → Queries MySQL (timetable WHERE student_id)
     │
     ▼
ReportLab builds PDF in memory (BytesIO)
     │
     ▼
PDF sent as file download to browser

# ✨ Features
# 🎓 Student Portal

✅ Register & Login with session management
✅ Forgot Password via OTP email verification
✅ Input multiple subjects with difficulty, performance & hours
✅ AI-generated time blocks using Random Forest ML model
✅ Risk level assessment per subject (Low / Medium / High)
✅ Smart scheduling starting from 8:00 AM in 2-hour slots
✅ View all saved schedules from history
✅ Download schedule as PDF

# 👨‍🏫 Teacher Portal

✅ Register & Login
✅ View all student schedules in one dashboard
✅ Generate schedule for a class/student group
✅ View personal profile from database
✅ Forgot Password with OTP

# 🤖 AI / ML Engine

✅ Random Forest Classifier trained on Train_Data.csv
✅ Predicts: Morning (0) / Afternoon (1) / Evening (2)
✅ Features: difficulty, performance, hours
✅ Risk score formula: 100 - performance + (difficulty × 5)
✅ Weak subject detection: performance < 50


# 🗄 Database Schema
student_login
ColumnTypestudent_idINT (PK, AUTO_INCREMENT)first_nameVARCHARlast_nameVARCHARusernameVARCHARemailVARCHARphone_numberVARCHARpasswordVARCHAR
teacher_login
ColumnTypeteacher_idINT (PK, AUTO_INCREMENT)first_nameVARCHARlast_nameVARCHARusernameVARCHARemailVARCHARphone_numberVARCHARpasswordVARCHAR
timetable
ColumnTypeidINT (PK, AUTO_INCREMENT)student_idINT (FK)subjectVARCHARpredicted_slotINTtime_blockVARCHARscheduled_timeDATETIMEdifficultyINTperformanceINThoursINTriskVARCHARweakVARCHARcreated_byVARCHAR

## 📁 Project Structure
smart_schedule/
│
├── apppp.py                  # Main Flask application
├── schedule_model.py         # ML model training & schedule generation
├── Train_Data.csv            # Training dataset (100 rows)
│
├── templates/
│   ├── index.html            # Landing page
│   ├── student_login.html    # Student login
│   ├── student_register.html # Student registration
│   ├── student_home.html     # Student dashboard
│   ├── student_schedule.html # Schedule input form
│   ├── display.html          # Generated schedule display
│   ├── view_schedules.html   # View saved schedules
│   ├── view_schedule.html    # Single schedule view
│   ├── teacher_login.html    # Teacher login
│   ├── teacher_register.html # Teacher registration
│   ├── teacher_home.html     # Teacher dashboard
│   ├── teacher_profile.html  # Teacher profile
│   ├── teacher_schedule.html # Teacher schedule generator
│   ├── teacher_tt.html       # All student timetables
│   ├── teacher_info.html     # Teacher info view
│   ├── password.html         # Forgot password
│   ├── verify_otp.html       # OTP verification
│   ├── reset_password.html   # Reset password
│   └── performance_input.html# Performance data input
│
└── static/
    ├── logo.png
    ├── bgm.png
    ├── download.jpg
    ├── download1.png
    └── download2.png

## ⚙️ Setup & Installation
Prerequisites

Python 3.8+
MySQL Server
pip

# Step 1 — Clone the Repository
bashgit clone https://github.com/yourusername/smart-schedule.git
 cd smart-schedule
# Step 2 — Install Dependencies
bashpip install flask mysql-connector-python pandas scikit-learn reportlab
# Step 3 — Setup MySQL Database
sqlCREATE DATABASE smart_schedule;

USE smart_schedule;

CREATE TABLE student_login (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100),
    phone_number VARCHAR(15),
    password VARCHAR(255)
);

CREATE TABLE teacher_login (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100),
    phone_number VARCHAR(15),
    password VARCHAR(255)
);

CREATE TABLE timetable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    subject VARCHAR(100),
    predicted_slot INT,
    time_block VARCHAR(20),
    scheduled_time DATETIME,
    difficulty INT,
    performance INT,
    hours INT,
    risk VARCHAR(20),
    weak VARCHAR(5),
    created_by VARCHAR(50),
    FOREIGN KEY (student_id) REFERENCES student_login(student_id)
);
Step 4 — Configure Database in apppp.py
pythondef get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD",   # ← Change this
        database="smart_schedule"
    )
Step 5 — Run the Application
bashpython apppp.py
Visit: http://127.0.0.1:5000

## 🔬 How It Works

Student registers with personal details → stored in MySQL
Student logs in → session created
Student inputs subjects → difficulty (1–100), performance score (1–100), hours available
ML model predicts the preferred study time block per subjec
Schedule is built with 2-hour time slots starting from 8:00 AM
Schedule is saved to the timetable MySQL table
Student views & downloads schedule as PDF


🤖 ML Model
PropertyDetailAlgorithmRandom Forest ClassifierLibraryscikit-learnTraining DataTrain_Data.csv (100 samples)Input Featuresdifficulty, performance, hoursOutput Labels0 = Morning, 1 = Afternoon, 2 = EveningFallback LogicIf CSV missing: performance > 70 → label 1, else 0

## 🔮 Future Scope

 Password hashing (bcrypt) for security
 Email OTP integration (SMTP)
 Student performance analytics dashboard
 Push notifications for study reminders
 Google Calendar integration
 Mobile app (Flutter)
 Admin panel for managing users
 Dark/Light mode toggle
 Multiple language support


## 👨‍💻 Author
Jayant

Project: Smart Schedule — AI-Powered Timetable Generator
Stack: Flask + MySQL + ML + HTML/CSS/JS
Year: 2025

