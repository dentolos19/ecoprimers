from flask import flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from database import sql
from main import app
from models import Event, Product, Transaction, User
from utils import require_admin

from werkzeug.utils import secure_filename
from utils import allowed_file

import os


@app.route("/admin")
@app.route("/admin/dashboard")
@require_admin
def admin():
    return render_template("admin/dashboard.html")


@app.route("/admin/events", methods=["GET", "POST"])
@require_admin
def admin_events():
    # Query all events from the database
    events = sql.session.query(Event).all()

    if request.method == "POST" and request.form.get("delete_event"):
        # Handle deletion of event
        event_id = request.form["delete_event"]
        event_to_delete = sql.session.query(Event).filter_by(id=event_id).first()

        if event_to_delete:
            try:
                sql.session.delete(event_to_delete)
                sql.session.commit()
                flash("Event deleted successfully!", "success")
            except Exception as e:
                sql.session.rollback()  # Rollback in case of error
                flash(f"An error occurred while deleting the event: {str(e)}", "danger")

        return redirect(url_for("admin_events"))

    return render_template("admin/events.html", events=events)


@app.route("/admin/events/new", methods=["GET", "POST"])
@require_admin
def admin_events_new():
    if request.method == "POST":
        # Collect data from the form
        event_title = request.form["title"]
        event_description = request.form["description"]
        event_location = request.form["location"]
        event_date = request.form["date"]
        image = request.files["image"]

        image_filename = None
        if image and allowed_file(image.filename):
            # Secure the filename and save it
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))


        # Create an Event object and save it to the database
        new_event = Event(
            title=event_title,
            description=event_description,
            location=event_location,
            date=event_date,
            image_filename=image_filename,
        )

        try:
            # Add the event to the session and commit it to the database
            sql.session.add(new_event)
            sql.session.commit()
            flash("Event added successfully!", "success")
        except Exception as e:
            sql.session.rollback()  # Rollback if there's an error
            flash(f"An error occurred while adding the event: {str(e)}", "danger")

        return redirect(url_for("admin_events"))

    return render_template("admin/events-new.html")


@app.route("/admin/events/<int:id>", methods=["GET", "POST"])
def admin_events_edit(id):
    # Query the event from the database
    event = sql.session.query(Event).filter_by(id=id).first()

    if request.method == "POST":
        # Collect data from the form
        event_title = request.form["title"]
        event_description = request.form["description"]
        event_location = request.form["location"]
        event_date = request.form["date"]
        image = request.files["image"]

        image_filename = None
        if image and allowed_file(image.filename):
            # Secure the filename and save it
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        # Update the event object with the new data
        event.title = event_title
        event.description = event_description
        event.location = event_location
        event.date = event_date
        event.image_filename = image_filename

        try:
            # Commit the changes to the database
            sql.session.commit()
            flash("Event updated successfully!", "success")
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred while updating the event: {str(e)}", "danger")

        return redirect(url_for("admin_events"))

    return render_template("admin/events-edit.html", event=event)


@app.route("/admin/events/<int:id>/delete", methods=["GET", "POST"])
def admin_events_delete(id):
    # Query the event from the database
    event = sql.session.query(Event).filter_by(id=id).first()

    if request.method == "POST":
        # Collect data from the form
        event_title = request.form["title"]

        if event.title != event_title:
            flash("The event title does not match. Please try again.", "danger")
            return redirect(url_for("admin_events_delete", id=id))

        try:
            sql.session.delete(event)
            sql.session.commit()
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred while deleting the event: {str(e)}", "danger")

        return redirect(url_for("admin_events"))

    return render_template("admin/events-delete.html", event=event)


@app.route("/admin/users")
@require_admin
def admin_users():
    # Query all events from the database
    users = sql.session.query(User).all()

    return render_template("admin/users.html", users=users)


@app.route("/admin/users/new", methods=["GET", "POST"])
@require_admin
def admin_users_new():
    if request.method == "POST":
        # Collect data from the form
        user_username = request.form["username"]
        user_email = request.form["email"]
        user_password = request.form["password"]
        user_bio = request.form["bio"]
        user_birthday = request.form["birthday"]

        user_hashed_password = generate_password_hash(user_password, method="pbkdf2:sha1")

        # Update the user object with the new data
        new_user = User(
            username=user_username,
            email=user_email,
            password=user_hashed_password,
            bio=user_bio,
            birthday=user_birthday,
        )

        try:
            # Commit the changes to the database
            sql.session.add(new_user)
            sql.session.commit()
            flash("User created successfully!", "success")
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred while creating the user: {str(e)}", "danger")

        return redirect(url_for("admin_users"))

    return render_template("admin/users-new.html")


@app.route("/admin/users/<int:id>", methods=["GET", "POST"])
@require_admin
def admin_users_edit(id):
    # Query the user from the database
    user = sql.session.query(User).filter_by(id=id).first()

    if request.method == "POST":
        # Collect data from the form
        user_username = request.form["username"]
        user_email = request.form["email"]
        user_bio = request.form["bio"]
        user_birthday = request.form["birthday"]

        # Update the user object with the new data
        user.email = user_email
        user.username = user_username
        user.bio = user_bio
        user.birthday = user_birthday

        try:
            # Commit the changes to the database
            sql.session.commit()
            flash("User updated successfully!", "success")
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred while updating the user: {str(e)}", "danger")

        return redirect(url_for("admin_users"))

    return render_template("admin/users-edit.html", user=user)


@app.route("/admin/users/<int:id>/delete", methods=["GET", "POST"])
@require_admin
def admin_users_delete(id):
    # Query the user from the database
    user = sql.session.query(User).filter_by(id=id).first()

    if request.method == "POST":
        # Collect data from the form
        user_username = request.form["username"]

        if user.username != user_username:
            flash("The username does not match. Please try again.", "danger")
            return redirect(url_for("admin_users_delete", id=id))

        try:
            sql.session.delete(user)
            sql.session.commit()
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred while deleting the user: {str(e)}", "danger")

        return redirect(url_for("admin_users"))

    return render_template("admin/users-delete.html", user=user)


@app.route("/admin/products")
@require_admin
def admin_products():
    # Query all products from the database
    products = sql.session.query(Product).all()

    return render_template("admin/products.html", products=products)


@app.route("/admin/products/new", methods=["GET", "POST"])
@require_admin
def admin_products_new():
    if request.method == "POST":
        # Collect data from the form
        product_name = request.form["name"]
        product_points = request.form["points"]
        product_stock = request.form["stock"]

        # Create a Product object and save it to the database
        new_product = Product(
            name=product_name,
            points=product_points,
            stock=product_stock,
        )

        try:
            # Add the product to the session and commit it to the database
            sql.session.add(new_product)
            sql.session.commit()
            flash("Product added successfully!", "success")
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred while adding the product: {str(e)}", "danger")

        return redirect(url_for("admin_products"))

    return render_template("admin/products-new.html")


@app.route("/admin/products/<int:id>", methods=["GET", "POST"])
@require_admin
def admin_products_edit(id):
    # Query the product from the database
    product = sql.session.query(Product).filter_by(id=id).first()

    if request.method == "POST":
        # Collect data from the form
        product_name = request.form["name"]
        product_points = request.form["points"]
        product_stock = request.form["stock"]

        # Update the product object with the new data
        product.name = product_name
        product.points = product_points
        product.stock = product_stock

        try:
            # Commit the changes to the database
            sql.session.commit()
            flash("Product updated successfully!", "success")
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred while updating the product: {str(e)}", "danger")

        return redirect(url_for("admin_products"))

    return render_template("admin/products-edit.html", product=product)


@app.route("/admin/products/<int:id>/delete", methods=["GET", "POST"])
@require_admin
def admin_products_delete(id):
    # Query the product from the database
    product = sql.session.query(Product).filter_by(id=id).first()

    if request.method == "POST":
        # Collect data from the form
        product_name = request.form["name"]

        if product.name != product_name:
            flash("The product name does not match. Please try again.", "danger")
            return redirect(url_for("admin_products_delete", id=id))

        try:
            sql.session.delete(product)
            sql.session.commit()
            flash("Product deleted successfully!", "success")
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred while deleting the product: {str(e)}", "danger")

        return redirect(url_for("admin_products"))

    return render_template("admin/products-delete.html", product=product)


@app.route("/admin/transactions")
@require_admin
def admin_transactions():
    # Query all transactions from the database
    transactions = sql.session.query(Transaction).all()

    return render_template("admin/transactions.html", transactions=transactions)


@app.route("/admin/transactions/<int:id>")
@require_admin
def admin_transactions_view(id):
    # Query the transaction and user from the database
    transaction = sql.session.query(Transaction).filter_by(id=id).first()
    user = sql.session.query(User).filter_by(id=transaction.user_id).first()

    return render_template("admin/transactions-view.html", transaction=transaction, user=user)


@app.route("/admin/transactions/<int:id>/delete", methods=["GET", "POST"])
@require_admin
def admin_transactions_delete(id):
    # Query the transaction from the database
    transaction = sql.session.query(Transaction).filter_by(id=id).first()

    if request.method == "POST":
        # Collect data from the form
        transaction_id = request.form["id"]

        if transaction.id != int(transaction_id):
            flash("The transaction ID does not match. Please try again.", "danger")
            return redirect(url_for("admin_transactions_delete", id=id))

        try:
            sql.session.delete(transaction)
            sql.session.commit()
            flash("Transaction deleted successfully!", "success")
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred while deleting the transaction: {str(e)}", "danger")

        return redirect(url_for("admin_transactions"))

    return render_template("admin/transactions-delete.html", transaction=transaction)