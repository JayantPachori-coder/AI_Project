from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import mysql.connector, random, os
from flask_mail import Mail, Message
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# ================= SECURITY HEADERS =================
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    response.headers['Content-Security-Policy'] = "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval'"
    return response

# ================= DATABASE CONNECTION =================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Jayant@2004",
        database="smart_schedule"
    )

# ================= ML MODEL TRAIN =================
def train_model_from_csv(csv_path="Train_Data.csv"):
    if not os.path.exists(csv_path):
        return None
    df = pd.read_csv(csv_path)
    X = df[['difficulty', 'performance', 'hours']]
    y = df['preferred']
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

# ================= GENERATE SCHEDULE =================
def generate_schedule(student_id, subjects_input):
    clf = train_model_from_csv()
    subjects_df = pd.DataFrame(subjects_input)

    if clf is not None:
        subjects_df['predicted'] = clf.predict(subjects_df[['difficulty','performance','hours']])
    else:
        subjects_df['predicted'] = subjects_df.apply(
            lambda r: 1 if r['performance'] > 70 and r['difficulty'] < 4 else 0, axis=1
        )

    slot_map = {0: "Morning", 1: "Afternoon", 2: "Evening"}
    subjects_df['time_block'] = subjects_df['predicted'].apply(
        lambda x: random.choice(list(slot_map.values())) if x==1 else random.choice(["Afternoon","Evening"])
    )

    start_time = datetime.now().replace(hour=8,minute=0,second=0,microsecond=0)
    subjects_df['scheduled_time_raw'] = [start_time + timedelta(hours=2*i) for i in range(len(subjects_df))]
    subjects_df['scheduled_time'] = subjects_df['scheduled_time_raw'].dt.strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for _, r in subjects_df.iterrows():
            cursor.execute("""
                INSERT INTO timetable
                (student_id, subject, predicted_slot, time_block, scheduled_time, difficulty, performance, hours, created_by)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                student_id, r['subject'], int(r['predicted']),
                r['time_block'], r['scheduled_time'],
                int(r['difficulty']), int(r['performance']),
                int(r['hours']), 'system'
            ))
        conn.commit()
    except Exception as e:
        print("DB Insert Error:", e)
    finally:
        conn.close()

    return subjects_df[['subject','difficulty','performance','hours','time_block','scheduled_time']]

# ================= ROUTES =================
@app.route('/')
def index():
    return render_template('index.html')

# ---------------- STUDENT ----------------
@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        user = {
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "username": request.form['username'],
            "email": request.form['email'],
            "phone_number": request.form['phone_number'],
            "password": request.form['password'],
        }
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO student_login (first_name,last_name,username,email,phone_number,password)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (user['first_name'], user['last_name'], user['username'], user['email'], user['phone_number'], user['password']))
            conn.commit()
            conn.close()
            flash("🎉 Student registered successfully!", "success")
            return redirect(url_for('student_login'))
        except Exception as e:
            flash(f"⚠️ Registration failed: {e}", "danger")
    return render_template('student_register.html')

@app.route('/studentLogin', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student_login WHERE username=%s AND password=%s", (username, password))
        stu = cursor.fetchone()
        conn.close()
        if stu:
            session['user_type'] = 'student'
            session['username'] = stu['username']
            session['student_id'] = stu['student_id']
            session['name'] = stu['first_name']
            flash("✅ Login successful!", "success")
            return redirect(url_for('student_home'))
        flash("❌ Invalid credentials.", "danger")
    return render_template('student_login.html')

@app.route("/student/home")
def student_home():
    if session.get('user_type') != 'student':
        flash("⚠️ Please login first.", "warning")
        return redirect(url_for('student_login'))
    return render_template("student_home.html", student_name=session.get('name'))

@app.route("/student/schedule", methods=["GET", "POST"])
def student_schedule():
    if session.get('user_type') != 'student':
        flash("⚠️ Please login first.", "warning")
        return redirect(url_for('student_login'))

    if request.method == "POST":
        student_id = session.get('student_id')
        subjects = request.form.getlist('subject[]')
        difficulties = request.form.getlist('difficulty[]')
        performances = request.form.getlist('performance[]')
        hours = request.form.getlist('hours[]')

        inputs = []
        for i in range(len(subjects)):
            if subjects[i].strip():
                inputs.append({
                    "subject": subjects[i],
                    "difficulty": int(difficulties[i]),
                    "performance": int(performances[i]),
                    "hours": int(hours[i])
                })

        if not inputs:
            flash("⚠️ Add at least one subject.", "warning")
            return redirect(url_for('student_schedule'))

        result_df = generate_schedule(student_id, inputs)
        return render_template("display.html",
                               schedule_data=result_df.to_dict(orient='records'),
                               student_id=student_id)

    return render_template("student_schedule.html", username=session.get('name'))

@app.route('/student/view_schedules')
def view_schedules():
    if session.get('user_type') != 'student':
        flash("⚠️ Please login first.", "warning")
        return redirect(url_for('student_login'))

    student_id = session.get('student_id')
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT subject, difficulty, performance, hours, time_block, scheduled_time
            FROM timetable
            WHERE student_id=%s
            ORDER BY timetable_id
        """, (student_id,))
        rows = cursor.fetchall()
    except Exception as e:
        flash(f"⚠️ Error fetching schedules: {e}", "danger")
        rows = []
    finally:
        conn.close()

    return render_template('view_schedules.html', schedules=rows, student_id=student_id)

@app.route('/download_schedule/<int:student_id>')
def download_schedule(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT subject, difficulty, performance, hours, time_block, scheduled_time FROM timetable WHERE student_id=%s ORDER BY timetable_id", (student_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        flash("⚠️ No schedule found.", "warning")
        return redirect(url_for('student_home'))

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Schedule")
    pdf.drawString(200, 750, f"Schedule for Student ID {student_id}")

    y = 700
    pdf.drawString(50, y, "Subject")
    pdf.drawString(200, y, "Time Block")
    pdf.drawString(350, y, "Scheduled Time")
    y -= 20
    for r in rows:
        pdf.drawString(50, y, str(r['subject']))
        pdf.drawString(200, y, str(r['time_block']))
        pdf.drawString(350, y, str(r['scheduled_time']))
        y -= 20
        if y < 50:
            pdf.showPage()
            y = 750
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name=f"{student_id}_schedule.pdf",
                     mimetype='application/pdf')

# ---------------- TEACHER ----------------
@app.route('/teacher_register', methods=['GET', 'POST'])
def teacher_register():
    if request.method == 'POST':
        user = {
            "first_name": request.form['first_name'],
            "last_name": request.form['last_name'],
            "username": request.form['username'],
            "email": request.form['email'],
            "phone_number": request.form['phone_number'],
            "password": request.form['password'],
        }
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO teacher_login (first_name,last_name,username,email,phone_number,password)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (user['first_name'], user['last_name'], user['username'], user['email'], user['phone_number'], user['password']))
            conn.commit()
            conn.close()
            flash("🎉 Teacher registered successfully!", "success")
            return redirect(url_for('teacher_login'))
        except Exception as e:
            flash(f"⚠️ Registration failed: {e}", "danger")
    return render_template('teacher_register.html')

@app.route('/teacherLogin', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM teacher_login WHERE username=%s AND password=%s", (username, password))
        teacher = cursor.fetchone()
        conn.close()
        if teacher:
            session['user_type'] = 'teacher'
            session['username'] = teacher['username']
            session['teacher_id'] = teacher['teacher_id']  # ✅ Correct PK
            session['name'] = teacher['first_name']
            flash("✅ Login successful!", "success")
            return redirect(url_for('teacher_home'))
        flash("❌ Invalid credentials.", "danger")
    return render_template('teacher_login.html')

@app.route("/teacher/home")
def teacher_home():
    if session.get('user_type') != 'teacher':
        flash("⚠️ Please login first.", "warning")
        return redirect(url_for('teacher_login'))
    return render_template("teacher_home.html", teacher_name=session.get('name'))

@app.route("/teacher/profile")
def teacher_profile():
    if session.get('user_type') != 'teacher':
        flash("⚠️ Please login first.", "warning")
        return redirect(url_for('teacher_login'))

    teacher_id = session.get('teacher_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teacher_login WHERE teacher_id=%s", (teacher_id,))
    teacher = cursor.fetchone()
    conn.close()

    if not teacher:
        flash("⚠️ Teacher not found.", "danger")
        return redirect(url_for('teacher_home'))

    return render_template("teacher_profile.html", teacher=teacher)

@app.route("/teacher/schedule", methods=["GET", "POST"])
def teacher_schedule():
    if session.get('user_type') != 'teacher':
        flash("⚠️ Please login first.", "warning")
        return redirect(url_for('teacher_login'))

    schedule = None
    if request.method == "POST":
        class_or_student = request.form['class_or_student']
        subjects = [s.strip() for s in request.form['subjects'].split(',')]
        schedule = [{"subject": s, "time_block": "Morning", "scheduled_time": "2025-11-08 08:00"} for s in subjects]

    return render_template("teacher_schedule.html", schedule=schedule)

@app.route("/teacher/info")
def teacher_info():
    if session.get('user_type') != 'teacher':
        flash("⚠️ Please login first.", "warning")
        return redirect(url_for('teacher_login'))

    teacher_id = session.get('teacher_id')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT first_name, last_name, email, phone_number, username FROM teacher_login WHERE teacher_id=%s", (teacher_id,))
    info = cursor.fetchone()
    conn.close()
    return render_template("teacher_info.html", info=info)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    flash("👋 Logged out successfully.", "info")
    return redirect(url_for('index'))

# ================= MAIN =================
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
