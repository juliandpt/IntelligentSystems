import sqlite3
import csv 

databasePath = 'RecomendationSystem/database/database.db'
csvPath = 'RecomendationSystem/data/'

con = sqlite3.connect(databasePath)
cur = con.cursor()

def createTables():
    print("Creating Links table...")
    cur.execute('CREATE TABLE IF NOT EXISTS Links(movieId INTEGER, imdbId INTEGER, tmdbId INTEGER);')

    print("Creating Movies table...")
    cur.execute('CREATE TABLE IF NOT EXISTS Movies(movieId INTEGER, title STRING, genres);')

    print("Creating Ratings table...")
    cur.execute('CREATE TABLE IF NOT EXISTS Ratings(userId INTEGER, movieId INTEGER, rating DOUBLE, timestamp);')

    print("Creating Tags table...")
    cur.execute('CREATE TABLE IF NOT EXISTS Tags(userId INTEGER, movieId INTEGER, tag, timestamp);')

    con.commit()
    print("Tables created saccesfully!")
    
def eliminateData():
    print("Deleting Links table...")
    cur.execute("DELETE FROM Links")

    print("Deleting Movies table...")
    cur.execute("DELETE FROM Movies")

    print("Deleting Ratings table...")
    cur.execute("DELETE FROM Ratings")

    print("Deleting Tags table...")
    cur.execute("DELETE FROM Tags")

    con.commit()
    print("Database data eleminated saccesfully!")

def uploadData(file):
    with open(csvPath + file, 'r', errors="ignore") as archive: 
        reader = csv.DictReader(archive)
        if file == 'links.csv':
            print('Inserting into links...')
            rows = [(i['movieId'], i['imdbId'], i['tmdbId']) for i in reader]
            cur.executemany("INSERT INTO Links(movieId, imdbId, tmdbId) VALUES (?,?,?);", rows)

        elif file == 'movies.csv':
            print('Inserting into movies...')
            rows = [(i['movieId'], i['title'], i['genres']) for i in reader]
            cur.executemany("INSERT INTO Movies(movieId, title, genres) VALUES (?,?,?);", rows)

        elif file == 'ratings.csv':
            print('Inserting into rating...')
            rows = [(i['userId'], i['movieId'], i['rating'], i['timestamp']) for i in reader]
            cur.executemany("INSERT INTO Ratings(userId, movieId, rating, timestamp) VALUES (?,?,?,?);", rows)

        elif file == 'tags.csv':
            print('Inserting into tags...')
            rows = [(i['userId'], i['movieId'], i['tag'], i['timestamp']) for i in reader]
            cur.executemany("INSERT OR IGNORE INTO Tags(userId, movieId, tag, timestamp) VALUES (?,?,?,?);", rows)
        
        con.commit()

def main():
    createTables()
    uploadData('links.csv')
    uploadData('movies.csv')
    uploadData('ratings.csv')
    uploadData('tags.csv')    

if __name__ == '__main__':
    main()