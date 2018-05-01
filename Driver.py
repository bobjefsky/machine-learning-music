def get_token():
    USERNAME = "bsunbury29"
    SCOPE = "user-library-read"
    CLIENT_ID = "592a4d0fce6249d48f7c0ad8a2519c68"
    CLIENT_SECRETE = "003fcf2e13e042f480ee1553f48be3c0"
    REDIRECT_URL = "http://localhost:8000"

    #when it asks for the redirect link, give it everything startin with ?code=...
    token = spotipy.util.prompt_for_user_token(
        username=USERNAME,
        scope=SCOPE,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRETE,
        redirect_uri=REDIRECT_URL)

    return token


def show_tracks(results):
    for i, item in enumerate(results['items']):
        track = item['track']
        #print("%d\t%32.32s\t%s\t%s" % (i, track['artists'][0]['name'], track['name'], track['preview_url']))
        print("%d\t%s\t%s\t%s" % (i, track['artists'][0]['name'], track['name'], track['preview_url']))


def download_songs(tracks):
    song_path = "mp3_songs"
    for i, item in enumerate(tracks['items']):
        track = item['track']
        if track['preview_url'] != "None":
            full_file_name = os.path.join(song_path, track['name'] + ".mp3") #should regex clean this input
            urllib.request.urlretrieve(track['preview_url'], full_file_name)
    print("downloaded songs from playlist")


def show_playlist(token):
    username = "bsunbury29"

    if token:
        sp = spotipy.Spotify(auth=token)
        playlists = sp.user_playlists(username)
        for playlist in playlists['items']:
            print(playlist['name'])

    else:
        print("Don't have a token for " + username)


def get_playlist(token):
    username = "bsunbury29"

    if token:
        #given_playlist = "CreateMusic"
        given_playlist = input("Enter the name of the playlist you would list to use ")
        sp = spotipy.Spotify(auth=token)
        playlists = sp.user_playlists(username)
        for playlist in playlists['items']:
            if playlist['name']==given_playlist:
                print("Using playlist " + playlist['name'])

                results = sp.user_playlist(username, playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                #show_tracks(tracks)
                download_songs(tracks)
                while tracks['next']:
                    tracks = sp.next(tracks)
                    #show_tracks(tracks)
                    download_songs(tracks)
    else:
        print("Don't have a token for " + username)


def main():
    # commented out everythin except generator because I just want to create new music
    #token = get_token()
    #show_playlist(token)
    #get_playlist(token)
    # convert the mp3 files to .mid
    #converter.main()
    print("Creating new music from .mid files")
    generator.main()


if __name__ == '__main__':
    import spotipy
    import spotipy.util
    import urllib.request
    import os
    import converter
    import generator
    main()
