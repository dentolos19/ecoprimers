import os

from flask import redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from lib.database import sql
from lib.models import Post, PostComment, PostLike, PostSaved, UserFollow
from main import app
from utils import allowed_file, require_login

@app.context_processor
def init_community():

    user_id = session.get('user_id')

    def is_liked(likes, user_id):
        return any(like.user_id == user_id for like in likes)

    def is_saved(saves, user_id):
        return any(save.user_id == user_id for save in saves)
    
    def is_followed(follows, user_id, follower_id):
        return any(follow.user_id == user_id and follow.follower_id == follower_id for follow in follows)
    
    def is_comment(comments, user_id):
        return any(comment.user_id == user_id for comment in comments)
    
    return dict(user_id=user_id, is_liked=is_liked, is_saved=is_saved, is_followed=is_followed, is_comment=is_comment)


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

@app.route("/community/saved")
@require_login
def community_saved():
    user_id = session.get("user_id")
    saved_posts = sql.session.query(PostSaved).filter_by(user_id=user_id).all()

    return render_template("community-saved.html", posts=saved_posts)

@app.route("/community/posts/<post_id>/delete", methods=["GET", "POST"])
@require_login
def delete_post(post_id):
    # post = Post.query.get(post_id)
    post = sql.session.query(Post).filter_by(id=post_id).first()
    sql.session.delete(post)
    sql.session.commit()
    return redirect(url_for("community"))
    


@app.route("/community/posts/<post_id>", methods=["GET", "POST"])
def update_post(post_id):
    post = sql.session.query(Post).filter_by(id=post_id).first()
    
    if not post:
        return "Post not found", 404

    if request.method == "POST":
        # Update post content
        post.description = request.form["content"]

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
    return render_template("community-update.html", post=post)


@app.route("/community/posts/<post_id>/like", methods=["GET", "POST"])
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

@app.route("/community/posts/<user_id>/follow", methods=["GET", "POST"])
def toggle_follow(user_id):
    follower_id = session.get("user_id")
    follow = sql.session.query(UserFollow).filter_by( user_id=user_id, follower_id=follower_id).first()

    if not follow:
        follow = UserFollow(
            user_id=user_id,
            follower_id=follower_id
        )
        sql.session.add(follow)
    else:
        sql.session.delete(follow)

    sql.session.commit()

    return redirect(url_for("community"))


@app.route("/community/posts/<post_id>/save", methods=["GET", "POST"])
def toggle_save(post_id):
    user_id = session.get("user_id")  # Get the current logged-in user's ID
    
    # Check if the post is already saved by the user
    save = sql.session.query(PostSaved).filter_by(post_id=post_id, user_id=user_id).first()

    if not save:
        # If the post is not already saved, add it to the PostSaved table
        save = PostSaved(
            post_id=post_id,
            user_id=user_id
        )
        sql.session.add(save)
    else:
        # If the post is already saved, remove it from the PostSaved table
        sql.session.delete(save)

    # Commit the changes to the database
    sql.session.commit()

    # Redirect back to the community page (or wherever you want)
    return redirect(url_for("community"))


@app.route("/community/posts/<post_id>/comment", methods=["GET", "POST"])
def post_comment(post_id):
    user_id = session.get("user_id")  # Get the current logged-in user's ID

    message = request.form["comment_text"]
    user_id = session.get("user_id")
        # Add post to the database

    
    print(message)
    new_comment = PostComment(
        message = message,
        post_id=post_id,
        user_id=user_id,
        )

    sql.session.add(new_comment)
    sql.session.commit()

    return redirect(url_for("community"))
