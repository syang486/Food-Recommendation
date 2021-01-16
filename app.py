import pyrebase
from flask import *
app = Flask(__name__)

config = {
	"apiKey": "AIzaSyBODB7dC9A9qSGsxS4yOU0kQ-_trZGQP-8",
    "authDomain": "food-e26c4.firebaseapp.com",
    "databaseURL": "https://food-e26c4-default-rtdb.firebaseio.com",
    "projectId": "food-e26c4",
    "storageBucket": "food-e26c4.appspot.com",
    "messagingSenderId": "98615884845"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth=firebase.auth()
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/welcome')
def welcome():
    if person["is_logged_in"] == True:
        return render_template('welcome.html', name = person["name"], emailAddress = person["email"])
    else:
        return redirect(url_for('login'))


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

if __name__ == '__main__':
	app.run(debug=True)