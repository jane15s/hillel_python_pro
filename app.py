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
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

class DBwrapper:
    def insert(self, table, data):
        with Database("financial_tracker.db") as cursor:
            columns = ', '.join([f'"{col}"' for col in data.keys()])
            placeholders = ', '.join(['?'] * len(data))
            values = list(data.values())
            query = f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})'
            cursor.execute(query, values)

    def select(self, table, params=None):
        with Database("financial_tracker.db") as cursor:
            query = f'SELECT * FROM "{table}"'
            values = []
            if params:
                result_params = []
                for key, value in params.items():
                    if isinstance(value, list) or isinstance(value, tuple):
                        placeholders = ', '.join(['?'] * len(value))
                        result_params.append(f'"{key}" IN ({placeholders})')
                        values.extend(value)
                    else:
                        result_params.append(f'"{key}" = ?')
                        values.append(value)
                query += " WHERE " + " AND ".join(result_params)
            cursor.execute(query, values)
            return cursor.fetchall()

@app.route("/user", methods=["GET"])
def user_handler():
    if "user_id" in session:
        db = DBwrapper()
        data = db.select("transactions", {"owner": session["user_id"]})
        transactions = [dict(row) for row in data]
        transactions.sort(key=lambda x: x["datetime"], reverse=True)
        return render_template("dashboard.html", transactions=transactions)
    return redirect("/login")

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
        db = DBwrapper()
        data = db.select("user", {"email": email, "password": password})
        if data:
            session["user_id"] = data[0]["id"]
            return redirect("/user")
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
        db = DBwrapper()
        db.insert("user", {"name": name, "surname": surname, "password": password, "email": email})
        return redirect("/user")

@app.route("/category", methods=["GET", "POST"])
def get_all_category():
    if "user_id" in session:
        db = DBwrapper()
        if request.method == "GET":
            data = db.select("category", {"owner": [session["user_id"], 1]})
            return render_template("user_categories.html", categories=data)
        else:
            category_name = request.form["category_name"]
            category_owner = session["user_id"]
            db.insert("category", {"name": category_name, "owner": category_owner})
            return redirect("/category")
    return redirect("/login")

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
        db = DBwrapper()
        if request.method == "GET":
            data = db.select("transactions", {"owner": session["user_id"], "type": INCOME})
            income_transactions = [dict(row) for row in data]
            return render_template("dashboard_income.html", income_transactions=income_transactions)
        else:
            transaction_description = request.form["description"]
            transaction_category = request.form["category"]
            transaction_amount = float(request.form["amount"])
            transaction_datetime = request.form["datetime"]
            transaction_owner = session["user_id"]
            transaction_type = INCOME
            db.insert("transactions",{"description": transaction_description, "category": transaction_category, "amount": transaction_amount, "datetime": transaction_datetime, "owner": transaction_owner, "type": transaction_type})
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
        db = DBwrapper()
        if request.method == "GET":
            data = db.select("transactions", {"owner": session["user_id"], "type": EXPENSE})
            expense_transactions = [dict(row) for row in data]
            return render_template("dashboard_expense.html", expense_transactions=expense_transactions)
        else:
            transaction_description = request.form["description"]
            transaction_category = request.form["category"]
            transaction_amount = float(request.form["amount"])
            transaction_datetime = request.form["datetime"]
            transaction_owner = session["user_id"]
            transaction_type = EXPENSE
            db.insert("transactions", {"description": transaction_description, "category": transaction_category, "amount": transaction_amount, "datetime": transaction_datetime, "owner": transaction_owner, "type": transaction_type})
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