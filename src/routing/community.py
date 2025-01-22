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

@app.route("/delete_post/<int:post_id>", methods=["POST"])
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


@app.route("/update_post/<int:post_id>", methods=["GET", "POST"])
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



def toggle_like():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    # Query the user from the database
    user = sql.session.query(User).filter(User.id == user_id).first()

    if not user:
        return "User not found", 404

    # Toggle the num value (increment if even, decrement if odd)
    postlike = sql.session.query(PostLike).filter_by(user_id=user.id)
    postlike.num += 1 if user.num % 2 == 0 else user.num - 1

    try:
        sql.session.commit()
        return render_template("community.html", num=postlike.num)  # Render the page with updated num value
    except Exception as e:
        sql.session.rollback()
        return "An error occurred: " + str(e), 400
