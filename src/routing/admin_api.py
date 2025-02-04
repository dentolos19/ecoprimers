from datetime import datetime, timedelta

from sqlalchemy import func

from lib.database import sql
from lib.models import Event, EventAttendee, Post, Transaction, User
from main import app


@app.route("/api/analysis")
def api_analysis():
    def get_monthly_data(model, data_limit):
        monthly_data = (
            sql.session.query(func.strftime("%Y-%m", model.created_at).label("month"), func.count(model.id))
            .filter(model.created_at >= data_limit)
            .group_by("month")
            .order_by("month")
            .all()
        )

        monthly_data_list = [{"month": month, "count": count} for month, count in monthly_data]

        # Ensure the data contains the current month, add it if it doesn't exist
        if not monthly_data_list or monthly_data_list[-1]["month"] != datetime.now().strftime("%Y-%m"):
            monthly_data_list.append({"month": datetime.now().strftime("%Y-%m"), "count": 0})

        # Ensure the data contains only 6 elements, fill in remaining months backwards
        while len(monthly_data_list) < 6:
            last_month = datetime.strptime(monthly_data_list[0]["month"], "%Y-%m") - timedelta(days=30)
            monthly_data_list.insert(0, {"month": last_month.strftime("%Y-%m"), "count": 0})
        return monthly_data_list[-6:]

    total_users = sql.session.query(func.count(User.id)).scalar()
    total_events = sql.session.query(func.count(Event.id)).scalar()
    total_posts = sql.session.query(func.count(Post.id)).scalar()

    data_limit = datetime.now() - timedelta(days=3 * 30)
    monthly_users = get_monthly_data(User, data_limit)
    monthly_signups = get_monthly_data(EventAttendee, data_limit)
    monthly_transactions = get_monthly_data(Transaction, data_limit)

    return {
        "totalUsers": total_users,
        "totalEvents": total_events,
        "totalPosts": total_posts,
        "monthlyUsers": monthly_users,
        "monthlySignups": monthly_signups,
        "monthlyTransactions": monthly_transactions,
    }