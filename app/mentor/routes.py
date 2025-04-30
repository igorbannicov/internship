from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Course

mentor_bp = Blueprint("mentor", __name__, url_prefix="/mentor")

@mentor_bp.route("/courses")
@login_required
def courses():
    if not current_user.is_mentor():
        flash("Access denied.")
        return redirect(url_for("main.index"))

    courses = Course.query.filter_by(mentor_id=current_user.id).all()
    return render_template("mentor/courses.html", courses=courses)

@mentor_bp.route("/courses/create", methods=["GET", "POST"])
@login_required
def create_course():
    if not current_user.is_mentor():
        flash("Access denied.")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        course = Course(title=title, description=description, mentor_id=current_user.id)
        db.session.add(course)
        db.session.commit()
        flash("Course created.")
        return redirect(url_for("mentor.courses"))

    return render_template("mentor/create_course.html")
