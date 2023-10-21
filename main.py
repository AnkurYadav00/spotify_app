from datetime import datetime
from pprint import pprint
import dotenv
import requests
from bs4 import BeautifulSoup
import spotipy
import os

# load environment variables
dotenv.load_dotenv()

clientID = os.getenv('SPOTIPY_CLIENT_ID')
clientSecret = os.getenv('SPOTIPY_CLIENT_SECRET')

# user Input for time period
userInput = datetime.strptime(input('Enter date of which you want top songs list, format:- YYYY-MM-DD '),
                              '%Y-%m-%d').date()
timeperiod = str(userInput) + '/'

# get source code
response = requests.get('https://www.billboard.com/charts/hot-100/' + timeperiod)

# fetch contents
content = BeautifulSoup(response.text, 'html.parser')
TopSongsTags = content.find_all(name='div', class_='o-chart-results-list-row-container')

# extract songs name
songs = []
for song in TopSongsTags:
    songs.append(song.ul.find_all('li')[3].h3.getText().strip())

pprint(songs)

################ Spotify code ################
response = spotipy.Spotify(
    auth_manager=spotipy.oauth2.SpotifyOAuth(
        scope='playlist-modify-private',
        client_id=clientID,
        client_secret=clientSecret,
        redirect_uri='http://example.com',
        username='Ankur',
        cache_path='token.txt',
        show_dialog=True,
    )
)

# fetching userID
user_id = response.current_user()['id']
year = str(userInput).split('-')[0]

# search songs and get their URI
songs_uri = []
for song in songs:
    result = response.search(q=f"track:{song} year:{year}", type='track')
    try:
        uri = result['tracks']['items'][0]['uri']
        songs_uri.append(uri)
    except IndexError:
        print('Songs skipped: Not found')
        continue


# create the new playlist
playlist = response.user_playlist_create(user=user_id,
                                         name=f"{userInput} 100 billboard songs",
                                         public=False,
                                         description=f'Top Songs of the Year {year}')

print(playlist)
playlistID = playlist['id']

with open('playlists.txt', 'a') as file:
    file.write('https://open.spotify.com/playlist/' + playlistID + '\n')

# add songs to playlist
response.playlist_add_items(playlist_id=playlistID, items=songs_uri)
