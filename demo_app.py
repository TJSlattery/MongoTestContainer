import os
import random
from db_connection import create_connection, find_movie

if __name__ == "__main__":
    # Get MongoDB URI from environment variable, which will be set by the test runner
    # Default to a common local URI for standalone execution if env var is not set.
    #Hello World!
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    
    # Create a connection to the MongoDB database
    client = create_connection(uri, tls_enabled=False) # TLS is usually handled by the Testcontainer setup or specified in URI

    if client:
        # These are the titles that are expected to be in the database from the test setup.
        # We pick one randomly to demonstrate a query.
        known_movie_titles = [
            "Inception", "The Matrix", "Interstellar", "The Dark Knight", "Parasite",
            "Spirited Away", "Pulp Fiction", "Fight Club", "Forrest Gump", "The Shawshank Redemption",
            "The Godfather", "The Lord of the Rings", "The Avengers", "Titanic", "Gladiator",
            "Toy Story", "Coco", "Jurassic Park", "Mad Max: Fury Road", "Whiplash"
        ]

        # Query a random movie from the known titles
        query_title = random.choice(known_movie_titles)
        print(f"Attempting to query for movie: {query_title}")
        found_movie = find_movie(client, {"title": query_title})
        
        if found_movie:
            print(f"Queried and found movie: {found_movie.get('title')} ({found_movie.get('year')})")
        else:
            print(f"Movie with title '{query_title}' not found.")
        
        client.close()
    else:
        print("Failed to establish connection to MongoDB.")