from django.shortcuts import render ,redirect
import firebase_admin
import pyrebase
import requests
from firebase_admin import firestore ,credentials,auth, initialize_app
config = {
    "apiKey": "apiKey",
    "authDomain": "projectId.firebaseapp.com",
    "databaseURL": "https://databaseName.firebaseio.com",
    "storageBucket": "projectId.appspot.com",
    "serviceAccount": "key/serviceAccountKey.json"
}
firebase = pyrebase.initialize_app(config) # use to auth user
cred = credentials.Certificate("key/serviceAccountKey.json")
initialize_app(cred)
db = firestore.client() # dateaase -> firestore
def login_page(request):
    if 'uid' in request.session :#try to reconize the user by session
        try : 
            users = auth.get_user(request.session['uid'])
            return render(request , 'login.html' , {
                'user_displayname' : users.display_name
            })
        except:
            return render(request, 'login.html', {
                'error_message' : 'cookie有誤，請刪除後再試',
            })
    if 'sid' in request.POST:
        if request.POST['username'] =='' or request.POST['password'] == '': # no enter email or password
            return render(request , 'login.html' , {
                'alert_message' : '請輸入帳號密碼'
            })
        try: #try to login by email and password
            login_user = firebase.auth().sign_in_with_email_and_password(request.POST['username'], request.POST['password'])
            request.session['uid'] =login_user['localId']
            users = auth.get_user(request.session['uid'])
        except requests.exceptions.HTTPError as e: # all error code
            return render(request , 'login.html' , {
            'alert_message' : e.args[0].response.json()['error']['message']
            })
        if auth.get_user(login_user['localId']).email_verified == False: # enail had not verified
            firebase.auth().send_email_verification(login_user['idToken'])
            return render(request , 'email_verified.html',{
                'user_displayname' : users.display_name
            })
        return redirect('../') # lgoin success, so redirect to home page
    return render(request, 'login.html', {})