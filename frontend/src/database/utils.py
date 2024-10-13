import os
import sqlite3

# Get the directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "..", "..", "users.db")


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


def update_cart(email, game_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT cart_games FROM users WHERE email = ?", (email,))
    cart_games = cursor.fetchone()[0]
    if cart_games:
        cart_games_list = cart_games.split(",")
    else:
        cart_games_list = []

    # Check if the game is already in the cart
    if game_name not in cart_games_list:
        cart_games_list.append(game_name)
        cursor.execute(
            "UPDATE users SET cart_games = ? WHERE email = ?",
            (",".join(cart_games_list), email),
        )
        conn.commit()

    conn.close()
