from flask import Flask
import os
from dotenv import load_dotenv
from flask import render_template, redirect, url_for, request, session,flash
from functools import wraps
import math 

load_dotenv()

app = Flask(__name__)

DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
PORT = int(os.getenv("FLASK_PORT", 8000))
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
app.config["SECRET_KEY"] = SECRET_KEY


query = ""
BOOKS=[]
NEXT_ID=1


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/", methods=["GET","POST"])
@login_required
def home():
    query = request.form.get("query", "").strip()
    result = [element for element in BOOKS if query.lower() in element["title"].lower() or query.lower() in element["author"].lower()]
##Recherche par auteur et par titre ! Cela évite de créer un filtre.



    per_page = 2
    page = request.args.get("page", 1, type=int)

    total_pages = math.ceil(len(result) / per_page)


    start = (page - 1) * per_page
    end = start + per_page

    paginated_books = result[start:end]
    return render_template("index.html", username=session["username"],books=paginated_books,page=page,total_pages=total_pages)

@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
@login_required
def edit_book(book_id):
    # 1. On cherche le livre dans la liste BOOKS par son ID
    # On utilise next() avec une compréhension pour extraire le premier résultat trouvé
    book = next((b for b in BOOKS if b["id"] == book_id), None)

    # Si le livre n'existe pas, on peut renvoyer une erreur 404
    if book is None:
        return "Livre non trouvé", 404

    if request.method == "POST":
        # 2. On récupère les nouvelles données du formulaire
        # Note : on utilise request.form car c'est un envoi POST
        book["title"] = request.form.get("title")
        book["author"] = request.form.get("author")
        book["description"] = request.form.get("description")
        # 3. Une fois mis à jour, on redirige vers l'accueil
        return redirect(url_for("home"))

    # 4. Si c'est un GET, on affiche le formulaire avec les infos du livre
    return render_template("edit.html", book=book)

@login_required
@app.get("/book/<int:book_id>")
def book(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    return render_template("book.html", book=book)

@app.route("/delete/<int:book_id>")
@login_required
def delete_book(book_id):
    global BOOKS
    # On reconstruit la liste en excluant le livre qui a l'ID correspondant
    BOOKS = [b for b in BOOKS if b["id"] != book_id]
    
    flash("Livre supprimé avec succès !")
    return redirect(url_for("home"))


@login_required
@app.route("/books/new", methods=["GET","POST"])
def new_book():
    global NEXT_ID
    if request.method == "GET":
        return render_template("new_book.html")
    title = request.form.get("title","").strip()
    author = request.form.get("author","").strip()
    description = request.form.get("description","").strip()

    if title == "" or author == "" or description == "":
        flash("Veuillez remplir tous les champs.")
        return redirect(url_for("new_book"))
    BOOKS.append({"id": NEXT_ID,"title": title,"author": author,"description": description})
    NEXT_ID += 1
    return redirect(url_for("home"))   


DEMO_USER = {"username": "admin", "password": "admin"}


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == DEMO_USER['username'] and password == DEMO_USER['password']:
            session.permanent = True
            session['username'] = username
            flash('Connexion reussie!')
            return redirect(url_for('home'))
        else:
            flash('Identifiants invalides.')

    return render_template('login.html')

@app.route("/delete-confirm/<int:book_id>")
@login_required
def delete_confirm(book_id):
    # On cherche le livre comme pour l'édition
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if book is None:
        return render_template("404.html"), 404
    
    return render_template("delete_confirm.html", book=book)



@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))





@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=DEBUG, host="127.0.0.1", port=PORT)
