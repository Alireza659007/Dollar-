from flask import Flask, render_template_string, request, redirect, session, url_for, flash
import json
import os
import random
import string

app = Flask(__name__)
app.secret_key = "secret123"  # حتما برای امنیت، یه کلید پیچیده بگذار

DATA_FILE = "data.json"
LEADER_CODE = "123098484skdA"  # کد پنل لیدر ثابت

# بارگذاری داده‌ها از فایل
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "leader_codes": {}}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ذخیره داده‌ها در فایل
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ساخت کد ۲۰ رقمی
def generate_code(length=20):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# صفحه اصلی (ورود یا ثبت نام)
@app.route("/", methods=["GET", "POST"])
def index():
    data = load_data()
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        if not username or not password:
            flash("نام کاربری و رمز عبور را وارد کنید")
            return redirect("/")
        if username in data["users"]:
            # ورود
            if data["users"][username]["password"] == password:
                session["user"] = username
                if username == "leader":
                    return redirect("/leader")
                else:
                    return redirect("/dashboard")
            else:
                flash("رمز عبور اشتباه است")
                return redirect("/")
        else:
            # ثبت نام
            data["users"][username] = {"password": password, "coins": 0}
            save_data(data)
            session["user"] = username
            return redirect("/dashboard")
    return render_template_string(INDEX_HTML)

# پنل کاربر عادی
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")
    data = load_data()
    user = session["user"]
    if request.method == "POST":
        code = request.form.get("code").strip()
        # چک کدهای ۲۰ رقمی لیدر
        if code in data["leader_codes"]:
            add_coins = data["leader_codes"].pop(code)
            data["users"][user]["coins"] += add_coins
            flash(f"{add_coins} دلار به حساب شما اضافه شد!")
            save_data(data)
        else:
            flash("کد معتبر نیست یا استفاده شده است")
        return redirect("/dashboard")
    # جدول امتیازات
    leaderboard = sorted(data["users"].items(), key=lambda x: x[1]["coins"], reverse=True)
    return render_template_string(DASHBOARD_HTML, username=user, coins=data["users"][user]["coins"], leaderboard=leaderboard)

# انتقال سکه بین کاربران
@app.route("/transfer", methods=["POST"])
def transfer():
    if "user" not in session:
        return redirect("/")
    data = load_data()
    sender = session["user"]
    receiver = request.form.get("receiver").strip()
    amount = int(request.form.get("amount"))
    if receiver not in data["users"]:
        flash("کاربر گیرنده وجود ندارد")
    elif amount <= 0:
        flash("مقدار انتقال باید مثبت باشد")
    elif data["users"][sender]["coins"] < amount:
        flash("سکه کافی ندارید")
    else:
        data["users"][sender]["coins"] -= amount
        data["users"][receiver]["coins"] += amount
        flash("انتقال با موفقیت انجام شد")
        save_data(data)
    return redirect("/dashboard")

# پنل لیدر
@app.route("/leader", methods=["GET", "POST"])
def leader():
    if "user" not in session or session["user"] != "leader":
        return redirect("/")
    data = load_data()
    if request.method == "POST":
        try:
            add_amount = int(request.form.get("add_amount"))
            if add_amount <= 0:
                flash("مقدار باید بزرگتر از صفر باشد")
                return redirect("/leader")
        except:
            flash("مقدار نامعتبر است")
            return redirect("/leader")
        new_code = generate_code()
        data["leader_codes"][new_code] = add_amount
        save_data(data)
        flash(f"کد {new_code} ساخته شد که {add_amount} دلار اضافه می‌کند")
        return redirect("/leader")
    return render_template_string(LEADER_HTML, leader_codes=data["leader_codes"])

# خروج
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# قالب‌ها (HTML ساده)
INDEX_HTML = """
<!DOCTYPE html>
<html lang="fa">
<head><meta charset="UTF-8" /><title>ورود یا ثبت نام</title></head>
<body>
<h2>ورود یا ثبت نام</h2>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul style="color:red;">
      {% for m in messages %}
        <li>{{m}}</li>
      {% endfor %}
    </ul>
  {% endif %}
{% endwith %}
<form method="post">
  <input name="username" placeholder="نام کاربری" required /><br/>
  <input name="password" placeholder="رمز عبور" type="password" required /><br/>
  <button type="submit">ورود / ثبت نام</button>
</form>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="fa">
<head><meta charset="UTF-8" /><title>پنل کاربر</title></head>
<body>
<h2>خوش آمدید، {{username}}</h2>
<p>سکه شما: {{coins}} دلار</p>

<form method="post">
  <input name="code" placeholder="کد ۲۰ رقمی وارد کنید" required />
  <button type="submit">افزودن سکه</button>
</form>

<h3>انتقال سکه</h3>
<form action="/transfer" method="post">
  <input name="receiver" placeholder="نام کاربری گیرنده" required />
  <input name="amount" type="number" min="1" placeholder="مقدار سکه" required />
  <button type="submit">انتقال</button>
</form>

<h3>جدول برترین‌ها</h3>
<table border="1" cellpadding="5" cellspacing="0">
  <tr><th>رتبه</th><th>نام کاربری</th><th>سکه</th></tr>
  {% for i, (user, data) in enumerate(leaderboard) %}
  <tr>
    <td>{{i+1}}</td>
    <td>{{user}}</td>
    <td>{{data.coins}}</td>
  </tr>
  {% endfor %}
</table>

<p><a href="/logout">خروج</a></p>

{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul style="color:red;">
      {% for m in messages %}
        <li>{{m}}</li>
      {% endfor %}
    </ul>
  {% endif %}
{% endwith %}
</body>
</html>
"""

LEADER_HTML = """
<!DOCTYPE html>
<html lang="fa">
<head><meta charset="UTF-8" /><title>پنل لیدر</title></head>
<body>
<h2>پنل لیدر</h2>

<form method="post">
  <input name="add_amount" type="number" min="1" placeholder="چند دلار اضافه شود؟" required />
  <button type="submit">ساخت کد ۲۰ رقمی</button>
</form>

<h3>کدهای ساخته شده</h3>
<ul>
  {% for code, val in leader_codes.items() %}
  <li>{{code}} - مقدار: {{val}} دلار</li>
  {% endfor %}
</ul>

<p><a href="/logout">خروج</a></p>

{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul style="color:red;">
      {% for m in messages %}
        <li>{{m}}</li>
      {% endfor %}
    </ul>
  {% endif %}
{% endwith %}
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
