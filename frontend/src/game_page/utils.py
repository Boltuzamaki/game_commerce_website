import os
import sqlite3


def get_game_data(game_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "..", "database", "games.db")
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
            "longDesc": game[8],
            "shortDesc": game[10],
            "reviews": game[11],
            "headerImage": game[12],
            "supportWindows": game[16],
            "supportMac": game[17],
            "supportLinux": game[18],
            "screenshots": game[37].split("|"),
            "totalDownloads": game[40],
            # Add other fields as necessary
        }

        print(game_data)
        return game_data
    else:
        return None
