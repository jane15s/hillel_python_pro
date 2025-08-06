import sqlite3

from flask import Flask, request, render_template, session, redirect

app = Flask(__name__)
app.secret_key = "hgdrY&$(ijdf_jf"
INCOME = 1
EXPENSE = 2

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
            result = cursor.execute(f"SELECT id FROM user where email = '{email}' and password = '{password}'")
            data = result.fetchone()
        if data:
            session["user_id"] = data[0]
            return redirect("/income")
        return redirect("/register")

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
        return redirect("/income")

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
    if "user_id" in session:
        if request.method == "GET":
            with Database("financial_tracker.db") as cursor:
                data = cursor.execute(f"SELECT * FROM 'transaction' where owner = {session["user_id"]} and type = {INCOME}")
                result = data.fetchall()
            return render_template("dashboard.html", income_transactions=result)
        else:
            with Database("financial_tracker.db") as cursor:
                transaction_description = request.form["description"]
                transaction_category = request.form["category"]
                transaction_amount = request.form["amount"]
                transaction_datetime = request.form["datetime"]
                transaction_owner = session["user_id"]
                transaction_type = INCOME
                cursor.execute(f"INSERT INTO 'transaction' (description, category, amount, datetime, owner, type) VALUES ('{transaction_description}', '{transaction_category}', '{transaction_amount}', '{transaction_datetime}', '{transaction_owner}', '{transaction_type}')")
            return redirect("/income")
    else:
        return redirect("/login")

@app.route("/income/<income_id>", methods=["GET"])
def get_income(income_id):
    return "<h1>stub for income_id</h1>"

@app.route("/income/<income_id>/edit", methods=["GET"])
def edit_income(income_id):
    return f"edit income - {income_id}"

@app.route("/income/<income_id>/delete", methods=["GET"])
def delete_income(income_id):
    return f"delete income - {income_id}"


@app.route("/expense", methods=["GET", "POST"])
def get_all_expenses():
    if "user_id" in session:
        if request.method == "GET":
            with Database("financial_tracker.db") as cursor:
                data = cursor.execute(
                    f"SELECT * FROM 'transaction' where owner = {session["user_id"]} and type = {EXPENSE}")
                result = data.fetchall()
            return render_template("dashboard.html", expense_transactions=result)
        else:
            with Database("financial_tracker.db") as cursor:
                transaction_description = request.form["description"]
                transaction_category = request.form["category"]
                transaction_amount = request.form["amount"]
                transaction_datetime = request.form["datetime"]
                transaction_owner = session["user_id"]
                transaction_type = EXPENSE
                cursor.execute(
                    f"INSERT INTO 'transaction' (description, category, amount, datetime, owner, type) VALUES ('{transaction_description}', '{transaction_category}', '{transaction_amount}', '{transaction_datetime}', '{transaction_owner}', '{transaction_type}')")
            return redirect("/expense")
    else:
        return redirect("/login")

@app.route("/expense/<expense_id>", methods=["GET"])
def get_expense(expense_id):
    return "<h1>stub for expense_id</h1>"

@app.route("/expense/<expense_id>/edit", methods=["GET"])
def edit_expense(expense_id):
    return f"edit expense - {expense_id}"

@app.route("/expense/<expense_id>/delete", methods=["GET"])
def delete_expense(expense_id):
    return f"delete expense - {expense_id}"



if __name__ == "__main__":
    app.run()