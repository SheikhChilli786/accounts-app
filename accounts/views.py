import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Max
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import BooleanField, Case, When, Value,F
from django.views.generic import ListView
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse ,HttpResponse,HttpResponseForbidden
from django.contrib import messages 
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import update_session_auth_hash,logout,authenticate,login,get_user_model
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
# Create your views here.
User = get_user_model()
def context_data(request):
    fullpath = request.get_full_path()
    abs_uri = request.build_absolute_uri()
    abs_uri = abs_uri.split(fullpath)[0]
    context = {
        'system_host': abs_uri,
        'page_name':'',
        'page_title':'',
        'system_name' : 'Accounts Managament System',
        'topbar':True,
        'footer':True,
    }
    return context

@login_required
def user_detail(request, pk=None):
    context = context_data(request)
    context['page'] = 'parties'
    context['page_title'] = 'Parties'
    options = []

    if pk:
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return HttpResponse(status=204)
        if (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None)==request.user or request.user.is_superuser:
            context['parties'] = Party.objects.select_related('user').filter(user = user)
            context['page_name'] = user
            context['user'] = user
            options.append(('product','Product')) if (request.user.has_perm('accounts.add_product') or request.user == user) else None
            options.append(('manage_transactions','Manage Transactions')) if (request.user.has_perm('accounts.can_manage_transactions') or request.user == user) else None
            options.append(('manage_s_p','Manage Sale/purchases')) if (request.user.has_perm('accounts.can_manage_s_p') or request.user == user) else None 
            options.append(('manage_conversion','Conversion Form'))  if (request.user.has_perm('accounts.view_conversion') or request.user == user) else None
        else:
            return redirect('accounts:user-detail')
    else:
        if (request.user.staffuser if hasattr(request.user, 'staffuser') else False) or request.user.is_superuser:
                return HttpResponse(status=204)
        user = User.objects.get(pk = request.user.pk)
        context['parties'] = Party.objects.filter(user = request.user)
        context['page_name'] = request.user
        context['user'] = request.user
        options.append(('product','Product')) if (request.user.has_perm('accounts.add_product') or request.user == user) else None
        options.append(('manage_transactions','Manage Transactions')) if (request.user.has_perm('accounts.can_manage_transactions') or request.user == user) else None
        options.append(('manage_s_p','Manage Sale/purchases')) if (request.user.has_perm('accounts.can_manage_s_p') or request.user == user) else None
        options.append(('manage_conversion','Conversion Form'))  if (request.user.has_perm('accounts.view_conversion') or request.user == user) else None
    context['options'] = options
    return render(request,'accounts/party.html',context)

@login_required
def manage_party(request,pk=None):
    context = context_data(request)
    context['page'] = 'manage_user'
    context['page_title'] = 'Manage User'

    if pk :
        try:
            party = Party.objects.select_related('user').get(pk=pk)
        except:
            HttpResponse(status=204)
        if party:

            if request.user.is_superuser or  (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.change_party')) or request.user == party.user :
                    context['party'] = party
            else:
                return HttpResponse("You are not Authorized to Edit This Party")
        else:
            return HttpResponse("The party is invalid")        
          
    else:
        user = User.objects.get(pk = request.GET.get('user_id'))

        if request.user.is_superuser or  (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None==request.user and  request.user.has_perm('accounts.add_party') or request.user == user ):
            context['user_id'] = user.pk
        else:
            HttpResponse("You are not Authorized to Add This Party")
    return render(request, 'accounts/manage_party.html', context)
            
@login_required
def save_party(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        post = request.POST
        party_id = post.get('id','')
        user_id = post.get('user','')
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except:
                resp['msg'] = "User couldn't be found. Please Try Again After Refresh"
                return JsonResponse(resp)
            if party_id:
                try:
                    party = Party.objects.select_related('user').get(pk=party_id)
                except:
                    resp['msg'] = "Party coludn't be found. Please Try Again After Refresh"
                    return JsonResponse(resp)
                if request.user.is_superuser or party.user == request.user or (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.change_party')):
                    form = SaveParty(post, instance=party)
                else:
                    resp['msg'] = "You are not authorized to edit Party"
                    return JsonResponse(resp)
            else:
                if request.user.is_superuser or user == request.user  or  (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.add_party')):
                    form = SaveParty(post)
                else:
                    resp['msg'] = "You are not authorized to Add Party"
                    return JsonResponse(resp)
                
        if form.is_valid():
            form.save()

            if party_id == '':
                messages.success(request, "Party has been saved successfully.")
            else:
                messages.success(request, "Party has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if resp['msg'] != '':
                        resp['msg'] += '<br/>'
                    resp['msg'] += f'[{field.name}] {error}'

    else:
        resp['msg'] = "There's no data sent in the request"
    return JsonResponse(resp)


@login_required
def delete_party(request, pk=None):
    resp = {
        'status': 'failed',
        'msg': ''
    }

    if pk:
        party = Party.objects.select_related('user').filter(pk = pk)
        if party:
            if request.user.is_superuser or party[0].user == request.user  or (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.delete_party')):
                if party[0].delete_flag == 0:
                    try:
                        party.update(delete_flag=1)
                        messages.success(request, "Party has been moved to recycle bin successfully.")
                        resp['status'] = 'success'
                    except:
                        resp['msg'] = "Deleting User Failed."
                else:
                    party.delete()
                    messages.success(request,"Party has been deleted successfully.")
                    resp['status'] = 'success'
            else:
                resp['msg'] = "You are not authorized to delete party."
                return JsonResponse(resp)
        else:
            resp['msg'] = "Party couldn't be found. Please Try agin after refresh"
            return JsonResponse(resp)
    
    else:
        resp['msg'] = "There's no data sent in the request"

    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def manage_transaction(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_transaction'
    context['page_title'] = 'Manage Transaction'
    user_id = request.GET.get('user_id', '')
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse("The user Couldn't be found. Please Refresh and Try again")

    if pk is None:
        # Adding a new transaction
        if request.user.is_superuser or request.user == user or  (user.assigned_staff.user if hasattr(user.assigned_staff,'user') else False == request.user and request.user.has_perm('accounts.can_manage_transactions')):
            
            context['user_id'] = user.id
            context['parties'] = Party.objects.filter(user=user, delete_flag=0)
        else:
            return HttpResponse("You are not allowed to manage Transactions. Please contact admin for further queries")
    else:
        resp = {
            'msg':"",
            'status':'failed'
        }
        # Editing an existing transaction
        if (request.user.is_superuser or 
            user == request.user or
            ((request.user.has_perm('accounts.change_transaction')  and
            user.assigned_staff.user if hasattr(user.assigned_staff,'user') else False == request.user))):
            try:
                transaction = Transaction.objects.get(pk=pk)
            except:
                resp['msg'] = "Transaction Couldn't be Found. Please Try again after refreshing"
            context['user_id'] = user.id
            resp['party']= transaction.party.name
            resp['description']= transaction.description
            resp['user']= transaction.party.user.username
            resp['debit']= transaction.debit
            resp['credit']= transaction.credit
            resp['date']= transaction.form.created_at
            resp['id']=transaction.pk
            resp['status'] = 'success'
            return JsonResponse(resp)
        else:
            resp['msg'] = "You are not authorized Edit Transactions"
            return JsonResponse(resp)
    return render(request, 'accounts/manage_transaction.html', context)

@login_required
def save_transaction(request):
    resp = {'status': 'failed', 'msg': '', 'transaction': None}

    if request.method == 'POST':

        post = request.POST
        id = post.get('id','') 
        user_id = post.get('user_id','') 
        date = post.get('date', '')
        party = post.get('name', '')
        debit = post.get('debit','')
        credit = post.get('credit','')
        if (debit == 0 and credit == 0) or (debit == '' and credit == ''):
            resp['msg'] = "Please enter a valid amount"
            return JsonResponse(resp)
        
        if user_id:
            try:
                party = Party.objects.get(name=party,user__id=user_id)
            except:
                resp['msg'] = "Party couldn't be found."
                return JsonResponse(resp)
            if party:
                form_obj, created = Form.objects.get_or_create(created_at=date)
                if id:
                    try:
                        transaction = Transaction.objects.get(id = id)
                    except:
                        resp['msg'] = "Transaction Couldn't be found. Please Try again After Refresh"
                        return JsonResponse(resp)
                    if request.user.is_superuser or party.user == request.user or  (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.change_transaction')) :
                        form = SaveForm(post,instance=transaction)
                    else:
                        resp['msg'] = "You are not authorized to Edit Transaction "
                        return JsonResponse(resp)
                else:
                    if request.user.is_superuser or party.user == request.user  or  (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.add_transaction')):
                        form = SaveForm(post)
                    else:
                        resp['msg'] = "You are not authorized to Add transaction"
                        return JsonResponse(resp)
            else:
                return JsonResponse(status=204)

            if form.is_valid():
                transaction_instance = form.save(commit=False)
                transaction_instance.party = party
                transaction_instance.form = form_obj
                if debit == '':
                    transaction_instance.debit = 0
                if credit == '':
                    transaction_instance.credit = 0
                transaction_instance.save()
                resp['status'] = 'success'
            
            else:
                for field in form:
                    for error in field.errors:
                        if resp['msg'] != '':
                            resp['msg'] += '<br/>'
                        resp['msg'] += f'[{field.name}] {error}'
    else:
        resp['msg'] = "There's no data sent in the request"
    balance = party.get_balance()
    party.balance = balance
    party.save()

    return JsonResponse(resp)

@login_required
def transaction_list(request):
    if request.method == 'GET':
        resp = {
            'msg' : "",
            'status': 'failed'
        }
        selected_date = request.GET.get('date')
        user_id = request.GET.get('user_id')
        limit = int(request.GET.get('limit'))
        
        try:
            user = User.objects.get(pk=user_id)
        except:
            resp['msg'] = "User Couldn't be found. Please Try Again."
        if user:
            if request.user.is_superuser or user == request.user or (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.view_transaction') ):
                if selected_date == '2000-01-01':
                    if limit == -1:
                        transactions = Transaction.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,party__user = user,is_sales=None)
                    else:
                        transactions = Transaction.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,party__user = user,is_sales=None)[:limit]
                else:
                    transactions = Transaction.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,form__created_at=selected_date,party__user = user,is_sales=None)
                resp['transaction_data'] =[{'party': transaction.party.name,
                                    'description': transaction.description,
                                    'user': transaction.party.user.username,
                                    'debit': transaction.debit,
                                    'credit': transaction.credit,
                                    'date': transaction.form.created_at,
                                    'id':transaction.pk} for transaction in transactions]
                resp['status'] = "success"
                return JsonResponse(resp)
        
            else:
                resp['msg'] = "You are not authorized to view transaction"
                return JsonResponse(resp)
        else:
            JsonResponse(status=204)
    else:
        return HttpResponse (status=405)
    
@login_required
def delete_transaction(request,pk=None):
    resp = {
        'status':'failed',
        'msg':''
    } 
    state_on = False
    state_off = False
    state_none = False
    if pk:  
        transactions = models.Transaction.objects.select_related('party__user').filter(pk = pk)
        if transactions[0]:
            items = TradeItem.objects.filter(trade=transactions[0])
            products = Product.objects.all()
            
            if transactions[0].is_sales ==True and (request.user.is_superuser or transactions[0].party.user == request.user  or  ((transactions[0].party.user.assigned_staff.user if hasattr(transactions[0].party.user.assigned_staff, 'user') else None)==request.user and request.user.has_perm('accounts.can_delete_sale'))):   
                state_on = True
                if transactions[0].delete_flag == 0:
                    try:
                        with transaction.atomic():
                            
                            transactions.update(delete_flag =1)
                            items.update(delete_flag=1)
                            for item in items:
                                products.filter(pk=item.product.pk).update(quantity=F('quantity')+item.quantity)

                    except:

                        resp['msg'] = "Moving Sale To RecycleBin Failed."
                        return JsonResponse(resp)
                else:
                    try:
                        transactions.delete()
                        items.delete()

                        messages.success(request,"Transaction has been deleted successfully") 
                        resp['status'] = "success"
                    except:
                        resp['msg'] = 'Deleting Transaction failed'
                        return JsonResponse(resp)
            if transactions[0].is_sales ==False and (request.user.is_superuser or transactions[0].party.user == request.user  or  (transactions[0].party.user.assigned_staff.user if hasattr(transactions[0].party.user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.can_delete_purchase'))):   
                state_off = True
                if transactions[0].delete_flag == 0:
                    try:
                        with transaction.atomic():
                            transactions.update(delete_flag =1)
                            items.update(delete_flag=1)
                            for item in items:
                                product = products.filter(pk=item.product.pk)
                                if product[0].quantity - item.quantity < 0:
                                    raise Exception
                                else:
                                    product.update(quantity=F('quantity')-item.quantity)

                    except:

                        resp['msg'] = "Moving Purchase To RecycleBin Failed. Sales can not be more then purchase. Please add new purchase before deleting this one or edit existing one"
                        return JsonResponse(resp)
                else:
                    try:
                        transactions.delete()
                        items.delete()

                        messages.success(request,"Transaction has been deleted successfully") 
                        resp['status'] = "success"
                    except:
                        resp['msg'] = 'Deleting Transaction failed'
                        return JsonResponse(resp)
                    
            if transactions[0].is_sales ==None and (request.user.is_superuser or transactions[0].party.user == request.user  or  (transactions[0].party.user.assigned_staff.user if hasattr(transactions[0].party.user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.delete_transaction'))):   
                state_none = True
                if transactions[0].delete_flag == 0:
                    try:
                        with transaction.atomic():
                            transactions.update(delete_flag =1)
                            items.update(delete_flag=1)
                            for item in items:
                                products.filter(pk=item.product.pk).update(quantity=F('quantity')-item.quantity)

                    except:

                        resp['msg'] = "Moving Purchase To RecycleBin Failed."
                        return JsonResponse(resp)
                else:
                    try:
                        transactions.delete()
                        items.delete()

                        messages.success(request,"Transaction has been deleted successfully") 
                        resp['status'] = "success"
                    except:
                        resp['msg'] = 'Deleting Transaction failed'
                        return JsonResponse(resp)
        else:

            resp['msg']= "No transaction found with the given id"
            return HttpResponse(status=204)
        
    else:
        resp['msg'] = "You are not authorized to delete Transaction"
    
    if transactions[0].is_sales == None and not state_none:
        resp['msg'] = "you are not authorized to delete Transaction"
        return JsonResponse(resp)
    if transactions[0].is_sales == True and not state_on:
        resp['msg'] = "you are not authorized to delete sale"
        return JsonResponse(resp)
    if transactions[0].is_sales == False and not state_off:
        resp['msg'] = "you are not authorized to delete Purchase"
        return JsonResponse(resp)

    party = Party.objects.get(id=transactions[0].party.pk)
    balance = party.get_balance()
    party.balance = balance
    party.save()

    return HttpResponse(json.dumps(resp),content_type = "application/json")

@login_required
def view_transactions(request,pk=None):
    if request.method == 'GET':
        
        party = models.Party.objects.filter(id=pk)
        if party[0].user == request.user  or request.user.is_superuser or (party[0].user.assigned_staff.user if hasattr(party[0].user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.view_transaction')):
            transactions = models.Transaction.objects.select_related('party').filter(delete_flag=0,party = party[0]).order_by('form__created_at', 'time')
            return render(request, 'accounts/transactions.html', {'transactions': transactions,"party":party[0]})
        else:
            return HttpResponse(status=204)
        
    else:
        return HttpResponse(status=405)
   

@login_required
def manage_sales_purchases(request,pk=None):
    context = context_data(request)
    context['page'] = 'manage_sales_purchases'
    context['page_title'] = 'Manage Sales/Purchases'

    sales_on = False
    sales_off = False
        
    user_id = request.GET.get('user_id', '')
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse(status=204)
    if pk is None:
        if (request.user.is_superuser or 
            (user == request.user) or
            (user.assigned_staff.user if hasattr(user.assigned_staff,'user')  else False == request.user and request.user.has_perm('accounts.can_manage_s_p'))):
            
            context['user_id'] = user.id
            context['parties'] = Party.objects.filter(user=user, delete_flag=0)
            context['products'] = Product.objects.filter(user=user,delete_flag=0)
        else:
            return HttpResponse("You are not allowed to manage Sales/purchases. Please contact admin for further queries")

    else:
        resp = {
            'msg':"",
            'status':'failed'
        }
        try:
            transaction = Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            return JsonResponse({'status': 'failed', 'msg': 'Transaction is invalid'})
        
        if transaction.is_sales == True and (request.user.is_superuser or 
            (user == request.user ) or
            (user.assigned_staff.user if hasattr(user.assigned_staff,'user') else False == request.user and request.user.has_perm('accounts.can_change_sale'))):
            sales_on = True
    
            transaction_items = TradeItem.objects.filter(trade=transaction)
            transaction_items_list = [
                {
                    'productName': item.product.name,
                    'quantity': item.quantity,
                    'price': item.price,
                    'total': item.quantity *  item.price,

                } for item in transaction_items
            ]
            context['user_id'] = user.id
            transaction_data = {
                'bill_number':transaction.bill_number,
                'party': transaction.party.name,
                'description': transaction.description,
                'date': transaction.form.created_at,
                'discount':transaction.discount,
                'id': transaction.pk,
                'items': transaction_items_list,
                'charges':transaction.charges,
                'palydar':transaction.pallydar
            }

            
        
    
        if transaction.is_sales == False and (request.user.is_superuser or 
            (user == request.user ) or
            (user.assigned_staff.user if hasattr(user.assigned_staff,'user') else False == request.user and request.user.has_perm('accounts.can_change_purchase'))):
                    sales_off = True
    
                    transaction_items = TradeItem.objects.filter(trade=transaction)
                    transaction_items_list = [
                        {   
                            'productName': item.product.name,
                            'quantity': item.quantity,
                            'price': item.price,
                            'total': item.quantity *  item.price,

                        } for item in transaction_items
                    ]
                    context['user_id'] = user.id
                    transaction_data = {
                        'bill_number':transaction.bill_number,
                        'party': transaction.party.name,
                        'description': transaction.description,
                        'date': transaction.form.created_at,
                        'discount':transaction.discount,
                        'id': transaction.pk,
                        'items': transaction_items_list,
                        'charges':transaction.charges,
                        'palydar':transaction.pallydar
                    }

        if transaction.is_sales == True and not sales_on:
            resp['msg']="You are not authorized to edit sales"
            return JsonResponse(resp)
        if transaction.is_sales == False and not sales_off:
            resp['msg']="You are not authorized to edit Purchase"
            return JsonResponse(resp)
        resp['transaction'] = transaction_data
        resp['status'] = 'success'
        return JsonResponse(resp)

    return render(request, 'accounts/manage_sales_purchase.html', context)


@login_required
def save_trade(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id','')
        user_id = data.get('user_id','')
        bill = data.get('bill_number',0) 
        name = data.get('name','') 
        date = data.get('date','')
        description = data.get('description','')
        state = data.get('state','off')
        total = data.get('total',0)
        discount = data.get('discount',0)
        charges = data.get('charges',0)
        items = data.get('items','')
        palydar = data.get('palydar','')
        if charges == None:
            charges=0
        if discount == None:
            discount = 0
        calc_total =0
            
        for item in items:
            calc_total += (item['quantity']*item['price']) 

        calc_total = calc_total - int(discount) + int(charges)

        def validate_total():
            
            return calc_total == total
        if date:
            try:
                form_obj, created = Form.objects.get_or_create(created_at=date)
            except Exception:
                resp['msg'] = "Date is invalid"
                return JsonResponse(resp)
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                products = Product.objects.filter(user=user)
            except Exception:
                resp['msg'] = "User isn't valid"
                return JsonResponse(resp)

            try:
                party = Party.objects.get(name=name,user__id=user_id)
            except Exception:
                resp['msg'] = "Party couldn't be found"
                return JsonResponse(resp)
        else:
            resp['msg'] = "Couldn't find any reference to user"
            return JsonResponse(resp)
        
           
        if id:
            try:
                trade = Transaction.objects.filter(id=id)
            except Exception:
                resp['msg'] = "Couldn't find any transaction"
                return JsonResponse(resp)
            if (state == "on" and trade[0].is_sales == True) and (request.user.is_superuser or party.user == request.user  or  (party.user.assigned_staff.user if hasattr(party.user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.can_change_sale'))):
                state_on =True
                try:
        
                    with transaction.atomic():
                        prev_items = TradeItem.objects.filter(trade=trade[0])
                        for item in prev_items:
                            products.filter(pk=item.product.pk).update(quantity= F('quantity')+item.quantity)
                        prev_items.delete()
                        for item in items:
                                product = products.filter(name=item['productName'])
                                product.update(quantity=F('quantity')-item['quantity'])
                        trade.update(party=party,description=description,credit=(total if validate_total() else calc_total),form=form_obj,discount=discount,is_sales=True,charges=charges,pallydar=palydar)
                        trade_items = [
                            TradeItem(
                                trade=trade[0],
                                product=products.filter(name=item['productName'])[0],
                                quantity=item['quantity'],
                                price=item['price']
                            )  for item in items
                        ]
                        TradeItem.objects.bulk_create(trade_items)
                        resp['msg'] = "Updated Sale Successfully"
                except Exception as e:
                    resp['msg'] = f"Couldn't Update Sale {e}"
                    return JsonResponse(resp)
            if (state == 'off' and trade[0].is_sales == False) and (request.user.is_superuser or user == request.user  or  (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.can_change_purchase'))):
                state_off = True
                if bill == None:
                    bill =0
                try:
                    with transaction.atomic():
                        prev_items = TradeItem.objects.filter(trade=trade[0])
                        for item in prev_items:
                            products.filter(pk=item.product.pk).update(quantity= F('quantity')-item.quantity)
                        prev_items.delete()
                        for item in items:
                                product = products.filter(name=item['productName'])
                                product.update(quantity=F('quantity')+item['quantity'])
                        trade.update(party=party,description=description,debit=(total if validate_total() else calc_total),form=form_obj,discount=discount,is_sales=False,charges=charges,bill_number=bill,pallydar=palydar)
                        trade_items = [
                            TradeItem(
                                trade=trade[0],
                                product=products.filter(name=item['productName'])[0],
                                quantity=item['quantity'],
                                price=item['price']
                            )  for item in items
                        ]
                        TradeItem.objects.bulk_create(trade_items)                        
                    resp['msg'] = "Updated Purchase Successfully"
                except Exception as e:
                    resp['msg'] = f"COuldn't update purchase {e}"
                    return JsonResponse(resp)
            if state == "on" and not state_on:
                resp['msg'] = "You dont have authorization to update sale"
                return JsonResponse(resp)
            if state == "off" and not state_off:
                resp['msg'] = "You dont have authorization to update purchase"
                return JsonResponse(resp)
        else:
            if state == 'on':
                    bill = 0
                    sales = Transaction.objects.select_related('party__user').filter(delete_flag=0, party__delete_flag=0, party__user=user, is_sales=True)
                    bill = sales.aggregate(Max('bill_number'))['bill_number__max']
                    if bill:
                        bill = bill + 1
                    else:
                        bill =1
            if bill == None:
                bill = 0
            if state == "on" and (request.user.is_superuser or user == request.user or  (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None)==request.user and request.user.has_perm('accounts.can_add_sale')) :
                state_on = True
                try:
                    with transaction.atomic():
                        for item in items:
                                try:
                                    with transaction.atomic():
                                        product = products.filter(name=item['productName'])
                                        if product[0].quantity-item['quantity'] < 0:
                                            raise Exception
                                        else:
                                            product.update(quantity=F('quantity')-item['quantity'])
                                except:
                                    resp['msg'] = f"Not enough {item['productName']} for this Sale"
                                    return JsonResponse(resp)
                                
                        trade = Transaction.objects.create(
                            bill_number=bill,
                            party=party,
                            description=description,
                            credit=(total if validate_total() else calc_total),
                            form=form_obj,
                            discount=discount,
                            charges=charges,
                            is_sales=True,
                            pallydar=palydar
                        )
                        trade_items = [
                            TradeItem(
                                trade=trade,
                                product=products.filter(name=item['productName'])[0],
                                quantity=item['quantity'],
                                price=item['price']
                            )  for item in items
                        ]
                        TradeItem.objects.bulk_create(trade_items)
                    resp['transaction_id'] = trade.pk
                    resp['msg'] = "Created new Sale successfully"
                except:
                    resp['msg'] = "Couldn't Create new Sale"
                    return JsonResponse(resp)

            if state == "off" and (request.user.is_superuser or user == request.user  or  (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None)==request.user and request.user.has_perm('accounts.can_add_purchase')):
                state_off = True
                try:
                    with transaction .atomic():
                        trade = Transaction.objects.create(bill_number=bill,party=party,description=description,debit=(total if validate_total() else calc_total),form=form_obj,discount=discount,is_sales=False,charges=charges,pallydar=palydar)
                        trade_items = [
                            TradeItem(
                                trade=trade,
                                product=products.filter(name=item['productName'])[0],
                                quantity=item['quantity'],
                                price=item['price']
                            )  for item in items
                        ]
                        for item in items:
                                try:
                                    products.filter(name=item['productName']).update(quantity=F('quantity')+item['quantity'])
                                except:
                                    resp['msg'] = f"Couldn't update inventory of {item['productName']}"
                                    return JsonResponse(resp)
                        TradeItem.objects.bulk_create(trade_items)
                        resp['transaction_id'] = trade.pk
                        resp['msg'] = "Created new Purchase Successfully"
                except Exception:
                    resp['msg'] = "Couldn't Create new Purchase"
                    return JsonResponse(resp)
            if state == "on" and not state_on:
                resp['msg'] = "You dont have authorization to add new sale"
                return JsonResponse(resp)
            if state == "off" and not state_off:
                resp['msg'] = "You dont have authorization to add new purchase"
                return JsonResponse(resp)
        
        balance = party.get_balance()
        party.balance = balance
        party.save()

        resp['status'] = "success"
        return JsonResponse(resp)
    else:
        JsonResponse(status=405)

@login_required
def sales_list(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'GET':
        selected_date = request.GET.get('date')
        user_id = request.GET.get('user_id')
        limit = int(request.GET.get('limit'))
        try:
            user = User.objects.get(pk=user_id)
        except:
            resp['msg'] = "User couldn't be found"
            JsonResponse(resp)
        if user:
            if request.user.is_superuser or user == request.user  or  (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.can_view_sale')):
                if selected_date == '2000-01-01':
                    if limit == -1:
                        sales = Transaction.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,party__user = user,is_sales=True)
                    else:
                        sales = Transaction.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,party__user = user,is_sales=True)[:limit]
                else:
                    sales = Transaction.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,form__created_at=selected_date,party__user = user,is_sales=True)
                resp['transaction_data'] = [{'party': transaction.party.name,
                                    'description': transaction.description,
                                    'debit': transaction.credit,
                                    'discount': transaction.discount,
                                    'date': transaction.form.created_at,
                                    'id':transaction.pk,
                                    'bill_number':transaction.bill_number} for transaction in sales]
                resp['status'] = 'success'
                return JsonResponse(resp)
        
            else:
                resp['msg'] = "You are not authorized to view sales"
                return JsonResponse(resp)
        else:
            JsonResponse(status=204)
    else:
        JsonResponse(status=405)
@login_required
def purchases_list(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'GET':
        selected_date = request.GET.get('date')
        user_id = request.GET.get('user_id')
        limit = int(request.GET.get('limit'))
        try:
            user = User.objects.get(pk=user_id)
        except:
            resp['msg'] = "User couldn't be found"
            JsonResponse(resp)
        if user:
            if request.user.is_superuser or user == request.user  or  (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.can_view_purchase')):
                if selected_date == '2000-01-01':
                    if limit == -1:
                        purchase = Transaction.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,party__user = user,is_sales=False)
                    else:
                        purchase = Transaction.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,party__user = user,is_sales=False)[:limit]

                else:
                    purchase = Transaction.objects.select_related('party__user').filter(delete_flag=0,party__delete_flag=0,form__created_at=selected_date,party__user = user,is_sales=False)
                resp['transaction_data'] = [{'party': transaction.party.name,
                                    'description': transaction.description,
                                    'debit': transaction.debit,
                                    'discount': transaction.discount,
                                    'date': transaction.form.created_at,
                                    'id':transaction.pk,
                                    'bill_number':transaction.bill_number} for transaction in purchase]
                resp['status'] = "success"
                return JsonResponse(resp)
        
            else:
                resp["msg"] = "You are not authorized to view Purchases"
                return JsonResponse(resp)
        else:
            JsonResponse(status=204)
    else:
        JsonResponse(status=405)
@login_required
def products(request,pk=None):
    context = context_data(request)
    context['page_name'] = "Products"
    context['page_title'] = "Products"
    options = []
    if pk:
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return HttpResponse(status=204)
        if (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.view_product')) or request.user.is_superuser or user == request.user:
            context['products'] = Product.objects.select_related('user').filter(user = user,delete_flag=0)
            context['page_name'] = user
            context['user'] = user
            options.append(('parties','Parties')) if (request.user.has_perm('accounts.add_party') or request.user == user) else None
            options.append(('manage_transactions','Manage Transactions')) if (request.user.has_perm('accounts.can_manage_transactions') or request.user == user) else None
            options.append(('manage_s_p','Manage Sale/purchases')) if (request.user.has_perm('accounts.can_manage_s_p') or request.user == user) else None 
            options.append(('manage_conversion','Conversion Form'))  if (request.user.has_perm('accounts.view_conversion') or request.user == user) else None

        else:
            return redirect("/products/")
    else:
        if (request.user.staffuser if hasattr(request.user, 'staffuser') else False) or request.user.is_superuser:
                return HttpResponse(status=204)
        context['products'] = Product.objects.filter(user = request.user,delete_flag=0)
        context['page_name'] = request.user
        context['user'] = request.user
        options.append(('parties','Parties')) if (request.user.has_perm('accounts.add_party') or request.user == user) else None
        options.append(('manage_transactions','Manage Transactions')) if request.user.has_perm('accounts.can_manage_transactions' or request.user == user) else None
        options.append(('manage_s_p','Manage Sale/purchases')) if request.user.has_perm('accounts.can_manage_s_p' or request.user == user) else None
        options.append(('manage_conversion','Conversion Form'))  if (request.user.has_perm('accounts.view_conversion') or request.user == user) else None
    context['options'] = options
    return render(request,"accounts/products.html",context)

@login_required
def manage_products(request,pk=None):
    context = context_data(request)
    context['page'] = 'manage_product'
    context['page_title'] = 'Manage Products'

    if pk :

        product = Product.objects.select_related('user').filter(pk=pk)
        if product[0]:
            if request.user.is_superuser or  (product[0].user.assigned_staff.user if hasattr(product[0].user.assigned_staff, 'user') else None==request.user  and request.user.has_perm('accounts.change_product')) or request.user == product[0].user:
                    context['product'] = product[0]
            else:
                return HttpResponse("You are not Authorized to Edit This Product")
        else:
            return HttpResponse("The product is invalid")        
          
    else:
        user = User.objects.get(pk = request.GET.get('user_id'))
        if request.user.is_superuser or  (request.user.assigned_staff.user if hasattr(request.user.assigned_staff, 'user') else None==request.user or  request.user.has_perm('accounts.add_product')) or request.user == user:
            context['user_id'] = user.pk
        else:
            HttpResponse("You are not Authorized to Add This Product")
    return render(request, 'accounts/manage_products.html', context)
            

@login_required
def save_product(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id','')
        user_id = data.get('user_id','')
        name = data.get('name','')
        quantity = data.get('quantity','')
        if quantity == '':
            quantity = 0
        try:
            user = User.objects.get(id=user_id)
        except:
            resp['msg'] = "User Couldn't be found"
            return JsonResponse(resp)
        if id == '':
            if request.user.is_superuser or request.user == user or (user.assigned_staff.user if hasattr(user.assigned_staff,'user') else False==request.user and request.user.has_perm('accounts.add_product')):
                try:
                    Product.objects.create(user=user,name=name,quantity=quantity)
                    resp['msg'] = "product was created successfully"
                except:
                    resp['msg'] = "Product Alredy Exists, Check your Recycle Bin"
                    return JsonResponse(resp)
            else:
                resp['msg'] = "You are not allowed to Add New Product"
                return JsonResponse(resp)
        else:
            if request.user.is_superuser or request.user == user or (user.assigned_staff.user if hasattr(user.assigned_staff,'user') else False==request.user and request.user.has_perm('accounts.change_product')):
                try:
                    product = Product.objects.get(id=id)
                except:
                    resp['msg'] = "Couldn't find product"
                    return JsonResponse(resp)
                try:
                    with transaction.atomic():
                        product.name = name
                        product.quantity = quantity
                        product.save()
                        resp['msg'] = "product was updated successfully"
                except:
                    resp['msg'] = "Couldn't Update Product"
                    return JsonResponse(resp)
            else:
                resp['msg'] = "You are not allowed to Update Product"
                return JsonResponse(resp)
            
    resp['status'] = 'success'
    return JsonResponse(resp)

@login_required
def print_veiw(request,pk):
    context = context_data(request)
    if request.method == 'GET':
        if pk:
            try:
                transactions = Transaction.objects.select_related('party__user').get(pk=pk)
            except:
                return HttpResponse(status=204)
            if request.user.is_superuser or transactions.party.user == request.user or (transactions.party.user.assigned_staff.user if hasattr(transactions.party.user.assigned_staff,'user') else False == request.user and request.user.has_perm('accounts.can_print_details')):
                context['transaction'] = transactions
                context['items'] = TradeItem.objects.filter(trade=transactions)
            else:
                return HttpResponse(status=204)
            return render(request,'accounts/print_item.html',context)
        
    else:
        return HttpResponse(status=405)
@login_required
def delete_product(request, pk=None):
    resp = {
        'status': 'failed',
        'msg': ''
    }

    if pk:
        product = Product.objects.select_related('user').filter(pk = pk)
        if product[0]:
            if request.user.is_superuser or product[0].user == request.user or (request.user.has_perm('accounts.delete_product') and (product[0].user.assigned_staff.user if hasattr(product[0].user.assigned_staff, 'user') else None)==request.user):            
                if product[0].delete_flag == 0:
                    try:
                        product.update(delete_flag=1)
                        messages.success(request, "product has been moved to recycle bin successfully.")
                        resp['status'] = 'success'
                    except:
                        resp['msg'] = "Deleting Product Failed."
                else:
                    product.delete()
                    messages.success(request,"product has been deleted successfully.")
                    resp['status'] = 'success'
            else:
                resp['msg' ] = "You are not authorized to delete Product"
                return JsonResponse(resp)
        else:
            messages.error(request,"product couldn't be found")
            return JsonResponse(resp)
    
    else:
        resp['msg'] = "There's no data sent in the request"

    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def conversion(request,pk=None):
    context = context_data(request)
    context['page'] = 'manage_transaction'
    context['page_title'] = 'Manage Transaction'
    user_id = request.GET.get('user_id', '')
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse("The user Couldn't be found. Please Refresh and Try again")
    
    if pk is None:
        # Adding a new transaction
        if request.user.is_superuser or request.user == user or  (user.assigned_staff.user if hasattr(user.assigned_staff,'user') else False == request.user and request.user.has_perm('accounts.can_manage_transactions')):
            
            context['user_id'] = user.id
            context['parties'] = Party.objects.filter(user=user, delete_flag=0)
            context['products'] = Product.objects.filter(user=user,delete_flag=0)
        else:
            return HttpResponse("You are not allowed to manage Transactions. Please contact admin for further queries")
        
    return render(request, 'accounts/manage_conversion.html', context)

@login_required
def check_identifier(request):
    if request.method == 'GET':
        identifier = request.GET.get('identifier', None)  # Get identifier from request
        
        if identifier is not None:
            # Check if the identifier exists in the model
            exists = Conversion.objects.filter(identifier=identifier).exists()

            # Return JSON response
            return JsonResponse({'exists': exists})
        
        # If no identifier is provided
        return JsonResponse({'error': 'No identifier provided'}, status=400)
    
    
@login_required
@csrf_exempt
def save_conversion(request):
    data = json.loads(request.body)
    conversion_id = data.get('id','')
    user_id = data.get('user_id','')
    date = data.get('date','')
    identifier = data.get('identifier','')
    items_data = data.get('items', [])
    services_data = data.get('services', [])
    convertion_product = data.get('convertion_product','')
    convertion_quantity = data.get('convertion_quantity','')
    if date:
        form_obj, created = Form.objects.get_or_create(created_at=date)
    else:
        return JsonResponse({
            'status':'error',
            'issue':'E101',
            'message':"Please Add Date"
        })
    try:
        user = User.objects.get(pk=user_id)
    except:
        return JsonResponse({
            'status':'error',
            'message':'No user with this id exist'
        })
    if request.method == 'POST':
        try:

            # Initialize lists to hold items and services
            with transaction.atomic():
                conversion,created = Conversion.objects.get_or_create(user=user,identifier=identifier,date=date)
                if not created:
                    return JsonResponse({
                        'status':'error',
                        'issue':'E100',
                        'message':"identifier already exists"
                    })
                converted_product = Product.objects.get(user=user,name=convertion_product)
                ProductConversion.objects.create(conversion=conversion,product=converted_product,quantity=convertion_quantity,converted=True)
            # Extract items and services from the data
            # Process items data
                for item in items_data:
                    # Assuming each item has 'product' and 'quantity' fields
                    iproduct = item.get('product')
                    iquantity = item.get('quantity')
                    product = Product.objects.get(name=iproduct,user=user)
                    # Append a tuple or dictionary to the items list
                    ProductConversion.objects.create(conversion=conversion,product=product,quantity=iquantity)
                    
                # Process services data
                for service in services_data:
                    # Assuming each service has 'party', 'amount', and 'description' fields
                    party = service.get('party')
                    amount = service.get('amount')
                    description = service.get('description')

                    party = Party.objects.get(name=party,user=user)
                    Transaction.objects.create(party=party,debit=amount,description=description,form=form_obj,conversion=conversion)

                # Return a response indicating success and the processed data (optional)
                return JsonResponse({
                    'status': 'success',
                    'message': "Conversion Successfully Performed",
                    'conversion_data': {
                        'date': conversion.date,  # or however you want to format the date
                        'id': conversion.pk,
                        'identifier': conversion.identifier,
                        
                    }
                })
        except json.JSONDecodeError:
            # Handle JSON decoding error
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
    elif request.method == 'PUT':
        with transaction.atomic():
            conversion = Conversion.objects.get(pk=conversion_id)
            conversion.identifier = identifier
            conversion.date = date
            conversion.save()
            Transaction.objects.filter(conversion=conversion).delete()
            ProductConversion.objects.filter(conversion=conversion).delete()
            converted_product = Product.objects.get(user=user,name=convertion_product)
            ProductConversion.objects.create(conversion=conversion,product=converted_product,quantity=convertion_quantity,converted=True)
            for item in items_data:
                iproduct = item.get('product')
                iquantity = item.get('quantity')
                product = Product.objects.get(name=iproduct,user=user)
                ProductConversion.objects.create(conversion=conversion,product=product,quantity=iquantity)

            for service in services_data:
                party = service.get('party')
                amount = service.get('amount')
                description = service.get('description')

                party = Party.objects.get(name=party,user=user)
                Transaction.objects.create(party=party,debit=amount,description=description,form=form_obj,conversion=conversion)

        return JsonResponse({
            'status':'success',
            'message': "Conversion Successfully Updated",
        })
    else:
    # Return error response for non-POST requests
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def delete_conversion(request,pk): 
    if request.method == "DELETE":
        conversion = Conversion.objects.get(pk=pk)
        transactions = Transaction.objects.filter(conversion=conversion)
        transactions.delete()
        conversion.delete()
        return JsonResponse({'status':'success'})
    
@login_required
def conversion_list(request):
    if request.method == 'GET':
        resp = {
            'msg' : "",
            'status': 'failed'
        }
        user_id = request.GET.get('user_id')
        limit = int(request.GET.get('limit'))
        
        try:
            user = User.objects.get(pk=user_id)
        except:
            resp['msg'] = "User Couldn't be found. Please Try Again."
        if user:
            if request.user.is_superuser or user == request.user or (user.assigned_staff.user if hasattr(user.assigned_staff, 'user') else None==request.user and request.user.has_perm('accounts.view_conversion') ):
                if limit == -1:
                    conversions = Conversion.objects.select_related('user').filter(user=user)
                else:
                    conversions = Conversion.objects.select_related('user').filter(user=user)[:limit]
                resp['conversion'] =[{'identifier': conversion.identifier,
                                    'date': conversion.date,
                                    'id':conversion.pk} for conversion in conversions]
                resp['status'] = "success"
                return JsonResponse(resp)
        
            else:
                resp['msg'] = "You are not authorized to view transaction"
                return JsonResponse(resp)
        else:
            JsonResponse(status=204)
    else:
        return HttpResponse (status=405)

@login_required
def edit_conversion(request,pk):
    if request.method == "GET":
        conversion = Conversion.objects.get(pk=pk)
        transactions = Transaction.objects.filter(conversion=conversion)
        product_conversions = ProductConversion.objects.filter(conversion=conversion,converted=False)
        product_converted = ProductConversion.objects.filter(conversion=conversion,converted=True)

        conversion_data = {
            'identifier':conversion.identifier,
            'date':conversion.date,
            'id':conversion.pk,
        }

        transactions_list = [
            {
                'party':transaction.party.name,
                'description':transaction.description,
                'amount': transaction.debit,
                'id':transaction.pk
            } for transaction in transactions
        ]

        products_list = [
            {
                'product':product_conversion.product.name,
                'quantity':product_conversion.quantity,
                'id':product_conversion.pk
            } for product_conversion in product_conversions
        ]
        product_converted_instance = {
            'product':product_converted[0].product.name,
            'quantity':product_converted[0].quantity
        } 

        return JsonResponse({
            'status':'success',
            'conversion':conversion_data,
            'transactions':transactions_list,
            'products':products_list,
            'product_instance':product_converted_instance
        })