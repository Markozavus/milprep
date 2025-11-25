from flask import Flask, render_template, url_for, request, session, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY_123"  # חובה לסשן

# ---------- Database ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "military_app.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            full_name TEXT,
            email TEXT UNIQUE,
            password TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            category TEXT
        )
    """)
    conn.commit()
    conn.close()


# ---------- Routes ----------

@app.route("/")
def home():
    reviews = [
        {
            "name": "ריף הרוש ז''ל",
            "unit": "07.2003 - 06.2024",
            "text": "לעשות חיים כל הזמן, לא לנוח"
        },
        {
            "name": "ריף הרוש ז''ל",
            "unit": "07.2003 - 06.2024",
            "text": "למה אני מסכן את החיים שלי? עשו את זה לפניי ויעשו את זה אחריי, ובשביל אותה מבוגרת שאומרת לי תודה ובוכה."
        },
        {
            "name": "ריף הרוש ז''ל",
            "unit": "07.2003 - 06.2024",
            "text": "אני מוכן להקריב את החיים שלי בשביל שהמשפחה שלי תשב בשקט ובנחת ושהם ידעו שיש מאחוריהם צבא ענק שישמור עליהם כל עוד אנחנו על הרגליים"
        },
        {
            "name": "ריף הרוש ז''ל",
            "unit": "07.2003 - 06.2024",
            "text": "ניסיתי את ההכי טוב שלי, וזה לאן שהגעתי"
        },
    ]
    return render_template("home.html", reviews=reviews)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form

        # תיקון: שמירת סיסמה בלי רווחים
        password = form["password"].strip()

        conn = get_db_connection()
        cursor = conn.execute("""
            INSERT INTO registrations
            (created_at, full_name, email, password, age, gender)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(timespec="seconds"),
            form["full_name"].strip(),
            form["email"].strip(),
            password,
            int(form["age"]),
            form["gender"]
        ))
        conn.commit()
        new_user_id = cursor.lastrowid
        conn.close()

        session["user_id"] = new_user_id
        session["user_name"] = form["full_name"]

        return redirect(url_for("first_choice"))

    return render_template("register.html")


@app.route("/first-choice", methods=["GET", "POST"])
def first_choice():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    conn = get_db_connection()

    if request.method == "POST":
        category = request.form.get("category")
        conn.execute("UPDATE registrations SET category = ? WHERE id = ?", (category, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))

    user = conn.execute("SELECT * FROM registrations WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    return render_template("firstChoice.html", user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    print("hi")
    error = None
    if request.method == 'POST':
        form = request.form
        full_name = form.get("full_name", "").strip()
        password = form.get("password", "").strip()

        print("\n\n\n\n\n" + full_name)

        # שליפת משתמש לפי שם מדויק (ללא LOWER)
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM registrations WHERE full_name = ?",
            (full_name,)
        ).fetchone()
        conn.close()

        # בדיקת סיסמה נקייה מול סיסמה נקייה
        if user and user["password"].strip() == password:
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            return redirect(url_for("first_choice"))
        else:
            error = True

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/admin/registrations")
def admin_registrations():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM registrations").fetchall()
    conn.close()

    html_rows = [
        f"<li>{r['id']} — {r['full_name']} — {r['email']} — קטגוריה: {r['category']}</li>"
        for r in rows
    ]

    return "<h2>הרשמות</h2><ul>" + "".join(html_rows) + "</ul>"


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
