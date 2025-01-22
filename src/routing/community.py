import os

from flask import redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from lib.database import sql
from lib.models import Post
from main import app
from utils import allowed_file, require_login


@app.route("/community/post", methods=["GET", "POST"])
@require_login
def community_post():
    if request.method == "POST":
        content = request.form["content"]
        image = request.files["image"]
        user_id = session.get("user_id")

        # Handle image upload
        image_filename = None
        if image and allowed_file(image.filename):
            # Secure the filename and save it
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        # Add post to the database
        new_post = Post(
            title="title",
            description=content,
            image_filename=image_filename,
            user_id=user_id,
        )

        sql.session.add(new_post)
        sql.session.commit()

        return redirect(url_for("community"))

    return render_template("community-post.html")


@app.route("/community")
@app.route("/community/explore")
@require_login
def community():
    posts = sql.session.query(Post).all()
    return render_template("community.html", posts=posts)