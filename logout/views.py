from django.shortcuts import render
from firebase_admin import auth 
def logout_page(request):
    if 'uid' in request.session: 
        try:
            users = auth.get_user(request.session['uid'])
        except:
            return render(request,'logout.html' ,{
                'error_logout' : True
            })
        try :
            del request.session['uid']
        except :
            return render(request,'logout.html' ,{
                'error_logout' : True , 'user_displayname' : users.display_name
            })
        return render(request , 'logout.html')
    return render(request,'logout.html' ,{
        'error_logout' : True
    })
