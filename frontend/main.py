import os
import sqlite3

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from src.game_page.utils import get_game_data
from src.index.utils import (
    get_games,
    get_top_games_by_genre,
    get_top_games_from_last_month,
)
from src.search.constants import GENRES
from src.search.utils import filter_games, get_high_score_games, search_games
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secret key for session management


# Get the directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "users.db")


# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


# Function to get user by username
def get_user(username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def add_user(username, email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, password),
    )
    conn.commit()
    conn.close()


@app.route("/")
def home():
    # Fetch games data from the database
    games = get_games()
    top_action_games = get_top_games_by_genre("Action")
    top_open_world_games = get_top_games_by_genre("RPG")
    get_top_games_from_lm = get_top_games_from_last_month()

    all_games = {
        "games": games,
        "top_action_games": top_action_games,
        "top_open_world_games": top_open_world_games,
        "get_top_games_from_last_month": get_top_games_from_lm,
    }
    # Render the template with game data
    return render_template(
        "index.html",
        all_games=all_games,
    )


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        data = request.get_json()

        selected_genres = data.get("genres", [])
        price_range = data.get("price")
        sort_by = data.get(
            "sort", None
        )  # Handle sort by value from POST request
        query = data.get("q", None)

        max_price = float(price_range) if price_range else None

        search_params = {
            "name": query,
            "genres": selected_genres,
            "min_price": 0,
            "max_price": max_price,
            "sort_by": sort_by,  # Pass sorting parameter to the filter function
        }

        search_results = filter_games(search_params)

        return jsonify(search_results)

    # GET request handling if needed
    query = request.args.get("q")
    sort_by = request.args.get("sort")
    selected_genres = request.args.getlist("genres")
    price_range = request.args.get("price")
    metacritic_score = request.args.get("metacriticScore")
    release_date = request.args.get("releaseDate")

    search_params = {
        "name": query,
        "genres": selected_genres,
        "min_price": 0,
        "max_price": float(price_range) if price_range else None,
        "metacriticScore": int(metacritic_score) if metacritic_score else None,
        "releaseDate": release_date,
        "tags": request.args.get("tags"),
        "sort_by": sort_by,  # Pass sorting parameter to the filter function
    }

    search_results = filter_games(search_params)

    get_high_score_games_list = get_high_score_games()

    return render_template(
        "search.html",
        search_results=search_results,
        genres=GENRES,
        get_high_score_games_list=get_high_score_games_list,
        query=query,
        selected_genres=selected_genres,
        price_range=price_range,
        sort_by=sort_by,  # Send sort_by to the template
    )


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = get_user(username)

        # Check if user exists and password matches
        if user and check_password_hash(user[2], password):
            session["user"] = username
            flash(
                "Successfully signed in!", "success"
            )  # Flash success message
            return redirect(url_for("home"))
        else:
            flash(
                "Invalid credentials. Please try again.", "error"
            )  # Flash error message
            return redirect(url_for("signin"))

    return render_template("signin_page.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if the user already exists
        if get_user(username):
            flash(
                "Username already exists. Please choose a different one.",
                "error",
            )
            return render_template("signup_page.html")

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        # Store the user information in the database
        add_user(username, email, hashed_password)

        flash("Account created successfully! Please sign in.", "success")
        return redirect(url_for("signin"))

    return render_template("signup_page.html")


@app.route("/signout")
def signout():
    session.pop("user", None)
    flash("Successfully signed out.", "success")
    return redirect(url_for("home"))


@app.route("/game/<game_name>")
def game_page(game_name):
    game_data = get_game_data(game_name)
    if game_data:
        return render_template("game_detail.html", game=game_data)
    else:
        return "Game not found", 404


# New route for cart
@app.route("/cart")
def cart():
    if "user" not in session:
        flash("Please sign in to access your cart.", "error")
        return redirect(url_for("signin"))
    # If the user is signed in, render the cart page
    return render_template("continue_payment.html")


if __name__ == "__main__":
    app.run(debug=True)
