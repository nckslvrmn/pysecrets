from flask import Flask, render_template
from pysecrets.handlers import encrypt, decrypt
from pysecrets.helpers import load_env


app = Flask(__name__)
with app.app_context():
    load_env()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/files", methods=["GET"])
def files():
    return render_template("files.html")


@app.route("/secret/<secret_id>", methods=["GET"])
def secret(secret_id):
    return render_template("secret.html")


@app.route("/encrypt", methods=["POST"])
def enc():
    return encrypt()


@app.route("/decrypt", methods=["POST"])
def dec():
    return decrypt()


if __name__ == "__main__":
    app.run()
