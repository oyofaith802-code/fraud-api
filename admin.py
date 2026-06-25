from database import SessionLocal, User

def get_stats():
    db = SessionLocal()
    users = db.query(User).all()

    return {
        "total_users": len(users),
        "total_requests": sum(u.requests or 0 for u in users),
        "total_revenue": sum(u.revenue or 0 for u in users)
    }