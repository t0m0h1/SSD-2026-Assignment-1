from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User, log_action
from patient_records import patient_bp

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = "your_secret_key"

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# Register blueprint
app.register_blueprint(patient_bp)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Home
@app.route("/")
def home():
    return render_template("home.html")


# Register
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


# Login
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

        flash("Invalid username or password")

    return render_template("login.html")


# Logout
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

    return render_template(
        "dashboard.html",
        user=current_user.username,
        role=current_user.role
    )


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)