from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import check_password_hash

app = Flask(__name__)


login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)



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