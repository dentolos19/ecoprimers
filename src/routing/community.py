import os

from flask import redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from lib.database import sql
from lib.models import Post, PostLike
from main import app
from utils import allowed_file, require_login

@app.context_processor
def init_community():
    def is_liked(likes, user_id):
        return any(like.user_id == user_id for like in likes)
    return dict(is_liked=is_liked)

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
    user_id = session.get("user_id")
    return render_template("community.html", posts=posts, user_id=user_id)

@app.route("/delete_post/<post_id>", methods=["POST"])
@require_login
def delete_post(post_id):
    # post = Post.query.get(post_id)
    post = sql.session.query(Post).filter_by(id=post_id).first()
    if post:
        # If the post has an image, delete it from the file system
        if post.image_filename:
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], post.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)

        sql.session.delete(post)
        sql.session.commit()
        return redirect(url_for("community"))
    else:
        return "Post not found", 404


@app.route("/update_post/<post_id>", methods=["GET", "POST"])
def update_post(post_id):
    #post = Post.query.get(post_id)
    post = sql.session.query(Post).filter_by(id=post_id).first()
    if not post:
        return "Post not found", 404

    if request.method == "POST":
        # Update post content
        post.content = request.form["content"]

        # Handle optional image update
        image = request.files.get("image")
        if image and allowed_file(image.filename):
            # Delete old image if it exists
            if post.image_filename:
                old_image_path = os.path.join(
                    app.config["UPLOAD_FOLDER"], post.image_filename
                )
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Save new image
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))
            post.image_filename = image_filename

        # Commit changes to the database
        sql.session.commit()
        return redirect(url_for("community"))

    # Render the update form with the current post data
    return render_template("update_post.html", post=post)


@app.route("/toggle_like/<post_id>", methods=["GET", "POST"])
def toggle_like(post_id):
    user_id = session.get("user_id")
    like = sql.session.query(PostLike).filter_by(post_id=post_id, user_id=user_id).first()

    if not like:
        like = PostLike(
            post_id=post_id,
            user_id=user_id
        )
        sql.session.add(like)
    else:
        sql.session.delete(like)

    sql.session.commit()

    return redirect(url_for("community"))