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


def filter_games(search_params):
    print(search_params)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "..", "database", "games.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Base SQL query
    query = """
        SELECT appID, name, price, headerImage, totalDownloads, positive, genres, metacriticScore, releaseDate
        FROM games
        WHERE 1=1
    """

    # List to store the query conditions and corresponding parameters
    conditions = []
    params = []

    # Add filters based on the search parameters
    if search_params.get("name"):
        conditions.append("name LIKE ?")
        params.append(f"%{search_params['name']}%")

    if search_params.get("genres"):
        genre_conditions = []
        for genre in search_params["genres"]:
            genre_conditions.append("genres LIKE ?")
            params.append(f"%{genre}%")
        # Combine the genre conditions using OR
        if genre_conditions:
            conditions.append(f"({' OR '.join(genre_conditions)})")

    if search_params.get("min_price") is not None:
        conditions.append("price >= ?")
        params.append(search_params["min_price"])

    if search_params.get("max_price") is not None:
        conditions.append("price <= ?")
        params.append(search_params["max_price"])

    if search_params.get("metacriticScore"):
        conditions.append("metacriticScore >= ?")
        params.append(search_params["metacriticScore"])

    if search_params.get("releaseDate"):
        conditions.append("releaseDate = ?")
        params.append(search_params["releaseDate"])

    if search_params.get("tags"):
        conditions.append("tags LIKE ?")
        params.append(f"%{search_params['tags']}%")

    # Join conditions to form the final query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Handle sorting
    sort_by = search_params.get("sort_by", "name")
    if sort_by:
        if sort_by == "price":
            query += " ORDER BY price ASC"
        elif sort_by == "releaseDate":
            query += " ORDER BY releaseDate DESC"
        elif sort_by == "reviews":
            query += " ORDER BY positive DESC"

    # Limit the results to 12
    query += " LIMIT 12"

    # Execute the query with the provided parameters
    cursor.execute(query, tuple(params))
    filtered_games = cursor.fetchall()
    conn.close()

    # Prepare the filtered games list for the template
    game_list = []
    for game in filtered_games:
        game_data = {
            "appID": game[0],
            "name": game[1],
            "price": game[2],
            "image": game[3],
            "downloads": game[4],
            "positive": game[5],
            "genres": game[6],
            "metacriticScore": game[7],
            "releaseDate": game[8],
        }
        game_list.append(game_data)

    return game_list
