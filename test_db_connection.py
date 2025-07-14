import pytest
import os
import subprocess
import sys
import time
from testcontainers.mongodb import MongoDbContainer
from db_connection import create_connection, insert_many_movies, find_movie, delete_all_movies # Added delete_all_movies

DEMO_MOVIES = [
    {"title": "Inception", "director": "Christopher Nolan", "year": 2010, "genre": "Sci-Fi", "rating": 8.8},
    {"title": "The Matrix", "director": "The Wachowskis", "year": 1999, "genre": "Sci-Fi", "rating": 8.7},
    {"title": "Interstellar", "director": "Christopher Nolan", "year": 2014, "genre": "Sci-Fi", "rating": 8.6},
    {"title": "The Dark Knight", "director": "Christopher Nolan", "year": 2008, "genre": "Action", "rating": 9.0},
    {"title": "Parasite", "director": "Bong Joon-ho", "year": 2019, "genre": "Thriller", "rating": 8.6},
    {"title": "Spirited Away", "director": "Hayao Miyazaki", "year": 2001, "genre": "Animation", "rating": 8.6},
    {"title": "Pulp Fiction", "director": "Quentin Tarantino", "year": 1994, "genre": "Crime", "rating": 8.9},
    {"title": "Fight Club", "director": "David Fincher", "year": 1999, "genre": "Drama", "rating": 8.8},
    {"title": "Forrest Gump", "director": "Robert Zemeckis", "year": 1994, "genre": "Drama", "rating": 8.8},
    {"title": "The Shawshank Redemption", "director": "Frank Darabont", "year": 1994, "genre": "Drama", "rating": 9.3},
    {"title": "The Godfather", "director": "Francis Ford Coppola", "year": 1972, "genre": "Crime", "rating": 9.2},
    {"title": "The Lord of the Rings", "director": "Peter Jackson", "year": 2003, "genre": "Fantasy", "rating": 8.9},
    {"title": "The Avengers", "director": "Joss Whedon", "year": 2012, "genre": "Action", "rating": 8.0},
    {"title": "Titanic", "director": "James Cameron", "year": 1997, "genre": "Romance", "rating": 7.9},
    {"title": "Gladiator", "director": "Ridley Scott", "year": 2000, "genre": "Action", "rating": 8.5},
    {"title": "Toy Story", "director": "John Lasseter", "year": 1995, "genre": "Animation", "rating": 8.3},
    {"title": "Coco", "director": "Lee Unkrich", "year": 2017, "genre": "Animation", "rating": 8.4},
    {"title": "Jurassic Park", "director": "Steven Spielberg", "year": 1993, "genre": "Adventure", "rating": 8.2},
    {"title": "Mad Max: Fury Road", "director": "George Miller", "year": 2015, "genre": "Action", "rating": 8.1},
    {"title": "Whiplash", "director": "Damien Chazelle", "year": 2014, "genre": "Drama", "rating": 8.5},
]

@pytest.fixture(scope="module")
def mongo_container_with_data():
    """
    Creates a single MongoDB 8.0 test container, inserts the 20 demo documents,
    and yields the MongoDB URI. This fixture runs once per module.
    """
    print("\nStarting MongoDB 8.0 test container and inserting demo data...")
    # Specify MongoDB 8.0 image
    with MongoDbContainer("mongo:8.0") as mongo:
        mongo_uri = mongo.get_connection_url()
        print(f"MongoDB container started. URI: {mongo_uri}")

        # Give MongoDB a moment to be fully ready inside the container
        # This is a common practice with testcontainers for services that need startup time.
        time.sleep(5) 

        # Connect to the running container and insert data
        client = create_connection(mongo_uri, tls_enabled=False)
        if client:
            # Ensure the database is clean before inserting data for the module's tests
            delete_all_movies(client) 
            insert_many_movies(client, DEMO_MOVIES)
            print(f"Inserted {len(DEMO_MOVIES)} demo movies into the container.")
            client.close()
        else:
            pytest.fail("Failed to connect to MongoDB container for data insertion.")
        
        yield mongo_uri # Provide the URI to tests that depend on this fixture
    print("MongoDB container stopped.")

def test_data_insertion_and_retrieval(mongo_container_with_data):
    """
    Tests that the MongoDB container is running and the data was inserted correctly
    and can be retrieved directly via db_connection functions.
    This is an integration test for db_connection.
    """
    mongo_uri = mongo_container_with_data
    client = create_connection(mongo_uri, tls_enabled=False)
    assert client is not None, "Failed to connect to MongoDB test container."

    # Verify that a specific inserted movie can be found
    found_movie = find_movie(client, {"title": "The Matrix"})
    assert found_movie is not None
    assert found_movie["year"] == 1999
    assert "director" in found_movie
    assert found_movie["director"] == "The Wachowskis"
    print(f"Integration test for db_connection: Found '{found_movie['title']}'.")
    client.close()

def test_app_can_query_mongodb(mongo_container_with_data):
    """
    Confirms that demo_app.py, when run as a script, can successfully connect to 
    and query data from the MongoDB test container.
    This is an integration test for the entire application flow.
    """
    mongo_uri = mongo_container_with_data
    print(f"\nRunning demo_app.py as a subprocess against MongoDB URI: {mongo_uri}")

    # Set the MONGO_URI environment variable for demo_app.py
    os.environ["MONGO_URI"] = mongo_uri

    try:
        # Run demo_app.py as a separate process and capture its output
        result = subprocess.run(
            [sys.executable, "demo_app.py"],
            capture_output=True,
            text=True,
            check=True, # Raise a CalledProcessError if demo_app.py returns a non-zero exit code
            env=os.environ # Pass the current environment including MONGO_URI
        )
        print("--- demo_app.py stdout ---")
        print(result.stdout)
        print("--- demo_app.py stderr ---")
        print(result.stderr)
        print("--------------------------")

        # Assert that the app successfully found a movie.
        # We look for specific output indicating success.
        assert "Queried and found movie:" in result.stdout
        assert "Movie with title" in result.stdout or "Queried and found movie:" in result.stdout
        assert "Failed to establish connection to MongoDB." not in result.stdout
        print("Integration test: demo_app.py successfully queried a movie!")

    except subprocess.CalledProcessError as e:
        pytest.fail(f"demo_app.py failed to run successfully against MongoDB. "
                   f"Return Code: {e.returncode}\nStdout: {e.stdout}\nStderr: {e.stderr}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during the app integration test: {e}")
    finally:
        # Clean up the environment variable after the test
        if "MONGO_URI" in os.environ:
            del os.environ["MONGO_URI"]