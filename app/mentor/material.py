# coding=utf-8

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Course, CoursePresentation, CourseNotes, CourseQuiz, CourseHomework
import os
from werkzeug.utils import secure_filename

material_bp = Blueprint("material", __name__, url_prefix="/mentor/course/<int:course_id>")

def check_course_owner(course_id):
    course = Course.query.get_or_404(course_id)
    if course.mentor_id != current_user.id:
        flash("Access denied.")
        return None
    return course



from app.utils.converter import convert_pptx_to_pdf

@material_bp.route("/presentation", methods=["GET", "POST"])
@login_required
def presentation(course_id):
    course = check_course_owner(course_id)
    if not course:
        return redirect(url_for("main.index"))

    my_presentation = course.presentation or CoursePresentation(course_id=course.id, filename="")
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1].lower()
            upload_folder = "app/static/uploads"
            os.makedirs(upload_folder, exist_ok=True)

            source_path = os.path.join(upload_folder, filename)
            file.save(source_path)

            # If PowerPoint → convert to PDF
            if ext == ".pptx":
                pdf_filename = convert_pptx_to_pdf(source_path, upload_folder)
                if pdf_filename:
                    my_presentation.filename = pdf_filename
                else:
                    flash("PowerPoint conversion failed.")
                    return redirect(url_for("material.presentation", course_id=course.id))
            elif ext == ".pdf":
                my_presentation.filename = filename
            else:
                flash("Only PDF or PPTX supported.")
                return redirect(url_for("material.presentation", course_id=course.id))

            db.session.add(my_presentation)
            db.session.commit()
            flash("Presentation uploaded.")
            return redirect(url_for("mentor.courses"))
        flash("No file selected.")
    return render_template("mentor/upload_presentation.html", file=my_presentation.filename if my_presentation.filename else None)

@material_bp.route("/notes", methods=["GET", "POST"])
@login_required
def notes(course_id):
    course = check_course_owner(course_id)
    if not course:
        return redirect(url_for("main.index"))

    my_notes = course.notes or CourseNotes(course_id=course.id, content="")
    if request.method == "POST":
        my_notes.content = request.form["content"]
        db.session.add(my_notes)
        db.session.commit()
        flash("Notes saved.")
        return redirect(url_for("mentor.courses"))

    return render_template("mentor/material_form.html", title="Edit Notes", material=my_notes.content)

@material_bp.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz(course_id):
    course = check_course_owner(course_id)
    if not course:
        return redirect(url_for("main.index"))

    my_quiz = course.quiz or CourseQuiz(course_id=course.id, questions="")
    if request.method == "POST":
        my_quiz.questions = request.form["content"]
        db.session.add(my_quiz)
        db.session.commit()
        flash("Quiz saved.")
        return redirect(url_for("mentor.courses"))

    return render_template("mentor/material_form.html", title="Edit Quiz (JSON)", material=my_quiz.questions)

@material_bp.route("/homework", methods=["GET", "POST"])
@login_required
def homework(course_id):
    course = check_course_owner(course_id)
    if not course:
        return redirect(url_for("main.index"))

    hw = course.homework or CourseHomework(course_id=course.id, instructions="")
    if request.method == "POST":
        hw.instructions = request.form["content"]
        db.session.add(hw)
        db.session.commit()
        flash("Homework saved.")
        return redirect(url_for("mentor.courses"))

    return render_template("mentor/material_form.html", title="Edit Homework", material=hw.instructions)


@material_bp.route("/quiz_builder", methods=["GET", "POST"])
@login_required
def quiz_builder(course_id):
    course = check_course_owner(course_id)
    if not course:
        return redirect(url_for("main.index"))

    my_quiz = course.quiz or CourseQuiz(course_id=course.id, questions="[]")

    if request.method == "POST":
        quiz_json = request.form["quiz_json"]
        my_quiz.questions = quiz_json
        db.session.add(my_quiz)
        db.session.commit()
        flash("Quiz saved.")
        return redirect(url_for("mentor.courses"))

    return render_template("mentor/build_quiz.html", course=course)
