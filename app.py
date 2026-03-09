from flask import Flask, render_template

app = Flask(__name__)


# Flask routes
@app.route("/")
def home():
    return render_template("dashboard.html")



# Run application

if __name__ == "__main__":
    app.run(debug=True)