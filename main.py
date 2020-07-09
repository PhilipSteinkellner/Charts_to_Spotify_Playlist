import json
import os
from bs4 import BeautifulSoup
import urllib.request
import requests
from termcolor import colored
from secrets import secrets
import unicodedata
    
def get_welle1_charts():
    url = "http://www.welle1.at/charts/"
    html = ""
    with urllib.request.urlopen(url) as f:
        html = f.read().decode('utf-8')
    html = unicodedata.normalize("NFKD", html)

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find_all("table")[0] # take first table

    # The first tr contains the column names.
    headings = [th.get_text().strip() for th in table.find("tr").find_all("td")]

    data = []
    for row in table.find_all("tr")[1:]:
        dataset = dict(zip(headings, (td.get_text() for td in row.find_all("td"))))
        data.append(dataset)

    for i in range (len(data)):
        keys = []
        for key, value in data[i].items():
            if key not in ["Interpret", "Titel"]:
                keys.append(key)
        for key in keys:
            data[i].pop(key, None)
    print(colored("Retrieved current charts successfully", "green"))
    return data

def get_spotify_uri(song_name, artist):
    """Search For the Song"""
    artist = artist.replace("feat. ", "").strip()
    song_name = song_name.strip()
    query = "https://api.spotify.com/v1/search?q={}+{}&type=track&offset=0&limit=20".format(
        song_name,
        artist
    )
    response = requests.get(
        query,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(secrets["spotify_token"])
        }
    )
    # check for valid response status
    if response.status_code != 200:
        raise Exception("Error fetching song uri")
    response_json = response.json()
    songs = response_json["tracks"]["items"]

    # only use the first song
    if len(songs) == 0:
        print(colored("Could not fetch song uri -> {} - {}".format(artist, song_name), "red"))
        return 
    else:
        uri = songs[0]['uri']
        print(colored("Fetched song uri -> {} - {}".format(artist, song_name), "blue"))
    return uri

def get_song_uris(charts):
    uris = []
    for obj in charts:
        uri = get_spotify_uri(obj["Titel"], obj["Interpret"])
        if uri:
            uris.append(uri)
    print(colored("Retrieved song uris of {} songs".format(len(uris)), "green"))
    return uris

def create_playlist(name, description="", public=True):
    """Create A New Playlist"""
    request_body = json.dumps({
        "name": name,
        "description": description,
        "public": public
    })
    query = "https://api.spotify.com/v1/users/{}/playlists".format(
        spotify_user_id)
    response = requests.post(
        query,
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(secrets["spotify_token"])
        }
    )
    
    # check for valid response status
    if response.status_code != 200:
        raise Exception("Creating playlist failed")   
    response_json = response.json()
    # playlist id
    playlist_id = response_json["id"]
    print(colored("Created playlist successfully", "green"))
    return playlist_id

def get_playlist_id(name):
    query = "https://api.spotify.com/v1/me/playlists"
    response = requests.get(
        query,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(secrets["spotify_token"])
        }
    )
    # check for valid response status
    if response.status_code != 200:
        raise Exception("Request failed")
    k = response.json()
    for item in response.json()["items"]:
        if item["name"] == name:
            print(colored("Playlist ID found", "green"))
            return item["id"]
    # playlist not found
    raise Exception("Playlist ID NOT found")    
    

def add_songs(playlist_id, uris):
    request_data = json.dumps(uris)
    query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
        playlist_id)

    response = requests.post(
        query,
        data=request_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(secrets["spotify_token"])
        }
    )

    # check for valid response status
    if response.status_code != 200:
        raise Exception("Adding songs failed")
    print(colored("Added songs successfuly", "green"))

def update_playlist(playlist_id, uris):
    request_data = json.dumps({"uris": uris})
    query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
        playlist_id)
    
    response = requests.put(
        query,
        data=request_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(secrets["spotify_token"])
        }
    )
    # check for valid response status
    if response.status_code != 201:
        raise Exception("Updating playlist failed")
    print(colored("Updated playlist successfuly", "green"))

def get_tokens():
    query = "https://accounts.spotify.com/authorize?client_id=5fe01282e44241328a84e7c5cc169165&response_type=code&redirect_uri=https://example.com/callback&scope=user-read-private user-read-email&state=34fFs29kd09"
    response = requests.get(
        query = ""
    )
    
def main():
    songs = get_welle1_charts()
    song_uris = get_song_uris(songs)
    #playlist_id = create_playlist("Welle 1 Charts")
    playlist_id = get_playlist_id("Welle 1 Charts")
    update_playlist(playlist_id, song_uris)

if __name__ == '__main__':
    main()