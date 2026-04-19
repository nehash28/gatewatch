from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)

# ── CONFIG ───────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "gatewatch.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "gatewatch-secret-2024"

db = SQLAlchemy(app)


# ── MODELS ───────────────────────────────────────────────

class User(db.Model):
    __tablename__ = "users"
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50),  unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)   # plain text for simplicity
    role     = db.Column(db.String(20),  nullable=False)   # admin | security | resident
    flat     = db.Column(db.String(20),  default="—")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "username": self.username,
                "role": self.role, "flat": self.flat}


class Visitor(db.Model):
    __tablename__ = "visitors"
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    phone    = db.Column(db.String(20),  default="Walk-in")
    flat     = db.Column(db.String(20),  nullable=False)
    purpose  = db.Column(db.String(50),  default="Guest")
    time     = db.Column(db.String(20))
    status   = db.Column(db.String(20),  default="pending")
    created  = db.Column(db.DateTime,    default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "phone": self.phone,
                "flat": self.flat, "purpose": self.purpose,
                "time": self.time, "status": self.status}


class Staff(db.Model):
    __tablename__ = "staff"
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(100), nullable=False)
    role    = db.Column(db.String(50))
    status  = db.Column(db.String(20),  default="absent")
    time    = db.Column(db.String(20),  default="-")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "role": self.role,
                "status": self.status, "time": self.time}


class Notice(db.Model):
    __tablename__ = "notices"
    id       = db.Column(db.Integer, primary_key=True)
    title    = db.Column(db.String(200), nullable=False)
    body     = db.Column(db.Text,        nullable=False)
    category = db.Column(db.String(20),  default="general")
    author   = db.Column(db.String(100), default="Management")
    date     = db.Column(db.String(30))
    is_new   = db.Column(db.Boolean,     default=True)
    created  = db.Column(db.DateTime,    default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "body": self.body,
                "category": self.category, "author": self.author,
                "date": self.date, "is_new": self.is_new}


# ── SEED ─────────────────────────────────────────────────

def seed_db():
    if User.query.count() == 0:
        users = [
            User(name="Mizba",         username="admin",    password="admin123",    role="admin",    flat="A-402"),
            User(name="Ramesh Yadav",  username="security", password="security123", role="security", flat="—"),
            User(name="Nisha Joshi",   username="resident", password="resident123", role="resident", flat="D-501"),
        ]
        db.session.add_all(users)

    if Visitor.query.count() == 0:
        db.session.add_all([
            Visitor(name="Arjun Mehta",    phone="+91 98765 00001", flat="A-101", purpose="Guest",    time="9:45 AM",  status="pending"),
            Visitor(name="Swati Kulkarni", phone="+91 98765 00002", flat="C-302", purpose="Delivery", time="10:12 AM", status="pending"),
            Visitor(name="Rohit Patil",    phone="+91 98765 00003", flat="B-204", purpose="Service",  time="10:30 AM", status="pending"),
            Visitor(name="Nisha Joshi",    phone="+91 98765 00004", flat="D-501", purpose="Cab/Taxi", time="8:20 AM",  status="approved"),
            Visitor(name="Vivek Desai",    phone="+91 98765 00005", flat="A-203", purpose="Guest",    time="7:55 AM",  status="denied"),
        ])

    if Staff.query.count() == 0:
        db.session.add_all([
            Staff(name="Kaveri Amma",   role="Housekeeping", status="present",     time="6:05 AM"),
            Staff(name="Ramesh Yadav",  role="Security",     status="present",     time="6:30 AM"),
            Staff(name="Sunita Bai",    role="Cook",         status="present",     time="7:15 AM"),
            Staff(name="Balu Swamy",    role="Driver",       status="present",     time="7:45 AM"),
            Staff(name="Meena Devi",    role="Housekeeping", status="checked_out", time="9:40 AM"),
            Staff(name="Ganesh Kumar",  role="Gardener",     status="present",     time="9:55 AM"),
            Staff(name="Priya Reddy",   role="Cook",         status="checked_out", time="10:15 AM"),
            Staff(name="Aruna Sharma",  role="Housekeeping", status="present",     time="8:00 AM"),
            Staff(name="Vinod Nair",    role="Plumber",      status="absent",      time="-"),
            Staff(name="Deepak Mallik", role="Electrician",  status="absent",      time="-"),
            Staff(name="Suresh G",      role="Security",     status="present",     time="6:00 AM"),
        ])

    if Notice.query.count() == 0:
        db.session.add_all([
            Notice(title="Water Supply Interruption — 19 Apr", body="Water supply will be shut off from 10 AM to 4 PM on Sunday for maintenance on the overhead tank. Please store water in advance.", category="urgent",  author="Management Committee", date="Apr 18", is_new=True),
            Notice(title="Monthly Maintenance Due — April",    body="Monthly society maintenance of ₹2,500 is due by April 30. Please transfer to the society account or pay at the office.",           category="info",    author="Treasurer",            date="Apr 15", is_new=True),
            Notice(title="Summer Camp for Kids — Register Now",body="We are organising a 2-week summer camp for children aged 5–14 in the clubhouse. Activities include art, sports, and coding.",     category="event",   author="Welfare Committee",    date="Apr 12", is_new=False),
            Notice(title="Parking Rules Reminder",             body="Kindly park only in your designated spots. Vehicles found in visitor bays for more than 2 hours will be towed without notice.",    category="general", author="Security Team",        date="Apr 10", is_new=False),
        ])

    db.session.commit()


# ── AUTH HELPERS ─────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("role") not in roles:
                return jsonify({"error": "Access denied"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── AUTH ROUTES ──────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user_id"] = user.id
            session["name"]    = user.name
            session["role"]    = user.role
            session["flat"]    = user.flat
            return redirect(url_for("index"))
        error = "Invalid username or password"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── MAIN ROUTE ───────────────────────────────────────────

@app.route("/")
@login_required
def index():
    role          = session.get("role")
    visitors      = Visitor.query.order_by(Visitor.created.desc()).all()
    staff         = Staff.query.order_by(Staff.id).all()
    notices       = Notice.query.order_by(Notice.created.desc()).all()
    pending_count = Visitor.query.filter_by(status="pending").count()
    present_count = Staff.query.filter_by(status="present").count()
    unread_count  = Notice.query.filter_by(is_new=True).count()
    urgent_count  = Notice.query.filter_by(category="urgent").count()

    # Residents only see notices + their own visitor history
    if role == "resident":
        my_flat   = session.get("flat")
        visitors  = Visitor.query.filter_by(flat=my_flat).order_by(Visitor.created.desc()).all()

    return render_template("index.html",
        visitors      = [v.to_dict() for v in visitors],
        staff         = [s.to_dict() for s in staff],
        notices       = [n.to_dict() for n in notices],
        pending_count = pending_count,
        present_count = present_count,
        unread_count  = unread_count,
        urgent_count  = urgent_count,
        today         = datetime.now().strftime("%a, %d %b %Y"),
        current_user  = {"name": session["name"], "role": role, "flat": session.get("flat", "—")},
    )


# ── VISITOR API ──────────────────────────────────────────

@app.route("/api/visitors", methods=["POST"])
@login_required
def add_visitor():
    if session.get("role") not in ("admin", "security", "resident"):
        return jsonify({"error": "Access denied"}), 403
    data    = request.get_json()
    name    = data.get("name", "").strip()
    flat    = data.get("flat", "").strip()
    purpose = data.get("purpose", "Guest").strip()
    if not name or not flat:
        return jsonify({"error": "Name and flat required"}), 400
    v = Visitor(name=name, phone="Walk-in", flat=flat, purpose=purpose,
                time=datetime.now().strftime("%I:%M %p"), status="pending")
    db.session.add(v)
    db.session.commit()
    return jsonify({"success": True, "visitor": v.to_dict()})


@app.route("/api/visitors/<int:visitor_id>", methods=["PATCH"])
@login_required
@role_required("admin", "security")
def update_visitor(visitor_id):
    data   = request.get_json()
    action = data.get("action")
    v = db.session.get(Visitor, visitor_id)
    if not v:
        return jsonify({"error": "Visitor not found"}), 404
    if action not in ("approved", "denied"):
        return jsonify({"error": "Invalid action"}), 400
    v.status = action
    db.session.commit()
    return jsonify({"success": True, "visitor": v.to_dict()})


# ── NOTICES API ──────────────────────────────────────────

@app.route("/api/notices", methods=["POST"])
@login_required
@role_required("admin")
def add_notice():
    data  = request.get_json()
    title = data.get("title", "").strip()
    body  = data.get("body",  "").strip()
    if not title or not body:
        return jsonify({"error": "Title and body required"}), 400
    n = Notice(title=title, body=body,
               category=data.get("category", "general"),
               author=data.get("author", "Management") or "Management",
               date=datetime.now().strftime("%b %d"), is_new=True)
    db.session.add(n)
    db.session.commit()
    return jsonify({"success": True, "notice": n.to_dict()})


# ── STAFF API ────────────────────────────────────────────

@app.route("/api/staff/<int:staff_id>", methods=["PATCH"])
@login_required
@role_required("admin", "security")
def update_staff(staff_id):
    data   = request.get_json()
    action = data.get("action")
    s = db.session.get(Staff, staff_id)
    if not s:
        return jsonify({"error": "Staff not found"}), 404
    if action == "checkin":
        s.status = "present";  s.time = datetime.now().strftime("%I:%M %p")
    elif action == "checkout":
        s.status = "checked_out"; s.time = datetime.now().strftime("%I:%M %p")
    else:
        return jsonify({"error": "Invalid action"}), 400
    db.session.commit()
    return jsonify({"success": True, "staff": s.to_dict()})


# ── INIT ─────────────────────────────────────────────────

with app.app_context():
    db.create_all()
    seed_db()

if __name__ == "__main__":
    app.run(debug=True)
