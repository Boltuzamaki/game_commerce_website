import os
import sqlite3
from datetime import datetime, timedelta


def get_top_games_from_last_month(limit=5):
    # Define the base directory and database path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "..", "database", "games.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the date for one month ago from today
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # Query to fetch the top 5 games by userScore from the last month
    cursor.execute(
        """
        SELECT appID, name, releaseDate, price, headerImage, metacriticScore
        FROM games
        WHERE releaseDate >= ?
        ORDER BY metacriticScore DESC
        LIMIT ?
        """,
        (one_month_ago, limit),
    )

    games = cursor.fetchall()
    conn.close()

    # Prepare the game data for the template
    games_list = []
    for game in games:
        game_data = {
            "appID": game[0],
            "name": game[1],
            "releaseDate": game[2],
            "price": game[3],
            "image": game[4],  # URL of the game cover
            "metacriticScore": game[5],
        }
        games_list.append(game_data)

    return games_list


def get_top_games_by_genre(genre, limit=6):
    # Define the base directory and database path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "..", "database", "games.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to fetch the top 6 games from a given genre, ordering by userScore
    cursor.execute(
        """
        SELECT appID, name, releaseDate, price, headerImage, metacriticScore
        FROM games
        WHERE genres LIKE ?
        ORDER BY metacriticScore DESC
        LIMIT ?
        """,
        (f"%{genre}%", limit),
    )

    games = cursor.fetchall()
    conn.close()

    # Prepare the game data for the template
    games_list = []
    for game in games:
        game_data = {
            "appID": game[0],
            "name": game[1],
            "releaseDate": game[2],
            "price": game[3],
            "image": game[4],  # URL of the game cover
            "metacriticScore": game[5],
        }
        games_list.append(game_data)

    return games_list


# Function to get data from the database
def get_games(limit=6):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "..", "database", "games.db")
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
