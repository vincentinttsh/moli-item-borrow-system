from django.shortcuts import render ,redirect
import requests
import pyrebase
import firebase_admin
config = {
    "apiKey": "apiKey",
    "authDomain": "projectId.firebaseapp.com",
    "databaseURL": "https://databaseName.firebaseio.com",
    "storageBucket": "projectId.appspot.com",
    "serviceAccount": "key/serviceAccountKey.json"
}
firebase = pyrebase.initialize_app(config)
db = firebase_admin.firestore.client()
def register(request):
    if 'uid' in request.session :
        try : # try to reconize the user by session
            users = firebase_admin.auth.get_user(request.session['uid'])
            return render(request, 'register.html', {
                'user_displayname' : users.display_name
            })
        except:
            return render(request , 'home.html',{
                'error_message' : 'cookie有誤，請刪除後再試',
            })
    if 'rid' in request.POST:
        for x in request.POST:
            if request.POST[x] == '':
                return render(request, 'register.html',{
                    'alert_message': '請填寫完成'
                })
        if request.POST['password1'] != request.POST['password2']:
            return render(request, 'register.html', {
                'alert_message': '密碼不一致'
            })
        if request.POST['email'][-12:] != '@ncnu.edu.tw' and request.POST['email'][-18:] != '@mail1.ncnu.edu.tw' and request.POST['email'][-16:] != 'mail.ncnu.edu.tw':
            return render(request, 'register.html',{
                'alert_message': '只接受學校信箱'
            })
        try:
            user = firebase_admin.auth.create_user(
                email = request.POST['email'],
                password = request.POST['password1'],
                display_name = request.POST['username'], 
                email_verified = False,
            )
            data = db.collection('user').document(user.uid)
            data.set({
                'admin' : False,
                'borrow_item_no' : [],
                'borrow_item_name' : [],
                'borrow_num' : [],
                'borrow_time': [],
                'email' : request.POST['email'],
                'name' : request.POST['username']
            })
            return render(request, 'register.html',{
                'alert_message': '登入後會寄電子信箱認證信'
            })
        except ValueError as e: #password less than 6
            return render(request, 'register.html', {
                'alert_message' : e
            })
        except firebase_admin.auth.AuthError as e :
            print(e.detail)
            return render(request, 'register.html', {
                'alert_message' : e.detail.response.json()['error']['message']
            })
    return render(request, 'register.html', {})
