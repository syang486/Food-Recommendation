from flask import Flask, render_template, request, url_for, redirect, abort, send_from_directory
import imghdr
import os
from werkzeug.utils import secure_filename
import mysql.connector
db = mysql.connector.connect(user="root", password="123456", database="test")
cursor = db.cursor()
user = {"name": "", "email": "", "birth": "", "selfie":"", "description": "", "checklists": [], "msg":"", "checklistOverview":[]}
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

@app.route("/updateNews")
def updateNews():
    return render_template("updateNews.html")

@app.route("/addList")
def addList():
    return render_template("addList.html")


@app.route("/checklist", methods=['POST', 'GET'])
def checklist():
    topic = request.form['topic']
    if (topic == ""):
        message = 'Please enter the topic!'
        return render_template("welcomeback.html", name=user["name"], checklist=user["checklists"], msg=user["msg"], msg1=message)
    else:
        cursor.execute('SELECT * from checklists WHERE topic = %s', (topic,))
        result = cursor.fetchall()
        if (result == []):
            message = 'No such checklist in the list!'
            return render_template("welcomeback.html", name=user["name"], checklist=user["checklists"], msg=user["msg"], msg1=message)
        else:
            cursor.execute('SELECT point1, point2, point3, point4, point5, point6 FROM checklists WHERE email=%s AND topic=%s', (user["email"], topic))
            points = cursor.fetchall()
            cursor.execute('SELECT content FROM checklists WHERE email=%s AND topic=%s', (user["email"], topic))
            overview = cursor.fetchall()
            return render_template("checklist.html", overview = overview, points= points, topic = topic)

@app.route("/friend1")
def friend1():
    return render_template("friend1.html")

@app.route("/friend2")
def friend2():
    return render_template("friend2.html")

@app.route("/review4")
def review4():
    return render_template("review4.html", user=user["name"])

@app.route("/review1")
def review1():
    return render_template("review1.html")

@app.route("/review2")
def review2():
    return render_template("review2.html", user=user["name"])

@app.route("/review3")
def review3():
    return render_template("review3.html")

@app.route("/addreview")
def addreview():
    return render_template("addreview.html", name=user["name"])

#Welcome page
@app.route("/welcomeback")
def welcome():
    if(user["checklists"] == []):
        return render_template("welcomeback.html", name=user["name"], checklist=user["checklists"], msg=user["msg"])
    else:
        message = ''
        return render_template("welcomeback.html", name=user["name"], checklist=user["checklists"], msg=message)
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

#If someone clicks on login, they are redirected to /result
@app.route("/result", methods=['POST','GET'])
def result():
    msg=''
    if request.method == 'POST' and 'email' in request.form and 'pass' in request.form:
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
                    cursor.execute('SELECT topic from users, checklists WHERE users.email=%s AND users.email=checklists.email',(e[0],))
                    checklists=cursor.fetchall()
                    cursor.execute('SELECT content from users, checklists WHERE users.email=%s AND users.email=checklists.email', (e[0],))
                    overview = cursor.fetchall()
                    global user
                    user["name"]= name[0][0]
                    user["email"]= e[0]
                    user["birth"]= birth[0][0]
                    user["selfie"]= selfie[0][0]
                    user["description"]= description[0][0]
                    user["checklists"] = checklists
                    user["checklistOverview"] = overview
                    if (user["checklists"] == []):
                        msg = 'Oops, You do not have checklist!'
                    user["msg"] = msg
                    return render_template('welcomeback.html', name=user["name"], checklist=user["checklists"], msg=msg)
                else:
                    msg = 'Incorrect email address/password!'
                    return render_template('login.html', msg=msg)
        msg = 'Email adress does not exist!'
        return render_template('login.html', msg = msg)        
    else:
        msg = 'Please enter the email address or the password'
        return render_template('login.html', msg = msg)
    cursor.close()
    db.close()


#If someone clicks on register, they are redirected to /register
@app.route("/register", methods=['POST','GET'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'pass' in request.form and 'birth' in request.form:
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        birth = request.form['birth']
        cursor.execute('SELECT * FROM users WHERE email = %s',(email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        else:
            add_user = ("INSERT INTO users (name, email, birth, password, selfie, description) VALUES (%s, %s, %s, %s, %s, %s)")
            data_user = (name, email, birth, password, "user.jpg", "none")
            cursor.execute(add_user, data_user)
            db.commit()
            msg = 'You have sucessfully registered!'
    else:
        msg = 'Please fill out the form!'
    return render_template('signup.html',msg=msg)
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

@app.route("/listAdded", methods=['POST'])
def listAdded():
    topic = request.form["topic"]
    overview = request.form["overview"]
    point1 = request.form["point1"]
    point2 = request.form["point2"]
    point3 = request.form["point3"]
    point4 = request.form["point4"]
    point5 = request.form["point5"]
    point6 = request.form["point6"]
    cursor.execute('INSERT INTO checklists (email, topic, content, point1, point2, point3, point4, point5, point6) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (user["email"], topic, overview, point1, point2, point3, point4, point5, point6))
    db.commit()
    cursor.execute('SELECT topic FROM checklists WHERE email=%s AND topic=%s', (user["email"], topic))
    listAdded = cursor.fetchall()
    cursor.execute('SELECT content FROM checklists WHERE email=%s AND topic=%s', (user["email"], topic))
    overview = cursor.fetchall()
    user["checklists"].append(listAdded[0])
    user["checklistOverview"].append(overview[0])
    return render_template('welcomeback.html', name=user["name"], checklist=user["checklists"], msg='')


@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


if __name__ == "__main__":
    app.run(debug=True, port=8888)