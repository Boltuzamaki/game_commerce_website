import json
import os
import sqlite3

from tqdm import tqdm  # Progress bar

# Path to the games.json file
json_file_path = "games.json"

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("games.db")
c = conn.cursor()

# Drop table for development purposes (optional)
c.execute("DROP TABLE IF EXISTS games")

# Create table for games if it doesn't already exist
c.execute(
    """
    CREATE TABLE IF NOT EXISTS games (
        appID TEXT PRIMARY KEY,
        name TEXT,
        releaseDate TEXT,
        estimatedOwners TEXT,
        peakCCU INTEGER,
        required_age INTEGER,
        price REAL,
        dlcCount INTEGER,
        longDesc TEXT,
        shortDesc TEXT,
        about_the_game TEXT,
        reviews TEXT,
        headerImage TEXT,
        website TEXT,
        supportWeb TEXT,
        supportEmail TEXT,
        supportWindows BOOLEAN,
        supportMac BOOLEAN,
        supportLinux BOOLEAN,
        metacriticScore INTEGER,
        metacriticURL TEXT,
        userScore INTEGER,
        scoreRank TEXT,
        positive INTEGER,
        negative INTEGER,
        achievements INTEGER,
        recommendations INTEGER,
        notes TEXT,
        supportedLanguages TEXT,
        fullAudioLanguages TEXT,
        packages TEXT,
        developers TEXT,
        publishers TEXT,
        averagePlaytime INTEGER,
        medianPlaytime INTEGER,
        categories TEXT,
        genres TEXT,
        screenshots TEXT,
        movies TEXT,
        tags TEXT,
        totalDownloads INTEGER
    )
"""
)

# Parse JSON and insert data into the SQLite database
if os.path.exists(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as fin:
        text = fin.read()
        if len(text) > 0:
            dataset = json.loads(text)

            # Use tqdm to add a progress bar while iterating over the dataset
            for app, game in tqdm(
                dataset.items(), desc="Inserting data into DB"
            ):

                # Extracting relevant information with default fallback for missing keys
                appID = app
                name = game.get("name", "")
                releaseDate = game.get("release_date", "")
                estimatedOwners = game.get("estimated_owners", "0-0")
                peakCCU = game.get("peak_ccu", 0)
                required_age = game.get("required_age", 0)
                price = game.get("price", 0.0)
                dlcCount = game.get("dlc_count", 0)
                longDesc = game.get("detailed_description", "")
                shortDesc = game.get("short_description", "")
                about_the_game = game.get("about_the_game", "")
                reviews = game.get("reviews", "")
                headerImage = game.get("header_image", "")
                website = game.get("website", "")
                supportWeb = game.get("support_url", "")
                supportEmail = game.get("support_email", "")
                supportWindows = game.get("windows", False)
                supportMac = game.get("mac", False)
                supportLinux = game.get("linux", False)
                metacriticScore = game.get("metacritic_score", 0)
                metacriticURL = game.get("metacritic_url", "")
                userScore = game.get("user_score", 0)
                scoreRank = game.get("score_rank", "")
                positive = game.get("positive", 0)
                negative = game.get("negative", 0)
                achievements = game.get("achievements", 0)
                recommendations = game.get("recommendations", 0)
                notes = game.get("notes", "")
                supportedLanguages = ", ".join(
                    game.get("supported_languages", [])
                )
                fullAudioLanguages = ", ".join(
                    game.get("full_audio_languages", [])
                )

                # Handle list of packages (assuming each dictionary has a "title" field)
                packages = ", ".join(
                    [
                        package.get("title", "")
                        for package in game.get("packages", [])
                    ]
                )

                # Handle developers and publishers lists
                developers = ", ".join(game.get("developers", []))
                publishers = ", ".join(game.get("publishers", []))

                averagePlaytime = game.get("average_playtime_forever", 0)
                medianPlaytime = game.get("median_playtime_forever", 0)

                # Categories, Genres, Screenshots, Movies, Tags are lists, so we'll join them into a single string
                categories = ", ".join(game.get("categories", []))
                genres = ", ".join(game.get("genres", []))
                screenshots = " | ".join(
                    game.get("screenshots", [])
                )  # Joining with ' | ' instead of ', '
                movies = ", ".join(game.get("movies", []))

                # Handle tags as either a list or a dictionary
                tags_data = game.get("tags", {})
                if isinstance(tags_data, list):
                    tags = ", ".join(tags_data)  # Join list elements
                elif isinstance(tags_data, dict):
                    tags = ", ".join(tags_data.keys())  # Join dictionary keys
                else:
                    tags = ""  # Default empty if neither list nor dict

                # Extract total downloads from estimated owners
                totalDownloads = (
                    int(estimatedOwners.split("-")[-1].strip())
                    if estimatedOwners
                    else 0
                )

                # Create the list of values to be inserted
                values = (
                    appID,
                    name,
                    releaseDate,
                    estimatedOwners,
                    peakCCU,
                    required_age,
                    price,
                    dlcCount,
                    longDesc,
                    shortDesc,
                    about_the_game,
                    reviews,
                    headerImage,
                    website,
                    supportWeb,
                    supportEmail,
                    supportWindows,
                    supportMac,
                    supportLinux,
                    metacriticScore,
                    metacriticURL,
                    userScore,
                    scoreRank,
                    positive,
                    negative,
                    achievements,
                    recommendations,
                    notes,
                    supportedLanguages,
                    fullAudioLanguages,
                    packages,
                    developers,
                    publishers,
                    averagePlaytime,
                    medianPlaytime,
                    categories,
                    genres,
                    screenshots,
                    movies,
                    tags,
                    totalDownloads,
                )

                # Logging statement to print the number of values and the actual values
                print(f"Number of values: {len(values)}")
                print(f"Values: {values}")

                # Insert the data into the database (41 columns with default values)
                c.execute(
                    """
                    INSERT OR REPLACE INTO games (
                        appID, name, releaseDate, estimatedOwners, peakCCU, required_age, price, dlcCount, longDesc, 
                        shortDesc, about_the_game, reviews, headerImage, website, supportWeb, supportEmail, 
                        supportWindows, supportMac, supportLinux, metacriticScore, metacriticURL, userScore, 
                        scoreRank, positive, negative, achievements, recommendations, notes, supportedLanguages, 
                        fullAudioLanguages, packages, developers, publishers, averagePlaytime, medianPlaytime, 
                        categories, genres, screenshots, movies, tags, totalDownloads
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    values,
                )

# Commit the transaction and close the connection
conn.commit()
conn.close()

print("Data inserted successfully!")
