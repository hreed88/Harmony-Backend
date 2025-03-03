#Contributers: Harrison Reed
#Date: 3/2/2025
#Description: This is the server(backend) for the harmony app.
#It will handle all the requests from the client and send them to the appropriate API. 
#It will also handle the database and store all the data.


from bottle import route, run, request, response
import json
import firebase_admin
from firebase_admin import credentials, firestore
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import soundcloud_utils
import ytmusicapi_utils
import import_utils

authFile = open("auth.json", "r")

authFile = json.load(authFile)

cred = credentials.Certificate(authFile["Firebase"])
            
firebase_admin.initialize_app(cred)
            
db = firestore.client()


@route("/Spotify", method=["POST"])
def spotify_api():
        try:
            params = json.loads(request.body.read())
            
        except:
            params = request.query.decode()
         
        if(params['Spotify']):
            print("Spotify")
            #TODO implement albums 
            #TODO Finish playlist implementation
            #TODO implement user data
           
            #global connection
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=authFile["Spotify"]["client_id"],
                                                            client_secret=authFile["Spotify"]["client_secret"],
                                                            redirect_uri=authFile["Spotify"]["redirect_uri"],
                                                            scope=authFile["Spotify"]["scope"]))#request info from harrison)
            
            #user connection
            user = spotipy.Spotify(auth=params['Spotify'])
            userInfo = user.me()
            
            #Check if user wants to import their playlists
            if(params['Options']['Playlists'] == True):
                print("Importing Playlists")
                
                #get user playlists
                playlists = user.user_playlists(userInfo['id'])
                
                #used for setting user data
                userDocRef = db.collection('Users').document(params['FirebaseID'])
                #used for setting global songs
                fireBaseDocRef = db.collection('Songs')
                i = 0
                for playlist in playlists['items']:
                    if i == 6: #TODO remove this in production
                        break
                    thisSong = sp.user_playlist_tracks(userInfo['id'], playlist['id'])
                    songsList = []
                    for song in thisSong['items']:
                        song.setdefault(None)
                        songDocRef = {
                            'Name' : song['track']['name'],
                            'Artist' : song['track']['artists'],
                            'Album' : song['track']['album']['name'],
                            'Images' : song.get("track").get("album").get("images"),
                            'URI' : song['track']['uri'],
                            "LinkedService" : ["Spotify"],
                        }
                        #add to global and playlist songs
                        songsList.append(import_utils.addSongToDataBase(songDocRef, fireBaseDocRef))
                        #print(songsList)
                    #add to user playlists songs as reference if not songDocRef in userDocRef.get().to_dict():
                    playlistDocRef = {
                        'Name' : playlist['name'],
                        'Tracks' : {"Tracklist": songsList, "Number of Tracks": len(songsList)},
                        'LinkedServices' : ['Spotify'],
                        'Description' : playlist['description'],
                        'Images' : playlist.get("images"),
                        'URI' : playlist['uri'],
                        'ExternalURL' : playlist['external_urls']['spotify'],
                        'Owner' : playlist['owner'],
                        
                    }
                    import_utils.addPlaylistToDataBase(playlistDocRef, userDocRef)
                    i += 1

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
            
            
run(host='192.168.0.31', port=8080)
