from django.shortcuts import render
from firebase_admin import firestore, credentials, auth
db = firestore.client() # dateaase -> firestore
def home_page(request) :
    if 'uid' in request.session:
        try : #try to reconize the user by session
            now_user = auth.get_user(request.session['uid'])
        except :
            return render(request , 'home.html',{
                'error_message' : 'cookie有誤，請刪除後再試',
            })
        try : # Figure out if the user is an administrator
            data = db.collection('user').document(request.session['uid'])
            is_admin = data.get().to_dict()['admin']
        except:
            is_admin = False
        return render(request , 'home.html',{
            'user_displayname' : now_user.display_name,
            'user_verified' : now_user.email_verified,
            'is_admin' : is_admin
        })
    return render(request , 'home.html')