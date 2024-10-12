import os
import sqlite3

from flask import Flask, render_template, request

app = Flask(__name__)


# Function to get data from the database
def get_games(limit=6):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "database", "games.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to fetch some games data (adjust the columns as necessary)
    cursor.execute(
        """
        SELECT name, price, headerImage, totalDownloads, positive
        FROM games
        LIMIT ?
        """,
        (limit,),
    )

    games = cursor.fetchall()
    conn.close()

    # Prepare game data for the template
    games_list = []
    for game in games:
        game_data = {
            "name": game[0],
            "price": game[1],
            "image": game[2],  # URL of the game cover
            "downloads": game[3],
            "positive": game[4],
        }
        games_list.append(game_data)

    return games_list


# Function to search games based on the query
def search_games(query):

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "database", "games.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL query to search for games by name, genres, or tags
    cursor.execute(
        """
        SELECT name, price, headerImage, totalDownloads, positive
        FROM games
        WHERE name LIKE ? OR genres LIKE ? OR tags LIKE ?
        """,
        (f"%{query}%", f"%{query}%", f"%{query}%"),
    )

    search_results = cursor.fetchall()
    conn.close()

    # Prepare search results for the template
    search_list = []
    for result in search_results:
        game_data = {
            "name": result[0],
            "price": result[1],
            "image": result[2],  # URL of the game cover
            "downloads": result[3],
            "positive": result[4],
        }
        search_list.append(game_data)

    return search_list


# Function to get 12 random games with scoreRank more than 8
def get_high_score_games():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "database", "games.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL query to fetch 12 random games with scoreRank > 8
    cursor.execute(
        """
        SELECT name, price, headerImage, totalDownloads, positive
        FROM games
        WHERE CAST(scoreRank AS INTEGER) > 8
        ORDER BY RANDOM()
        LIMIT 12
        """
    )

    high_score_games = cursor.fetchall()
    conn.close()

    # Prepare the list of high-score games
    game_list = []
    for game in high_score_games:
        game_data = {
            "name": game[0],
            "price": game[1],
            "image": game[2],  # URL of the game cover
            "downloads": game[3],
            "positive": game[4],
        }
        game_list.append(game_data)

    return game_list


@app.route("/search")
def search():
    query = request.args.get("q")
    if query:
        search_results = search_games(query)
    else:
        search_results = []
    genres = [
        "360 Video",
        "Accounting",
        "Action",
        "Adventure",
        "Animation & Modeling",
        "Audio Production",
        "Casual",
        "Design & Illustration",
        "Documentary",
        "Early Access",
        "Education",
        "Episodic",
        "Free To Play",
        "Free to Play",
        "Game Development",
        "Gore",
        "Indie",
        "Massively Multiplayer",
        "Movie",
        "Nudity",
        "Photo Editing",
        "RPG",
        "Racing",
        "Sexual Content",
        "Short",
        "Simulation",
        "Software Training",
        "Sports",
        "Strategy",
        "Tutorial",
        "Utilities",
        "Video Production",
        "Violent",
        "Web Publishing",
    ]

    get_high_score_games_list = get_high_score_games()
    print(get_high_score_games_list)
    return render_template(
        "search.html",
        search_results=search_results,
        genres=genres,
        get_high_score_games_list=get_high_score_games_list,
    )


def get_games_by_release_date():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "database", "games.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL query to fetch games sorted by release date in descending order
    query = "SELECT name, price, headerImage, releaseDate, totalDownloads, positive FROM games ORDER BY releaseDate DESC"
    cursor.execute(query)
    games = cursor.fetchall()
    conn.close()

    # Prepare games data for the template
    games_list = []
    for game in games:
        game_data = {
            "name": game[0],
            "price": game[1],
            "image": game[2],  # URL of the game cover
            "releaseDate": game[3],
            "downloads": game[4],
            "positive": game[5],
        }
        games_list.append(game_data)

    return games_list


def get_game_data(game_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "database", "games.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games WHERE name=?", (game_name,))
    game = cursor.fetchone()
    conn.close()

    if game:
        # Map the fetched data to appropriate fields
        game_data = {
            "appID": game[0],
            "name": game[1],
            "releaseDate": game[2],
            "price": game[6],
            "longDesc": game[9],
            "shortDesc": game[10],
            "about_the_game": game[11],
            "reviews": game[12],
            "headerImage": game[13],
            "supportWindows": game[16],
            "supportMac": game[17],
            "supportLinux": game[18],
            "totalDownloads": game[39],
            # Add other fields as necessary
        }
        return game_data
    else:
        return None


@app.route("/")
def home():
    # Fetch games data from the database
    games = get_games()

    # Render the template with game data
    return render_template("index.html", games=games)


@app.route("/signin")
def signin():
    # Fetch games data from the database
    games = get_games()

    # Render the template with game data
    return render_template("signin_page.html", games=games)


@app.route("/game/<game_name>")
def game_page(game_name):
    game_data = get_game_data(game_name)
    if game_data:
        return render_template("game_detail.html", game=game_data)
    else:
        return "Game not found", 404


if __name__ == "__main__":
    app.run(debug=True)
