
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Course, CoursePresentation, CourseNotes, CourseQuiz, CourseHomework

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

    presentation = course.presentation or CoursePresentation(course_id=course.id, filename="")
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
                    presentation.filename = pdf_filename
                else:
                    flash("PowerPoint conversion failed.")
                    return redirect(url_for("material.presentation", course_id=course.id))
            elif ext == ".pdf":
                presentation.filename = filename
            else:
                flash("Only PDF or PPTX supported.")
                return redirect(url_for("material.presentation", course_id=course.id))

            db.session.add(presentation)
            db.session.commit()
            flash("Presentation uploaded.")
            return redirect(url_for("mentor.courses"))
        flash("No file selected.")
    return render_template("mentor/upload_presentation.html", file=presentation.filename if presentation.filename else None)
