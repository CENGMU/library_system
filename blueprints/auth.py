from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.books"))
    return render_template("auth_login.html")

@auth_bp.post("/login")
def login_post():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        flash("用户名或密码错误", "danger")
        return redirect(url_for("auth.login"))

    login_user(user)
    flash("登录成功", "success")
    if user.role == "admin":
        return redirect(url_for("admin.panel"))
    return redirect(url_for("main.books"))

@auth_bp.get("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.books"))
    return render_template("auth_register.html")

@auth_bp.post("/register")
def register_post():
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""
    password2 = request.form.get("password2") or ""

    if not username or not password:
        flash("用户名和密码不能为空", "danger")
        return redirect(url_for("auth.register"))

    if password != password2:
        flash("两次密码不一致", "danger")
        return redirect(url_for("auth.register"))

    if User.query.filter_by(username=username).first():
        flash("用户名已存在", "danger")
        return redirect(url_for("auth.register"))

    u = User(username=username, email=email, role="user")
    u.set_password(password)
    db.session.add(u)
    db.session.commit()

    flash("注册成功，请登录", "success")
    return redirect(url_for("auth.login"))

@auth_bp.get("/logout")
def logout():
    logout_user()
    flash("已退出登录", "info")
    return redirect(url_for("auth.login"))
