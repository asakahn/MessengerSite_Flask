from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import random, string

app = Flask(__name__)
app.secret_key = "ThisIsASecretKey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3" # 'users' is the name of the database table
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(seconds=30)

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    friendcode = db.Column(db.String(6))
    username = db.Column(db.String(100))

    def __init__(self, email, password, friendcode, username):
        self.email = email
        self.password = password
        self.friendcode = friendcode
        self.username = username

@app.route("/", methods=["POST", "GET"])
@app.route("/home/", methods=["POST", "GET"])
def home():
    if "email" in session:
        email = session["email"]
        found_email = users.query.filter_by(email=email).first()
        if found_email.username == None:
            return redirect(url_for("registration"))
        else:
            return render_template("home.html")
    else:
        if request.method == "POST":
            session.permanent = True
            emailBeforeLower = (request.form["email"])
            email = emailBeforeLower.lower()
            password = request.form["password"]
            session["email"] = email
            session["password"] = password

            if emailBeforeLower == None or password == None or emailBeforeLower == "" or password == "":
                session.pop("email", None)
                session.pop("password", None)
                session.pop("friendcode", None)
                session.pop("username", None)
                flash("Please enter your details below.")
            else:
                found_email = users.query.filter_by(email=email).first()

                if found_email:
                    if password == found_email.password:
                        print("Password match")
                        if found_email.username == None:
                            return redirect(url_for("registration"))
                        else:
                            return render_template("home.html")
                    else:
                        flash("Password does not match with this account.")
                else:
                    usr = users(email, password, "", None)
                    db.session.add(usr)
                    db.session.commit()
                    print("New account registered")
                    return redirect(url_for("registration"))

        return render_template("login.html")

@app.route("/registration/", methods=["POST", "GET"])
def registration():
    username = None
    if "email" in session:
        email = session["email"]
        found_email = users.query.filter_by(email=email).first()
        if found_email.username == None:
            if request.method == "POST":
                counter = 1 # Counter for while to check whether friend code exists or not
                friendcode = ""
                while counter == 1:
                    def get_random_string(length): # Generate random string for "friend" code
                        letters = string.ascii_uppercase
                        result_str = ''.join(random.choice(letters) for i in range(length))
                        return result_str

                    CheckIfCodeExists = get_random_string(6)
                    found_friendcode = users.query.filter_by(friendcode=CheckIfCodeExists).first()
                    if found_friendcode:
                        continue
                    else:
                        friendcode = CheckIfCodeExists
                        counter = 0
                        break

                session["friendcode"] = friendcode
                username = request.form["username"]
                session["username"] = username
                found_email.username = username
                found_email.friendcode = friendcode
                db.session.commit()
                print("Username saved")
                return redirect(url_for("home"))
        else:
            return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))


    return render_template("registration.html")

@app.route("/friends/")
def friends():
    if "email" in session:
        email = session["email"]
        found_email = users.query.filter_by(email=email).first()
        if found_email.username == None:
            return redirect(url_for("registration"))
        else:
            friendcode = found_email.friendcode
            username = found_email.username
            return render_template("friends.html", friendcode=friendcode, username=username) # LEFT OFF HERE, need to create a new database for friends names
    else:
        return redirect(url_for("registration"))

@app.route("/logout/")
def logout():
    if "email" in session:
        flash("You have been logged out.")
    session.pop("email", None)
    session.pop("password", None)
    session.pop("friendcode", None)
    session.pop("username", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
