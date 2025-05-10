# coding=utf-8

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/users")
@login_required
def users():
    if not current_user.is_admin():
        flash("Access denied.")
        return redirect(url_for("main.index"))

    my_users = User.query.all()
    return render_template("admin/users.html", users=my_users)

@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        flash("Access denied.")
        return redirect(url_for("main.index"))

    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        flash("You cannot delete another admin.")
        return redirect(url_for("admin.users"))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted.")
    return redirect(url_for("admin.users"))

@admin_bp.route("/users/<int:user_id>/toggle_active", methods=["POST"])
@login_required
def toggle_active(user_id):
    if not current_user.is_admin():
        flash("Access denied.")
        return redirect(url_for("main.index"))

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f"User {'activated' if user.is_active else 'deactivated'}.")
    return redirect(url_for("admin.users"))

@admin_bp.route("/users/<int:user_id>/reset_password", methods=["POST"])
@login_required
def reset_password(user_id):
    if not current_user.is_admin():
        flash("Access denied.")
        return redirect(url_for("main.index"))

    new_password = request.form.get("new_password")
    if not new_password:
        flash("Password cannot be empty.")
        return redirect(url_for("admin.users"))

    user = User.query.get_or_404(user_id)
    user.set_password(new_password)
    db.session.commit()
    flash("Password updated.")
    return redirect(url_for("admin.users"))

@admin_bp.route("/courses")
@login_required
def all_courses():
    if not current_user.is_admin():
        flash("Access denied.")
        return redirect(url_for("main.index"))

    from app.models import Course
    courses = Course.query.all()
    return render_template("admin/courses.html", courses=courses)

@admin_bp.route("/courses/<int:course_id>/delete", methods=["POST"])
@login_required
def delete_course(course_id):
    if not current_user.is_admin():
        flash("Access denied.")
        return redirect(url_for("main.index"))

    from app.models import Course
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted.")
    return redirect(url_for("admin.all_courses"))
