from __future__ import unicode_literals
from django.shortcuts import render, redirect, reverse
# from django.core.urlresolvers import reverse
from django.views.generic import FormView, DetailView, ListView
from .models import *
from django.db.models import Q
from django.contrib import messages
import bcrypt
from datetime import datetime
from Vipr import settings
import stripe



def index(request):
    return render(request, 'vipr/index.html')

def register(request):
    return render(request, 'vipr/register.html')

def registeruser(request):
    if request.method != 'POST':
        return redirect('/')
    if len(request.POST['milid']) > 0:
        mil_id_check = User.objects.filter(military_id = request.POST['milid'])
    else:
        messages.error(request, "Military ID can not be blank. Please correct.")  
        return redirect('/register') 
    if len(mil_id_check):
        messages.error(request, "Military ID is in use. Please correct or log in")
    errors =  User.objects.basic_validator(request.POST)
    if len(errors):
        for tag, error in errors.items():
            messages.error(request, error, extra_tags = tag)
        return redirect('/register')
    else:
        user = User.objects.create_user(request.POST)
        request.session['user_id'] = user.id
        # adding stripe stuff
        if user.pay_svc_level == 'gold':
            amount = 2999
            description = "Gold Service"
        elif user.pay_svc_level == 'silver':
            amount = 1999
            description = "Silver Service"
        else:
            amount = 999
            description = "Bronze Service"
        request.session['amount'] = amount
        request.session['description'] = description
        context = {
            "stripe_key": settings.STRIPE_PUBLIC_KEY,
            "amount" : amount,
            "description" : description,     
        }
        return render(request, 'vipr/charge.html', context)
    return redirect('/login')

def checkout(request):
    print('in chekcout')
    if request.method != 'POST':
        return redirect('/')
    if not 'user_id' in request.session:
        return redirect('/')
    user = User.objects.get(id = request.session['user_id'])
    print('post', request.POST)
    if request.method == "POST":
        token    = request.POST.get("stripeToken")
        stripe.api_key = settings.STRIPE_SECRET_KEY
        print('got token')

    try:
        charge  = stripe.Charge.create(
            amount      = request.session['amount'],
            currency    = "usd",
            source      = token,
            description = request.session['description'],
        )
        print('got charge')
        user.charge_id   = charge.id
        print('updated user')

    except stripe.error.CardError as ce:
        return False, ce

    else:
        user.save()
        return redirect("/login")

def login(request):
    print("in login")
    return render(request, 'vipr/login.html')

def dashboard(request):
    print("in dashboard views")
    if request.method != 'POST':
        return redirect('/')
    if len(request.POST['milid']) > 0:
        user = User.objects.filter(military_id = request.POST['milid'])
    else:
        messages.error(request, "Military ID can not be blank. Please correct.")  
        return redirect('/login') 
    # user = User.objects.filter(military_id = request.POST['milid'])
    if not len(user):
        message.error(request, "The Military ID entered is not found in the system")
        return redirect('/register')
    else:
        user = User.objects.filter(military_id = request.POST['milid'])
        user = user[0]
        password = bcrypt.checkpw(request.POST['password'].encode(), user.password.encode())
        print("sys access", user.sys_access_level)
        if password == True:
            if user.sys_access_level == 1:
                print("in access level 1")
                now = datetime.now()
                temp_date = user.updated_at
                user.updated_at = now
                user.save()
                request.session['user_id'] = user.id
                last_login = user.updated_at
                context = {

                    "user" : User.objects.get(id=request.session['user_id']),
                    "requests" : Request.objects.filter(Q(requester = user) & Q(req_res = " ")),
                    "answered" : Request.objects.filter(Q(requester = user) & ~Q(req_res = " ")),
                    # "answered" : Request.objects.exclude(Q(requester = user) & Q(req_res = " ")),

                }
                return render(request, 'vipr/dashboard.html', context)
            # else:
            elif user.sys_access_level == 2:
                print('access level 2')
                request.session['user_id'] = user.id
                context = {
                    "user" : User.objects.get(id = request.session['user_id']),
                    "worklist" : Request.objects.filter(req_res = " "),     
                }
                return render(request, 'vipr/adminboard.html', context)
            else:
                print('access level 9')
                request.session['user_id'] = user.id
                context = {
                    "user" : User.objects.get(id = request.session['user_id']),
                    "worklist" : Request.objects.filter(req_res = " "),
                    "userlist" : User.objects.all(),
                }
                return render(request, 'vipr/adminboard.html', context)
        else:
            messages.error(request, "Your password is incorrect")
            return redirect('/login')

def addrequest(request):
    if not 'user_id' in request.session:
        return redirect('/')
    context = {
          
        "user" : User.objects.get(id=request.session['user_id']),

    }
    return render(request, 'vipr/addreq.html', context)
    
def request_add(request):
    print('in request_add')
    if not 'user_id' in request.session:
        return redirect('/')  
    if request.method != 'POST':
        return redirect('/')
    errors = Request.objects.basic_validator(request.POST)
    if len(errors):
        for tag, error in errors.items():
            messages.error(request, error, extra_tags = tag)
        return redirect('/addrequest')
    else:
        user = User.objects.get(id=request.session['user_id'])
        new_req = Request.objects.create_request(request.POST, user)
        return redirect('/home')
    
def home(request):
    if not 'user_id' in request.session:
        return redirect('/') 
    user = User.objects.get(id=request.session['user_id'])
    if user.sys_access_level == 1:
        print('access level 1')
        context = {

            "user" : User.objects.get(id=request.session['user_id']),
            "requests" : Request.objects.filter(Q(requester = user) & Q(req_res = " ")),
            "answered" : Request.objects.filter(Q(requester = user) & ~Q(req_res = " ")),
            # "answered" : Request.objects.exclude(Q(requester = user) & Q(req_res = " ")),

        }
        return render(request, 'vipr/dashboard.html', context)
    elif user.sys_access_level == 2:
        print('access level 2')
        context = {
            "user" : User.objects.get(id = request.session['user_id']),
            "worklist" : Request.objects.filter(req_res = " "),     
        }
        return render(request, 'vipr/adminboard.html', context)
    else:
        print('access level 9')
        context = {
            "user" : User.objects.get(id = request.session['user_id']),
            "worklist" : Request.objects.filter(req_res = " "),
            "userlist" : User.objects.all(),
        }
        return render(request, 'vipr/adminboard.html', context)


def show_request(request, req_id):
    if not 'user_id' in request.session:
        return redirect('/') 
    req = Request.objects.get(id=req_id)
    print('req', req.document_for.all())
    context = {

        "user" : User.objects.get(id=request.session['user_id']),
        "request" : Request.objects.get(id=req_id),
        "documents" : req.document_for.all(),

    }
    return render(request, 'vipr/requestview.html', context)

def keywordsrch(request):
    if not 'user_id' in request.session:
        return redirect('/')  
    context = {
          
        "user" : User.objects.get(id=request.session['user_id']),

    }
    return render(request, 'vipr/keysrch.html', context)

def search(request):
    if not 'user_id' in request.session:
        return redirect('/') 
    if request.method != 'POST':
        return redirect('/') 
    if len(request.POST['searchkey']) < 0:
        messages.error(request,"It is impossible to do a search with an empty value")
    results = Request.objects.filter(req_desc__contains = request.POST['searchkey'])
    context = {

        "user" : User.objects.get(id=request.session['user_id']),
        "srcresults" : results,
    }
    return render(request, 'vipr/keysrch.html', context)

def logout(request):
    request.session.clear()
    return redirect('/')
   
def update_request(request, req_id):
    if not 'user_id' in request.session:
        return redirect('/') 
    req = Request.objects.get(id=req_id)
    context = {

        "user" : User.objects.get(id=request.session['user_id']),
        "request" : Request.objects.get(id=req_id),
        "documents" : req.document_for.all(),

    }
    return render(request, 'vipr/updatereq.html', context)

def update(request):
    if not 'user_id' in request.session:
        return redirect('/') 
    if request.method != 'POST':
        return redirect('/') 
    req = Request.objects.get(id = request.POST['req_id'])  
    req.req_res = request.POST['req_res']
    req.save()
    print("add_a_rec", request.POST)
    if 'add_a_rec' in request.POST:
        if request.POST['add_a_rec'] == "Yes":
            context ={
                "request" : req,
                "documents" : Document.objects.all(),
            }
            return render(request, 'vipr/add_a_rec.html', context)
    return redirect('/home')

def update_user(request, usr_id):
    if not 'user_id' in request.session:
        return redirect('/') 
    context = {

        "user" : User.objects.get(id=request.session['user_id']),
        "userU" : User.objects.get(id = usr_id),

    }
    return render(request, 'vipr/updateusr.html', context)

def user_update(request):
    if not 'user_id' in request.session:
        return redirect('/') 
    if request.method != 'POST':
        return redirect('/') 
    usr = User.objects.get(id = request.POST['user_id'])
    usr.first_name = request.POST['fname']
    usr.last_name = request.POST['lname']
    usr.service_branch = request.POST['svc_branch']
    usr.sys_access_level = request.POST['sys_access_level']
    usr.save()
    return redirect('/home')

def adddocument(request):
    print("request.post", request.POST['ddocument'])
    print("request.post", request.POST)
    print("request.file", request.FILES)
    req = Request.objects.get(id = request.POST['req_id'])
    if 'document' in request.FILES:
        documentin = request.FILES['document']
        document = Document.objects.create(
            document = documentin,
            # document  er = req,
        )
    else: 
        document = Document.objects.get(id = request.POST['ddocument'])
        # adding new record
        documentin = document.document
        # document = Document.objects.create(
        #     document = documentin,
        #     documenter = req,
        # )
    document.documenter.add(req)
    url = '/updatereq/' + str(req.id)
    return redirect(url)
