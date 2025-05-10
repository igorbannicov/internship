# coding=utf-8
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

    my_courses = Course.query.filter_by(mentor_id=current_user.id).all()
    return render_template("mentor/courses.html", courses=my_courses)

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


@mentor_bp.route("/course/<int:course_id>/dashboard")
@login_required
def course_dashboard(course_id):
    from app.models import QuizResult, CourseProgress, Course
    course = Course.query.get_or_404(course_id)
    if course.mentor_id != current_user.id:
        flash("Access denied")
        return redirect(url_for("main.index"))

    quiz_results = QuizResult.query.filter_by(course_id=course.id).all()
    progresses = CourseProgress.query.filter_by(course_id=course.id).all()

    quiz_labels = [r.intern.name for r in quiz_results]
    quiz_scores = [round(r.score / r.total * 100, 1) if r.total else 0 for r in quiz_results]

    hw_submitted = sum(1 for p in progresses if p.homework_submitted)
    hw_not_submitted = len(progresses) - hw_submitted

    return render_template("mentor/dashboard.html", course=course,
                           quiz_results=quiz_results,
                           progresses=progresses,
                           quiz_labels=quiz_labels,
                           quiz_scores=quiz_scores,
                           hw_submitted=hw_submitted,
                           hw_not_submitted=hw_not_submitted)
