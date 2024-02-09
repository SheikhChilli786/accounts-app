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

@login_required
def home(request):
    context = context_data(request)
    context['page'] = 'home'
    context['page_title'] = 'Home'
    context['page_name'] = context['system_name']
    if request.user.is_superuser:
        context['users'] = User.objects.exclude(id = request.user.id)
    else:
        return redirect('home-client')
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
    
    if pk is None:
        context['user'] = {}
    else:
        context['user'] = get_object_or_404(User, id=pk)

    return render(request, 'manage_user.html', context)

@login_required
def delete_user(request,pk=None):
    resp = {
        'status':'failed',
        'msg':''
    }   
    if pk is None:
        resp['msg'] = 'User ID is invalid'
    else:
        try:
            User.objects.filter(pk=pk).delete()
            messages.success(request,"User has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting User Failed."

    return HttpResponse(json.dumps(resp),content_type = "application/json")

@login_required
def client(request,pk=None):
    context = context_data(request)
    context['page'] = 'home'
    context['page_title'] = 'Home'
    if pk is not None:
        context['user_id'] = pk
        context['page_name'] = User.objects.get(pk=pk)
        context['parties'] = models.Party.objects.filter(user__id=pk)
    else:
        if request.user.is_superuser:
            return redirect('home-page')
        context['page_name'] = request.user
        context['parties'] = models.Party.objects.filter(user=request.user)
    return render(request,'party.html',context)


@login_required
def save_party(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        if not request.user.is_superuser:
            resp['msg'] = "You are not authorized"
            return JsonResponse(resp, status=403)  # Return 403 Forbidden status

        post = request.POST
        if post['id'] != '':
            
            party = models.Party.objects.get(id=post['id'])
            form = forms.SaveParty(request.POST, instance=party)
        else:
            form = forms.SaveParty(request.POST)

        print(post) 
        if form.is_valid():
            print(post) 
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
    if pk is None:
        context['party'] = {}
    else:
        context['party'] = get_object_or_404(models.Party,id=pk)
    
    return render(request, 'manage_party.html', context)

@login_required
def manage_party_new(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_party'
    context['page_title'] = 'Manage Party'
    context['user_id'] = pk
    return render(request, 'manage_party.html', context)


@login_required
def manage_form(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_party'
    context['page_title'] = 'Manage Party'
    if pk is None:
        context['parties'] = {}
    else:
        context['parties'] = models.Party.objects.filter(user__id = pk)
    return render(request, 'manage_form.html', context)

@login_required
def delete_party(request,pk=None):
    resp = {
        'status':'failed',
        'msg':''
    }   
    if pk is None:
        resp['msg'] = 'User ID is invalid'
    else:
        try:
            models.Party.objects.filter(pk=pk).delete()
            messages.success(request,"User has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting User Failed."

    return HttpResponse(json.dumps(resp),content_type = "application/json")

def transaction_list(request):
    if request.method == 'GET':
        selected_date = request.GET.get('date')
        print(selected_date)
        transactions = models.Transaction.objects.select_related('party').filter(form__created_at=selected_date)
        print(transactions)

        transaction_data = [{'party': transaction.party.name,
                             'description': transaction.description,
                             'debit': transaction.debit,
                             'credit': transaction.credit,
                             'id':transaction.id} for transaction in transactions]

        return JsonResponse({'transactions': transaction_data})
    
@login_required
def save_form(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        if not request.user.is_superuser:
            resp['msg'] = "You are not authorized"
            return JsonResponse(resp, status=403)  # Return 403 Forbidden status

        post = request.POST
        date = post.get('date', '')
        name = post.get('name', '')
        party = get_object_or_404(models.Party, name=name)
        form_obj, created = models.Form.objects.get_or_create(created_at=date)
        form = forms.SaveForm(post)

        if form.is_valid():
            transaction_instance = form.save(commit=False)
            transaction_instance.party = party
            transaction_instance.form = form_obj
            transaction_instance.save()
        
        

        #     if post['id'] == '':
        #         messages.success(request, "Party has been saved successfully.")
        #     else:
        #         messages.success(request, "Party has been updated successfully.")
        #     resp['status'] = 'success'
        # else:
        #     for field in form:
        #         for error in field.errors:
        #             if resp['msg'] != '':
        #                 resp['msg'] += '<br/>'
        #             resp['msg'] += f'[{field.name}] {error}'
    else:
        resp['msg'] = "There's no data sent in the request"

    return JsonResponse(resp)

@login_required
def edit_transaction(request,pk=None):
    if pk is None:
        JsonResponse("No id was given")
    else:
        context = context_data(request)
        context['page'] = 'edit_transaction'
        context['page_title'] = 'Edit Party'
        context['transaction'] = models.Transaction.objects.get(id=pk)
