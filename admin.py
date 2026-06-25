from database import SessionLocal, User

# GET ALL USERS
def get_all_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users


# GET STATS
def get_stats():
    db = SessionLocal()
    users = db.query(User).all()

    total_users = len(users)
    total_requests = sum(u.requests for u in users)
    total_revenue = sum(getattr(u, "revenue", 0) for u in users)

    db.close()

    return {
        "total_users": total_users,
        "total_requests": total_requests,
        "total_revenue": total_revenue
    }