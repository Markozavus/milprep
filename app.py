from flask import Flask, render_template, url_for, request
import sqlite3
from datetime import datetime
import os
from werkzeug.security import generate_password_hash


app = Flask(__name__)

# ---------- הגדרות בסיסיות ----------

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
            email TEXT,
            password_hash TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            height_cm INTEGER,
            weight_kg INTEGER,
            fitness_level TEXT,
            skills TEXT,
            health_issues TEXT,
            target_unit TEXT,
            unit_free_text TEXT
        )
    """)
    conn.commit()
    conn.close()



# ---------- ראוטים ----------

@app.route("/")
def home():
    newline = "\n"
    reviews = [
        {
            "name": "ריף הרוש ז''ל",
            "unit": "07.2003 - 06.2024",
            "text": "לעשות חיים כל הזמן, לא לנוח" 
        },
        {
            "name": "ריף הרוש ז''ל",
            "unit": "07.2003 - 06.2024",
            "text":     "למה אני מסכן את החיים שלי? עשו את זה לפניי ויעשו את זה אחריי, ובשביל אותה מבוגרת שאומרת לי תודה ובוכה. "


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


@app.route("/main")
def main_page():
    return "<h1>עמוד ראשי (Main) – בקרוב</h1>"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form

        # יצירת hash לסיסמה
        raw_password = form.get("password")
        password_hash = generate_password_hash(raw_password) if raw_password else None

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO registrations (
                created_at,
                full_name,
                email,
                password_hash,
                age,
                gender,
                height_cm,
                weight_kg,
                fitness_level,
                skills,
                health_issues,
                target_unit,
                unit_free_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(timespec="seconds"),
            form.get("full_name"),
            form.get("email"),
            password_hash,
            int(form.get("age")) if form.get("age") else None,
            form.get("gender"),
            int(form.get("height")) if form.get("height") else None,
            int(form.get("weight")) if form.get("weight") else None,
            form.get("fitness_level"),
            form.get("skills"),
            form.get("health_issues"),
            form.get("target_unit"),
            form.get("unit_free_text"),
        ))
        conn.commit()
        conn.close()

        return render_template(
            "register.html",
            success=True,
            form_data=form
        )

    return render_template("register.html", success=False, form_data=None)



# אופציונלי: עמוד קטן לראות את כל ההרשמות (development בלבד)
@app.route("/admin/registrations")
def admin_registrations():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM registrations ORDER BY created_at DESC").fetchall()
    conn.close()

    html_rows = []
    for r in rows:
        html_rows.append(
            f"<li>{r['created_at']} – {r['full_name']} ({r['email']}), גיל {r['age']}, יחידה: {r['target_unit']}</li>"
        )
    return "<h2>הרשמות</h2><ul>" + "".join(html_rows) + "</ul>"


if __name__ == "__main__":
    init_db()  # מוודא שהטבלה קיימת לפני שמריצים את השרת
    app.run(debug=True)
