import os
import sqlite3
import time
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from src.database.utils import add_user, get_user, update_cart
from src.game_page.utils import get_game_data
from src.index.utils import (
    get_games,
    get_top_games_by_genre,
    get_top_games_from_last_month,
)
from src.search.constants import GENRES
from src.search.utils import filter_games, get_high_score_games
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secret key for session management
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Admin required decorator with stronger security
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            abort(401)  # Unauthorized
        if not session.get("is_admin"):
            abort(403)  # Forbidden
        return f(*args, **kwargs)

    return decorated_function


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_db_connection_games():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "database", "games.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


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
            password TEXT NOT NULL,
            cart_games TEXT
        )
    """
    )
    conn.commit()
    conn.close()


with app.app_context():
    init_db()


@app.context_processor
def inject_cart_count():
    cart_count = 0
    if "user" in session:
        user = get_user(session["user"])
        if user and user[3]:
            cart_count = len(user[3].split(","))
    return dict(cart_count=cart_count)


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

    # Check if the user is signed in and get cart count
    cart_count = 0
    if "user" in session:
        user = get_user(session["user"])
        if (
            user and user[3]
        ):  # cart_games is stored as a comma-separated string
            cart_count = len(user[3].split(","))

    # Render the template with game data and cart count
    return render_template(
        "index.html", all_games=all_games, cart_count=cart_count
    )


@app.route("/dashboard")
@admin_required
def dashboard():
    # Data for the chart
    chart_data = {
        "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "datasets": [
            {
                "label": "Wolfenstein II",
                "data": [12, 19, 3, 5],
                "backgroundColor": "rgba(34, 197, 94, 0.8)",
            },
            {
                "label": "WWE 2K24",
                "data": [5, 10, 8, 15],
                "backgroundColor": "rgba(168, 85, 247, 0.8)",
            },
            {
                "label": "Cyberpunk 2077",
                "data": [10, 12, 15, 20],
                "backgroundColor": "rgba(163, 230, 53, 0.8)",
            },
        ],
    }

    return render_template(
        "admin_dashboard.html", chart_data=chart_data, admin_name="Admin"
    )


@app.route("/publisher-settings")
def publishersetting():
    # Data for the chart

    return render_template("publisher_setting.html")


@app.route("/remove-game")
def remove_game():
    query = request.args.get("q", "")
    search_params = {}
    if query:
        search_params["name"] = query
        games_list = filter_games(search_params)
    else:
        games_list = get_high_score_games()
    return render_template(
        "admin_remove_game.html", get_high_score_games_list=games_list
    )


@app.route("/remove-game/<game_name>", methods=["POST"])
@admin_required
def remove_game_by_name(game_name):
    try:
        conn = get_db_connection_games()
        cursor = conn.cursor()

        # Use the LOWER() function to normalize casing for comparison
        cursor.execute(
            "DELETE FROM games WHERE LOWER(name) = ?", (game_name.lower(),)
        )

        # Commit and close the connection
        conn.commit()
        conn.close()

        return jsonify(
            {"success": True, "message": f"{game_name} removed successfully"}
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/publisher-dashboard")
def publisherdashboard():
    chart_data = {
        "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
        "datasets": [
            {
                "label": "Wolfenstein II",
                "data": [12, 19, 3, 5],
                "backgroundColor": "rgba(34, 197, 94, 0.8)",
            },
            {
                "label": "WWE 2K24",
                "data": [5, 10, 8, 15],
                "backgroundColor": "rgba(168, 85, 247, 0.8)",
            },
            {
                "label": "Cyberpunk 2077",
                "data": [10, 12, 15, 20],
                "backgroundColor": "rgba(163, 230, 53, 0.8)",
            },
        ],
    }

    return render_template("publisher_dashboard.html", chart_data=chart_data)


@app.route("/publisher-add-new-game")
def publisher_add_new_game():
    # Data for the chart

    return render_template("publisher_add_new_game.html")


@app.route("/settings")
@admin_required
def usersetting():
    # Data for the chart

    return render_template("admin_user_settings.html")


@app.route("/add-game", methods=["GET", "POST"])
@admin_required
def add_game():
    if request.method == "POST":
        # Get form data
        title = request.form.get("title")
        description = request.form.get("description")
        tags = request.form.get("tags")
        price = request.form.get("price")

        # Handle cover image upload
        cover_image = request.files.get("cover_image")
        if cover_image and allowed_file(cover_image.filename):
            cover_filename = (
                f"{title.replace(' ', '_')}_cover_{cover_image.filename}"
            )
            cover_path = os.path.join(
                app.config["UPLOAD_FOLDER"], cover_filename
            )
            cover_image.save(cover_path)
            # Store relative path for database
            cover_db_path = f"/static/uploads/{cover_filename}"
        else:
            flash(
                "Invalid cover image file type! Only PNG, JPG, JPEG, and GIF are allowed."
            )
            return redirect(url_for("add_game"))

        # Handle screenshots upload
        screenshot_paths = []
        screenshots = request.files.getlist("screenshots[]")
        for i, screenshot in enumerate(screenshots):
            if screenshot and allowed_file(screenshot.filename):
                screenshot_filename = (
                    f"{title.replace(' ', '_')}_ss{i}_{screenshot.filename}"
                )
                screenshot_path = os.path.join(
                    app.config["UPLOAD_FOLDER"], screenshot_filename
                )
                screenshot.save(screenshot_path)
                # Store relative path for database
                screenshot_db_path = f"/static/uploads/{screenshot_filename}"
                screenshot_paths.append(screenshot_db_path)

        # Join screenshot paths with separator for storage
        screenshots_str = (
            " | ".join(screenshot_paths) if screenshot_paths else ""
        )

        # Generate unique app ID
        app_id = str(hash(title + str(time.time())))[:6]

        # Save game data to database
        conn = get_db_connection_games()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO games (
                appID, name, releaseDate, estimatedOwners, longDesc, tags, 
                headerImage, screenshots, price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                app_id,
                title,
                datetime.now().strftime("%b %d, %Y"),
                "0 - 20000",  # Default initial value
                description,
                tags,
                cover_db_path,  # Store relative path
                screenshots_str,  # Store relative paths
                price,
            ),
        )
        conn.commit()
        conn.close()

        flash("Game added successfully!")
        return redirect(url_for("add_game"))

    return render_template("admin_add_game_user.html")


@app.route("/notifications")
@admin_required
def notificationmanagement():
    # Data for the chart

    return render_template("admin_notification_management.html")


@app.route("/user-management")
@admin_required
def user_management():
    users = [
        {"id": 1, "name": "UserName #1"},
        {"id": 2, "name": "UserName #2"},
        {"id": 3, "name": "UserName #3"},
        {"id": 4, "name": "UserName #4"},
        {"id": 5, "name": "UserName #5"},
        {"id": 6, "name": "UserName #6"},
    ]
    return render_template("admin_user_management.html", users=users)


@app.route("/notification-management")
@admin_required
def notification_management():
    return render_template("admin_notification_management.html")


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

        # Check for admin credentials
        if username == "admin@gmail.com" and password == "admin":
            session["user"] = username
            session["is_admin"] = True
            flash("Welcome Admin!", "success")
            return redirect(url_for("dashboard"))

        user = get_user(username)

        # Check if user exists and password matches
        if user and check_password_hash(user[2], password):
            session["user"] = username
            session["is_admin"] = False
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
    session.pop("is_admin", None)
    flash("Successfully signed out.", "success")
    return redirect(url_for("home"))


@app.route("/game/<game_name>", methods=["GET", "POST"])
def game_page(game_name):
    game_data = get_game_data(game_name)
    added_to_cart = False

    # Check if user is logged in and if the game is already in the cart
    if "user" in session:
        username = session["user"]
        user = get_user(username)
        if user and user[3]:  # Check if cart_games is not None
            cart_games_list = user[3].split(",")
            added_to_cart = game_name in cart_games_list

    if request.method == "POST":
        if "user" not in session:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Please sign in to add games to your cart.",
                    }
                ),
                403,
            )

        # Update cart and set added_to_cart to True
        update_cart(username, game_name)
        added_to_cart = True

        # Respond with JSON for AJAX requests
        return jsonify(
            {
                "success": True,
                "message": f"{game_name} added to cart.",
                "added_to_cart": added_to_cart,
            }
        )

    # Handle GET request to render the game detail page
    if game_data:
        return render_template(
            "game_detail.html", game=game_data, added_to_cart=added_to_cart
        )
    else:
        return "Game not found", 404


@app.route("/buy_now", methods=["POST"])
def buy_now():
    if "user" not in session:
        flash("Please sign in to purchase games.", "error")
        return jsonify({"redirect": url_for("signin")}), 401

    data = request.get_json()
    game_name = data.get("game_name")
    username = session["user"]

    update_cart(username, game_name)
    flash(f"{game_name} added to cart. Proceeding to checkout.", "success")

    # Return a JSON response with the redirect URL
    return jsonify({"redirect": url_for("cart")}), 200


# New route for cart
@app.route("/cart", methods=["GET", "POST"])
def cart():
    if "user" not in session:
        flash("Please sign in to access your cart.", "error")
        return redirect(url_for("signin"))

    username = session["user"]
    user = get_user(username)
    cart_games_list = user[3].split(",") if user and user[3] else []

    if request.method == "POST":
        data = request.get_json()
        action = data.get("action")
        game_name = data.get("game_name", None)

        if action == "remove" and game_name:
            if game_name in cart_games_list:
                cart_games_list.remove(game_name)
        elif action == "remove_all":
            cart_games_list = []

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET cart_games = ? WHERE email = ?",
            (",".join(cart_games_list), username),
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True})

    cart_games_data = [
        get_game_data(game_name) for game_name in cart_games_list
    ]

    return render_template(
        "continue_payment.html", cart_games=cart_games_data, username=username
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
