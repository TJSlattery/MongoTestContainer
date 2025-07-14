from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def create_connection(uri, tls_enabled=False):
    """
    Establishes a connection to the MongoDB database.
    """
    try:
        if tls_enabled:
            client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)
        else:
            client = MongoClient(uri)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        return client
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while connecting to MongoDB: {e}")
        return None

def insert_one_movie(client, movie):
    """
    Inserts a single movie document into the 'movies' collection.
    Returns the ID of the inserted document.
    """
    db = client.movie_database  # Using 'movie_database' as the database name
    collection = db.movies      # Collection Name
    return collection.insert_one(movie).inserted_id

def insert_many_movies(client, movies):
    """
    Inserts multiple movie documents into the 'movies' collection.
    """
    db = client.movie_database  # Using 'movie_database' as the database name
    collection = db.movies
    if movies:
        try:
            result = collection.insert_many(movies)
            return result.inserted_ids
        except Exception as e:
            print(f"Error inserting many movies: {e}")
            return []
    return []

def find_movie(client, query):
    """
    Finds a single movie document based on the provided query.
    """
    db = client.movie_database  # Using 'movie_database' as the database name
    collection = db.movies
    return collection.find_one(query)

def delete_all_movies(client):
    """
    Deletes all documents from the 'movies' collection.
    Useful for ensuring a clean state between test runs if scope is function.
    """
    db = client.movie_database
    collection = db.movies
    return collection.delete_many({})