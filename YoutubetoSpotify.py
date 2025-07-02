import requests
import base64

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from ytmusicapi import YTMusic
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import re

client_id = "***********************************"
client_secret = "*********************************"

# 1. Access token al
def get_token(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        headers={"Authorization": f"Basic {b64_auth_str}"}
        
    )
    return response.json().get("access_token")


def youtube_Id_finder():
    ytmusic = YTMusic()
    input1 = input("Send playlist Id : ")
    playlist_id = input1
    print(playlist_id)
    try:
        playlist = ytmusic.get_playlist(playlist_id)
    except:
        playlist_id = input1[-41:]
        print(playlist_id)
    playlist = ytmusic.get_playlist(playlist_id)
    playlist_name = playlist["title"]
    tracks_name = []
    for track in playlist["tracks"]:
        title = track["title"]
        artist = track["artists"][0]["name"]
        video_id = track["videoId"]
        print(f"track : {title[:20]} artist : {artist[:10]}")
        if len(artist) > 25:
            tracks_name.append(re.sub(r"\[.*?\]", "",re.sub(r"\(.*?\)", "",f" {title}").strip()).strip())
        else:
            tracks_name.append(re.sub(r"\[.*?\]", "",re.sub(r"\(.*?\)", "",f" {title} {artist}").strip()).strip())
        
    return tracks_name,playlist_name


def spotify_Playlist(title,tracks_name):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="playlist-modify-public user-read-private"
    ))

    user_id = sp.current_user()["id"]

    playlist = sp.user_playlist_create(
        user=user_id,
        name=title,
        public=True,
        description="Automatically generated"
    )
    
    playlist_id = playlist["id"]

    user_info = sp.current_user()
    user_country = user_info['country']

 
    
    spotify_tracks = []
    
    for track in tracks_name:
        searches = sp.search(q=track ,type="track", limit = 5,market=user_country)["tracks"]["items"]
        print(track)
        print(f"\nArama: {track}")
        for item in searches:
            name = item["name"]
            artist = item["artists"][0]["name"]
            popularity = item["popularity"]
            print(f"{name} - {artist} | Popularity: {popularity}")
        track_url = searches[0]["uri"]
        spotify_tracks.append(track_url)
        
    print(tracks_name)
    print(spotify_tracks)
    offset = 0
    while spotify_tracks[offset:offset+25] != [] :
        sp.playlist_add_items(playlist_id,spotify_tracks[offset:offset+25])
        offset += 25
        
    
def main():
    tracks_name,playlist_name = youtube_Id_finder()
    spotify_Playlist(playlist_name,tracks_name)
    
if __name__ == "__main__":
    main()