from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User:
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)
    
    def delete(self):
        # Implement user deletion logic here
        pass


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         # save user to the database later:

#         flash("Registration successful! Please log in.")
#         return redirect(url_for("login"))
#     return render_template("register.html")


# Flask routes
@app.route("/")
def home():
    return render_template("home.html")


# Login route
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         # user = User.query.filter_by(username=username).first()
#         if user and check_password_hash(user.password_hash, password):
#             login_user(user)
#             return redirect(url_for("dashboard"))
#         flash("Invalid username or password")
#     return render_template("login.html")


# Run application
if __name__ == "__main__":
    app.run(debug=True)