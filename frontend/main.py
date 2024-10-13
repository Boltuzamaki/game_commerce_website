from flask import Flask, jsonify, render_template, request
from src.game_page.utils import get_game_data
from src.index.utils import (
    get_games,
    get_top_games_by_genre,
    get_top_games_from_last_month,
)
from src.search.constants import GENRES
from src.search.utils import filter_games, get_high_score_games, search_games

app = Flask(__name__)


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


@app.route("/signin")
def signin():
    # Fetch games data from the database
    games = get_games()

    # Render the template with game data
    return render_template("signin_page.html", games=games)


@app.route("/signin")
def signup():
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
