from flask import Flask, render_template, request

from src.game_page.utils import get_game_data
from src.index.utils import (
    get_games,
    get_top_games_by_genre,
    get_top_games_from_last_month,
)
from src.search.constants import GENRES
from src.search.utils import get_high_score_games, search_games

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


@app.route("/search")
def search():
    query = request.args.get("q")
    if query:
        search_results = search_games(query)
    else:
        search_results = []

    get_high_score_games_list = get_high_score_games()
    print(get_high_score_games_list)
    return render_template(
        "search.html",
        search_results=search_results,
        genres=GENRES,
        get_high_score_games_list=get_high_score_games_list,
    )


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
