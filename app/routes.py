from flask import Blueprint, render_template, session, redirect, url_for, flash, request, send_from_directory, current_app
from .models import Upload, db, User
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template("home.html")


@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access dashboard.", "danger")
        return redirect(url_for('auth.login'))
    uploads = Upload.query.order_by(Upload.uploaded_at.desc()).all()
    return render_template("dashboard.html", uploads=uploads)


@main.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('auth.login'))

    file = request.files.get('file')
    if file:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        filepath = os.path.join(upload_folder, filename)
        # Ensure the upload directory exists
        os.makedirs(upload_folder, exist_ok=True)
        file.save(filepath)

        new_upload = Upload(filename=filename)
        db.session.add(new_upload)
        db.session.commit()

        flash("File uploaded successfully !", "success")
    else:
        flash("No file selected for upload.", "danger")
    return redirect(url_for('main.dashboard'))


@main.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Login first", "danger")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    return render_template("profile.html", user=user)


@main.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash("Login required to edit profile.", "danger")
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        username = request.form.get('username')
        bio = request.form.get('bio')
        image = request.files.get('profile_pic')

        if username:
            user.username = username

        if bio:
            user.bio = bio

        if image and image.filename != '':
            filename = secure_filename(image.filename)
            upload_path = os.path.join('app', 'static', 'profile_pics')

            # Ensure the upload directory exists
            os.makedirs(upload_path, exist_ok=True)
            image.save(os.path.join(upload_path, filename))
            user.profile_pic = filename

            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('main.profile'))

    return render_template("edit_profile.html", user=user)


@main.route('/search')
def search():
    if 'user_id' not in session:
        flash("Please log in to search files.", "danger")
        return redirect(url_for('auth.login'))

    query = request.args.get('query')
    if not query:
        flash("Please enter a search term!", "warning")
        return redirect(url_for('main.dashboard'))

    results = Upload.query.filter(Upload.filename.ilike(f"%{query}%")).all()

    return render_template("search_results.html", results=results, query=query)


@main.route('/uploads/<filename>')
def view_file(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'uploads'), filename)


@main.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    file = Upload.query.get_or_404(file_id)
    filepath = os.path.join(current_app.root_path, 'uploads', file.filename)

    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        db.session.delete(file)
        db.session.commit()
        flash("File deleted successfully!", "success")
    except Exception as e:
        flash("Failed to delete file., please try again.", "danger")

    return redirect(url_for('main.dashboard'))
