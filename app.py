from flask import Flask, render_template

app = Flask(__name__)


# Flask routes
@app.route("/")
def home():
    return render_template("dashboard.html")


# Login route

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):

            login_user(user)

            return redirect(url_for("dashboard"))

        flash("Invalid username or password")

    return render_template("login.html")




# Run application

if __name__ == "__main__":
    app.run(debug=True)