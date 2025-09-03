#Contributers: Harrison Reed
#Date: 3/2/2025
#Description: This is the server(backend) for the harmony app.
#It will handle all the requests from the client and send them to the appropriate API. 
#It will also handle the database and store all the data.


from bottle import route, run, request, response, hook,static_file
import json
import firebase_admin
from firebase_admin import credentials, firestore
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import spotify_utils as su
import soundcloud_utils
import ytmusicapi_utils
import import_utils
import os, requests, json

authFile = open("auth.json", "r")

authFile = json.load(authFile)

cred = credentials.Certificate(authFile["Firebase"])
            
firebase_admin.initialize_app(cred)
            
db = firestore.client()

@route('/spotify_auth')
def spotify_auth():
    return static_file('spotify_auth.html', root='./')

@route("/Spotify", method=["POST"])
def spotify_api():

        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI")

        print(request)
        try:
            params = request.json  # Handle incoming params
            
        except:
            print("Error")
            return https_fn.Response("Error")
            #params = request.query.decode()
        
        print(params)
        thisResponse = ""
        if(params['Spotify']):
            print("Spotify")
            #TODO implement albums 
            #TODO Finish playlist implementation
            #TODO implement user data
            
            #global connection
            sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                            client_secret=client_secret,))
                                                            # redirect_uri=authFile["Spotify"]["redirect_uri"],
                                                            # scope=authFile["Spotify"]["scope"]))#request info from harrison)
            
            #user connection
            print(sp)
            user = spotipy.Spotify(auth=params['Spotify'])
            userInfo = user.me()
            
            #Check if user wants to import their playlists
            print(params['Options'])
            print(params['Options']['Albums'])
            if(params['Options']['Playlists'] == True):
                print("Importing Playlists")
                try:    
                    su.importPlaylists(user, userInfo, db, params, sp)
                    thisResponse = thisResponse + "Playlists imported successfully!"
                except Exception as e:
                    print(f"Playlists import failed!{e}")          
                    return https_fn.Response("Playlists import failed!")
            
            #Check if user wants to import their albums
            if(params['Options']['Albums'] == True):
                print("Importing Albums")
                su.importAlbums(user, db, params)
                thisResponse = thisResponse + " Albums imported successfully!"
        response.status = 200
        return{"message": "Playlists imported successfully"}

#----------------------------------------------------------------------------------------------
#TODO Note: Youtube must be implemented in flutter frontend
@route("/Youtube", method=["POST"])
def youtube_api():
    try:
        params = json.loads(request.body.read())  # Handle incoming params
    except:
        params = request.query.decode()

    if "Youtube" in params and "FirebaseID" in params:
        print("YouTube Music Integration")

        access_token = params["Youtube"]
        firebase_id = params["FirebaseID"]

        # Initialize YTMusic with credentials
        ytmusic = ytmusicapi_utils.get_ytmusic_credentials(access_token)

        if not ytmusic:
            response.status = 400
            return {"error": "Failed to authenticate with YouTube Music API"}

        # Fetch user info and playlists
        user_info = ytmusicapi_utils.get_user_info(ytmusic)
        if not user_info:
            response.status = 400
            return {"error": "Failed to retrieve user data"}

        playlists = ytmusicapi_utils.get_user_playlists(ytmusic)
        if not playlists:
            response.status = 400
            return {"error": "Failed to retrieve user playlists"}

        # Process playlists and store in Firebase
        result = ytmusicapi_utils.import_youtube_playlists_to_firestore(playlists, firebase_id, db)

        return {"message": "Playlists imported successfully", "data": result}
    else:
        response.status = 400
        return {"error": "Invalid request"}

#----------------------------------------------------------------------------------------------
#TODO Note: Soundcloud must be implemented in flutter frontend
@route("/Soundcloud", method=["POST"])
def soundcloud_api():
    """Handles SoundCloud authentication and playlist import."""
    try:
        params = json.loads(request.body.read())
    except:
        params = request.query.decode()

    if "SoundCloud" in params and "FirebaseID" in params:
        print("SoundCloud Integration")

        access_token = params["SoundCloud"]
        firebase_id = params["FirebaseID"]

        # Import playlists from SoundCloud using the access token and Firebase ID
        result = soundcloud_utils.import_soundcloud_playlists(access_token, firebase_id,db)

        if "error" in result:
            response.status = 400  # Set HTTP status to 400 if there's an error
            return result  # Return the error message

        response.status = 200  # Set HTTP status to 200 for successful response
        return result  # Return success message

    response.status = 400  # Set HTTP status to 400 if the request is invalid
    return {"error": "Invalid request"}
        
#-----------------------------------------------------------------------------------------------
#TODO Note: AppleMusic must be implemented in flutter frontend

@route("/AppleMusic", method=["POST"])
def applemusic_api():
    pass        
        # if(params['AppleMusic']):
        #     print("AppleMusic")
        #     #TODO implement applemusic api
        
#-----------------------------------------------------------------------------------------------
#TODO Note: Bandcamp must be implemented in flutter frontend
@route("/Bandcamp", method=["POST"])
def bandcamp_api():
    pass           
        # if(params['Bandcamp']):
        #     print("Bandcamp")
        #     #TODO implement bandcamp api

@route("/spotify_token", method=["POST"])
def spotify_token():

    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI")
    print(redirect_uri)

    data = request.json
    code = data.get("code")

    if not code:
        response.status = 400
        return {"error": "Missing code"}

    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }

    r = requests.post(token_url, data=payload, headers={
        "Content-Type": "application/x-www-form-urlencoded"
    })

    if r.status_code != 200:
        response.status = r.status_code
        return r.json()

    return r.json() 

@route("/spotify_client_id", method=["POST"])
def get_spotify_client_id():
    
    # Read your secrets from environment
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI")
    print("returning" , client_id)
    return {"ClientID" : client_id}
                
            
run(host='0.0.0.0', port=44303)
