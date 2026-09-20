# Importation de librairies et des fonctions utiles
from flask import Flask, render_template, g, request, session, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import os

# Création du fichier
app = Flask(__name__)
DATABASE = "beatmaker.db"

# Variables qui récupèrent les clés admin
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "local_password")
R2_BASE_URL = os.environ.get("R2_BASE_URL", "https://pub-488e9edc41e84b88bc3090ea7c511424.r2.dev")

# Instanciation de l'objet Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[]
)

# Création de la base de données

# Ouvre une connexion à la base de données et la laisse ouverte le temps d'une requête
# g permet de stocker des informations
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        # Fonction qui permet d'acceder aux colonnes directement par leur nom (et non par l'index)
        g.db.row_factory = sqlite3.Row
    return g.db

# Fonction qui va fermer la connexion à chaque fin de requête
@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# Création de la table

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS prods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            genre TEXT NOT NULL,
            bpm INTEGER NOT NULL,
            prix REAL NOT NULL,
            fichier_audio TEXT NOT NULL,
            image TEXT
        )
    """)
    db.commit()


# Routes

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/prods")
def prods():
    db = get_db()
    # Méthode fetchall permet de récupérer littéralement les prods
    # Affichage initial lorsque l'on arrive sur la page
    prods = db.execute("SELECT * FROM prods ORDER BY id DESC").fetchall()
    return render_template("prods.html", prods=prods, r2_url=R2_BASE_URL)


@app.route("/videos")
def videos():
    return render_template("videos.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/admin/login", methods=["GET", "POST"])
# Fonction qui empêche une attaque brute force 
# Bloque l'IP d'un attaquant qui tente + de 5 mots de passe en 5 minutes 
@limiter.limit("5 per 5 minutes")
def admin_login():

    # Initialisation de la variable error
    error = None

    # Si la requête envoyée est POST
    if request.method == "POST":

        # Si dans la valeur du password dans la liste form correspond au mot de passe de l'admin
        if request.form["password"] == ADMIN_PASSWORD:

            # La valeur de admin dans la liste session devient True 
            session["admin"] = True

            # Fonction redirect pour envoyer vers l'url admin
            return redirect(url_for("admin"))
        else:

            # Si le mot de passe ne correspond pas, la variable error devient cette chaine de caractère
            error = "Mot de passe incorrect"

    # Renvoie cette page et la variable error
    return render_template("login.html", error=error)



@app.route("/admin/logout", methods=["POST", "GET"])
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))



@app.route("/admin", methods=["POST", "GET"])
def admin():

    # Si la requête n'est pas get("admin")
    if not session.get("admin"):
        # Rediriger vers la page "admin_login"
        return redirect(url_for("admin_login"))

    # Instanciation de la base de données
    db = get_db()

    # Si la requête envoyée est POST
    if request.method == "POST":

        # Variables associées aux valeurs correspondantes de la liste form
        titre = request.form["titre"]
        genre = request.form["genre"]
        bpm = request.form["bpm"]
        prix = request.form["prix"]
        fichier_audio = request.form["fichier_audio"]

        # Execution de la commande SQL suivante
        db.execute(
            "INSERT INTO prods (titre, genre, bpm, prix, fichier_audio, image) VALUES (?, ?, ?, ?, ?, ?)",
            (titre, genre, bpm, prix, fichier_audio, "")
        )
        db.commit()

        # Rediriger vers la page "admin"
        return redirect(url_for("admin"))       

    # Variable qui reprend la valeur de la commande SQL suivante
    prods = db.execute("SELECT * FROM prods ORDER BY id DESC").fetchall()

    # Renvoie la page admin.html et la variable prods
    return render_template("admin.html", prods=prods)


@app.route("/admin/delete/<int:prod_id>")
def admin_delete(prod_id):

    # Si la requête n'est pas get("admin")
    if not session.get("admin"):
        # Rediriger vers l'url "admin_login"
        return redirect(url_for("admin_login"))

    # Instanciation de la base de données
    db = get_db()

    # Execution de la commande SQL suivante 
    db.execute("DELETE FROM prods WHERE id = ?", (prod_id,))
    db.commit()

    # Rediriger vers l'url "admin"
    return redirect(url_for("admin"))

# Lancement du site

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=False)
