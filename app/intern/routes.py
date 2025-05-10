# coding=utf-8

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Course, CourseProgress
from werkzeug.utils import secure_filename
import json

intern_bp = Blueprint("intern", __name__, url_prefix="/intern")

UPLOAD_FOLDER = "app/static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@intern_bp.route("/courses")
@login_required
def courses():
    if not current_user.is_intern():
        flash("Access denied.")
        return redirect(url_for("main.index"))

    my_courses = Course.query.all()
    return render_template("intern/courses.html", courses=my_courses)

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
    from app.models import QuizResult

    course = Course.query.get_or_404(course_id)
    if not current_user.is_intern():
        return "Access denied", 403

    progress = CourseProgress.query.filter_by(intern_id=current_user.id, course_id=course.id).first()
    if not progress or not progress.presentation_viewed:
        return "You must view the presentation first.", 403

    try:
        questions = json.loads(course.quiz.questions)
    except Exception as e:
        print(e)
        return "Quiz format error", 400


    if request.method == "POST":
        data = request.get_json()
        user_answers = data.get("answers", [])

        score = 0
        results = []
        for user_answer in user_answers:
            question_text = user_answer.get("question")
            selected = user_answer.get("selected", [])

            q = next((q for q in questions if q["question"] == question_text), None)
            if not q:
                continue

            correct = q["answer"]
            if isinstance(correct, str):
                correct = [correct]

            is_correct = sorted(selected) == sorted(correct)
            if is_correct:
                score += 1

            results.append({
                "question": question_text,
                "selected": selected,
                "correct": correct,
                "is_correct": is_correct
            })

        progress.quiz_passed = True
        db.session.commit()

        result = QuizResult(intern_id=current_user.id, course_id=course.id, score=score, total=len(questions))
        db.session.add(result)
        db.session.commit()

        return render_template("intern/quiz_result.html", course=course, results=results, score=score, total=len(questions))

    return render_template("intern/quiz.html", course=course, questions=questions)





