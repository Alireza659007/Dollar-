from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

users = {}  # username: password
coins = {}  # username: coin balance
codes = {}  # code: (amount, used)

leader_panel_code = "123098484skdA"

# قالب ساده HTML برای راحتی
template = '''
<h1>صفحه اصلی</h1>
<p><a href="/register">ثبت نام</a> | <a href="/login">ورود</a> | <a href="/leader-panel">پنل لیدر</a></p>
<h2>جدول برترین‌ها</h2>
{% for user, coin in leaderboard %}
<p>{{ user }}: ${{ coin }}</p>
{% endfor %}
<hr>
<h3>وارد کردن کد 20 رقمی (برای افزایش سکه)</h3>
<form action="/redeem" method="post">
<input name="username" placeholder="نام کاربری">
<input name="code" placeholder="کد">
<button type="submit">ثبت</button>
</form>
'''

@app.route('/')
def home():
    leaderboard = sorted(coins.items(), key=lambda x: x[1], reverse=True)
    return render_template_string(template, leaderboard=leaderboard)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return 'این نام کاربری وجود دارد.'
        users[username] = password
        coins[username] = 0
        return redirect(url_for('home'))
    return '''
    <h1>ثبت نام</h1>
    <form method="post">
    <input name="username" placeholder="نام کاربری">
    <input name="password" placeholder="رمز عبور">
    <button type="submit">ثبت نام</button>
    </form>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            return f'خوش آمدید {username}!'
        return 'نام کاربری یا رمز اشتباه است.'
    return '''
    <h1>ورود</h1>
    <form method="post">
    <input name="username" placeholder="نام کاربری">
    <input name="password" placeholder="رمز عبور">
    <button type="submit">ورود</button>
    </form>
    '''

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        sender = request.form['sender']
        receiver = request.form['receiver']
        amount = int(request.form['amount'])
        if sender in users and receiver in users and coins[sender] >= amount:
            coins[sender] -= amount
            coins[receiver] += amount
            return f'{amount}$ از {sender} به {receiver} انتقال یافت.'
        return 'موجودی کافی نیست یا کاربری یافت نشد.'
    return '''
    <h1>انتقال سکه</h1>
    <form method="post">
    <input name="sender" placeholder="فرستنده">
    <input name="receiver" placeholder="گیرنده">
    <input name="amount" placeholder="مقدار">
    <button type="submit">انتقال</button>
    </form>
    '''

@app.route('/leader-panel', methods=['GET', 'POST'])
def leader_panel():
    if request.method == 'POST':
        code = request.form['leader_code']
        if code != leader_panel_code:
            return 'کد لیدر اشتباه است.'
        new_code = request.form['new_code']
        amount = int(request.form['amount'])
        codes[new_code] = (amount, False)
        return f'کد {new_code} ساخته شد و {amount}$ ارزش دارد.'
    return '''
    <h1>پنل لیدر</h1>
    <form method="post">
    <input name="leader_code" placeholder="کد لیدر">
    <input name="new_code" placeholder="کد جدید (20 رقمی)">
    <input name="amount" placeholder="مقدار دلار">
    <button type="submit">ایجاد کد</button>
    </form>
    '''

@app.route('/redeem', methods=['POST'])
def redeem():
    username = request.form['username']
    code = request.form['code']
    if username in users and code in codes and not codes[code][1]:
        amount = codes[code][0]
        coins[username] += amount
        codes[code] = (amount, True)
        return f'{amount}$ به حساب {username} اضافه شد.'
    return 'کد نامعتبر یا تکراری.'

if __name__ == '__main__':
    app.run(debug=True)
