from flask import Blueprint, render_template, request, redirect, session, flash
from database.database import db
from database.models import User

auth_bp = Blueprint("auth", __name__)
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        login_id = request.form.get("login_id")
        password = request.form.get("password")

        user = User.query.filter(
            (User.email == login_id) |
            (User.employee_id == login_id)
        ).first()

        if user and user.check_password(password):

            session["user_id"] = user.id
            session["role"] = user.role

            return redirect("/dashboard")

        flash("Invalid Login")

    return render_template("login.html")

@auth_bp.route("/signup", methods=["GET","POST"])
def signup():

    if request.method=="POST":

        user=User(
            fullname=request.form["fullname"],
            email=request.form["email"],
            employee_id=request.form["employee_id"],
            department=request.form["department"],
            role="Employee"
        )

        user.set_password(request.form["password"])

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("signup.html")