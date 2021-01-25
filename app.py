import pyrebase
from flask import *
import imghdr
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)

config = {
	"apiKey": "AIzaSyBODB7dC9A9qSGsxS4yOU0kQ-_trZGQP-8",
    "authDomain": "food-e26c4.firebaseapp.com",
    "databaseURL": "https://food-e26c4-default-rtdb.firebaseio.com",
    "projectId": "food-e26c4",
    "storageBucket": "food-e26c4.appspot.com",
    "messagingSenderId": "98615884845"
}

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'

firebase = pyrebase.initialize_app(config)
db = firebase.database()
st = firebase.storage()
auth=firebase.auth()
person = {"is_logged_in": False, "name": "", "email": "", "uid": "", "password": "", "selfieId": ""}

def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/welcome')
def welcome():
    if person["is_logged_in"] == True:
        return render_template('welcome.html', name = person["name"])
    else:
        return redirect(url_for('login'))

@app.route('/forgetpwd')
def forgetpwd():
    return render_template('forgetpwd.html')

@app.route('/profile')
def home():
    return render_template('profile.html', name = person["name"], emailAddress = person["email"])

@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = auth.sign_in_with_email_and_password(email, password)
        global person
        person["is_logged_in"] = True
        person["email"] = user["email"]
        person["uid"] = user["localId"]
        person["password"] = password
        data = db.child("users").get()
        person["name"] = data.val()[person["uid"]]["name"]
        return redirect(url_for('welcome'))
    return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name'] 
        email = request.form['email']
        password = request.form['password']
        user = auth.create_user_with_email_and_password(email, password)
        if request.form['submit'] == 'Sign Up':
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)
            return redirect(url_for('login'))
        return render_template('signup.html')
    return render_template('signup.html')

@app.route('/resetpwd', methods=['POST', 'GET'])
def resetpwd():
    if request.form == 'POST':
        name = request.form['name']
        email = request.form['email']

        reset_email = auth.send_password_reset_email(email)
        return render_template('login.html')
    return render_template('login.html')

@app.route('/updateProfile', methods=['POST', 'GET'])
def updateProfile():
    if request.form == 'POST':
        uploaded_selfie = request.files['selfie']
        filename = secure_filename(uploaded_selfie.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_image(uploaded_selfie.stream):
                abort(400)
            uploaded_selfie.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return redirect(url_for('updateProfile'))

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

if __name__ == '__main__':
	app.run(debug=True)