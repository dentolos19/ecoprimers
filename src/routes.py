from flask import render_template, request, redirect, url_for, session


import os
from main import app
from database import session as db_session
from models import Post
from utils import allowed_file
from werkzeug.utils import secure_filename
from datetime import datetime

# Page Routes


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/chat")
def chat():
    return render_template("chat.html")


@app.route("/admin")
def admin():
    return render_template("admin-dashboard.html")


@app.route("/admin/events")
def admin_events():
    return render_template("admin-events.html")


@app.route("/admin/users")
def admin_users():
    return render_template("admin-users.html")


@app.route("/admin/transactions")
def admin_transactions():
    return render_template("admin-transactions.html")

@app.route('/community')
@app.route('/community/explore')
def community():
    posts = db_session.query(Post).all()  # Get all posts
    return render_template('community.html', posts=posts)


@app.route('/community/post', methods=['GET', 'POST'])
def community_post():
    if request.method == 'POST':
        content = request.form['content']
        image = request.files['image']
        user_id = 1 # Hardcoded user ID

        # Handle image upload
        image_filename = None
        if image and allowed_file(image.filename):
            # Secure the filename and save it
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # Add post to the database
        new_post = Post(title="title", description=content, image_filename=image_filename, user_id=user_id, created_at=datetime.utcnow())
        db_session.add(new_post)
        db_session.commit()

        return redirect(url_for('home'))

    return render_template('community-post.html')