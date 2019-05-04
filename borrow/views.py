from django.shortcuts import render, HttpResponseRedirect
from firebase_admin import firestore, credentials, auth, initialize_app
import datetime
'''
item_key    
type        1 = 書籍 , 2 = 電子產品 , 3 = 其他
from        1 = 老俞 , 2 = 學校 , 3 = 校友
no          xxx
''' 
db = firestore.client() # database -> firestore
def borrow_page(request) :
    # if type ilegal redirect to default type
    if 'type' in request.GET and request.GET['type'] > '0' and request.GET['type'] < '4':
        thing = int(request.GET['type'])
    else :
        return HttpResponseRedirect('../borrow/?type=1')
    if 'uid' in request.session:
        try:
            now_user = auth.get_user(request.session['uid'])
        except:
            return render(request , 'borrow.html',{
                'error_message' : 'cookie有誤，請刪除後再試',
            })
        try: #Figure out if the user is an administrator
            user_data = db.collection('user').document(request.session['uid'])
            is_admin = user_data.get().to_dict()['admin']
        except:
            is_admin = False
        if now_user.email_verified == False :
            return render(request , 'borrow.html',{
                'user_displayname' : now_user.display_name,
                'user_verified' : now_user.email_verified,
                'error_message' : '須信箱認證後才能使用',
                'is_admin' : is_admin,
            })
        try: #load all property of this type
            item_no = db.collection('item').get()
            item = list()
            for x in item_no :
                if int(x.id) // 10000 == thing:
                    data = x.to_dict()
                    item.append({
                        'id' : x.id,
                        'name' : data['name'],
                        'num' : data['num_have']-data['num_borrow']
                    })
        except:
            return render(request , 'borrow.html',{
                'error_message' : '讀取資料錯誤',
                'user_displayname' : now_user.display_name,
                'user_verified' : now_user.email_verified,
                'is_admin' : is_admin
            })
        if 'bid' in request.POST: # user try to borrow property
            borrow = list()
            try:
                for x in item :
                    if request.POST[x['id']] != '' and request.POST[x['id']] != '0':
                        # The number of borrowed is greater than the number of possessions
                        if int(request.POST[x['id']]) > int(x['num']) :
                            return render(request , 'borrow_result.html',{
                                'error' : True,
                                'user_displayname' : now_user.display_name,
                                'user_verified' : now_user.email_verified,
                                'is_admin' : is_admin
                            })
                        else :
                            borrow.append({
                                'id' : x['id'],
                                'name' : x['name'],
                                'borrow' : request.POST[x['id']]
                            })
                            # update item database
                            temp = db.collection('item').document(x['id']).get().to_dict()
                            #if the user had borrow this item before
                            if request.session['uid'] in temp['borrow_people']: 
                                key = temp['borrow_people'].index(request.session['uid'])
                                temp['borrow_num'][key] += int(request.POST[x['id']])
                            else :
                                temp['borrow_num'].append(int(request.POST[x['id']]))
                                temp['borrow_people'].append(request.session['uid'])
                            temp['num_borrow'] += int(request.POST[x['id']])
                            db.collection('item').document(x['id']).set(temp)
                            # update user database
                            temp = db.collection('user').document(request.session['uid']).get().to_dict()
                            if x['id'] in temp['borrow_item_no'] :
                                key = temp['borrow_item_no'].index(x['id'])
                                temp['borrow_num'][key]+=int(request.POST[x['id']])
                                temp['borrow_time'][key] = datetime.datetime.now()
                            else :
                                temp['borrow_item_no'].append(x['id'])
                                temp['borrow_item_name'].append(x['name'])
                                temp['borrow_num'].append(int(request.POST[x['id']]))
                                temp['borrow_time'].append(datetime.datetime.now())
                            db.collection('user').document(request.session['uid']).set(temp)
            except:
                return render(request , 'borrow_result.html',{
                    'error' : True,
                    'user_displayname' : now_user.display_name,
                    'user_verified' : now_user.email_verified,
                    'is_admin' : is_admin
                })
            return render(request , 'borrow_result.html',{
                    'error' : False,
                    'user_displayname' : now_user.display_name,
                    'user_verified' : now_user.email_verified,
                    'is_admin' : is_admin,
                    'item' : borrow
            })
        return render(request , 'borrow.html',{
            'user_displayname' : now_user.display_name,
            'user_verified' : now_user.email_verified,
            'is_admin' : is_admin,
            'item' : item
        })
    return render(request , 'borrow.html',{
        'error_message' : '須登入帳號才能使用',
    })