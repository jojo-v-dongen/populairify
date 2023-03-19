import mysql.connector
from db_connection import connection_pool


def Close_DB(cursor, cnx):
    print("CLOSED")
    cursor.close()
    cnx.close()

def Connect_to_DB():

    try:
        cnx = connection_pool.get_connection()
        cursor = cnx.cursor(buffered=True)
        connected = True
        print("CONNECTED")
        return cnx, cursor
    except mysql.connector.Error as err:
        print("Failed to connect to the database: {}".format(err))
        exit(1)
        connected = False


# Connect to the MySQL database
def Update_Leaderboard():
    cnx, cursor = Connect_to_DB()

    # Create a cursor to execute SQL queries


    # Select all rows from the table
    cursor.execute("SELECT song_id, song_all_votes, song_amount_ratings FROM Songs")

    # Iterate over each row and update the song_rating column
    for row in cursor.fetchall():
        song_id = row[0]
        song_all_votes = row[1]
        song_amount_ratings = row[2]

        # Check if song_all_votes is not empty
        if song_all_votes:
            # Convert the song_all_votes blob to a list of integers
            all_votes = [int(x) for x in song_all_votes.decode().split(", ") if x]
            # Calculate the mean rating
            mean_rating = sum(all_votes) / song_amount_ratings
        else:
            # If song_all_votes is empty, set the mean rating to 0
            mean_rating = 0
        
        # Update the song_rating column with the mean rating
        sql = "UPDATE Songs SET song_rating = %s WHERE song_id = %s"
        val = (mean_rating, song_id)
        cursor.execute(sql, val)
        
    # Commit the changes to the database
    cnx.commit()
    Close_DB(cursor=cursor, cnx=cnx)

def Get_Leaderboard():
    cnx, cursor = Connect_to_DB()
    # Select the top 10 songs with the highest ratings
    cursor.execute("SELECT song_name, song_artist_name, song_album_pfp, song_rating, song_artist_url, song_album_url, song_url_spotify FROM Songs ORDER BY song_rating DESC LIMIT 10")
    top_songs = cursor.fetchall()
    songs = []
    for i, song in enumerate(top_songs):
        song_dict = {'name': song[0], 'artist_name': song[1], 'cover_url': song[2], 'rating': song[3], 'ranking': i+1, 'song_artist_url': song[4], 'song_album_url': song[5], 'song_url_spotify': song[6]}
        songs.append(song_dict)
    Close_DB(cursor=cursor, cnx=cnx)
    
    return songs