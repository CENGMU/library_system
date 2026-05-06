from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)

    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)  # admin/user

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw: str):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(120), nullable=True, index=True)
    isbn = db.Column(db.String(40), nullable=True, index=True)
    publisher = db.Column(db.String(120), nullable=True)
    publish_year = db.Column(db.String(10), nullable=True)

    tags = db.Column(db.String(200), nullable=True)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    category = db.relationship("Category", backref=db.backref("books", lazy=True))

    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BorrowRecord(db.Model):
    __tablename__ = "borrow_records"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False, index=True)

    user = db.relationship("User", backref=db.backref("borrow_records", lazy=True))
    book = db.relationship("Book", backref=db.backref("borrow_records", lazy=True))

    borrow_time = db.Column(db.DateTime, default=datetime.utcnow)
    due_time = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    return_time = db.Column(db.DateTime, nullable=True)

    status = db.Column(db.String(20), default="borrowing")  # borrowing/returned

    @property
    def is_overdue(self) -> bool:
        if self.status == "returned":
            return False
        return datetime.utcnow() > self.due_time
