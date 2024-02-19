from django.shortcuts import render
from django.shortcuts import redirect,render 
import json 
from django.http import JsonResponse 
from django.contrib import messages 
from django .http import HttpResponse
from . import models,forms
from django.contrib.auth import update_session_auth_hash,logout,authenticate,login,get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from datetime import datetime

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

def home(request):
    context = context_data(request)
    context['footer'] = False
    context['page_name'] = 'home'
    context['page_title'] = 'Home'
    return render(request,'index.html',context)

def login_page(request):
    context = context_data(request)
    context['topbar'] = False
    context['footer'] = False
    context['page_name'] = 'login'
    context['page_title'] = 'Login'
    return render(request,'login.html',context)

def logout_user(request):
    logout(request)
    return redirect("login-page")


def login_user(request):
    logout(request)
    resp = {
        "status":'failed',
        'msg':''
    }
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username,password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                resp['status'] = 'success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type = 'application/json')

### Views For Users

@login_required
def users_list(request):
    context = context_data(request)
    context['page'] = 'home'
    context['page_title'] = 'Home'
    context['page_name'] = context['system_name']
    if request.user.is_superuser:
        context['users'] = User.objects.exclude(id = request.user.id).filter(is_active=True)
    else:
        return redirect('party-list')
    return render(request,'users.html',context)

@login_required
def save_user(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        post = request.POST
        user_id = post.get('id', '')

        if request.user.is_superuser:
            try:
                if user_id:
                    user = User.objects.get(id=user_id)
                    form = forms.UpdateUser(post, instance=user)
                else:
                    form = forms.SaveUser(post)
            except User.DoesNotExist:
                    resp['msg'] = f"User with id {user_id} does not exist."
                    return JsonResponse(resp)
        else:
            resp['msg'] = "You are not authorized to edit/create Users"
            return JsonResponse(resp)

        if form.is_valid():
            form.save()
            if not user_id:
                messages.success(request, "User has been saved successfully.")
            else:
                messages.success(request, "User has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    resp['msg'] += f"[{field.name}] {error}<br/>"
    else:
        resp['msg'] = "There's no data sent on the request"

    return JsonResponse(resp)
 

@login_required
def manage_user(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_user'
    context['page_title'] = 'Manage User'
    if request.user.is_superuser:
        if pk is None:
            context['user'] = {}
        else:
            context['user'] = get_object_or_404(User, id=pk)
    else:
        return render(request,'unauthorized.html',context)
    return render(request, 'manage_user.html', context)

@login_required
def restore_user(request,pk=None):
    resp = {
        'status': 'failed',
        'msg': ''
    }

    if pk is None:
        resp['msg'] = 'User ID is invalid'
    else:
        user = get_object_or_404(User, pk=pk)
        parties = models.Party.objects.filter(user=user)
        if request.user.is_superuser:
            if not user.is_active:
                try:
                    user.is_active = True
                    user.save()
                    parties.update(delete_flag=0)
                    messages.success(request, "User has been activated successfully.")
                    resp['status'] = 'success'
                except Exception as e:
                    resp['msg'] = "Deactivating User Failed."
            
        else:
            resp['msg'] = "You are not authorized to delete User"

    return HttpResponse(json.dumps(resp), content_type="application/json")
@login_required
def delete_user(request, pk=None):
    resp = {
        'status': 'failed',
        'msg': ''
    }

    if pk is None:
        resp['msg'] = 'User ID is invalid'
    else:
        user = get_object_or_404(User, pk=pk)
        parties = models.Party.objects.filter(user=user)

        if request.user.is_superuser:
            if user.is_active:
                try:
                    user.is_active = False
                    user.save()
                    parties.update(delete_flag=1)
                    messages.success(request, "User has been deactivated successfully.")
                    resp['status'] = 'success'
                except Exception as e:
                    resp['msg'] = "Deactivating User Failed."
            else:
                try:
                    user.delete()
                    messages.success(request, "User has been deleted successfully.")
                    resp['status'] = 'success'
                except Exception as e:
                    resp['msg'] = "Deleting User Failed."
        else:
            resp['msg'] = "You are not authorized to delete User"

    return HttpResponse(json.dumps(resp), content_type="application/json")
### Views for Parties

@login_required
def parties(request,pk=None):
    context = context_data(request)
    context['page'] = 'parties'
    context['page_title'] = 'Parties'
    if pk and request.user.is_superuser:
        context['user_id'] = pk
        context['page_name'] = User.objects.get(pk=pk)
        context['parties'] = models.Party.objects.filter(user__id=pk,delete_flag=0)
    else:
        if request.user.is_superuser:
            return redirect('users-list')
        context['user_id'] = request.user.id
        context['page_name'] = request.user
        context['parties'] = models.Party.objects.filter(user=request.user,delete_flag=0)
    return render(request,'party.html',context)

@login_required
def save_party(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        if not request.user.is_superuser:
            resp['msg'] = "You are not authorized"
            return JsonResponse(resp)  # Return 403 Forbidden status

        post = request.POST
        if post['id'] != '':
            
            party = models.Party.objects.get(id=post['id'])
            form = forms.SaveParty(request.POST, instance=party)
        else:
            form = forms.SaveParty(request.POST)

        if form.is_valid():
            form.save()

            if post['id'] == '':
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
def manage_party(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_party'
    context['page_title'] = 'Manage Party'
    if request.user.is_superuser:
        if pk is None:
            context['party'] = {}
        else:
            context['party'] = get_object_or_404(models.Party,id=pk)
    else:
        return render(request,'unauthorized.html',context)
    return render(request, 'manage_party.html', context)

@login_required
def manage_party_new(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_party'
    context['page_title'] = 'Manage Party'
    if request.user.is_superuser:
        context['user_id'] = pk
        return render(request, 'manage_party.html', context)
    else:
        return render(request, 'unauthorized.html', context)
        
@login_required
def delete_party(request,pk=None):
    resp = {
        'status':'failed',
        'msg':''
    }   
    if request.user.is_superuser:
        if pk is None:
            resp['msg'] = 'User ID is invalid'
        else:
            party = models.Party.objects.filter(pk = pk)
            if party[0].delete_flag == 0:
                try:
                    party.update(delete_flag=1)
                    messages.success(request, "Party has been moved to recycle bin successfully.")
                    resp['status'] = 'success'
                except:
                    resp['msg'] = "Deleting User Failed."
            else:
                party.delete()
                messages.success(request,"User has been moved to recycle bin successfully.")
                resp['status'] = 'success'
    else:
        resp['msg'] = "You are not authorized to delete party"
    return HttpResponse(json.dumps(resp),content_type = "application/json")


@login_required
def restore_party(request,pk=None):
    resp = {
        'status': 'failed',
        'msg': ''
    }

    if pk is None:
        resp['msg'] = 'Party ID is invalid'
    else:
        party = models.Party.objects.filter(pk=pk)
        if request.user.is_superuser:
            if  party[0].delete_flag == 1:
                try:
                    party.update(delete_flag=0)
                    messages.success(request, "Party has been restored successfully0.")
                    resp['status'] = 'success'
                except Exception as e:
                    resp['msg'] = "Deactivating User Failed."
            else:
                    messages.error(request, "Party has been already restored or have been deleted.")
                    resp['status'] = 'error'
        else:
            resp['msg'] = "You are not authorized to delete User"

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def manage_transaction(request,pk=None):
    context = context_data(request)
    context['page'] = 'manage_transaction'
    context['page_title'] = 'Manage Transaction'
    if pk is None:
            context['parties'] = {}
    else:   
        if request.user.is_superuser:
                context['user_id'] = pk
                context['parties'] = models.Party.objects.filter(user__id=pk,delete_flag=0)
        else:
            return render(request,'unauthorized.html',context)
    return render(request, 'manage_transaction.html', context)

@login_required
def save_transaction(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        if not request.user.is_superuser:
            resp['msg'] = "You are not authorized"
            return JsonResponse(resp, status=403)  # Return 403 Forbidden status

        post = request.POST
        id = post.get('id','') 
        user_id = post.get('user_id','') 
        date = post.get('date', '')
        party = post.get('name', '')
        debit = post.get('debit','')
        credit = post.get('credit','')
        party = get_object_or_404(models.Party, name=party,user__id=user_id)
        form_obj, created = models.Form.objects.get_or_create(created_at=date)
        if id != '':
            transaction = models.Transaction.objects.get(id = id)
            form = forms.SaveForm(post,instance=transaction)
        else: 
            form = forms.SaveForm(post)

        if form.is_valid():
            transaction_instance = form.save(commit=False)
            transaction_instance.party = party
            transaction_instance.form = form_obj
            if debit == '':
                transaction_instance.debit = 0
            if credit == '':
                transaction_instance.credit = 0
            transaction_instance.save()
        
           
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
def transaction_list(request):
    if request.method == 'GET':
        if request.user.is_superuser:
            selected_date = request.GET.get('date')
            user_id = request.GET.get('user_id')
            if selected_date == '2000-01-01':
                transactions = models.Transaction.objects.select_related('party').filter(delete_flag=0,party__delete_flag=0,party__user__id = user_id)
            else:
                transactions = models.Transaction.objects.select_related('party').filter(delete_flag=0,party__delete_flag=0,form__created_at=selected_date,party__user__id = user_id)
            transaction_data = [{'party': transaction.party.name,
                                'description': transaction.description,
                                'user': transaction.party.user.username,
                                'debit': transaction.debit,
                                'credit': transaction.credit,
                                'date': transaction.form.created_at,
                                'id':transaction.id} for transaction in transactions]

            return JsonResponse({'transactions': transaction_data})
        
        else:
            return JsonResponse({
                "msg" : "You are not authorized to view transaction"
            })
        

@login_required
def edit_transaction(request,pk=None):
    context = context_data(request)
    context['page'] = 'edit_transaction'
    context['page_title'] = 'Edit Transaction'
    if request.user.is_superuser:
            
        transaction = models.Transaction.objects.select_related('party').get(id=pk)
        user = transaction.party.user
        context['user_id'] = user.id
        context['transaction'] = transaction
        context['parties'] = models.Party.objects.filter(user=user )
        return render(request,'edit_transaction.html',context)
    else:
        return render(request,'unauthorized.html',context)

@login_required
def delete_transaction(request,pk=None):
    resp = {
        'status':'failed',
        'msg':''
    }   
    if request.user.is_superuser:
        if pk is None:
            resp['msg'] = 'User ID is invalid'
        else:
            transaction = models.Transaction.objects.filter(pk = pk)
            if transaction[0].delete_flag == 0:
                try:
                    transaction.update(delete_flag =1)
                except:
                    resp['msg'] = "Deleting User Failed."
            else:
                try:
                    transaction.delete()
                    messages.success(request,"Transaction hasd been deleted successfully") 
                    resp['status'] = "success"
                except:
                    resp['msg'] = 'Deleting user failed'
    else:
        resp['msg'] = "You are not authorized to delete Transaction"
    return HttpResponse(json.dumps(resp),content_type = "application/json")

@login_required
def restore_transaction(request,pk=None):
    resp = {
        'status': 'failed',
        'msg': ''
    }

    if pk is None:
        resp['msg'] = 'User ID is invalid'
    else:
        transaction = models.Transaction.objects.filter(pk=pk)
        if request.user.is_superuser:
            if transaction[0].delete_flag==1:
                try:
                    transaction.update(delete_flag=0)
                    messages.success(request, "transaction has been restored successfully.")
                    resp['status'] = 'success'
                except Exception as e:
                    resp['msg'] = "Deactivating User Failed."
            else:
                    resp['msg'] = "Transaction has been already deleted or restored."

        else:
            resp['msg'] = "You are not authorized to delete User"

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def range_transaction(request,pk=None):
    context = context_data(request)
    context['page'] = 'range_transactions'
    context['page_title'] = 'Range Transactions'
    context['party_id'] = pk
    return render(request,'manage_range.html',context)


@login_required
def view_transactions(request,pk=None):
    if request.method == 'GET':
        # date_from = request.POST.get('date_from')
        # date_to = request.POST.get('date_to')
        # party_id = request.POST.get('id')
        # Filter transactions based on date range
        party = models.Party.objects.get(id=pk)
        if party.user == request.user or request.user.is_superuser:
        # prior_transactions = models.Transaction.objects.select_related('party').filter(delete_flag=0,party = party,form__created_at__lt=date_from)
        # transactions = models.Transaction.objects.select_related('party').filter(delete_flag=0,party = party,form__created_at__range=[date_from, date_to]).order_by('form__created_at', 'time')
            transactions = models.Transaction.objects.select_related('party').filter(delete_flag=0,party = party).order_by('form__created_at', 'time')
        # prior_debit_total = sum(transaction.debit for transaction in prior_transactions)
        # prior_credit_total = sum(transaction.credit for transaction in prior_transactions)
        
        # Calculate sum of debit and credit for current transactions
            debit_total = sum(transaction.debit for transaction in transactions)
            credit_total = sum(transaction.credit for transaction in transactions)
        
        # Calculate net balance by subtracting credit from debit
        # prior_balance = (prior_debit_total) - (prior_credit_total )
        
        # Render the transactions template with the filtered transactions
            return render(request, 'transactions.html', {'transactions': transactions,
                                                     "party":party,
                                                    #  'from':date_from,
                                                    #  "to":date_to,
                                                    #  'prior_balance': prior_balance,
                                                    #  'point_balance':
                                                     })

    # Handle GET requests or other cases as needed
        return render(request, 'unauthorized.html')

@login_required
def recycle_bin(request):
    context = context_data(request)

    if request.method == 'GET':
        if not request.user.is_superuser:
            return render(request,'unauthorized.html')
            
        context['users'] = User.objects.filter(is_active=False)
        context['parties'] = models.Party.objects.select_related('user').filter(delete_flag=1)
        context['transactions'] = models.Transaction.objects.select_related('party','form').filter(delete_flag=1)

        return render(request,'recycle.html',context)