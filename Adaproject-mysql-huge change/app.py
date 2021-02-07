from flask import Flask, render_template, request, url_for, redirect, abort, send_from_directory
import imghdr
import os
from werkzeug.utils import secure_filename
import mysql.connector
db = mysql.connector.connect(user="root", password="123456", database="test")
cursor = db.cursor()
user = {"name": "", "email": "", "birth": "", "selfie":"", "description": ""}
app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'

def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/map")
def map():
    return render_template("map.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/forgetpwd")
def forgetpwd():
    return render_template("forgetpwd.html")

#Welcome page
@app.route("/welcomeback")
def welcome():
    return render_template("welcomeback.html", name=user["name"])

@app.route("/profile")
def profile():
    return render_template("profile.html", name=user["name"], email=user["email"], birth=user["birth"], selfie=user["selfie"], description=user["description"])

@app.route("/logout")
def logout():
    return render_template("logout.html", name=user["name"])

@app.route("/manageProfile")
def manageProfile():
    return render_template("manageProfile.html", email=user["email"], selfie=user["selfie"], description=user["description"])

@app.route("/changepwd")
def changepwd():
    return render_template("changepwd.html")

@app.route("/share")
def share():
    return render_template("share.html")

#If someone clicks on login, they are redirected to /result
@app.route("/result", methods=['POST'])
def result():
    cursor.execute('SELECT email FROM users')
    email = cursor.fetchall()
    for e in email:
        if request.form['email'] == e[0]:
            cursor.execute('SELECT password from users WHERE email=%s',(e[0],))
            password=cursor.fetchall()
            if request.form['pass']==password[0][0]:
                cursor.execute('SELECT name from users WHERE email=%s',(e[0],))
                name=cursor.fetchall()
                cursor.execute('SELECT birth from users WHERE email=%s',(e[0],))
                birth=cursor.fetchall()
                cursor.execute('SELECT selfie from users WHERE email=%s', (e[0],))
                selfie=cursor.fetchall()
                cursor.execute('SELECT description from users WHERE email=%s', (e[0],))
                description=cursor.fetchall()
                global user
                user["name"]= name[0][0]
                user["email"]= e[0]
                user["birth"]= birth[0][0]
                user["selfie"]= selfie[0][0]
                user["description"]= description[0][0] 
                return render_template('welcomeback.html', name=user["name"])
    
    cursor.close()
    db.close()


#If someone clicks on register, they are redirected to /register
@app.route("/register", methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['pass']
    birth = request.form['birth']
    add_user = ("INSERT INTO users (name, email, birth, password, selfie, description) VALUES (%s, %s, %s, %s, %s, %s)")
    data_user = (name, email, birth, password, "user.jpg", "none")
    cursor.execute(add_user, data_user)
    db.commit()
    return render_template('login.html')
    cursor.close()
    db.close()

@app.route("/findpwd", methods=['POST'])
def findpwd():
    name = request.form['name']
    cursor.execute('SELECT email FROM users')
    email = cursor.fetchall()
    for e in email:
        if request.form['email'] == e[0]:
            cursor.execute('SELECT birth from users WHERE email=%s',(e[0],))
            birth=cursor.fetchall()
            if request.form['birth']==birth[0][0]:
                cursor.execute('SELECT password from users WHERE email=%s',(e[0],))
                password=cursor.fetchall()
                return render_template('pwdfound.html', name = name, email = e[0], password=password[0][0])

    cursor.close()
    db.close()
    
@app.route("/pwdchanged", methods=['POST'])
def changed():
    newpass=request.form['newpass']
    currentEmail = request.form['email']
    cursor.execute('SELECT email FROM users')
    email = cursor.fetchall()
    for e in email:
        if currentEmail == e[0]:
            cursor.execute('SELECT password from users WHERE email=%s', (e[0],))
            password=cursor.fetchall()
            if request.form['oldpass'] ==password[0][0]:
                user["password"] = newpass
                cursor.execute("UPDATE users SET password= %s WHERE email=%s", (newpass, currentEmail))
                db.commit()
                return render_template('pwdchanged.html', name=user["name"])
                cursor.close()
                db.close()


@app.route("/profilechanged", methods=['POST'])
def profilechanged():
    name = request.form["name"]
    birth = request.form["birth"]
    description = request.form["description"]
    uploaded_selfie = request.files['selfie']
    filename = secure_filename(uploaded_selfie.filename)
    if filename != '':
        user["selfie"] = filename
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_image(uploaded_selfie.stream):
            abort(400)
        uploaded_selfie.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    if name != '':
        user["name"] = name
    if birth != '':
        user["birth"] = birth
    if description != '':
        user["description"] = description
    cursor.execute("UPDATE users SET name=%s, birth=%s, selfie=%s, description=%s WHERE email=%s", (user["name"], user["birth"], user["selfie"], user["description"], user["email"]))
    db.commit()
    return redirect(url_for('profile'))
    cursor.close()
    db.close()

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


if __name__ == "__main__":
    app.run(debug=True, port=8888)