

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = "authors"

#changed for textbook.sqlite3 databank
    author_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column("birth", db.String(10), nullable=True)
    date_of_death = db.Column("death", db.String(10), nullable=True)

    def __repr__(self):
        return f"<Author author_id={self.author_id} name={self.name!r}>"


class Book(db.Model):
    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.author_id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)

#super helpful
    author = db.relationship("Author", backref="books", lazy="joined")

#translation from diffrent colum names
    @property
    def id(self):
        return self.book_id

    def __repr__(self):
        return f"<Book book_id={self.book_id} title={self.title!r} author_id={self.author_id}>"

