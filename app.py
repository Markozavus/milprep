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
            city TEXT,
            category TEXT,
            sub_category TEXT,
            role_priority TEXT  -- הוספת העמודה החדשה
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
            (created_at, full_name, email, password, age, gender, city)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(timespec="seconds"),
            form["full_name"].strip(),
            form["email"].strip(),
            password,
            int(form["age"]),
            form["gender"],
            form["city"]
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
        # עדכון קטגוריה בבסיס הנתונים
        conn.execute("UPDATE registrations SET category = ? WHERE id = ?", (category, user_id))
        conn.commit()
        conn.close()

        # נווט לעמוד הבא (second-choice)
        return redirect(url_for("second_choice"))

    user = conn.execute("SELECT * FROM registrations WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    return render_template("firstChoice.html", user=user)



@app.route("/second-choice", methods=["GET", "POST"])
def second_choice():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    conn = get_db_connection()

    # שליפת הקטגוריה שבחר המשתמש בעמוד הראשון
    user = conn.execute("SELECT * FROM registrations WHERE id = ?", (user_id,)).fetchone()
    selected_category = user["category"]
    options = []

    # הצגת האפשרויות לפי הקטגוריה
    if selected_category == "technology":
        options = ['פיזיקה', 'מתמטיקה', 'מדעי המחשב']
    elif selected_category == "warfare":
        options = ['חיל רגלים', 'חיל הים', 'חיל האוויר']
    elif selected_category == "Fighting supporters":
        options = ['מנהלה ושלישות', 'שיטור', 'תפקידי אבטחה']
    elif selected_category == "communication":
        options = ['ייצור תוכן', 'תשתית וטכנולוגיה', 'מערכות מידע']
    elif selected_category == "logistics":
        options = ['הכשרת כוח אדם', 'מערך ההובלה', 'הכנה לחירום']
    else:
        options = []  # אם אין קטגוריה מוגדרת או שיש קטגוריה לא ידועה

    if request.method == "POST":
        sub_category = request.form.get("sub_category")
        
        # עדכון הבחירה של תת-הקטגוריה בבסיס הנתונים
        conn.execute("UPDATE registrations SET sub_category = ? WHERE id = ?", (sub_category, user_id))
        conn.commit()
        conn.close()

        # נווט לעמוד הבא (third-choice)
        return redirect(url_for("third_selection"))

    conn.close()
    return render_template("secondSelection.html", options=options)



@app.route("/third-selection", methods=["GET", "POST"])
def third_selection():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    conn = get_db_connection()

    # שליפת הקטגוריה ותת-הקטגוריה שבחר המשתמש
    user = conn.execute("SELECT * FROM registrations WHERE id = ?", (user_id,)).fetchone()
    selected_category = user["category"]
    selected_sub_category = user["sub_category"]
    roles = []

    # הצגת 5 תפקידי צה"ל על פי תת-הקטגוריה שנבחרה
    if selected_category == "technology":
        if selected_sub_category == "מדעי המחשב":
            roles = ['מפתח תוכנה', 'מנהל פרויקטים טכנולוגיים', 'מתכנתי בינה מלאכותית', 'מהנדס תוכנה', 'מנהל צוות פיתוח']
        elif selected_sub_category == "פיזיקה":
            roles = ['פיזיקאי', 'מהנדס אלקטרוניקה', 'חוקר טכנולוגיות חדשות', 'מתכנתי מערכות צבאיות', 'מנהל צוות מחקר']
        elif selected_sub_category == "מתמטיקה":
            roles = ['מתמטיקאי צבאי', 'מהנדס מתמטי', 'חוקר שיטות חישוב', 'מתכנתי סימולציות', 'אנליסט טכנולוגי']
    elif selected_category == "warfare":
        if selected_sub_category == "חיל רגלים":
            roles = ['גולני', 'גבעתי', 'נח"ל', 'צנחנים', 'הנדסה קרבית']
        elif selected_sub_category == "חיל האוויר":
            roles = ['שלדג', '669', 'טייס', 'טייס מסוק','הגנה אווירית']
        elif selected_sub_category == "חיל הים":
            roles = ['שייטת 13', 'חובלים', 'שייטת 3 ', 'שירות בצוללות', 'משמר הגבולות הימיות']
    elif selected_category == "Fighting supporters":
        if selected_sub_category == "מנהלה ושלישות":
            roles = ['שליש', 'מנהל צוות לוגיסטי', 'מנהל רישום חיילים', 'יועץ לוגיסטי', 'מנהל אבטחת מידע']
        elif selected_sub_category == "שיטור":
            roles = ['שוטר צבאי', 'מפקד תחנה', 'מפקד צוות', 'חוקר שיטור', 'מנהל תיקי חקירה']
        elif selected_sub_category == "תפקידי אבטחה":
            roles = ['מאבטח מתקנים', 'מנהל אבטחה', 'חוקר אירועים', 'מפקד צוות אבטחה', 'מנהל אבטחת מידע']
    elif selected_category == "communication":
        if selected_sub_category == "ייצור תוכן":
            roles = ['עורך תוכן', 'מפיק', 'מנהל תוכן', 'תסריטאי', 'מנהל פרויקטים יצירתיים']
        elif selected_sub_category == "תשתית וטכנולוגיה":
            roles = ['מנהל רשתות', 'מפתח אינטרנט', 'מנהל מערכת', 'אנליסט טכנולוגי', 'מנהל אבטחת מידע']
        elif selected_sub_category == "מערכות מידע":
            roles = ['מנהל פרויקט IT', 'מפתח מערכות מידע', 'מנהל מסד נתונים', 'אנליסט מערכות', 'מפתח אפליקציות']
    elif selected_category == "logistics":
        if selected_sub_category == "הכשרת כוח אדם":
            roles = ['מדריך לוחמים', 'מנהל הכשרה טכנולוגית', 'מנהל צוות הכשרה', 'מאמן קרב מגע', 'מדריך חירום']
        elif selected_sub_category == "מערך ההובלה":
            roles = ['מוביל חיילים', 'מנהל שינוע', 'מפקד צוות הובלה', 'מנהל תחבורה', 'אחראי ציוד']
        elif selected_sub_category == "הכנה לחירום":
            roles = ['מפקד חירום', 'מנהל תחום חירום', 'מפקד יחידת חירום', 'מאמן חירום', 'מנהל ציוד חירום']

    conn.close()

    if request.method == "POST":
        # קבלת סדר העדיפויות מה-form
        priority_order = request.form.get("roles_order")  # כאן מתקבל סדר התפקידים ב-JSON

        # עדכון סדר העדיפויות בבסיס הנתונים
        conn = get_db_connection()
        conn.execute("UPDATE registrations SET role_priority = ? WHERE id = ?", (priority_order, user_id))
        conn.commit()
        conn.close()

        # העברה לעמוד "results"
        return redirect(url_for("results"))

    return render_template("questionary.html", roles=roles)




@app.route("/results")
def results():
    return render_template("results.html")


@app.route("/about")
def about():
    return render_template("about.html")



@app.route("/questionary")
def questionary():
    return render_template("questionary.html")


@app.route("/communication")
def communication():
    return render_template("communication.html")







@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        form = request.form
        full_name = form.get("full_name", "").strip()
        password = form.get("password", "").strip()

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


def next_selection(request):
    # קבלת הקטגוריה שבחר המשתמש מה-SESSION
    selected_category = request.session.get('selected_category')

    # הכנה של האפשרויות המתאימות לכל קטגוריה
    if selected_category == 'technology':
        options = ['פיזיקה', 'מתמטיקה', 'מדעי המחשב']
    elif selected_category == 'warfare':
        options = ['חיל רגלים', 'טיס', 'שייטת']
    else:
        options = []  # אם אין קטגוריה מוגדרת או שיש קטגוריה לא ידועה

    return render(request, 'next_selection.html', {'options': options})


def final_page(request):
    selected_category = request.session.get('selected_category')
    selected_sub_category = request.session.get('selected_sub_category')

    return render(request, 'final_page.html', {
        'selected_category': selected_category,
        'selected_sub_category': selected_sub_category
    })

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
