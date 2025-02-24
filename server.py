from bottle import route, run, request
import json
import firebase_admin
from firebase_admin import credentials, firestore
import spotipy
from spotipy.oauth2 import SpotifyOAuth

@route("/", method=["POST"])
def api():
        try:
            params = json.loads(request.body.read())
            
        except:
            params = request.query.decode()
         
        if(params['Spotify']):
            print("Spotify")
            #insert track
            #global connection
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="", #talk to harrison about authentication
                                                   client_secret="",
                                                   redirect_uri="",
                                                   scope="user-library-read"))
            
            #user connection
            user = spotipy.Spotify(auth=params['Spotify'])
            userInfo = user.me()
            
           #print(user.user_playlists(userInfo['id']))
            
            #add playlists to firebase
            cred = credentials.Certificate("firebase-adminsdk.json")
            
            firebase_admin.initialize_app(cred)
            
            db = firestore.client()
            playlists = user.user_playlists(userInfo['id'])
            
            docRef = db.collection('Users').document(params['FirebaseID'])
            for playlist in playlists['items']:
                docRef.update({
                        #Union allows for just one item to be put into the database if it already exists,
                        #Future update is to make it so if it comes from different source we can update the account it came from
                    "playlists" : firestore.ArrayUnion(["playlists", playlist])
                })
            
            print(sp)
run(host='192.168.0.31', port=8080)
