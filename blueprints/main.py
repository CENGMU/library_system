from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Book, Category, BorrowRecord

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
def index():
    return redirect(url_for("main.books"))

@main_bp.get("/books")
@login_required
def books():
    q = (request.args.get("q") or "").strip()
    cat = (request.args.get("cat") or "").strip()

    query = Book.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Book.title.like(like)) |
            (Book.author.like(like)) |
            (Book.isbn.like(like)) |
            (Book.tags.like(like))
        )
    if cat and cat.isdigit():
        query = query.filter(Book.category_id == int(cat))

    page = int(request.args.get("page", 1))
    per_page = 8
    pagination = query.order_by(Book.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("books.html", pagination=pagination, categories=categories, q=q, cat=cat)

@main_bp.get("/book/<int:book_id>")
@login_required
def book_detail(book_id: int):
    book = Book.query.get_or_404(book_id)
    return render_template("book_detail.html", book=book)

@main_bp.post("/borrow/<int:book_id>")
@login_required
def borrow(book_id: int):
    book = Book.query.get_or_404(book_id)
    if book.available_copies <= 0:
        flash("库存不足，无法借阅", "danger")
        return redirect(url_for("main.book_detail", book_id=book_id))

    exists = BorrowRecord.query.filter_by(
        user_id=current_user.id, book_id=book_id, status="borrowing"
    ).first()
    if exists:
        flash("你已经借阅了这本书，未归还前不能重复借阅", "warning")
        return redirect(url_for("main.book_detail", book_id=book_id))

    book.available_copies -= 1
    record = BorrowRecord(user_id=current_user.id, book_id=book_id)
    db.session.add(record)
    db.session.commit()

    flash("借阅成功", "success")
    return redirect(url_for("main.my_borrows"))

@main_bp.get("/my/borrows")
@login_required
def my_borrows():
    records = BorrowRecord.query.filter_by(user_id=current_user.id).order_by(BorrowRecord.id.desc()).all()
    return render_template("borrow_my.html", records=records)

@main_bp.post("/return/<int:record_id>")
@login_required
def return_book(record_id: int):
    record = BorrowRecord.query.get_or_404(record_id)
    if record.user_id != current_user.id and current_user.role != "admin":
        flash("无权限", "danger")
        return redirect(url_for("main.my_borrows"))

    if record.status == "returned":
        flash("该记录已归还", "info")
        return redirect(url_for("main.my_borrows"))

    record.status = "returned"
    from datetime import datetime
    record.return_time = datetime.utcnow()

    record.book.available_copies += 1
    db.session.commit()

    flash("归还成功", "success")
    return redirect(url_for("main.my_borrows"))
