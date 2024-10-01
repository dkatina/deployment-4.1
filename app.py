from datetime import date
from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select, delete
from flask_sqlalchemy import SQLAlchemy
from typing import List


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:BAC146@localhost/library_db'

db.init_app(app)
ma = Marshmallow(app)

loan_book = db.Table(
    "loan_book",
    Base.metadata,
    db.Column("loan_id", db.ForeignKey("loans.id")),
    db.Column("book_id", db.ForeignKey("books.id"))
)

class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    DOB: Mapped[date] = mapped_column(nullable=False)

    loans: Mapped[List["Loan"]] = db.relationship(back_populates="member")

class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_date: Mapped[date]
    member_id: Mapped[int] = mapped_column(db.ForeignKey("members.id"), nullable=False)

    member: Mapped["Member"] = db.relationship(back_populates="loans")
    books: Mapped[List["Book"]] = db.relationship(secondary=loan_book, back_populates="loans")

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(db.String(100), nullable=False)
    genre: Mapped[str] = mapped_column(db.String(50), nullable=False)
    desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    title: Mapped[str] = mapped_column(db.String(100), nullable=False)

    loans: Mapped[List["Loan"]] = db.relationship(secondary=loan_book, back_populates="books")


with app.app_context():
    db.create_all()


#============SCHEMAS=============

class MemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Member

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)


#============CRUD==================

@app.route("/members", methods=['POST'])
def create_member():
    try: 
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_member = Member(name=member_data['name'], email=member_data['email'], DOB=member_data['DOB'])
    
    db.session.add(new_member)
    db.session.commit()

    return member_schema.jsonify(new_member), 201


@app.route("/members", methods=['GET'])
def get_members():
    query = select(Member)
    result = db.session.execute(query).scalars().all()
    return members_schema.jsonify(result), 200


@app.route("/members/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    query = select(Member).where(Member.id == member_id)
    member = db.session.execute(query).scalars().first()
    
    if member == None:
        return jsonify({"message": "invalid member id"})
    
    try: 
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in member_data.items():
        setattr(member, field, value)

    db.session.commit()
    return member_schema.jsonify(member), 200

@app.route("/members/<int:member_id>", methods=['DELETE'])
def delete_member(member_id):
    query = delete(Member).where(Member.id == member_id)
    member = db.session.execute(query)

    db.session.commit()
    return jsonify({"message": f"succesfully deleted user {member_id}"})
    
    
    


app.run(debug=True)