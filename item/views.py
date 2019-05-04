from django.shortcuts import render, HttpResponseRedirect
from firebase_admin import firestore ,credentials ,auth ,initialize_app
db = firestore.client()
def item_page(request) :
    fun_have = ['inquire', 'add', 'delete'] #function 
    if 'fun' in request.GET and request.GET['fun'] in fun_have :#if users in item page, they must to be one function
        fun = request.GET['fun']
    else :
        return HttpResponseRedirect('../item/?fun=inquire')
    if 'uid' in request.session : 
        try: #try to reconize the user by session
            users = auth.get_user(request.session['uid'])
        except:
            return render(request , 'item_'+ fun +'.html',{
                'error_message' : 'cookie有誤，請刪除後再試',
            })
        try: # Figure out if the user is an administrator
            data = db.collection('user').document(request.session['uid'])
            is_admin = data.get().to_dict()['admin']
        except:
            is_admin = False
        if users.email_verified == True and is_admin == True : # only work if user is admin
            if request.GET['fun'] == 'inquire' :
                if 'items' in request.GET : # admin earmark one item
                    try :
                        the_item_data = db.collection('item').document(request.GET['items']).get().to_dict()
                        users_data = list()
                        for i in range(len(the_item_data['borrow_num'])):
                            users_data.append({
                                'email' : db.collection('user').document(the_item_data['borrow_people'][i]).get().to_dict()['email'],
                                'name' : db.collection('user').document(the_item_data['borrow_people'][i]).get().to_dict()['name'],
                                'num' : the_item_data['borrow_num'][i],
                        })
                        the_item_detail = {
                            'last_num' : the_item_data['num_have']-the_item_data['num_borrow'],
                            'name' : the_item_data['name'],
                            'borrow_num' : the_item_data['num_borrow'],
                            'id' : request.GET['items'],
                        }
                    except:
                        return render(request , 'item_detail.html',{
                            'error_message' : '讀取指定item資料錯誤',
                            'user_displayname' : users.display_name,
                            'user_verified' : users.email_verified,
                            'is_admin' : is_admin,
                        })
                    return render(request, 'item_detail.html',{
                        'user_displayname' : users.display_name,
                        'is_admin' : is_admin,
                        'user_verified' : users.email_verified,
                        'data' : users_data,
                        'item' : the_item_detail
                    })
                try:
                    all_item_data = db.collection('item').get()
                    items_data = list()
                    for x in all_item_data :
                        temp = x.to_dict()
                        items_data.append({
                            'last_num' : temp['num_have']-temp['num_borrow'],
                            'name' : temp['name'],
                            'borrow_num' : temp['num_borrow'],
                            'id' : x.id,
                        })
                except:
                    return render(request , 'item_'+ fun +'.html',{
                        'error_message' : '讀取items資料錯誤',
                        'user_displayname' : users.display_name,
                        'user_verified' : users.email_verified,
                        'is_admin' : is_admin,
                    })
                return render(request, 'item_'+ fun +'.html',{
                    'user_displayname' : users.display_name,
                    'is_admin' : is_admin,
                    'user_verified' : users.email_verified,
                    'data' : items_data,
                })
            if request.GET['fun'] == 'add' :
                if 'iaid' in request.POST :
                    try :
                        if request.POST['id'][0] >'3' or request.POST['id'][1] >'3' or request.POST['id'][1] =='0' or request.POST['id'][0] =='0' :
                            return render(request , 'item_'+ fun +'.html',{
                                'user_displayname' : users.display_name,
                                'is_admin' : is_admin,
                                'user_verified' : users.email_verified,
                                'alert_message' : 'id 錯誤'
                            })
                        if not request.POST['id'].isdigit() :
                            return render(request , 'item_'+ fun +'.html',{
                                'user_displayname' : users.display_name,
                                'is_admin' : is_admin,
                                'user_verified' : users.email_verified,
                                'alert_message' : 'id 為數字'
                            })
                        all_item_no = db.collection('item').get()
                        for x in all_item_no :
                            if request.POST['id'] == x.id :
                                return render(request , 'item_'+ fun +'.html',{
                                    'user_displayname' : users.display_name,
                                    'is_admin' : is_admin,
                                    'user_verified' : users.email_verified,
                                    'alert_message' : 'id 已有'
                                })
                        new_item = db.collection('item').document(request.POST['id'])
                        new_item.set({
                            'borrow_num' : [],
                            'borrow_people' : [],
                            'describe' : request.POST['describe'],
                            'name' : request.POST['name'],
                            'num_have' : int(request.POST['have']),
                            'num_borrow' : 0,
                        })
                        return render(request , 'item_'+ fun +'.html',{
                            'user_displayname' : users.display_name,
                            'is_admin' : is_admin,
                            'user_verified' : users.email_verified,
                            'alert_message' : '成功新增'
                        })
                    except :
                        return render(request , 'item_'+ fun +'.html',{
                            'user_displayname' : users.display_name,
                            'is_admin' : is_admin,
                            'user_verified' : users.email_verified,
                            'alert_message' : '資料錯誤'
                        })
                return render(request , 'item_'+ fun +'.html',{
                    'user_displayname' : users.display_name,
                    'is_admin' : is_admin,
                    'user_verified' : users.email_verified,
                })
            if request.GET['fun'] == 'delete':
                if 'idid' in request.POST :
                    try :
                        all_item_no = db.collection('item').get()
                        for x in all_item_no :
                            if request.POST['id'] == x.id :
                                delete_item = db.collection('item').document(x.id).get().to_dict()
                                if int(request.POST['num']) <= 0 or int(request.POST['num']) > delete_item['num_have'] - delete_item['num_borrow'] :
                                    return render(request , 'item_'+ fun +'.html',{
                                        'user_displayname' : users.display_name,
                                        'is_admin' : is_admin,
                                        'user_verified' : users.email_verified,
                                        'alert_message' : '數量錯誤'
                                    })
                                if int(request.POST['num']) == delete_item['num_have'] - delete_item['num_borrow'] :
                                    if delete_item['num_borrow'] == 0 : # no one borrow
                                        db.collection('item').document(x.id).delete()
                                    else :
                                        delete_item['num_have'] -= int(request.POST['num'])
                                        db.collection('item').document(x.id).set(delete_item)
                                else :
                                    delete_item['num_have'] -= int(request.POST['num'])
                                    db.collection('item').document(x.id).set(delete_item)
                                return render(request , 'item_'+ fun +'.html',{
                                    'user_displayname' : users.display_name,
                                    'is_admin' : is_admin,
                                    'user_verified' : users.email_verified,
                                    'alert_message' : '刪除成功, id :' +x.id + ', name : ' + delete_item['name']
                                })
                        return render(request , 'item_'+ fun +'.html',{
                            'user_displayname' : users.display_name,
                            'is_admin' : is_admin,
                            'user_verified' : users.email_verified,
                            'alert_message' : 'id錯誤'
                        })
                    except:
                        return render(request , 'item_'+ fun +'.html',{
                            'user_displayname' : users.display_name,
                            'is_admin' : is_admin,
                            'user_verified' : users.email_verified,
                            'alert_message' : '資料錯誤'
                        })
                return render(request , 'item_'+ fun +'.html',{
                    'user_displayname' : users.display_name,
                    'is_admin' : is_admin,
                    'user_verified' : users.email_verified,
                })
        else :
            return render(request , 'item_'+ fun +'.html',{
                'error_message' : '只有管理員才能使用',
                'user_displayname' : users.display_name,
                'is_admin' : is_admin,
                'user_verified' : users.email_verified,
            })
        
    return render(request , 'item_'+ fun +'.html',{
        'error_message' : '須登入帳號才能使用',
    })