import os

import mysql.connector
import bcrypt
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy_song_finder import get_random, get_song
import datetime
import re
import random
from threading import Thread
from db_connection import connection_pool
from main import Increment_User_Group
import numpy as np
import secrets
import string


# Encryption function
def encrypt_password(password):
    # Create a password hash
    salt = bcrypt.gensalt(11)

    # print("s", salt)

    password = password.encode('utf-8')
    encrypted_password = bcrypt.hashpw(password, salt)

    return encrypted_password


def sign_up(username, email, password):
    # Check if the username already exists in the database
    if not is_valid_email(email):
        return "Email is invalid."
  
    cnx, cursor = Connect_to_DB()
    sql = "SELECT * FROM ##### WHERE email = %s"
    cursor.execute(sql, (email,))
    result = cursor.fetchone()
    if result:
        #print("email already exists. Please login.")
        # Close_DB(cursor, cnx)
        t = Thread(target=Close_DB, args=(cursor, cnx)).start()
        return "email is already registered. Please login."
    # Encrypt the password
    encrypted_password = encrypt_password(password)
    # Insert the new user into the database
    sql = "INSERT INTO ##### (username, email, password, current_group, voted_songs) VALUES (%s, %s, %s, %s, %s)"
    val = (username, email.lower(), encrypted_password, 0, "")
    # print(salt)
    print("pass", password)
    cursor.execute(sql, val)
    cnx.commit()
    print("Sign up successful!")
    # Close_DB(cursor, cnx)
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()
    return True


def login(email, password):
    cnx, cursor = Connect_to_DB()
    # Check if the username exists in the database
    sql = "SELECT * FROM ##### WHERE email = %s"
    cursor.execute(sql, (email.lower(),))
    result = cursor.fetchone()
    # Close_DB(cursor, cnx)
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()
    if not result:
        #print("Invalid email or password.")
        return "Invalid email or password."
    

    hashed_password = result[3]
    password = password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')
    if bcrypt.checkpw(password, hashed_password):
        return True
    else:
        return "Invalid email or password."


def popular_artists():
  pop_list = ['The Weeknd', 'Taylor Swift', 'Rihanna', 'Miley Cyrus', 'Shakira', 'Ed Sheeran', 'Sam Smith', 'David Guetta', 'SZA', 'Justin Bieber', 'Drake', 'Eminem', 'Ariana Grande', 'Harry Styles', 'Bad Bunny', 'Dua Lipa', 'Calvin Harris', 'Coldplay', '21 Savage', 'Imagine Dragons', 'Bruno Mars', 'Lady Gaga', 'Selena Gomez', 'Maroon 5', 'Chris Brown', 'Metro Boomin', 'Beyoncé', 'Kanye West', 'Bizarrap', 'Doja Cat', 'Post Malone', 'Khalid', 'Billie Eilish', 'Katy Perry', 'Adele', 'J Balvin', 'Daddy Yankee', 'Bebe Rexha', 'KAROL G', 'OneRepublic', 'Ozuna', 'Elton John', 'Future', 'Tiësto', 'Shawn Mendes', 'Sia', 'Nicki Minaj', 'Kim Petras', 'Travis Scott', 'Halsey', 'Marshmello', 'Kendrick Lamar', 'Queen', 'The Kid LAROI', 'Rauw Alejandro', 'Arctic Monkeys', 'Lana Del Rey', 'Black Eyed Peas', 'Camila Cabello', 'Rema', 'ROSALÍA', 'Lil Nas X', 'BTS', 'Feid', 'One Direction', 'Charlie Puth', 'JAY-Z', 'P!nk', 'Meghan Trainor', 'Lil Uzi Vert', 'RAYE', 'Olivia Rodrigo', 'XXXTENTACION', 'Manuel Turizo', 'Michael Jackson', 'Farruko', 'Quevedo', 'Robin Schulz', 'PinkPantheress', 'Avicii', 'Miguel', 'Maluma', 'James Arthur', 'The Chainsmokers', 'Oliver Tree', 'Stephen Sanchez', 'Jason Derulo', 'Ellie Goulding', 'Linkin Park', 'J. Cole', 'Pitbull', 'The Neighbourhood', 'Britney Spears', 'Tate McRae', 'Lewis Capaldi', 'Ice Spice', 'd4vd', 'Myke Towers', 'Cardi B', 'Juice WRLD', 'Ava Max', '070 Shake', 'Lil Baby', 'Gorillaz', 'Anuel AA', 'Lizzo', '50 Cent', 'Chencho Corleone', 'Arijit Singh', 'Justin Timberlake', 'Jack Harlow', 'Steve Lacy', 'DaBaby', 'Lil Wayne', 'Arcángel', 'Romeo Santos', 'JVKE', 'Joji', 'Snoop Dogg', 'DJ Snake', 'Diplo', 'Wiz Khalifa', 'The Beatles', 'Tom Odell', 'DJ Khaled', 'Pritam', 'Demi Lovato', 'Sean Paul', 'Central Cee', 'Red Hot Chili Peppers', 'Yandel', 'Calum Scott', 'Don Omar', 'Kygo', 'Måneskin', 'Young Thug', 'Nirvana', 'Jhayco', 'Ty Dolla $ign', 'Sebastian Yatra', 'AC/DC', 'Flo Rida', 'Fleetwood Mac', "Guns N' Roses", 'Em Beihold', 'Becky G', 'Giveon', 'Swae Lee', 'A.R. Rahman', 'Macklemore', 'Glass Animals', 'Alan Walker', 'Anitta', 'Usher', 'ABBA', 'Elley Duhé', 'Niall Horan', 'John Legend', 'Gunna', 'Don Toliver', 'Labrinth', 'Metallica', 'Mariah Carey', 'Madonna', 'Megan Thee Stallion', 'Anne-Marie', 'Pop Smoke', 'A$AP Rocky', 'Coi Leray', 'Polo G', 'Kodak Black', 'Pharrell Williams', 'Frank Ocean', 'Kali Uchis', 'Sech', 'Martin Garrix', 'Wisin & Yandel', 'Shreya Ghoshal', 'Christina Aguilera', 'Green Day', 'Alok', 'Skrillex', 'Bon Jovi', 'Nicky Jam', 'Creedence Clearwater Revival', 'Tame Impala', 'Conan Gray', 'Duki', 'Whitney Houston', 'Kid Cudi', 'Tyga', 'Hozier', 'Sabrina Carpenter', 'The Rolling Stones', 'Felix Jaehn', 'Bee Gees', 'Anderson .Paak', 'Daniel Caesar', 'Lost Frequencies', 'Alicia Keys', 'Dr. Dre', 'TINI', 'NewJeans', 'Mark Ronson', 'Mac Miller', 'Aerosmith', 'Zara Larsson', 'Ñengo Flow', 'Jennifer Lopez', 'Tainy', 'Panic! At The Disco', '2Pac', 'Swedish House Mafia', 'Luis Fonsi', 'Lil Durk', 'Trippie Redd', 'Steve Aoki', 'Rosa Linn', 'Akon', 'Vishal-Shekhar', 'The Police', 'Disney', 'Twenty One Pilots', 'Fall Out Boy', 'Morgan Wallen', 'Roddy Ricch', 'Christian Nodal', 'Enrique Iglesias', 'Ruth B.', 'The Notorious B.I.G.', 'Tyler, The Creator', 'MEDUZA', 'Major Lazer', 'Childish Gambino', 'ZAYN', 'Clean Bandit', 'Grupo Frontera', 'Tory Lanez', 'Maria Becerra', 'De La Ghetto', 'BLACKPINK', 'Tanishk Bagchi', 'Justin Quiles', 'JID', 'Jonas Brothers', 'Nicki Nicole', 'Mora', 'R3HAB', 'Zion & Lennox', 'Jessie Reyez', 'Camilo', 'Reik', 'The Killers', 'PNAU', 'Billy Joel', 'Radiohead', '5 Seconds of Summer', 'Becky Hill', 'Carin Leon', 'Ovy On The Drums', 'blackbear', 'Vance Joy', 'Daft Punk', 'Alesso', 'Fuerza Regida', 'Paramore', 'Nelly Furtado', 'League of Legends', 'Dean Lewis', 'U2', 'Ne-Yo', 'Summer Walker', 'Sachin-Jigar', 'A Boogie Wit da Hoodie', 'Amitabh Bhattacharya', 'Big Sean', 'Gesaffelstein', 'Jonas Blue', 'Troye Sivan', 'Imanbek', 'Cris Mj', 'Foo Fighters', 'Bastille', 'Outkast', 'Pink Floyd', 'Lauv', 'Eagles', 'Danny Ocean', 'Little Mix', 'Natanael Cano', 'Bryan Adams', 'PARTYNEXTDOOR', 'Bomba Estéreo', 'Macklemore & Ryan Lewis', 'George Ezra', 'benny blanco', 'Lorde', 'Ryan Lewis', 'Migos', 'Phil Collins', 'Joel Corry', 'Elvis Presley', 'Lil Tjay', 'Jubin Nautiyal', 'Led Zeppelin', 'Oasis', 'Avril Lavigne', 'Kesha', 'Stevie Wonder', 'Vishal Dadlani', 'Cigarettes After Sex', 'Junior H', 'French Montana', 'Peso Pluma', 'Julia Michaels', 'The Lumineers', 'David Bowie', 'NF', 'Kumaar', 'Zedd', 'Nelly', 'Rels B', 'Tove Lo', 'Burna Boy', 'Alessia Cara', 'YoungBoy Never Broke Again', 'Mac DeMarco', 'Bryson Tiller', 'Timbaland', 'El Alfa', 'John Mayer', 'Journey', 'Juanes', 'Alec Benjamin', 'beabadoobee', 'Playboi Carti', 'Luke Combs', 'Rex Orange County', 'Bob Marley & The Wailers', 'TOTO', 'Prince Royce', 'Galantis', 'Offset', 'blink-182', 'The 1975', 'Morat', 'Dire Straits', 'Arcane', 'Jason Mraz', 'R.E.M.', 'Backstreet Boys', 'Baby Keem', 'Tears For Fears', 'Topic', 'Charli XCX', '6LACK', 'Udit Narayan', 'System Of A Down', 'Shaggy', 'MC Ryan SP', 'WILLOW', 'The Offspring', 'The Script', 'Marvin Gaye', 'The Cure', 'Ricky Martin', 'Aventura', 'B.o.B', 'Jax Jones', 'Dove Cameron', 'Tiago PZK', 'sped up nightcore', 'Jay Wheeler', 'Chris Stapleton', 'Train', 'Silk Sonic', 'Jung Kook', 'Alka Yagnik', 'Carlos Vives', 'Kelly Clarkson', 'Rita Ora', 'Gabry Ponte', 'Piso 21', 'Maná', 'Amit Trivedi', 'Hotel Ugly', 'Nicky Youre', 'Zach Bryan', 'Earth, Wind & Fire', 'Jessie J', 'Ella Henderson', 'Luis Miguel', 'Lil Peep', 'Brent Faiyaz', 'Carly Rae Jepsen', '24kGoldn', 'Shekhar Ravjiani', 'G-Eazy', 'Plan B', 'Sigala', 'Natti Natasha', 'Ice Cube', 'King', 'Marília Mendonça', 'Paulo Londra', 'Shankar Mahadevan', 'Alejandro Fernández', 'Atif Aslam', 'a-ha', 'Machine Gun Kelly', 'Shania Twain', 'Neha Kakkar', 'NLE Choppa', 'Bruce Springsteen', 'Kordhell', 'Dalex', 'Tones And I', 'Dermot Kennedy', 'Quavo', 'Russ', 'Polimá Westcoast', 'Asees Kaur', 'Armaan Malik', 'Banda MS de Sergio Lizárraga', 'Keane', 'Lyanno', 'Kate Bush', 'Marc Anthony', 'Kehlani', 'X Ambassadors', 'Julieta Venegas', 'George Michael', 'Nickelback', 'Maren Morris', 'Badshah', 'Lenny Tavárez', 'Disclosure', 'Luis R Conriquez', 'Alejandro Sanz', 'Tems', 'CKay', 'Amy Winehouse', 'Depeche Mode', 'iann dior', 'Meek Mill', 'KK', 'The Cranberries', 'Kings of Leon', 'Shilpa Rao', 'Fred again..', 'dazy', 'Thundercat', 'Florence + The Machine', 'MNEK', 'Grupo Firme', 'The White Stripes', 'Sonu Nigam', 'Logic', 'Rae Sremmurd', 'Gucci Mane', 'Lynyrd Skynyrd', 'Libianca', 'Standly', 'James Hype', 'Lil Tecca', 'Eladio Carrion', 'Cults', 'Bradley Cooper', 'My Chemical Romance', 'Anirudh Ravichander', 'Céline Dion', "Destiny's Child", 'Coolio', 'Grupo Marca Registrada', 'Mohit Chauhan', 'Cyndi Lauper', 'Annie Lennox', 'Sunidhi Chauhan', 'Ana Castela', 'KISS', 'Wisin', 'Seafret', 'Brray', 'Gabito Ballesteros', 'AURORA', 'New West', 'Black Sabbath', 'Gwen Stefani', 'Nio Garcia', 'Leo Santana', 'Calibre 50', 'Mike Posner', 'Melanie Martinez', 'Mau y Ricky', 'Muse', 'The Goo Goo Dolls', 'Daryl Hall & John Oates', 'girl in red', 'Pearl Jam', 'Dolly Parton', 'Sam Feldt', 'Neeti Mohan', 'Lord Huron', 'Paul McCartney', 'Frank Sinatra', 'Bon Iver', 'H.E.R.', 'The Game', 'Cage The Elephant', 'Goodboys', 'Bazzi', 'Lil Yachty', 'Armin van Buuren', 'Jeremy Zucker', 'Mc Don Juan', 'Mari Fernandez', 'Rick Ross', 'Jowell & Randy', 'Lukas Graham', 'Scorpions', 'B Praak', 'Tony Dize', 'Los Ángeles Azules', 'Madison Beer', 'Pablo Alborán', 'Normani', 'Foster The People', 'Kane Brown', 'Christina Perri', 'Weezer', 'Jaymes Young', 'Lin-Manuel Miranda', 'Hailee Steinfeld', 'Aitana', 'DJ Nelson', 'YG', 'Michael Bublé', 'Jeremih', 'Mithoon', 'Passenger', 'Justine Skye', 'Jorge & Mateus', 'The Walters', 'Boney M.', 'FAST BOY', 'MGMT', 'Taio Cruz', 'Bring Me The Horizon', 'Sachet Tandon', 'Bill Withers', 'Beach House', 'Limp Bizkit', 'Chase Atlantic', 'GAYLE', 'Clairo', 'Eric Clapton', 'Slipknot', 'Gym Class Heroes', 'Zendaya', 'Ryan Castro', 'Yeat', 'Fergie', 'The Strokes', 'Migrantes', 'Noah Cyrus', 'Shankar-Ehsaan-Loy', 'Latto', 'Jonita Gandhi', 'Yuridia', 'Lizzy McAlpine', 'TWICE', 'Moneybagg Yo', 'Van Halen', 'James Bay', 'Gusttavo Lima', 'Sean Kingston', 'Eden Muñoz', 'A7S', 'ACRAZE', 'Blur', 'Jesse & Joy', 'Florida Georgia Line', 'Paloma Faith', 'AJR', 'Pailita', 'Ayra Starr', 'Javed Ali', 'Miggy Dela Rosa', 'L7NNON', 'Oscar Maydon', 'Jack Johnson', 'Fujii Kaze', 'Omar Apollo', 'T.I.', 'Tulsi Kumar', 'DJ Luian', 'DNCE', 'James Carter', 'Electric Light Orchestra', 'T-Pain', 'Johnny Cash', 'Rahat Fateh Ali Khan', 'Devi Sri Prasad', 'Mambo Kingz', 'Zé Felipe', 'Shouse', 'Van Morrison', 'Himesh Reshammiya', 'Milky Chance', 'Beach Weather', 'Xamã', 'Matheus & Kauan', '$uicideboy$', 'Chinmayi', 'Henrique & Juliano', 'Jhené Aiko', 'Rochak Kohli', 'A$AP Ferg', 'Amaal Mallik', 'La Joaqui', 'TV Girl', 'Ángela Aguilar', 'Robbie Williams', 'Regard', 'SAINt JHN', 'Danna Paola', 'Ms. Lauryn Hill', 'Maiara & Maraisa', 'The Pussycat Dolls', 'Lata Mangeshkar', 'The Smiths', 'Cheat Codes', 'Chance the Rapper', 'Stromae', 'Simon & Garfunkel', 'Baby Rasta', 'Dominic Fike', 'Nas', 'Takeoff', 'Selena Gomez & The Scene', 'Tom Grennan', 'John Lennon', 'Flume', 'The Clash', 'The Beach Boys', 'Evanescence', 'Julión Álvarez y su Norteño Banda', 'Papa Roach', 'Anu Malik', 'Aretha Franklin', 'Darshan Raval', 'Busta Rhymes', 'Prince', 'LiL CaKe', 'Seeb', 'Luísa Sonza', 'Israel & Rodolffo', 'Freddie Dredd', 'Dan + Shay', 'Chayanne', 'Mitski', 'WALK THE MOON', 'Gryffin', 'Thaman S', 'NAV', 'Blondie', 'Los Enanitos Verdes', 'ILLENIUM', 'Rod Stewart', 'Soulja Boy', 'SYML', 'Rammstein', 'Lionel Richie', 'Brytiago', 'Rvssian', 'Ashe', 'AP Dhillon', 'Timmy Trumpet', 'Fifth Harmony', 'Gustavo Mioto', 'Kelsea Ballerini', 'M83', 'Eurythmics', 'Disturbed', 'Darell', 'Sid Sriram', 'Santana', 'The Smashing Pumpkins', 'Marco Antonio Solís', 'Stormzy', 'La Adictiva', 'Mustard', 'Baby Tate', 'MARINA', 'DMX', 'Mary J. Blige', 'Internet Money', 'Missy Elliott', 'Key Glock', 'Pink Sweat$', 'Chief Keef', 'James Blunt', 'Juan Luis Guerra 4.40', 'Nikhita Gandhi', 'WIU', 'Thalia', 'C. Tangana', 'Caralisa Monteiro', 'Guilherme & Benuto', 'Dhvani Bhanushali', 'Riton', 'Birdy', 'Natalia Lafourcade', 'Gotye', 'Lunay', 'Blessd', 'Benson Boone', 'Wizkid', 'Sting', 'Loud Luxury', 'Spice Girls', 'Isabel LaRosa', 'Roxette', 'John Newman', 'will.i.am', 'Sasha Alex Sloan', 'Kenny Loggins', 'Three Days Grace', 'Joan Sebastian', 'bbno$', 'Hans Zimmer', 'INTERWORLD', 'Andy Grammer', 'Ofenbach', 'Vishal Mishra', '3 Doors Down', 'Leon Bridges', 'Olivia Newton-John', 'Foreigner', 'Empire of the Sun', 'Billy Idol', 'Emilia', 'LE SSERAFIM', 'NIKI', 'Bob Dylan', 'Hariharan', 'BoyWithUke', '6ix9ine', 'Mabel', 'BYOR', 'Guru Randhawa', 'Diljit Dosanjh', 'Lasso', 'MAX', 'Aya Nakamura', 'La Oreja de Van Gogh', 'Saweetie', '2 Chainz', 'Carrie Underwood', 'Benny Dayal', 'Oliver Heldens', 'TOMORROW X TOGETHER', 'Yo Yo Honey Singh', 'Sukriti Kakar', 'Wham!', 'Jatin-Lalit', 'Ali Gatie', 'Diddy', 'Korn', 'Thomas Rhett', 'Kimbra', 'LANY', 'Ski Mask The Slump God', 'Alfredo Olivas', 'LUDMILLA', 'S. P. Balasubrahmanyam', 'Mumford & Sons', 'Survivor', 'Chris Jedi', 'Counting Crows', 'Yuvan Shankar Raja', 'Juan Gabriel', 'Eyedress', 'Rage Against The Machine', "Gigi D'Agostino", 'Dimitri Vegas & Like Mike', 'Carla Morrison', 'Lenny Kravitz', 'Ghost', 'Los Tigres Del Norte', 'ThxSoMch', 'Aitch', 'Pixies', 'Jess Glynne', 'DVRST', 'Owl City', 'Jasleen Royal', 'Dave', 'Lenin Ramírez', 'Soda Stereo', 'Armani White', 'Shashaa Tirupati', 'Maldy', 'K. S. Chithra', 'YNW Melly', 'Ozzy Osbourne', 'Xanemusic', 'Luan Santana', 'Shubh', 'TLC', 'Xand Avião', 'Paloma Mami', 'Zac Brown Band', 'KHEA', 'Edgardo Nuñez', 'Icona Pop', 'Parampara Tandon', 'Tina Turner', 'Tracy Chapman', 'Manu Chao', 'Phoebe Bridgers', 'Norah Jones', 'Pedro Capó', 'dhruv', 'Camila', 'Neeraj Shridhar', 'Vicente Fernández', "Rag'n'Bone Man", 'Mc Danny', 'Mahalini', 'Yusuf / Cat Stevens', 'Ella Eyre', 'LUM!X', 'Kungs', 'Yasser Desai', 'Hombres G', 'The Fray', 'ScHoolboy Q', 'Surf Curse', 'keshi', 'JP Cooper', 'Kodaline', 'ZZ Top', 'Fetty Wap', 'INXS', 'Ricardo Arjona', 'Cher', 'Ciara', 'Eslabon Armado', 'Carlos Rivera', 'Joey Bada$$', 'Gurinder Gill', 'Jimi Hendrix', 'Blxst', 'Bryant Myers', 'Sleepy Hallow', 'AFROJACK', 'Two Feet', 'Tammi Terrell', 'Salim–Sulaiman', 'Talking Heads', 'Jordan Davis', 'Miranda Lambert', 'Duncan Laurence', 'Years & Years', 'Rudimental', 'MAGIC!', 'Lykke Li', 'Sofía Reyes', 'Trueno', 'MC Cabelinho', 'Louis Armstrong', 'Eric Church', 'The Vamps', 'Noriel', 'Jason Aldean', 'The Mamas & The Papas', 'Luke Bryan', 'Santa Fe Klan', 'Mc Daniel', 'Hoobastank', 'Wesley Safadão', 'Tom Petty', 'Snow Patrol', 'Rashmi Virag', 'G. V. Prakash', 'Lady A', "Why Don't We", 'Tego Calderón', 'Mon Laferte', 'Gera MX', 'Willy William', 'Ben E. King', 'Sam Hunt', 'NATTAN', 'LISA', 'José José', 'Felipe Amorim', 'Mc Paiva ZS', 'Kotim', 'El Fantasma', 'Mimi Webb', 'Benny Benassi', 'Sachet-Parampara', 'LMFAO', 'Tion Wayne', 'Kansas', 'Dilsinho', '(G)I-DLE', '$NOT', 'Zac Efron', 'Bob Sinclar', 'Will Smith', 'Purple Disco Machine', 'Mae Stephens', 'Belinda', 'Rascal Flatts', 'Powfu', 'Cosculluela', 'BØRNS', 'Sade', 'Matheus Fernandes', 'Aleman', 'Tulus', 'TWISTED', 'Ludovico Einaudi', 'João Gomes', 'Mötley Crüe', 'Dynoro', 'Noah Kahan', 'CNCO', 'JP Saxe', 'Kool & The Gang', 'Patrick Watson', 'Orochi', 'Masked Wolf', 'Rich Brian', 'Beéle', 'Iron Maiden', 'fun.', 'Bonnie Tyler', 'Fivio Foreign', 'Colbie Caillat', 'The Marías', 'PEDRO SAMPAIO', 'Ella Mai', 'Kumar Sanu', 'Sum 41', 'Vacations', 'Jorja Smith', 'Johann Sebastian Bach', 'Dread Mar I', 'Laura Pausini', 'Cartel De Santa', 'Nathan Dawe', 'Abhijeet', 'David Bisbal', 'Gracie Abrams', 'Neo Beats', 'Grey', 'Sukhwinder Singh', 'Diana Ross', 'Gerardo Ortiz', 'Stray Kids', 'John Denver', 'Heart', 'Sufjan Stevens', 'Luan Pereira', 'VIZE', 'Otis Redding', 'HUGEL', 'Blake Shelton', 'GloRilla', 'America', 'Fireboy DML', 'DJ ESCOBAR', 'Matt Sassari', 'Sidhu Moose Wala', 'Zion', '11:11 Music Group', 'Chelsea Cutler', 'The Temptations', 'Shaan', 'Keith Urban', 'Lauren Spencer Smith', 'Palak Muchhal', 'Stacey Ryan', 'No Doubt', 'Capital Cities', 'Kylie Minogue', 'Los Tucanes De Tijuana', 'Teto', 'Yung Gravy', 'FINNEAS', 'Diego & Victor Hugo', 'Jay Sean', 'Kany García', 'Def Leppard', 'The Who', 'Ha*Ash', 'Denzel Curry', 'Shiloh Dynasty', 'Yohani', 'alt-J', 'Zack Tabudlo', 'Ankit Tiwari', 'Young Nudy', 'Mother Mother', 'Zé Neto & Cristiano', 'Jimmy Eat World', 'Kailash Kher', 'Miranda!', 'Ana Gabriel', 'Martin Jensen', 'Deorro', 'Miguel Bosé', 'The Black Keys', 'MC Menor MT', 'Lil Mosey', 'Montell Fish', 'ARIZONATEARS', 'Trevor Daniel', 'Aminé', 'Cali Y El Dandee', 'Oh Wonder', 'Ivete Sangalo', 'Río Roma', 'Morad', 'Chicago', 'Bailey Zimmerman', 'Hugo & Guilherme', 'Simple Minds', 'Casper Magico', 'Iggy Azalea', 'Selena', 'Matuê', 'Duran Duran', 'Jeet Gannguli', 'YUNGBLUD', 'Avenged Sevenfold', 'Jul', 'Bacilos', '88rising', 'Ruel', 'Ricardo Montaner', 'Bellakath', 'Deftones', 'Red Velvet', 'L-Gante', 'Surfaces', 'Travis Barker', 'Clinton Kane', 'The Verve', 'Shweta Mohan', 'MC MENOR HR', 'BONES', 'Karthik', 'Of Monsters and Men', 'DJ Jeeh FDC', 'Kevin Kaarl', 'Vansire', 'FISHER', 'Wallows', 'Oruam', 'Nessa Barrett', 'Willie Nelson', 'Paul Simon', 'Kevin Roldan', 'LIT killah', 'creamy', 'Skillet', 'MKTO', 'La Arrolladora Banda El Limón De Rene Camacho', 'Juan Magán', 'Mr.Kitty', 'GIMS', 'Mario', 'Öwnboss', 'Madhur Sharma', 'Eliza Rose', 'Harrdy Sandhu', 'Maggie Rogers', 'Matoma', 'HITMAKER', 'Tom Walker', 'M.I.A.', 'Jon Pardi', 'Kenshi Yonezu', 'Marca MP', 'Cristian Castro', 'Cordae', 'Bea Miller', 'Beastie Boys', 'Dxrk ダーク', 'Guaynaa', 'Interplanetary Criminal', 'Tinashe', 'Yng Lvcas', 'Etta James', 'Astrid S', 'Intense', 'Paulina Rubio', 'Vintage Culture', 'Connor Price', 'Ray Charles', 'Ray Dalton', 'Sofi Tukker', 'Rajat Nagpal', 'George Harrison', 'Rekha Bhardwaj', 'Lazza', 'Nardo Wick', 'Sublime', 'HVME', 'Luar La L', 'Elle King', 'MC Hariel', 'Yuri Redicopa', 'BIA', 'Cascada', 'The Jackson 5', 'Cavetown', 'HARDY', 'Sandro Cavazza', 'Banda El Recodo', 'Calle 13', 'All Time Low', 'Majid Jordan', 'KALEO', 'King Von', 'Nina Simone', 'Idina Menzel', '42 Dugg', 'Tony Aguirre', 'The Doobie Brothers', 'Ludwig van Beethoven', 'YOASOBI', 'Kina', 'Smash Mouth', 'Trey Songz', 'James Blake', 'UB40', 'Leona Lewis', 'Roop Kumar Rathod', 'Lucky Daye', 'INNA', 'Fuego', 'Tim McGraw', 'Dierks Bentley', 'Romy', 'Andrés Calamaro', 'Skylar Grey', 'Zoe Wees', 'Yot Club', 'Dhanush', 'Rusherking', 'Elderbrook', 'Luny Tunes', 'Kacey Musgraves', 'Kenny Rogers', 'Kenny Chesney', 'Zoé', 'Genesis', 'Ricky Montgomery', 'Gloria Estefan', 'Franco De Vita', 'London Symphony Orchestra', 'Novo Amor', 'Brooks & Dunn', 'Sajid-Wajid', 'Gnarls Barkley', 'M. M. Keeravani', 'Micro TDH', 'Nightcrawlers', 'Sin Bandera', 'Audioslave', 'salem ilese', 'Payal Dev', 'Gente De Zona', 'Fugees', 'Kxllswxtch', 'Bad Gyal', 'The Wanted', 'Intocable', 'R. D. Burman', 'Lee Brice', 'Marcianeke', 'MC MENOR SG', 'Maite Perroni', 'BENEE', 'NEIKED', 'Stebin Ben', 'Mariah Angeliq', 'Tito "El Bambino"', 'Mc Jacaré', 'Five Finger Death Punch', 'American Authors', 'Kavitaa Seth', 'Au/Ra', 'MIKA', 'Neil Diamond', 'IVE', 'Falling In Reverse', 'BANNERS', 'Pusha T', 'Dreamville', 'Cian Ducrot', 'Pepe Aguilar', 'Sam Fischer', 'Dulce María', 'Men At Work', 'Tai Verdes', 'Dillon Francis', 'The Temper Trap', 'Tchakabum', 'Sheryl Crow', 'Lil Pump', 'Tyler Childers', 'Kaifi Khalil', 'Tokischa', 'Masego', 'Alejo', 'Social House', 'Karan Aujla', 'Ovi', 'Alan Jackson', 'Kenia OS', 'Starship', 'The Outfield', 'Hippie Sabotage', 'Tochi Raina', 'Tom Petty and the Heartbreakers', 'Sam Cooke', 'Wolfgang Amadeus Mozart', 'Franz Ferdinand', 'Simple Plan', 'Jarabe De Palo', 'SLANDER', 'Rocío Dúrcal', 'Omar Montes', 'Cat Burns', 'Billy Ray Cyrus', 'OMI', 'Eros Ramazzotti', 'Arko', 'Boston', 'Subelo NEO', 'The All-American Rejects', 'Frédéric Chopin', 'Tungevaag', 'Arizona Zervas', 'Anahí', 'Mika Singh', 'Fat Joe', 'Murilo Huff', 'Mc Tato', 'Sfera Ebbasta', 'Matisse', '4 Non Blondes', 'Lennon Stella', 'Rise Against', 'The Kooks', 'Treyce', 'Wale', 'Kadu Martins', 'Rvfv', 'RBD', 'G Herbo', 'Russ Millions', 'Nakash Aziz', 'Ivan Cornejo', 'Prezioso', 'Don Diablo', 'Queens of the Stone Age', 'Ja Rule', 'Neon Trees', 'Mike Perry', 'Far East Movement', 'Anvita Dutt', 'Los Dos Carnales', 'Iyaz', 'Melendi', 'Hiko', 'AgroPlay', 'Roy Orbison', 'Luciano', 'JACKBOYS', 'Two Door Cinema Club', 'New Order', 'Yeah Yeah Yeahs', 'Aditya A', 'Tom Rosenthal', 'Lalo Ebratt', 'Dusty Springfield', 'Gilberto Santa Rosa', 'Christian Chávez', 'Oxlade', 'Naiara Azevedo', 'Alex Rose', 'Haricharan', 'Madism', 'Los Auténticos Decadentes', 'Olly Murs', 'Sevek', 'Rod Wave', 'Ashnikko', 'Old Dominion', 'Quality Control', 'Alanis Morissette', 'ENHYPEN', 'Europe', 'Sleeping At Last', '*NSYNC', 'Sheck Wes', 'FLETCHER', 'Axwell /\\ Ingrosso', 'DJ Ak beats', 'Phantogram', 'Pineapple StormTv', 'ITZY', 'El Chachito', 'MØ', 'Antara Mitra', 'Kishore Kumar', 'Soft Cell', 'Ludacris', 'Incubus', 'MK', 'Gloria Trevi', 'Bone Thugs-N-Harmony', 'Beck', 'Victoria Monét', 'Beach Bunny', 'Hardwell', 'The Cars', 'The Animals', 'Fitz and The Tantrums', 'Gloria Gaynor', 'Joan Jett & the Blackhearts', 'Ashanti', 'Greeicy', 'Marilyn Manson', 'Akhil Sachdeva', 'Chuck Berry', 'Ginuwine', 'Mainstreet', 'Dennis Lloyd', 'Callejero Fino', 'Kevin Gates', 'Celia Cruz', 'Dayglow', 'Jon Z', 'Virlan Garcia', 'Carlos Baute', 'GAMPER & DADONI', 'Ikky', 'The Kinks', 'Beret', 'Crowded House', 'Thirty Seconds To Mars', 'Jaani', 'Majestic', 'Yung Bleu', 'Meet Bros.', 'Sub Urban', 'Asha Bhosle', 'Rick Astley', 'ODESZA', 'Mike Bahía', 'Ajay-Atul', 'El Padrinito Toys', 'Lily Allen', 'NATHY PELUSO', 'The Paper Kites', 'Lola Indigo', 'Soolking', 'Matt Maltese', "Plain White T's", 'Lainey Wilson', 'HRVY', 'Soundgarden', 'Nat King Cole', 'Rich The Kid', 'Portugal. The Man', 'Divya Kumar', 'Rei', 'Joe Cocker', 'Jory Boy', '1nonly', 'Brando', 'Angel Y Khriz', 'Lil Jon', 'Dj LK da Escócia', 'Fonseca', 'g3ox_em', 'Eve', 'Ana Bárbara', 'Alan Gomez', 'Frankie Valli & The Four Seasons', 'Sara Bareilles', 'Grupo Arriesgado', 'KSI', 'deadmau5', 'Andy Rivera', 'Alan Menken', 'Shaarib Toshi', 'Pet Shop Boys', 'Chino Pacas', 'MF DOOM', 'Walker Hayes', 'Filipe Ret', 'Angèle', 'Grupo Los de la O', 'Kausar Munir', 'Kaskade', '347aidan', 'Tayc', 'LF SYSTEM', 'Luude', 'Ghostemane', 'Dopamine', 'KIDDO', 'Nickoog Clk', 'Mufasa & Hypeman', 'Mc Davi', 'Yura Yunita', 'Sanjay Leela Bhansali', 'MC K.K', 'Pamungkas', 'Brett Young', 'TAEYANG', 'Jamie Miller', 'Chlöe', 'Conjunto Primavera', 'Joyner Lucas', 'Os Gemeos da Putaria', 'Mae Muller', 'Seether', 'Cuco', 'Café Tacvba', 'PSY', 'Cazzu', 'raissa anggiani', 'Luis Mexia', 'Nick Jonas', 'Janet Jackson', 'DVBBS', 'SEVENTEEN', 'Grupo Menos É Mais', 'Moby', 'BIBI', 'Indila', 'Natasha Bedingfield', 'Edward Maya', 'Øneheart', 'Santhosh Narayanan', 'AnnenMayKantereit', 'Commodores', 'MUPP', 'Sadfriendd', 'Cody Johnson', 'Shinda Kahlon', 'Krono', 'Jengi', 'Dido', 'Bronco', 'Alle Farben', 'León Larregui', 'Aaron Smith', 'Aaliyah', 'Westlife', 'Sickick', 'Nacho', 'Keyshia Cole', 'Alvaro Soler', 'Fiersa Besari', 'J Alvarez', 'Willie Colón', 'Martin Solveig', 'Marta Sánchez', 'MC Xenon', 'Gabb MC', 'Dj TG Beats', 'Ana Mena', 'NOTD', 'Ajaxx', 'Sido', 'Codiciado', 'Muppet DJ', 'Omar Varela', 'Daya', 'Ayushmann Khurrana', 'LP', 'Mareux', 'Cypress Hill', 'Hensonn', 'Harshdeep Kaur', 'southstar', 'RÜFÜS DU SOL', 'Tz da Coronel', 'Ed Maverick', 'Vijay Prakash', 'Dimitri Vegas', 'Claude Debussy', 'Stevie Nicks', 'The Cardigans', 'Jimin', 'Alvaro Diaz', 'Salve Malak', 'The Alchemist', 'Dj Aurélio', 'La Ley', 'Ñejo', 'Wu-Tang Clan', 'Chefin', 'Kenny Dope', 'Sofia Carson', 'La Maquinaria Norteña', 'Grover Washington, Jr.', 'Akhil', 'James Taylor', 'Peter Gabriel', 'Raim Laode', 'Feby Putri', 'Dom Dolla', 'Banda Los Recoditos', 'Rainbow Kitten Surprise', 'Stone Temple Pilots', 'Darius Rucker', 'Adam Levine', 'Cole Swindell', 'Leony', 'Ash King', 'Marc Seguí', 'Still Woozy', 'Bo Burnham', 'Tinlicker', 'James TW', 'Apache 207', 'MC Kevin o Chris', 'zzoilo', 'Gazo', 'Al Green', 'Felipe e Rodrigo', 'Haddaway', 'Dubdogz', 'Tiara Andini', 'Ninho', 'MoonDeity', 'Young Dolph', 'Whethan', 'Taiu', 'SECA Records', 'WOS', 'Eric Prydz', 'KSLV Noh', 'Stealers Wheel', 'Mr. Probz', 'Cafuné', 'KC & The Sunshine Band', 'Skepta', 'Budi Doremi', 'Leo Dan', 'Los Bukis', 'Young Money', 'Grimes', 'W&W', 'Jaideep Sahni', 'Dustin Lynch', 'Gloria Groove', 'Dímelo Flow', 'The Living Tombstone', 'Bakermat', 'A Touch Of Class', 'Money Man', 'Flo Milli', 'BROCKHAMPTON', 'The Score', 'Milo j', 'Grouplove', 'Duke Dumont', 'Ali Sethi', 'KSHMR', 'N.W.A.', 'CJ', 'K.Flay', 'Headie One', 'putri dahlia', 'Eiffel 65', 'Los Gemelos De Sinaloa', 'Yuri', 'Pol Granch', 'Pantera', 'Vampire Weekend', "Adolescent's Orquesta", 'Valentín Elizalde', 'FKJ', 'Randy', 'yuji', 'Chani Nattan', 'Zé Vaqueiro', 'Anson Seabra', 'Andrea Bocelli', 'Waka Flocka Flame', 'Shafqat Amanat Ali', 'Only The Family', 'Bas', 'OFFICIAL HIGE DANDISM', 'Luck Ra', 'Simply Red', 'Abraham Mateo', 'Jubël', 'Tom Morello', 'Haley Reinhart', 'Roberto Carlos', 'Lil Skies', 'Irene Cara', 'Miksu / Macloud', 'KAYTRANADA', 'Anand Raj Anand', 'Don McLean', 'Ilaiyaraaja', 'Naresh Iyer', 'Grupo Recluta', 'Culture Club', 'Andmesh', 'Chino & Nacho', 'Klaas', 'Omah Lay', 'Whitesnake', 'Michael Giacchino', 'ATB', 'Pierce The Veil', 'Flowdan', 'IU', 'Boza', 'Griff', 'Kid Ink', 'Virgoun', 'Cardenales De Nuevo León', 'Nathan Evans', 'Angel Dior', 'PnB Rock', 'Katrina & The Waves', "Olivia O'Brien", 'Pabllo Vittar', 'KYLE', 'Liam Payne', 'La Quinta Estacion', 'Jacquees', 'Donna Summer', 'Mark Morrison', 'Mahalakshmi Iyer', 'EST Gee', 'Bella Poarch', 'Toby Keith', 'Dadju', 'Chord Overstreet', 'Young the Giant', 'Dallass', 'Savage Garden', 'La Factoria', 'Khruangbin', 'AJ Tracey', 'Dj Chris No Beat', 'La Roux', 'Gianluca Grignani', 'Los Fabulosos Cadillacs', 'R. City', 'DEKKO', 'Dance Fruits Music', 'Wyclef Jean', 'Adriel Favela', 'Megadeth', 'Matchbox Twenty', 'Shae Gill', 'Grupo Niche', 'Stefflon Don', 'Jet', 'Hiphop Tamizha', 'Pretenders', 'Emmanuel', 'Good Charlotte', 'Tujamo', 'Sixpence None The Richer', 'La T y La M', 'Jim Croce', 'Gaab', 'Surf Mesa', 'Ke Personajes', 'Conor Maynard', 'Gminxr', 'Sireesha Bhagavatula', 'Chris Young', 'Lauren Daigle', 'Robin Thicke', 'Alisha Chinai', 'Jake Owen', 'Tarcísio do Acordeon', 'Extreme', 'Craig David', 'John Summit', 'gnash', 'Chris Isaak', 'Bruno Martini', 'Desiigner', 'Alina Baraz', 'Juicy Luicy', 'Jessie Murph', 'Jawsh 685', 'Hillsong Worship', 'Turma do Pagode', 'NVBR', 'Cochise', 'Belanova', 'Boyz II Men', 'The xx', 'Disciples', 'La Mosca Tse-Tse', 'Marco Mengoni', 'Natalie Imbruglia', '3AM', 'Little Big Town', 'Mobb Deep', 'Quinn XCII', 'Damso', 'Gerardo Coronel', 'grandson', 'Blueface', 'Nanpa Básico', 'Bruno & Marrone', 'Air Supply', 'Yebba', 'Mike WiLL Made-It', 'Julien Marchal', 'Blackstreet', 'Glee Cast', 'NCT DREAM', 'Bruno Major', 'The Pointer Sisters', 'GoldLink', 'Nina Chuba', 'Vilen', 'Ace of Base', 'Silambarasan TR', 'vaultboy', 'Pyotr Ilyich Tchaikovsky', 'Haze', 'Aruma', 'Michael Sembello', 'Jennifer Warnes', 'Jamie Foxx', 'Kid Rock', 'MC Kevinho', 'Cassie', "La K'onga", 'Yo-Yo Ma', 'twocolors', 'Vanessa Carlton', 'John Williams', 'Kelis', 'Frankie Valli', 'Russell Dickerson', 'XG', 'The Emotions', 'Ghibran', 'Chris MC', 'Toploader', 'Jay Rock', 'Dybbukk', 'Wings', 'Charlie Brown Jr.', 'Alexandra Stan', 'Jaden', 'Vaundy', 'Buffalo Springfield', 'Mc Poze do Rodo', 'Huey Lewis & The News', 'Vince Staples', 'Yo Gotti', 'RealestK', 'Lifehouse', 'John Travolta', 'Brandy', 'Bonez MC', 'Natalie Cole', 'Madame', 'Mc Pedrinho', 'Elevation Worship', 'Corinne Bailey Rae', 'Charly Black', 'Tiakola', 'Hillsong UNITED', 'Dev Negi', 'Lucas & Steve', 'MOTi', 'Volbeat', 'Punto40', 'Mabel Matiz', 'Rixton', 'Mecano', 'Salim Merchant', 'reidenshi', 'Miky Woodz', 'City Girls', "Lil' Kim", 'Gajendra Verma', 'Carly Simon', 'Motörhead', 'John Mellencamp', 'Iggy Pop', 'Max Richter', 'Aloe Blacc', 'Kiki Dee', 'Stephanie Beatriz', 'Slayer', 'Simone Mendes', 'D-Block Europe', 'Javed-Mohsin', 'MC L da Vinte', 'The Bangles', 'MC Davo', 'Mandy Moore', 'DDG', 'Hamza', 'Jamiroquai', 'Manuel Medrano', 'Anuradha Paudwal', 'The Righteous Brothers', 'Vegedream', 'Vundabar', 'Neoni', 'Chimbala', 'SG Lewis', 'Nic D', 'A Day To Remember', 'RADWIMPS', 'Last Child', 'Crystal Castles', 'Nicky Romero', 'Neto Peña', 'Seal', 'RAF Camora', 'Nate Smith', 'Péricles', 'Alice Cooper', 'Zahrah S Khan', 'VINAI', 'Angus & Julia Stone', 'Billy Currington', 'LAGOS', 'Juicy J', 'Javiielo', 'Hindia', 'Thiaguinho', 'Niska', 'Tom Jones', 'Eddie Santiago', 'Edward Sharpe & The Magnetic Zeros', 'Mc Livinho', 'Mura Masa', 'DJ Yuri Martins', 'aespa', 'Keala Settle', 'Kenny Beats', 'Los Plebes del Rancho de Ariel Camacho', 'HAIM', 'Alejandra Guzman', 'George Henrique & Rodrigo', 'The Rare Occasions', 'Daniel Hope', 'Damian Marley', 'Meat Loaf', 'Vishal Chandrashekhar', 'DJ Cayoo', 'Pat Benatar', 'Aldo Trujillo', 'The Human League', 'EXO', 'Dardan', 'Declan McKenna', 'Frankie Ruiz', 'Jon Secada', 'Nusrat Fateh Ali Khan', 'Aqua', 'Kaash Paige', 'Tori Kelly', 'Modern Talking', 'Trinix', 'Godsmack', 'Caifanes', 'Estelle', 'A Tribe Called Quest', 'Elefante', 'Awdella', 'Reyli Barba', 'The Proclaimers', 'RM', 'Diego Torres', 'Bakar', 'Dj Aladin GDB', 'Garry Sandhu', 'Bootsy Collins', 'Jordin Sparks', 'Dj Chetas', 'Prashant Katheriya', 'Snakehips', 'Guilherme & Santiago', 'Cash Cash', 'Dean Martin', 'Buscabulla', 'Koffee', 'Rob Zombie', 'Fatboy Slim', 'Diego Verdaguer', 'Lil Jon & The East Side Boyz', 'Hugh Jackman', 'M.M.Manasi', 'The Chicks', 'Aastha Gill', 'The Calling', 'Arjun Kanungo', 'Mijares', 'Ferrugem', 'Don Henley', 'José Feliciano', 'CHVRCHES', 'Y2K', 'Playero', 'Ivy Queen', 'SXMPRA', 'The Greatest Showman Ensemble', 'Anna Kendrick', 'Pablo Chill-E', 'Ari Abdul', 'Juhn', 'Moira Dela Torre', 'Ikka', 'Ravi Basrur', 'Mr Eazi', 'Ella Fitzgerald', 'CRO', 'Robert Miles', 'Lyodra', 'LIZOT', 'Keisya Levronka', 'Gala', 'Night Lovell', 'Warren G', 'Vengaboys', 'Bryce Vine', 'Travie McCoy', 'Lilly Wood and The Prick', 'Duelo', 'Yves V', 'Dexys Midnight Runners', 'Gulzar', 'La Santa Grifa', 'Naughty Boy', 'Lil Tracy', 'Amaarae', 'Ghostface Playa', 'Coti', 'ERNEST', 'T3R Elemento', 'El Komander', 'Barbra Streisand', 'BIN', 'Sam Tinnesz', 'Rushawn', 'Davido', 'Rachel Platten', 'Deepend', 'Lupe Fiasco', 'Paolo Nutini', 'Jerry Rivera', 'Pancho Barraza', '220 KID', 'A Great Big World', 'Ben&Ben', 't.A.T.u.', 'MERO', 'The National', 'Sanam', 'Aimer', 'Boyce Avenue', 'The Blessed Madonna', 'Pooh Shiesty', 'Madcon', 'Carpenters', 'Villano Antillano', 'Mr.Rain', 'Pav Dharia', 'R. Kelly', 'Josh Turner', 'Encanto - Cast', 'Popcaan', 'j-hope', 'Teddy Swims', 'Smino', 'Sonder', 'Ado', 'meLLo', 'K-391', 'Maggie Lindemann', 'Morray', 'Los Legendarios', 'Tyler Hubbard', 'CamelPhat', 'Kim Carnes', "Auli'i Cravalho", 'Phoenix', 'YouNotUs', 'Aleks Syntek', 'Lang Lang', 'Love Funk', 'Four Tops', 'Melody', 'Wheatus', 'Sorriso Maroto', 'Alex Gaudino', 'James Morrison', 'Twisted Sister', 'Suki Waterhouse', 'Tyler Cole', 'George Benson', 'Jon Bellion', 'Adriano Rhod', 'Ingratax', 'Parker McCollum', 'Fran C', 'Cutting Crew', 'Village People', 'THE ANXIETY', 'Hollywood Undead', 'The Cinematic Orchestra', 'Los Temerarios', 'Liana Flores', 'IZA', 'Fabio Asher', 'ChiChi Peralta', 'Amanda Seyfried', 'Royal Philharmonic Orchestra', 'Cheap Trick', 'Hollow Coves', 'Helsloot', 'Izzamuzzic', 'SIDEPIECE', 'Tech N9ne', 'Clayton & Romário', 'Afgan', 'PNL', 'Kim Loaiza', 'Young Miko', 'Armand Van Helden', 'Mitchell Tenpenny', 'NCT 127', 'Maninder Buttar', 'Victor Cibrian', 'Reneé Rapp', 'Mrs. GREEN APPLE', 'KayBlack', 'Alexander 23', 'Tornillo', 'Brad Paisley', 'Eric Carmen', 'CeeLo Green', 'Los 2 de la S', 'Baby Bash', 'Lloyd', 'Berlin', 'Mýa', 'Guè', 'FMK', 'DJ Arana', 'Edwin Luna y La Trakalosa de Monterrey', 'Blue Öyster Cult', 'Hikaru Utada', 'Giant Rooks', 'Chris Lake', 'Dybbukk Covers', 'Héctor "El Father"', 'MC Rogerinho', 'MC STAN', 'The Backseat Lovers', 'José González', 'John K', 'Nico & Vinz', 'Ziva Magnolya', 'LeAnn Rimes', 'Vicetone', 'Belinda Carlisle', 'Dylan Matthew', 'Perera DJ', 'AVAION', 'LSD', 'Rizky Febian', 'Lou Reed', 'Alexander Stewart', 'Gipsy Kings', 'RENEE', 'Los Invasores De Nuevo León', 'Anuv Jain', 'goddard.', 'YBN Nahmir', 'DIVINE', 'Ray LaMontagne', 'Jeezy', 'Bootie Brown', 'James Brown', 'Redman', 'Michael Kiwanuka', 'A-Trak', 'Tananai', 'Fabolous', 'Os Barões Da Pisadinha', 'Jax', 'Emma Peters', 'India Martinez', 'Coyote Theory', 'lovelytheband', 'SoFaygo', 'TREASURE', 'Jenni Rivera', 'Polo Gonzalez', 'NAYEON', 'MC G15', 'Claptone', 'HONNE', 'Mc Delux', 'Adie', 'Super Yei', 'Priya Saraiya', 'Pouya', 'Richard Marx', 'Ezhel', 'KUTE', 'JAWNY', 'Bagua Records', 'Pras', 'Dj Yo!', 'Grupo Revelação', 'Shahid Mallya', 'Justin Hurwitz', 'Showtek', 'Phillip Phillips', 'MC ORSEN', 'Muni Long', 'The Wombats', 'Ronan Keating', 'Thin Lizzy', 'Rubén Blades', 'Ufo361', 'Hector & Tito', 'DJ Drama', 'S.P. Charan', 'Olga Tañón', 'Sony no Beat', 'Monica', 'María José', 'Jungle', 'The Supremes', 'Third Eye Blind', 'Espinoza Paz', 'Sam Fender', 'Leon James', 'Ken Carson', 'Alida', 'Imran Khan', 'Nadin Amizah', 'Evaluna Montaner', 'Abhijit Vaghani', 'Chaka Khan', 'MC Marks', 'thasup', 'Gabby Barrett', 'Vicentico', 'ONIMXRU', 'Bullet For My Valentine', 'Elvis Crespo', 'Los Cadetes De Linares', 'Braaheim', 'ArrDee', 'Ari Lennox', 'UZI', 'Shiva', 'Felupe', 'Blind Melon', 'Vierra', 'Tay-K', 'Mau P', 'Alicia Villarreal', 'ROBI', 'Sheila On 7', 'Delacruz', 'Neil Young', 'Run–D.M.C.', 'I Prevail', 'Ben Howard', 'Hal', 'Grupo Yndio', 'Gustavo Cerati', 'Hungria Hip Hop', 'Shakthisree Gopalan', 'Vulgo FK', 'Bobby Pulido', 'S. Janaki', 'Luther Vandross', 'Elodie', 'Trinidad Cardona', 'Semicenk', 'Felipe Araújo', 'Luis Angel "El Flaco"', 'Kiana Ledé', 'Maddie & Tae', '2Rare', 'Snoh Aalegra', 'YSY A', 'Bread', 'PlayaPhonk', 'iamjakehill', 'JoJo', 'Paty Cantú', 'Los Elegantes de Jerez', 'Andra & The Backbone', 'Nena', 'Hot Shade', 'Twista', 'Manoj Muntashir', 'Grupo Mojado', 'Sheff G', 'ZHU', 'Jósean Log', 'Mc Gw', 'Alexis y Fido', 'Kidd Keo', 'Mc Kevin', 'The Magician', 'Freya Ridings', 'Meryl Streep', 'Arem Ozguc', 'Arman Aydin', 'Naps', 'Los Dareyes De Le Thompson', 'El Bebeto', 'DJ Scheme', 'Iron & Wine', 'Michael Schulte', 'Pinkfong', 'Djavan', 'Yiyo Sarante', 'Babasónicos', 'Baby Gang', 'Anand-Milind', 'No Te Va Gustar', 'Isaiah Rashad', 'Big Soto', 'Nicole Scherzinger', 'Dr. Dog', 'Beenie Man', 'Blasterjaxx', 'Sophie and the Giants', 'José Luis Rodríguez', 'Corona', 'Eric Bellinger', 'kevoxx', 'Güneş', 'Bob', 'Mumuzinho', 'Maisie Peters', 'Geolier', 'Katelyn Brown', 'St. Vincent', 'Lil Dicky', 'AYLIVA', 'Death Cab for Cutie', 'Harris & Ford', 'Simone & Simaria', 'Matt Simons', 'Rick Springfield', 'Kiiara', 'Sanjoy', 'La Sonora Dinamita', 'Staind', 'Celeste', 'CORPSE', 'DaniLeigh', 'Lary Over', 'RAC', 'Ananya Bhat', 'venbee', 'Kris Kross Amsterdam', 'LiSA', 'Tony Kakkar', 'Stone Sour', 'Parmalee', 'Mokita', 'Chris de Burgh', 'Capital Bra', 'Massive Attack', 'Estopa', 'Jack Ü', 'Rochy RD']
  return pop_list

def Generate_Random_Song():

    cnx, cursor = Connect_to_DB()
    while True:
        rand_num = random.randint(1, 100)

        if rand_num <= 90:
            hipster = False
        else:
            hipster = True
            print("hipster")
    

        while True:  # Keep generating new songs as long as they're too popular
            # offset_max= 900, offset_min=600
            min_off = random.randint(200,600)
            max_off = random.randint(620, 1000)
            random_artist = get_random(spotify=sp, type="track", offset_min=min_off, offset_max=max_off, tag_hipster=hipster)
            if random_artist["popularity"] < 56:  # popularity filter
                pop_artists = popular_artists()
                if random_artist["artists"][0]["name"] in pop_artists:
                    print("TOO POPULAR", random_artist["artists"][0]["name"], "             ", min_off, max_off)
                else:
                    print("GOOD:", random_artist["artists"][0]["name"])
                    print(min_off, max_off)
                    break
                
        


        debug_message = f"""
      ID:             {random_artist["id"]}
      Song Name:      {random_artist["name"]}
      Artist Name:    {random_artist["artists"][0]["name"]}
      Artist URL:     {random_artist["artists"][0]["external_urls"]["spotify"]}
      Populairity:    {random_artist["popularity"]}
      Album Name:     {random_artist["album"]["name"]}
      Album URL:      {random_artist["album"]["external_urls"]["spotify"]}
      Album pfp:      {random_artist["album"]["images"][0]["url"]}
      Explicit:       {random_artist["explicit"]}
      Release Date:   {random_artist["album"]["release_date"]}
      Preview URL:    {random_artist["preview_url"]}
      Song URL:       {random_artist["external_urls"]["spotify"]}
      """
        # print(debug_message)
        random_artist["artists"][0]["name"]
        sql = "SELECT * FROM Songs WHERE song_id = %s"
        cursor.execute(sql, (random_artist["id"],))
        result = cursor.fetchall()
        if not result:
            break
    # Close_DB(cursor, cnx)
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()
    return random_artist

    # return random_artist

def Check_If_User_Already_Voted(user_email, song_id):
    cnx, cursor = Connect_to_DB()
    sql = "SELECT voted_songs FROM ##### WHERE email = %s"
    cursor.execute(sql, (user_email,))
    
    # retrieve the blob data

    result = cursor.fetchone()
    # Close_DB(cursor, cnx)
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()
    if result:
        # convert the bytes to a string and split by comma
        song_list = result[0].decode('UTF-8').split(',')

        # remove any leading or trailing whitespace
        song_list = [song.strip() for song in song_list]

        # print(song_list)
        # print the list of songs
        if song_id in song_list:
            return True
        else:
            return False
        
    else:
        return False


def Add_Song_To_Database(random_song):
    cnx, cursor = Connect_to_DB()
    # Insert the data into the table
    count_query = "SELECT COUNT(*) FROM Songs"
    cursor.execute(count_query)
    result = cursor.fetchone()
    # print(result[0])
    group = result[0]//20

    # print(datetime.datetime.strptime(str(date), '%y/%m/%d'))
    date = random_song["album"]["release_date"]


    try:
        if datetime.datetime.strptime(str(date), "%Y-%m-%d"):
            print("OK")
    except ValueError:
    
        date = f"{date}/01/01"
        # date = f"{date}/00/00"
        date = datetime.datetime.strptime(str(date), '%Y/%m/%d').date()

        # print(datetime.datetime.strptime(str(date), '%Y/%m/%d').date())
    insert_query = """
  INSERT INTO Songs (song_group, song_rating, song_amount_ratings, song_all_votes, song_id, song_name,song_artist_name,song_artist_url,song_artist_pfp,song_populairity,song_album_name,song_album_url,song_album_pfp,song_explicit,song_release_date,song_preview_url,song_url_spotify)
  VALUES (%s, %s, %s, "", %s, %s, %s, %s, DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s)
  """

    data = (group,
            0,
            0,
            random_song["id"], random_song["name"], random_song["artists"][0]["name"],
            random_song["artists"][0]["external_urls"]["spotify"], random_song["popularity"],
            random_song["album"]["name"], random_song["album"]["external_urls"]["spotify"],
            random_song["album"]["images"][0]["url"], random_song["explicit"],
            date, random_song["preview_url"],
            random_song["external_urls"]["spotify"])
    cursor.execute(insert_query, data)
    cnx.commit()
    # Close_DB(cursor, cnx)
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()
    #print("SUCCESS")


def Add_Voted_Song_To_User(user_email, song_id):
    # Append the song_id to the existing value in the voted_songs column
    # Check if the voted_songs column is empty
    cnx, cursor = Connect_to_DB()
    query = "SELECT voted_songs FROM ##### WHERE email = %s"
    cursor.execute(query, (user_email,))
    result = cursor.fetchone()

    if result == None:

        # If the column is empty, set the song_id as the value
        query = "UPDATE ##### SET voted_songs = %s WHERE email = %s"
        try:
            cursor.execute(query, (song_id, user_email))
        except Exception as e:
            print(f"Error executing query: {e}")

    elif str(result[0]) == "b''":
        # If the column is empty, set the song_id as the value
        query = "UPDATE ##### SET voted_songs = %s WHERE email = %s"
        cursor.execute(query, (song_id, user_email))
    else:
        # If the column is not empty, append the song_id to the existing value
        query = "UPDATE ##### SET voted_songs = CONCAT(voted_songs, ', ', %s) WHERE email = %s"
        cursor.execute(query, (song_id, user_email))
    cnx.commit()
    # Close_DB(cursor, cnx)
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()

    # Close the cursor and connection

    print("SUCCESS")


def Check_Song_Duplicate(user_email, song_id):
    cnx, cursor = Connect_to_DB()
    query = "SELECT voted_songs FROM ##### WHERE email = %s"
    cursor.execute(query, (user_email,))
    result = cursor.fetchone()
    all_voted_song_ids = result[0].decode("utf-8").split(", ")
    # Close_DB(cursor, cnx)
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()
    if song_id in all_voted_song_ids:
        return True
    else:
        return False



def Prepare_Songs(amount_repeats):
    amount_repeats = int(amount_repeats)
    cnx, cursor = Connect_to_DB()
    for i in range(amount_repeats):
        random_song = Generate_Random_Song()
        #print("GOT RANDOM SONG")
        Add_Song_To_Database(random_song)
        print("ADDED SONG TO DATABASE")
    # Close_DB(cursor, cnx)
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()


def Grab_Song_From_DB(user_group, email):


    cnx, cursor = Connect_to_DB()
    count_query = "SELECT song_id FROM Songs WHERE song_group = %s;"
    cursor.execute(count_query, (user_group,))
    
    result = cursor.fetchall()
    print(result)

    if len(result) < 1:
        print("AMOUNT:", len(result))
        amount = 20 - len(result)
        Prepare_Songs(1)
        t = Thread(target=Prepare_Songs, args=str(amount-1),).start()
        # cnx, cursor = Connect_to_DB()
    
    elif len(result) < 10:
        print("AMOUNT2:", len(result))
        amount = str(20 - len(result))
        t = Thread(target=Prepare_Songs, args=(amount,))
        t.start()

    song_id_list = []
    for i in range(0, len(result)):
        song_id_list.append(result[i][0])


    count_query = "SELECT voted_songs FROM ##### WHERE email = %s;"
    cursor.execute(count_query, (email,))
    result = cursor.fetchone()
    user_voted_list = []
    result = result[0].decode("utf-8")
    result = result.split(", ")
    #print("##########RESULT: ", result)
    for i in result:
        user_voted_list.append(str(i))

    # print("USER: ", user_voted_list)

    # print("LIST: ", song_id_list)

    song_id_list = [x for x in song_id_list if x not in user_voted_list]

    #If the user has NOT voted for all songs in group
    if song_id_list:  

        # print("CHOICE: ", song_id_list)
        random_choice = random.choice(song_id_list)
        print("CHOOOOOOOOOOOOOOOOOOOOOSEN:", random_choice)

        # Close_DB(cursor, cnx)
        t = Thread(target=Close_DB, args=(cursor, cnx)).start()
        return random_choice

    #If the user has voted for all songs in group, increment group by 1
    else:
        print(song_id_list)
        print('ok')
        sql = "UPDATE ##### SET current_group = %s WHERE email = %s"

        # execute the SQL query with the email variable as a parameter
        current_group = int(grab_user_group_from_account(email)) + 1
        cursor.execute(sql, (current_group, email,))
        Increment_User_Group()
        
        cnx.commit()
        # Close_DB(cursor, cnx)
        t = Thread(target=Close_DB, args=(cursor, cnx)).start()
        return Grab_Song_From_DB(current_group, email)

def add_vote_to_song(song_id, user_vote):
    cnx, cursor = Connect_to_DB()
    cursor.execute("SELECT song_all_votes FROM Songs WHERE song_id = %s", (song_id,))
    current_votes = cursor.fetchone()

    temp = []
    if current_votes:
        for i in current_votes:
            temp.append(i.decode('UTF-8'))

    temp = ", ".join(temp)
    # Append the user_vote to the existing value of song_all_votes
    if str(current_votes) == "(b'',)" or not current_votes:

        new_votes = f"{user_vote}"

    else:
        new_votes = f"{temp}, {user_vote}"



    # Update the database with the new value of song_all_votes
    sql = "UPDATE Songs SET song_all_votes = %s WHERE song_id = %s"
    val = (new_votes, song_id)
    cursor.execute(sql, val)


    query = "SELECT song_amount_ratings FROM Songs WHERE song_id = %s"
    cursor.execute(query, (song_id,))
    result = cursor.fetchone()

    # increment the value and update the column in the database
    new_value = int(result[0]) + 1
    update_query = "UPDATE Songs SET song_amount_ratings = %s WHERE song_id = %s"
    cursor.execute(update_query, (new_value,song_id))
    cnx.commit()


    # Close_DB(cursor, cnx)
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()


def grab_username_from_account(email):
    cnx, cursor = Connect_to_DB()
    count_query = "SELECT username FROM ##### WHERE email = %s;"
    cursor.execute(count_query, (email,))
    result = cursor.fetchone()

    # Close_DB(cursor, cnx)
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()
    return result

def grab_user_group_from_account(email):

    cnx, cursor = Connect_to_DB()
    count_query = "SELECT current_group FROM ##### WHERE email = %s;"
    cursor.execute(count_query, (email,))
    result = cursor.fetchone()
    # Close_DB(cursor, cnx)
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()


    return result[0]

def grab_embed_from_song(song_id):
    cnx, cursor = Connect_to_DB()
    count_query = "SELECT song_preview_url FROM Songs WHERE song_id = %s;"
    cursor.execute(count_query, (song_id,))
    result = cursor.fetchone()

    # Close_DB(cursor, cnx)
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()
    return result

def is_valid_email(email):
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(pattern, email):
        return True
    else:
        return False


def Generate_Password_Reset_URL(user_email):

    id = Grab_ID_From_User(user_email=user_email)
    characters = string.ascii_letters + string.digits

    # Generate a 20-character long random string
    random_string = ''.join(secrets.choice(characters) for i in range(20))

    first_char = user_email[0]
    last_char = re.findall(r'(.*)@', user_email)[0][-1]

    # Initialize the mixed variable
    mix = ""

    # Check if the first character is valid
    if re.match(r'[A-Za-z0-9_.-]', first_char):
        mix += first_char
    else:
        # If not, try the next character until a valid one is found
        for char in user_email[1:]:
            if re.match(r'[A-Za-z0-9_.-]', char):
                mix += char
                break
        else:
            mix+="_"


    # Check if the last character is valid
    if re.match(r'[A-Za-z0-9_.-]', last_char):
        mix += last_char
    else:
        # If not, try the second last character until a valid one is found
        for char in user_email[::-1]:
            if re.match(r'[A-Za-z0-9_.-]', char):
                mix += char
                break
        else:
            mix+="_"

    
    reset_url = f"http://127.0.0.1:5000/reset_passw/{id}/{mix}{random_string}{mix[::-1]}" #TODO CHANGE THIS
    return reset_url


def Change_User_Password(user_email, password):
    try:
        encrypted_password = encrypt_password(password)
        cnx, cursor = Connect_to_DB()
        query = "UPDATE ##### SET password = %s WHERE email = %s"
        cursor.execute(query, (encrypted_password, user_email))
        cnx.commit()
        t = Thread(target=Close_DB, args=(cursor, cnx)).start()
        return True
    except Exception as e:
        print(e)
        return False


def Grab_ID_From_User(user_email):
    cnx, cursor = Connect_to_DB()
    sql = "SELECT ID FROM ##### WHERE email = %s"

    # execute the query with the user_email variable as parameter
    cursor.execute(sql, (user_email,))

    # fetch the results of the query
    result = cursor.fetchone()

    t = Thread(target=Close_DB, args=(cursor, cnx)).start()
    if result:
        return result[0]
    else:
        return None


def Add_Song_To_Suggestions(song_id, user_email):
    try:
        cnx, cursor = Connect_to_DB()
        # Check if the song_id is already in the database
        query = "SELECT * FROM Song_Suggestions WHERE song_id = %s"
        cursor.execute(query, (song_id,))
        existing_rows = cursor.fetchall()
        if existing_rows:
            return "Someone beat you to it, this song already is in our database."
        else:
            # Insert a new row with the song_id, user_email, and default value for song_added
            query = ("INSERT INTO Song_Suggestions "
                    "(song_id, song_added, user_email) "
                    "VALUES (%s, %s, %s)")
            cursor.execute(query, (song_id, 0, user_email))
            cnx.commit()
            print("New row added to database.")

        # Close the database connection
        Close_DB(cnx=cnx, cursor=cursor)
        return "Thank you very much for your suggestion."

    except Exception as e:
        return "Something went wrong."


def Check_If_Song_Exists(song_id):
    x = get_song(sp, song_id)
    if x == None:
        return False
    else:
        return True

def Connect_to_DB():
    global sp
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id="", client_secret=""))

    except Exception as e:
        print("Spotify API failed to login:", e)

    try:
        cnx = connection_pool.get_connection()
        cursor = cnx.cursor(buffered=True)

        print("CONNECTED")
        return cnx, cursor
    except mysql.connector.Error as err:
        print("Failed to connect to the database: {}".format(err))
        exit(1)


def Check_If_Email_Exists(email):
    cnx, cursor = Connect_to_DB()
    query = "SELECT COUNT(*) FROM ##### WHERE email = %s"
    cursor.execute(query, (email,))
    
    # Get the query result
    result = cursor.fetchone()[0]
    t = Thread(target=Close_DB, args=(cursor, cnx)).start()
    return result > 0

def Close_DB(cursor, cnx):
    print("CLOSED")
    cursor.close()
    cnx.close()





# Connect to the database
if __name__ == "__main__":
    # Connect_to_DB()
#     Grab_Song_From_DB(0)
    # random_song = Generate_Random_Song()
    # Add_Song_To_Database(random_song)
    pass

