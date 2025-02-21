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
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="ed7c834dad2d41bba8f3642c7ed07350",
                                                   client_secret="80e2afa04e284dfd90febe557d9375bb",
                                                   redirect_uri="http://localhost:8888/callback",
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
                    "playlists" : firestore.ArrayUnion(["playlists", playlist])
                })
            
            print(sp)
run(host='192.168.0.31', port=8080)