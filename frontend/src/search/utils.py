import os
import sqlite3


# Function to search games based on the query
def search_games(query):

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "..", "database", "games.db")
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
    db_path = os.path.join(base_dir, "..", "..", "database", "games.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL query to fetch 12 random games with scoreRank > 8
    cursor.execute(
        """
        SELECT name, price, headerImage, totalDownloads, positive
        FROM games
        WHERE CAST(metacriticScore AS INTEGER) > 8
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
            "image": game[2],
            "downloads": game[3],
            "positive": game[4],
        }
        game_list.append(game_data)

    return game_list
