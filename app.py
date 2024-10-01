from datetime import date
from flask import Flask
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from typing import List

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:BAC146@localhost/library_db'

db.init_app(app)

loan_book = db.Table(
    "loan_book",
    Base.metadata,
    db.Column("loan_id", db.ForeignKey("loans.id")),
    db.Column("book_id", db.ForeignKey("books.id"))
)

class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100))
    email: Mapped[str] = mapped_column(db.String(150), unique=True)
    DOB: Mapped[date]

    loans: Mapped[List["Loan"]] = db.relationship(back_populates="member")

class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_date: Mapped[date]
    member_id: Mapped[int] = mapped_column(db.ForeignKey("members.id"))

    member: Mapped["Member"] = db.relationship(back_populates="loans")
    books: Mapped[List["Book"]] = db.relationship(secondary=loan_book)

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(db.String(100))
    genre: Mapped[str] = mapped_column(db.String(50))
    desc: Mapped[str] = mapped_column(db.String(255))
    title: Mapped[str] = mapped_column(db.String(100))

    loans: Mapped[List["Loan"]] = db.relationship(secondary=loan_book)


with app.app_context():
    db.create_all()

app.run(debug=True)