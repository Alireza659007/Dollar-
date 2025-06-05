from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

# پایگاه داده موقت در حافظه
users = {}
codes = {}
banned_users = []

html = """
<!DOCTYPE html>
<html>
<head>
  <title>سامانه ثبت‌نام با کد</title>
  <meta charset="UTF-8">
  <style>
    body { font-family: sans-serif; direction: rtl; text-align: center; }
    input, button { margin: 5px; padding: 10px; font-size: 16px; }
    #output { margin-top: 20px; color: #333; font-weight: bold; }
  </style>
</head>
<body>
  <h1>سامانه مدیریت کاربران</h1>

  <h2>ثبت نام</h2>
  <input id="username" placeholder="نام کاربری">
  <input id="code" placeholder="کد">
  <button onclick="register()">ثبت نام</button>

  <h2>بررسی ثبت‌نام</h2>
  <input id="checkUser" placeholder="نام کاربری">
  <button onclick="checkCode()">بررسی</button>

  <h2>پنل مدیریت</h2>
  <input id="adminCode" placeholder="افزودن کد">
  <button onclick="addCode()">افزودن</button><br>
  <input id="banUser" placeholder="بن کردن کاربر">
  <button onclick="ban()">بن</button>

  <p id="output"></p>

  <script>
    function showMessage(msg) {
      document.getElementById('output').innerText = msg;
    }

    function register() {
      fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          username: document.getElementById('username').value,
          code: document.getElementById('code').value
        })
      }).then(res => res.json()).then(data => showMessage(data.message));
    }

    function checkCode() {
      fetch('/check', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          username: document.getElementById('checkUser').value
        })
      }).then(res => res.json()).then(data => showMessage(data.message));
    }

    function addCode() {
      fetch('/add_code', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          code: document.getElementById('adminCode').value
        })
      }).then(res => res.json()).then(data => showMessage(data.message));
    }

    function ban() {
      fetch('/ban', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          username: document.getElementById('banUser').value
        })
      }).then(res => res.json()).then(data => showMessage(data.message));
    }
  </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    code = data['code']
    if username in banned_users:
        return jsonify({'message': 'شما بن شده‌اید.'})
    if username in users:
        return jsonify({'message': 'قبلاً ثبت نام کرده‌اید.'})
    if code not in codes:
        return jsonify({'message': 'کد اشتباه است.'})
    users[username] = code
    del codes[code]
    return jsonify({'message': 'ثبت‌نام با موفقیت انجام شد.'})

@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    username = data['username']
    if username in users:
        return jsonify({'message': f'ثبت نام شده با کد: {users[username]}'})
    return jsonify({'message': 'کاربری یافت نشد.'})

@app.route('/add_code', methods=['POST'])
def add_code():
    data = request.get_json()
    code = data['code']
    if code in codes:
        return jsonify({'message': 'کد قبلاً اضافه شده.'})
    codes[code] = True
    return jsonify({'message': 'کد اضافه شد.'})

@app.route('/ban', methods=['POST'])
def ban():
    data = request.get_json()
    username = data['username']
    if username not in banned_users:
        banned_users.append(username)
    return jsonify({'message': 'کاربر بن شد.'})

if __name__ == '__main__':
    app.run(debug=True)
