from flask import redirect, session, flash
from functools import wraps
from models import Admin

def signin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'admin_id' not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            admin_id = session.get("admin_id")
            if admin_id is None:
                flash("You need to log in to access this page.", "error")
                return redirect("/")

            admin = Admin.query.filter_by(id=admin_id).first()
            if not admin:
                flash("Admin not found.", "error")
                return redirect("/")

            if admin.role not in roles:
                flash("You do not have permission to access this page.", "error")
                return redirect("/admin")

            return f(*args, **kwargs)
        return decorated_function
    return decorator