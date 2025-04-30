
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models import Course, CoursePresentation, CourseNotes, CourseQuiz, CourseHomework, CourseProgress
from werkzeug.utils import secure_filename

intern_bp = Blueprint("intern", __name__, url_prefix="/intern")

UPLOAD_FOLDER = "app/static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@intern_bp.route("/courses")
@login_required
def courses():
    if not current_user.is_intern():
        flash("Access denied.")
        return redirect(url_for("main.index"))

    courses = Course.query.all()
    return render_template("intern/courses.html", courses=courses)

@intern_bp.route("/course/<int:course_id>", methods=["GET", "POST"])
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    if not current_user.is_intern():
        flash("Access denied.")
        return redirect(url_for("main.index"))

    progress = CourseProgress.query.filter_by(intern_id=current_user.id, course_id=course.id).first()
    if not progress:
        progress = CourseProgress(intern_id=current_user.id, course_id=course.id)
        db.session.add(progress)
        db.session.commit()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "view_presentation":
            progress.presentation_viewed = True
        elif action == "pass_quiz":
            progress.quiz_passed = True
        elif action == "submit_homework" and "homework_file" in request.files:
            file = request.files["homework_file"]
            if file.filename:
                filename = secure_filename(file.filename)
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)
                progress.homework_submitted = True
                progress.submission_filename = filename
        db.session.commit()
        return redirect(url_for("intern.course_detail", course_id=course.id))

    return render_template("intern/course_detail.html", course=course, progress=progress)

@intern_bp.route("/course/<int:course_id>/quiz", methods=["GET", "POST"])
@login_required
def course_quiz(course_id):
    course = Course.query.get_or_404(course_id)
    if not current_user.is_intern():
        flash("Access denied.")
        return redirect(url_for("main.index"))

    progress = CourseProgress.query.filter_by(intern_id=current_user.id, course_id=course.id).first()
    if not progress or not progress.presentation_viewed:
        flash("You must view the presentation first.")
        return redirect(url_for("intern.course_detail", course_id=course.id))

    import json
    try:
        questions = json.loads(course.quiz.questions)
    except Exception:
        flash("Quiz is not properly formatted.")
        return redirect(url_for("intern.course_detail", course_id=course.id))

    results = []
    if request.method == "POST":
        score = 0
        for i, q in enumerate(questions):
            selected = request.form.getlist(f"q{i}")
            correct = q["answer"]
            if isinstance(correct, str):
                correct = [correct]

            is_correct = sorted(selected) == sorted(correct)
            if is_correct:
                score += 1
            results.append({
                "question": q["question"],
                "selected": selected,
                "correct": correct,
                "is_correct": is_correct
            })

        progress.quiz_passed = True
        db.session.commit()
        return render_template("intern/quiz_result.html", course=course, results=results, score=score, total=len(questions))

    return render_template("intern/quiz.html", course=course, questions=questions)


