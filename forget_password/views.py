from django.shortcuts import render
import pyrebase
import requests
from firebase_admin import auth 
config = {
    "apiKey": "apiKey",
    "authDomain": "projectId.firebaseapp.com",
    "databaseURL": "https://databaseName.firebaseio.com",
    "storageBucket": "projectId.appspot.com",
    "serviceAccount": "key/serviceAccountKey.json"
}
firebase = pyrebase.initialize_app(config)
def forget_password(request):
    if 'fid' in request.POST : # user had inputted the email 
        try:
            firebase.auth().send_password_reset_email(request.POST['email'])
        except:
            return render(request, 'forget_password.html', {
                'alert_message' : '如果有此信箱您將會收到密碼重置信'
            })
        return render(request, 'forget_password.html', {
            'alert_message' : '如果有此信箱您將會收到密碼重置信'
        }) 
    return render(request, 'forget_password.html', {})