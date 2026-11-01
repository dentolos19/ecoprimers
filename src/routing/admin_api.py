from datetime import UTC, datetime

from sqlalchemy import func

from lib import ai
from lib.database import sql
from lib.models import Event, EventAttendee, Post, Product, Transaction, User
from lib.prompts import load
from main import app
from utils import require_admin


def complete_months(
    counts: dict[str, int], now: datetime
) -> list[dict[str, str | int]]:
    current = now.year * 12 + now.month - 1
    result = []
    for offset in range(5, -1, -1):
        year, month = divmod(current - offset, 12)
        label = f"{year:04d}-{month + 1:02d}"
        result.append({"month": label, "count": counts.get(label, 0)})
    return result


@app.route("/api/analysis")
@require_admin
def api_analysis():
    def get_monthly_data(model, data_limit):
        month_expr = func.to_char(model.created_at, "YYYY-MM")
        monthly_data = (
            sql.session.query(month_expr.label("month"), func.count(model.id))
            .filter(model.created_at >= data_limit)
            .group_by("month")
            .order_by("month")
            .all()
        )

        return complete_months(dict(monthly_data), now)

    total_users = sql.session.query(func.count(User.id)).scalar()
    total_events = sql.session.query(func.count(Event.id)).scalar()
    total_posts = sql.session.query(func.count(Post.id)).scalar()
    total_products = sql.session.query(func.count(Product.id)).scalar()

    now = datetime.now(UTC)
    year, month = divmod(now.year * 12 + now.month - 1 - 5, 12)
    data_limit = datetime(year, month + 1, 1, tzinfo=UTC)
    monthly_users = get_monthly_data(User, data_limit)
    monthly_signups = get_monthly_data(EventAttendee, data_limit)
    monthly_transactions = get_monthly_data(Transaction, data_limit)

    return {
        "totalUsers": total_users,
        "totalEvents": total_events,
        "totalPosts": total_posts,
        "totalProducts": total_products,
        "monthlyUsers": monthly_users,
        "monthlySignups": monthly_signups,
        "monthlyTransactions": monthly_transactions,
    }


@app.route("/api/analysis/recommendations")
@require_admin
def api_analysis_recommend():
    data = api_analysis()

    # Get prompt
    prompt = load("generate-recommendations").format(content=data)

    # Generate response
    response = ai.generate_text(prompt)

    return {"response": response}
