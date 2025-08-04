import sqlite3

from flask import Flask, request, render_template

app = Flask(__name__)

class Database:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

@app.route("/user", methods=["GET"])
def user_handler():
    return "get user"

@app.route("/user/delete", methods=["GET"]) # тут й у відповідному випадку далі - GET для можиливості перевірки. з POST на цьому етапі буде "Method NOT Allowed"
def delete_user():
    return "delete user"

@app.route("/login", methods=["GET", "POST"])
def get_login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form["email"]
        password = request.form["psw"]
        with Database("financial_tracker.db") as cursor:
            result = cursor.execute(f"SELECT * FROM user where email = '{email}' and password = '{password}'")
            data = result.fetchone()
        if data:
            return f"registered user logged in"
        return f"user does not exist. Register first"

@app.route("/register", methods=["GET", "POST"])
def get_register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form["name"]
        surname = request.form["surname"]
        password = request.form["psw"]
        email = request.form["email"]
        with Database('financial_tracker.db') as cursor:
            cursor.execute(f"INSERT INTO user (name, surname, password, email) VALUES ('{name}', '{surname}', '{password}', '{email}')")
        return f"user registered"

@app.route("/category", methods=["GET", "POST"])
def get_all_category():
    if request.method == "GET":
        return "<h1>stub for category</h1>"
    else:
        return "POST data"

@app.route("/category/<category_id>", methods=["GET"])
def get_category(category_id):
    return "<h1>stub for category_id</h1>"

@app.route("/category/<category_id>/edit", methods=["GET"])
def edit_category(category_id):
    return f"edit category - {category_id}"

@app.route("/category/<category_id>/delete", methods=["GET"])
def delete_category(category_id):
    return f"delete category - {category_id}"

@app.route("/income", methods=["GET", "POST"])
def get_all_income():
    if request.method == "GET":
        return "<h1>stub for income</h1>"
    else:
        return "POST data"

@app.route("/income/<income_id>", methods=["GET"])
def get_income(income_id):
    return "<h1>stub for income_id</h1>"

@app.route("/income/<income_id>/edit", methods=["GET"])
def edit_income(income_id):
    return f"edit income - {income_id}"

@app.route("/income/<income_id>/delete", methods=["GET"])
def delete_income(income_id):
    return f"delete income - {income_id}"


@app.route("/spend", methods=["GET", "POST"])
def get_all_spend():
    if request.method == "GET":
        return "<h1>stub for spend</h1>"
    else:
        return "POST data"

@app.route("/spend/<spend_id>", methods=["GET"])
def get_spend(spend_id):
    return "<h1>stub for spend_id</h1>"

@app.route("/spend/<spend_id>/edit", methods=["GET"])
def edit_spend(spend_id):
    return f"edit spend - {spend_id}"

@app.route("/spend/<spend_id>/delete", methods=["GET"])
def delete_spend(spend_id):
    return f"delete spend - {spend_id}"



if __name__ == "__main__":
    app.run()