import os

from flask import flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from lib.database import sql
from lib.models import Event, Product, Transaction, User
from main import app
from utils import allowed_file, require_admin


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

        if image and not allowed_file(image.filename):
            flash("Invalid file type! Only images with extensions .png, .jpg, .jpeg, and .gif are allowed.", "danger")
            return redirect(request.url)

        image_filename = None
        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        new_event = Event(
            title=event_title,
            description=event_description,
            location=event_location,
            date=event_date,
            image_filename=image_filename,
        )

        try:
            sql.session.add(new_event)
            sql.session.commit()
            flash("Event added successfully!", "success")
        except Exception as e:
            sql.session.rollback()  # Rollback if there's an error
            flash(f"An error occurred while adding the event: {str(e)}", "danger")

        return redirect(url_for("admin_events"))

    return render_template("admin/events-new.html")


@app.route("/admin/events/<id>", methods=["GET", "POST"])
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

        if image and not allowed_file(image.filename):
            flash("Invalid file type! Only images with extensions .png, .jpg, .jpeg, and .gif are allowed.", "danger")
            return redirect(request.url)

        image_filename = None
        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        event.title = event_title
        event.description = event_description
        event.location = event_location
        event.date = event_date
        event.image_filename = image_filename

        try:
            sql.session.commit()
            flash("Event updated successfully!", "success")
        except Exception as e:
            sql.session.rollback()
            flash(f"An error occurred while updating the event: {str(e)}", "danger")

        return redirect(url_for("admin_events"))

    return render_template("admin/events-edit.html", event=event)


@app.route("/admin/events/<id>/delete", methods=["GET", "POST"])
def admin_events_delete(id):
    # Query the event from the database
    event = sql.session.query(Event).filter_by(id=id).first()

    if request.method == "POST":
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
        user_name = request.form["name"]
        user_email = request.form["email"]
        user_password = request.form["password"]
        user_bio = request.form["bio"]
        user_birthday = request.form["birthday"]

        user_hashed_password = generate_password_hash(user_password, method="pbkdf2:sha1")

        # Update the user object with the new data
        new_user = User(
            name=user_name,
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


@app.route("/admin/users/<id>", methods=["GET", "POST"])
@require_admin
def admin_users_edit(id):
    # Query the user from the database
    user = sql.session.query(User).filter_by(id=id).first()

    if request.method == "POST":
        # Collect data from the form
        user_name = request.form["name"]
        user_email = request.form["email"]
        user_bio = request.form["bio"]
        user_birthday = request.form["birthday"]

        # Update the user object with the new data
        user.email = user_email
        user.name = user_name
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


@app.route("/admin/users/<id>/delete", methods=["GET", "POST"])
@require_admin
def admin_users_delete(id):
    # Query the user from the database
    user = sql.session.query(User).filter_by(id=id).first()

    if request.method == "POST":
        # Collect data from the form
        user_name = request.form["name"]

        if user.name != user_name:
            flash("The name does not match. Please try again.", "danger")
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


@app.route("/admin/products/<id>", methods=["GET", "POST"])
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


@app.route("/admin/products/<id>/delete", methods=["GET", "POST"])
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
    transactions = sql.session.query(Transaction).order_by(Transaction.created_at.desc()).all()

    return render_template("admin/transactions.html", transactions=transactions)


@app.route("/admin/transactions/<id>")
@require_admin
def admin_transactions_view(id):
    # Query the transaction and user from the database
    transaction = sql.session.query(Transaction).filter_by(id=id).first()
    user = sql.session.query(User).filter_by(id=transaction.user_id).first()

    return render_template("admin/transactions-view.html", transaction=transaction, user=user)


@app.route("/admin/transactions/<id>/delete", methods=["GET", "POST"])
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