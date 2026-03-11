from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)

# Configuration to be fixed later.
# 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


# Audit Log Model
class AuditLog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50))
    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Log actions
def log_action(user, action):

    log = AuditLog(
        user=user,
        action=action
    )

    db.session.add(log)
    db.session.commit()


# User Model
class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)



# User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Home Route
@app.route("/")
def home():
    return render_template("home.html")



# Registration Route
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            password_hash=hashed_password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        log_action(username, "User registered")

        flash("Account created. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")



# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):

            login_user(user)

            log_action(username, "User logged in")

            flash("Logged in successfully")
            return redirect(url_for("dashboard"))

        else:
            flash("Invalid username or password")

    return render_template("login.html")


# Logout Route
@app.route("/logout")
@login_required
def logout():

    log_action(current_user.username, "User logged out")

    logout_user()
    flash("Logged out successfully")

    return redirect(url_for("home"))


# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():

    return render_template("dashboard.html", user=current_user.username)


# Run Application
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)