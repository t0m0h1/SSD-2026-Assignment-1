from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from auth import role_required

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


# helper function (for username validation)
def is_valid_username(username):
    if not username:
        return False, "Username is required"

    if len(username) < 3 or len(username) > 20:
        return False, "Username must be between 3 and 20 characters"

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"

    return True, ""


# helper function (for password validation)
import re
import time

def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not re.search(r"[A-Z]", password):
        return False, "Must include an uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Must include a lowercase letter"

    if not re.search(r"[0-9]", password):
        return False, "Must include a number"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Must include a special character"

    return True, ""
    

COMMON_PASSWORDS = ["password", "123456", "qwerty", "admin"]

# Simple in-memory login protection
login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 60




# Register route with new admin code
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        admin_code_entered = request.form.get("admin_code", "").strip()

        # Default role is user
        role = "user"
        ADMIN_SECRET_CODE = "123"  # This would be replaced with something much more secure in deployment...

        # assign admin role if correct
        if admin_code_entered == ADMIN_SECRET_CODE:
            role = "admin"

        # Empty field check
        if not username or not password or not confirm_password:
            flash("All fields are required")
            return redirect(url_for("register"))

        # Validate username
        valid, message = is_valid_username(username)
        if not valid:
            flash(message)
            return redirect(url_for("register"))

        # Normalise username
        username = username.lower()

        # Prevent overly large input (DoS protection)
        if len(password) > 128:
            flash("Password too long")
            return redirect(url_for("register"))

        # Check if username exists
        from sqlalchemy import func
        existing_user = User.query.filter(
            func.lower(User.username) == username.lower()
        ).first()

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        # Password match check
        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for("register"))

        # Common password check
        if password.lower() in COMMON_PASSWORDS:
            flash("Password is too common")
            return redirect(url_for("register"))

        # Strength check
        valid, message = is_strong_password(password)
        if not valid:
            flash(message)
            return redirect(url_for("register"))

        # Hash password
        hashed_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=16
        )

        # Create user with role
        new_user = User(
            username=username,
            password_hash=hashed_password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        log_action(username, f"User registered as {role}")

        flash(f"Account created as {role}. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")







# Login route
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        ip = request.remote_addr

        # Check lockout
        if ip in login_attempts:
            attempts, last_attempt = login_attempts[ip]

            if attempts >= MAX_ATTEMPTS and time.time() - last_attempt < LOCKOUT_TIME:
                flash("Too many login attempts. Try again later.")
                return redirect(url_for("login"))

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):

            # Reset attempts on success
            login_attempts.pop(ip, None)

            login_user(user)
            log_action(username, "User logged in")

            flash("Logged in successfully")
            return redirect(url_for("dashboard"))

        else:
            # Track failed attempts
            if ip not in login_attempts:
                login_attempts[ip] = [1, time.time()]
            else:
                login_attempts[ip][0] += 1
                login_attempts[ip][1] = time.time()

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




# Admin panel
@app.route("/admin")
@login_required
@role_required("admin")
def admin_panel():
    return render_template("admin.html")


# Driver code to run app
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)