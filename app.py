from flask import Flask
from datetime import datetime, date
from flask import render_template, request
from data_models import db, Author, Book
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "data", "textbook.sqlite3")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
print("USING DB ->", app.config["SQLALCHEMY_DATABASE_URI"])


db.init_app(app)


#home for queries
@app.route("/", methods=["GET"])
def home():
    q = (request.args.get("q") or "").strip()
    sort = (request.args.get("sort") or "title").lower()
    direction = (request.args.get("direction") or "asc").lower()
    reverse = direction == "desc"

    if q:
        books = Book.query.filter(Book.title.ilike(f"%{q}%")).all()
    else:
        books = Book.query.all()
    q = Book.query

    if sort == "author":
        q = q.join(Author).order_by(Author.name.desc() if reverse else Author.name.asc())
    else:
        q = q.order_by(Book.title.desc() if reverse else Book.title.asc())

    books = q.all()
    return render_template("home.html", books=books)


#add author
@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "GET":
        return render_template("add_author.html")

    name = (request.form.get("name") or "").strip()
    birth_raw = (request.form.get("birthdate") or "").strip()
    death_raw = (request.form.get("date_of_death") or "").strip()

    if not name:
        return render_template("add_author.html", error="Name is required.")

#for sort-function, otherwise date = string...
    birth_date = date.fromisoformat(birth_raw) if birth_raw else None
    date_of_death = date.fromisoformat(death_raw) if death_raw else None

    author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
    db.session.add(author)
    db.session.commit()

    return render_template("add_author.html", message=f"Author '{author.name}' added successfully.")


#add book with basic validation
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    authors = Author.query.order_by(Author.name.asc()).all()

    if request.method == "GET":
       return render_template("add_book.html", authors=authors)
#POST request
    title = (request.form.get("title") or "").strip()
#    isbn = (request.form.get("isbn") or "").strip()
    publication_year_raw = (request.form.get("publication_year") or "").strip()
    author_id = request.form.get("author_id", type=int)
    if author_id is None or not Author.query.get(author_id):
        return render_template("add_book.html", authors=authors,
                               error="Valid author selection is required.")

#validation for title
    if not title:
        return render_template(
            "add_book.html",
            error="Title is required."
        )

#error handling "NONE"
    year_val = None
    if publication_year_raw:
        try:
            year_val = int(publication_year_raw)
        except ValueError:
            return render_template("add_book.html", authors=authors,
                                   error="Publication year must be a number.")

    book = Book(
        title=title,
#        isbn=isbn or None,
        publication_year=year_val or None,
        author_id=author_id or None,
    )
    db.session.add(book)
    db.session.commit()

    return render_template(
        "add_book.html",
        authors=authors,
        message="Book '{book.title}' added successfully."
    )

#POST for delete by title
@app.post("/book/<int:book_id>/delete")
def delete_book(book_id: int):
    book = Book.query.get_or_404(book_id)
    author_id = book.author_id
    title = book.title

    db.session.delete(book)
    return redirect(url_for("home"))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)