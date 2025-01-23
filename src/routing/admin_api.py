from datetime import datetime, timedelta

from sqlalchemy import func

from lib.database import sql
from lib.models import Event, EventAttendee, Post, Transaction, User
from main import app


@app.route("/api/analysis")
def api_analysis():
    total_users = sql.session.query(func.count(User.id)).scalar()
    total_events = sql.session.query(func.count(Event.id)).scalar()
    total_posts = sql.session.query(func.count(Post.id)).scalar()

    data_limit = datetime.now() - timedelta(days=3 * 30)

    monthly_signups_data = (
        sql.session.query(func.strftime("%Y-%m", EventAttendee.created_at).label("month"), func.count(EventAttendee.id))
        .filter(EventAttendee.created_at >= data_limit)
        .group_by("month")
        .order_by("month")
        .all()
    )

    monthly_signups = [{"month": month, "count": count} for month, count in monthly_signups_data]

    # Ensure the data contains the current month, add it if it doesn't exist
    if not monthly_signups or monthly_signups[-1]["month"] != datetime.now().strftime("%Y-%m"):
        monthly_signups.append({"month": datetime.now().strftime("%Y-%m"), "count": 0})

    # Ensure the data contains only 6 elements, fill in remaining months backwards
    while len(monthly_signups) < 6:
        last_month = datetime.strptime(monthly_signups[0]["month"], "%Y-%m") - timedelta(days=30)
        monthly_signups.insert(0, {"month": last_month.strftime("%Y-%m"), "count": 0})
    monthly_signups = monthly_signups[-6:]

    monthly_transactions_data = (
        sql.session.query(func.strftime("%Y-%m", Transaction.created_at).label("month"), func.count(Transaction.id))
        .filter(Transaction.created_at >= data_limit)
        .group_by("month")
        .order_by("month")
        .all()
    )

    monthly_transactions = [{"month": month, "count": count} for month, count in monthly_transactions_data]

    # Ensure the data contains the current month, add it if it doesn't exist
    if not monthly_transactions or monthly_transactions[-1]["month"] != datetime.now().strftime("%Y-%m"):
        monthly_transactions.append({"month": datetime.now().strftime("%Y-%m"), "count": 0})

    # Ensure the data contains only 6 elements, fill in remaining months backwards
    while len(monthly_transactions) < 6:
        last_month = datetime.strptime(monthly_transactions[0]["month"], "%Y-%m") - timedelta(days=30)
        monthly_transactions.insert(0, {"month": last_month.strftime("%Y-%m"), "count": 0})
    monthly_transactions = monthly_transactions[-6:]

    return {
        "totalUsers": total_users,
        "totalEvents": total_events,
        "totalPosts": total_posts,
        "monthlySignups": monthly_signups,
        "monthlyTransactions": monthly_transactions,
    }