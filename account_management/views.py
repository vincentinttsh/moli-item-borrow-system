from django.shortcuts import render, HttpResponseRedirect
from firebase_admin import firestore, credentials, auth, initialize_app
db = firestore.client() # database -> firestore
def account_page(request) :
    if 'uid' in request.session: 
        try : #try to reconize the user by session
            now_user = auth.get_user(request.session['uid'])
        except :
            return render(request , 'account.html',{
                'error_message' : 'cookie有誤，請刪除後再試',
            })
        try : # Figure out if the user is an administrator
            data = db.collection('user').document(request.session['uid'])
            is_admin = data.get().to_dict()['admin']
        except :
            is_admin = False
        if now_user.email_verified == True and is_admin == True :
            if 'inquire' in request.GET :
                try: # try to recognize if the user exist
                    check = auth.get_user(request.GET['inquire'])
                except:
                   return render(request , 'account.html',{
                        'error_message' : '查無該user',
                        'user_displayname' : now_user.display_name,
                        'user_verified' : now_user.email_verified,
                        'is_admin' : is_admin,
                })
                try:# load the user data
                    the_user_data = db.collection('user').document(request.GET['inquire']).get().to_dict()
                    borrow_data = list()
                    for i in range(len(the_user_data['borrow_item_name'])):
                        borrow_data.append({
                            'no' : the_user_data['borrow_item_no'][i],
                            'name' : the_user_data['borrow_item_name'][i],
                            'num' : the_user_data['borrow_num'][i],
                            'date' : the_user_data['borrow_time'][i]
                        })
                    the_user_detail = {
                        'email' : the_user_data['email'],
                        'admin' : the_user_data['admin'],
                        'name' : the_user_data['name'],
                        'verified' : auth.get_user(request.GET['inquire']).email_verified,
                    }
                except:
                    return render(request , 'account_detail.html',{
                        'error_message' : '讀取user資料錯誤',
                        'user_displayname' : now_user.display_name,
                        'user_verified' : now_user.email_verified,
                        'is_admin' : is_admin,
                    })
                return render(request, 'account_detail.html',{
                        'user_displayname' : now_user.display_name,
                        'is_admin' : is_admin,
                        'user_verified' : now_user.email_verified,
                        'data' : borrow_data,
                        'user' : the_user_detail
                    })
            try : #load all users data
                all_users_data = db.collection('user').get()
                users_data = list()
                for x in all_users_data :
                    temp = x.to_dict()
                    users_data.append({
                        'admin' : temp['admin'],
                        'name' : temp['name'],
                        'email' : temp['email'],
                        'id' : x.id,
                    })
            except:
                return render(request , 'account.html',{
                    'error_message' : '讀取所有users資料錯誤',
                    'user_displayname' : now_user.display_name,
                    'user_verified' : now_user.email_verified,
                    'is_admin' : is_admin,
                })
            return render(request, 'account.html',{
                    'user_displayname' : now_user.display_name,
                    'is_admin' : is_admin,
                    'user_verified' : now_user.email_verified,
                    'data' : users_data,
            })
        else :
            return HttpResponseRedirect('../')
    else :
        return HttpResponseRedirect('../')