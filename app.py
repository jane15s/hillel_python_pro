import sqlite3

from flask import Flask, request, render_template, session, redirect
import models
from datetime import datetime
from sqlalchemy import select, desc, or_
from database import db_session, init_db

app = Flask(__name__)
app.secret_key = "hgdrY&$(ijdf_jf"
INCOME = 1
EXPENSE = 2

@app.route("/user", methods=["GET"])
def user_handler():
    if "user_id" in session:
        stmt = select(models.Transactions).filter_by(owner=session["user_id"])
        if "date_from" in request.args and "date_to" in request.args:
            date_from = datetime.strptime(request.args["date_from"], "%Y-%m-%d")
            date_to = datetime.strptime(request.args["date_to"], "%Y-%m-%d")
            stmt = stmt.filter(models.Transactions.datetime.between(date_from, date_to))
        stmt = stmt.order_by(desc(models.Transactions.datetime))
        transactions = db_session.execute(stmt).scalars().all()
        stmt_cat = select(models.Category).filter(or_(models.Category.owner == session["user_id"],models.Category.owner == 1))
        categories = db_session.execute(stmt_cat).scalars().all()
        cat_map = {c.id: c.name for c in categories}
        for t in transactions:
            t.category_name = cat_map.get(t.category, "Unknown")
        income_sum = round(sum(t.amount for t in transactions if t.type == 1), 2)
        expense_sum = round(sum(t.amount for t in transactions if t.type == 2), 2)
        balance = income_sum - expense_sum
        total = income_sum + expense_sum
        income_percent = round((income_sum / total * 100), 2) if total > 0 else 0
        expense_percent = round((expense_sum / total * 100), 2) if total > 0 else 0
        transactions_json = [
            {
                "id": t.id,
                "description": t.description,
                "category": t.category_name,
                "amount": float(t.amount),
                "datetime": t.datetime.isoformat() if t.datetime else None,
                "type": t.type,
            }
        ]
        return render_template("dashboard.html", transactions=transactions, transactions_json=transactions_json, income_sum=income_sum, expense_sum=expense_sum, income_percent=income_percent, expense_percent=expense_percent, balance=balance)
    return redirect("/login")

@app.route("/user/delete", methods=["GET"])
def delete_user():
    return "delete user"

@app.route("/login", methods=["GET", "POST"])
def get_login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form["email"]
        password = request.form["psw"]
        init_db()
        stmt = select(models.User).filter_by(email=email, password=password)
        data = db_session.execute(stmt).scalars().first()
        if data:
            session["user_id"] = data.id
            return redirect("/user")
        return redirect("/register")

@app.route("/logout", methods=["GET"])
def log_out():
    session.clear()
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def get_register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form["name"]
        surname = request.form["surname"]
        password = request.form["psw"]
        email = request.form["email"]
        birth_date_str = request.form["birthdate"]
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        gender = request.form["gender"]

        init_db()
        new_user = models.User(name=name, surname=surname, password=password, email=email, birth_date=birth_date, gender=gender)
        db_session.add(new_user)
        db_session.commit()
        session["user_id"] = new_user.id
        session["user_name"] = new_user.name
        return redirect("/user")

@app.route("/category", methods=["GET", "POST"])
def get_all_category():
    if "user_id" in session:
        init_db()
        if request.method == "GET":
            stmt = select(models.Category).filter(or_(models.Category.owner == session["user_id"],models.Category.owner == 1))
            data = db_session.execute(stmt).scalars().all()
            return render_template("user_categories.html", categories=data)
        else:
            category_name = request.form["category_name"]
            category_owner = session["user_id"]
            new_category = models.Category(name=category_name, owner=category_owner)
            db_session.add(new_category)
            db_session.commit()
            return redirect("/category")
    return redirect("/login")

@app.route("/category/<category_id>", methods=["GET"])
def get_category(category_id):
    if "user_id" in session:
        init_db()
        stmt = select(models.Category).filter_by(owner=session["user_id"], id=category_id)
        data = db_session.execute(stmt).scalars().first()
        return render_template("single_category.html", one_category=data)
    return redirect("/login")

@app.route("/category/<category_id>/edit", methods=["POST"])
def edit_category(category_id):
    if "user_id" in session:
        init_db()
        category_name = request.form["category_name"]
        stmt = select(models.Category).filter_by(owner=session["user_id"], id=category_id)
        data = db_session.execute(stmt).scalars().first()
        data.name = category_name
        db_session.commit()
        return redirect(f"/category/{category_id}")
    return redirect("/login")

@app.route("/category/<category_id>/delete", methods=["GET"])
def delete_category(category_id):
    if "user_id" in session:
        init_db()
        stmt = select(models.Category).filter_by(owner=session["user_id"], id=category_id)
        category = db_session.execute(stmt).scalars().first()
        if category:
            db_session.delete(category)
            db_session.commit()
            return redirect("/category")
        else:
            return "Category does not exist / System category"
    return redirect("/login")

@app.route("/income", methods=["GET", "POST"])
def get_all_income():
    if "user_id" in session:
        init_db()
        if request.method == "GET":
            stmt = select(models.Transactions, models.Category.name.label("category_name")).join(models.Category, models.Transactions.category == models.Category.id).filter(models.Transactions.owner == session["user_id"],models.Transactions.type == INCOME, or_(models.Category.owner == 1, models.Category.owner == session["user_id"]))
            result = db_session.execute(stmt).all()
            stmt_cat = select(models.Category).filter(or_(models.Category.owner == 1, models.Category.owner == session["user_id"]))
            categories = db_session.execute(stmt_cat).scalars().all()
            income_transactions = []
            for transaction, category_name in result:
                income_transactions.append({
                    "id": transaction.id,
                    "description": transaction.description,
                    "category_name": category_name,
                    "amount": transaction.amount,
                    "datetime": transaction.datetime
                })
            return render_template("dashboard_income.html", income_transactions=income_transactions, categories=categories)
        else:
            transaction_description = request.form["description"]
            transaction_category = int(request.form["category"])
            transaction_amount = float(request.form["amount"])
            # transaction_datetime = datetime.strptime(request.form["datetime"], "%Y-%m-%dT%H:%M")
            raw_datetime = request.form["datetime"]
            transaction_datetime = datetime.strptime(raw_datetime, "%Y-%m-%dT%H:%M")
            transaction_owner = session["user_id"]
            transaction_type = INCOME
            new_transaction = models.Transactions(description=transaction_description, category=transaction_category,
                                                 amount=transaction_amount, datetime=transaction_datetime,
                                                 owner=transaction_owner, type=transaction_type)
            db_session.add(new_transaction)
            db_session.commit()
            return redirect("/income")
    else:
        return redirect("/login")

@app.route("/income/<income_id>", methods=["GET", "POST"])
def get_income(income_id):
    if "user_id" in session:
        init_db()
        stmt = select(models.Transactions).filter_by(owner=session["user_id"], type=INCOME, id=income_id)
        transaction = db_session.execute(stmt).scalars().first()
        stmt_cat = select(models.Category).filter(or_(models.Category.owner == session["user_id"],models.Category.owner == 1))
        categories = db_session.execute(stmt_cat).scalars().all()
        transaction.category_id = transaction.category
        return render_template("income_transaction.html", transaction=transaction, categories=categories)
    return redirect("/login")

@app.route("/income/<income_id>/edit", methods=["POST"])
def edit_income(income_id):
    if "user_id" in session:
        init_db()
        transaction_description = request.form["description"]
        transaction_category = int(request.form["category"])
        transaction_amount = float(request.form["amount"])
        raw_datetime = request.form["datetime"]
        transaction_datetime = datetime.strptime(raw_datetime, "%Y-%m-%dT%H:%M")
        stmt = select(models.Transactions).filter_by(owner=session["user_id"], type=INCOME, id=income_id)
        data = db_session.execute(stmt).scalars().first()
        data.description = transaction_description
        data.category = transaction_category
        data.amount = transaction_amount
        data.datetime = transaction_datetime
        db_session.commit()
        return redirect("/income")
    return redirect("/login")

@app.route("/income/<income_id>/delete", methods=["GET"])
def delete_income(income_id):
    if "user_id" in session:
        init_db()
        stmt = select(models.Transactions).filter_by(owner=session["user_id"], type=INCOME, id=income_id)
        transaction = db_session.execute(stmt).scalars().first()
        if transaction:
            db_session.delete(transaction)
            db_session.commit()
            return redirect("/income")
        else:
            return "Transaction does not exist"
    return redirect("/login")


@app.route("/expense", methods=["GET", "POST"])
def get_all_expenses():
    if "user_id" in session:
        init_db()
        if request.method == "GET":
            stmt = select(models.Transactions, models.Category.name.label("category_name")).join(models.Category,
                                                                                                 models.Transactions.category == models.Category.id).filter(
                models.Transactions.owner == session["user_id"], models.Transactions.type == EXPENSE,
                or_(models.Category.owner == 1, models.Category.owner == session["user_id"]))
            result = db_session.execute(stmt).all()
            stmt_cat = select(models.Category).filter(
                or_(models.Category.owner == 1, models.Category.owner == session["user_id"]))
            categories = db_session.execute(stmt_cat).scalars().all()
            expense_transactions = []
            for transaction, category_name in result:
                expense_transactions.append({
                    "id": transaction.id,
                    "description": transaction.description,
                    "category_name": category_name,
                    "amount": transaction.amount,
                    "datetime": transaction.datetime
                })
            return render_template("dashboard_expense.html", expense_transactions=expense_transactions,
                                   categories=categories)
        else:
            transaction_description = request.form["description"]
            transaction_category = int(request.form["category"])
            transaction_amount = float(request.form["amount"])
            # transaction_datetime = datetime.strptime(request.form["datetime"], "%Y-%m-%dT%H:%M")
            raw_datetime = request.form["datetime"]
            transaction_datetime = datetime.strptime(raw_datetime, "%Y-%m-%dT%H:%M")
            transaction_owner = session["user_id"]
            transaction_type = EXPENSE
            new_transaction = models.Transactions(description=transaction_description, category=transaction_category,
                                                  amount=transaction_amount, datetime=transaction_datetime,
                                                  owner=transaction_owner, type=transaction_type)
            db_session.add(new_transaction)
            db_session.commit()
            return redirect("/expense")
    else:
        return redirect("/login")

@app.route("/expense/<expense_id>", methods=["GET"])
def get_expense(expense_id):
    if "user_id" in session:
        init_db()
        stmt = select(models.Transactions).filter_by(owner=session["user_id"], type=EXPENSE, id=expense_id)
        transaction = db_session.execute(stmt).scalars().first()
        stmt_cat = select(models.Category).filter(
            or_(models.Category.owner == session["user_id"], models.Category.owner == 1))
        categories = db_session.execute(stmt_cat).scalars().all()
        transaction.category_id = transaction.category
        return render_template("expense_transaction.html", transaction=transaction, categories=categories)
    return redirect("/login")

@app.route("/expense/<expense_id>/edit", methods=["POST"])
def edit_expense(expense_id):
    if "user_id" in session:
        init_db()
        transaction_description = request.form["description"]
        transaction_category = int(request.form["category"])
        transaction_amount = float(request.form["amount"])
        raw_datetime = request.form["datetime"]
        transaction_datetime = datetime.strptime(raw_datetime, "%Y-%m-%dT%H:%M")
        stmt = select(models.Transactions).filter_by(owner=session["user_id"], type=EXPENSE, id=expense_id)
        data = db_session.execute(stmt).scalars().first()
        data.description = transaction_description
        data.category = transaction_category
        data.amount = transaction_amount
        data.datetime = transaction_datetime
        db_session.commit()
        return redirect("/expense")
    return redirect("/login")

@app.route("/expense/<expense_id>/delete", methods=["GET"])
def delete_expense(expense_id):
    if "user_id" in session:
        init_db()
        stmt = select(models.Transactions).filter_by(owner=session["user_id"], type=EXPENSE, id=expense_id)
        transaction = db_session.execute(stmt).scalars().first()
        if transaction:
            db_session.delete(transaction)
            db_session.commit()
            return redirect("/expense")
        else:
            return "Transaction does not exist"
    return redirect("/login")



if __name__ == "__main__":
    app.run()