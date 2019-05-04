from django.shortcuts import render
from firebase_admin import firestore ,credentials ,auth ,initialize_app
import datetime
'''
item_key    
type        1 = 書籍 , 2 = 電子產品 , 3 = 其他
from        1 = 老俞 , 2 = 學校 , 3 = 校友
no          xxx
''' 
db = firestore.client()
def return_page(request) :
    if 'uid' in request.session:
        try: #try to reconize the user by session
            users = auth.get_user(request.session['uid'])
        except:
            return render(request , 'return.html',{
                'error_message' : 'cookie有誤，請刪除後再試',
            })
        try:# Figure out if the user is an administrator
            user_data = db.collection('user').document(request.session['uid'])
            is_admin = user_data.get().to_dict()['admin']
        except:
            is_admin = False
        try:
            borrow_item = db.collection('user').document(request.session['uid']).get().to_dict()
            item = list()
            for i in range(len(borrow_item['borrow_item_no'])) :
                item.append({
                    'id' : borrow_item['borrow_item_no'][i],
                    'name' : borrow_item['borrow_item_name'][i],
                    'num' : borrow_item['borrow_num'][i]
                })
        except:
            return render(request , 'return.html',{
                'error_message' : '讀取資料錯誤',
                'user_displayname' : users.display_name,
                'user_verified' : users.email_verified,
                'is_admin' : is_admin
            })
        if 'reid' in request.POST:
            return_item = list()
            try:
                for x in item :
                    if request.POST[x['id']] != '' and request.POST[x['id']] != '0':
                        if int(request.POST[x['id']]) > int(x['num']) : # request to return bigger than user had borrowed
                            return render(request , 'return_result.html',{
                                'error' : True,
                                'user_displayname' : users.display_name,
                                'user_verified' : users.email_verified,
                                'is_admin' : is_admin
                            })
                        else :
                            return_item.append({
                                'id' : x['id'],
                                'name' : x['name'],
                                'return' : request.POST[x['id']]
                            })
                            temp = db.collection('item').document(x['id']).get().to_dict()
                            temp['num_borrow']-=int(request.POST[x['id']])
                            if temp['borrow_num'][temp['borrow_people'].index(request.session['uid'])] == int(request.POST[x['id']]) :
                                del temp['borrow_num'][temp['borrow_people'].index(request.session['uid'])]
                                del temp['borrow_people'][temp['borrow_people'].index(request.session['uid'])]
                            else :
                                temp['borrow_num'][temp['borrow_people'].index(request.session['uid'])]-=int(request.POST[x['id']])
                            db.collection('item').document(x['id']).set(temp)
                            temp = db.collection('user').document(request.session['uid']).get().to_dict()
                            if temp['borrow_num'][temp['borrow_item_no'].index(x['id'])] == int(request.POST[x['id']]):
                                del temp['borrow_item_name'][temp['borrow_item_no'].index(x['id'])]
                                del temp['borrow_num'][temp['borrow_item_no'].index(x['id'])]
                                del temp['borrow_time'][temp['borrow_item_no'].index(x['id'])]
                                del temp['borrow_item_no'][temp['borrow_item_no'].index(x['id'])]
                            else :
                                temp['borrow_num'][temp['borrow_item_no'].index(x['id'])]-= int(request.POST[x['id']])
                            db.collection('user').document(request.session['uid']).set(temp)
            except:
                return render(request , 'return_result.html',{
                    'error' : True,
                    'user_displayname' : users.display_name,
                    'user_verified' : users.email_verified,
                    'is_admin' : is_admin
                })
            return render(request , 'return_result.html',{
                    'error' : False,
                    'user_displayname' : users.display_name,
                    'user_verified' : users.email_verified,
                    'is_admin' : is_admin,
                    'item' : return_item
                })
        return render(request , 'return.html',{
            'user_displayname' : users.display_name,
            'user_verified' : users.email_verified,
            'is_admin' : is_admin,
            'item' : item
        })
    return render(request , 'return.html',{
        'error_message' : '須登入帳號且信箱認證後才能使用',
    })