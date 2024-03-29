
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
import jwt
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.shortcuts import render
import os
# Create your views here.


@csrf_exempt
def login(request):
    try:
        if request.method == "POST":
            # check if a user exists
            # with the username and password
            username = request.POST['username']
            print("username", username)
            password = request.POST['password']
            print("pss", password)
            user = authenticate(username=username, password=password)
            print('USER: ', user)
            if not user:
                raise ObjectDoesNotExist("Wrong Username/Password combination or register before login.")
            if user is not None and user.is_active is True:
                return HttpResponse("You are Logged In Successfully...!")
            else:
                if user.is_active is False:
                    return HttpResponse("Please verify your email by clicking link sent to your mail-id.")
        else:
            return HttpResponse("Error: Invalid Credentials..")
    except ObjectDoesNotExist as e:
        return HttpResponse(str(e))


@csrf_exempt
def signup(request):
    if request.method == "POST":
        if request.POST['password'] == request.POST['password2']:
            '''if both the passwords matched.
            check if a previous user exists.'''
            try:
                user = User.objects.get(username=request.POST['username'])  # Checking if user is present or not.
                if user:
                    return HttpResponse("Username Has Already Been Taken")
            except ObjectDoesNotExist:
                '''If User doesn't exist 
                Create a new User.'''
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password'],
                                                first_name=request.POST['first_name'],
                                                last_name=request.POST['last_name'], email=request.POST['email'])
                user.is_active = False  # making is_active false until the email is verified.
                user.save()
                '''Generating jwt token.'''
                # creating payload
                payload = {
                    'uid': user.id,
                    'email': user.email,
                    'username': user.username
                }
                token = jwt.encode(payload, "SECRET_KEY", algorithm='HS256').decode('utf-8')  # .decode('utf-8')
                current_site = get_current_site(request)
                mail_subject = 'Activate your account by clicking below link.'
                message = render_to_string('chat/account_active_email.html', {
                    'user': user.username,
                    'domain': current_site.domain,
                    'token': token
                }
                                           )
                to_email = user.email

                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
                return HttpResponse("Registered Successfully !!\nPlease confirm your email address to complete "
                                    "the registration by clicking link sent to ur email")
        else:
            return HttpResponse("error:Passwords Don't Match")
    else:
        return HttpResponse('Error: Something went wrong.')


@csrf_exempt
def activate(request, token):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithm='HS256')  # .decode('utf-8')
        uid = payload['uid']  # getting the user id from the payload
        user = User.objects.get(id=uid)  # getting the user through the id
        if not user:
            raise ObjectDoesNotExist("User Not Exist..")
        user.is_active = True  # making user is_active to true for login purposes
        user.save()  # saving the user
        return HttpResponse('Registration successful !\nNow you can login to your account.')
    except ObjectDoesNotExist as error:
        return HttpResponse(str(error))
    except Exception as e:
        return HttpResponse('Error:', str(e))


@csrf_exempt
def delete(request):
    try:
        User.objects.filter(last_name='ff').delete()
        return HttpResponse('Done')
    except ObjectDoesNotExist:
        return HttpResponse('User with this username not found')


@csrf_exempt
def forget(request):
    try:
        email = request.POST["email"]  # getting the email from the request
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            user = User.objects.get(email=email)
            if not user:
                raise ObjectDoesNotExist('User does not exist.')
            if user:
                current_site = get_current_site(request)  # getting the domain
                payload = {
                    'email': user.email,  # generating the payload
                    'password': password
                }

                mail_subject = "Forgot password"  # mail subject
                token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm='HS256').decode('utf-8')  # generating the token
                message = render_to_string('chat/forget_password.html', {
                    'user': user.username,
                    "domain": current_site,
                    "token": token
                })
                email = EmailMessage(mail_subject, message, to=[email])  # generating the email using EmailMessage class
                email.send()  # sending the email
                return HttpResponse("please do check your email ")
            else:
                return HttpResponse('Invalid Email id')
    except (ValueError, ObjectDoesNotExist) as e:
        return HttpResponse(str(e))


@csrf_exempt
def reset(request, token):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithm='HS256')
        email = payload['email']
        password = password2 = payload['password']
        if password == password2:
            user = User.objects.get(email=email)
            if user:
                user.Password = password
                user.save()
                return HttpResponse('Password Reset Successfully Done !')
            else:
                return HttpResponse('Wrong entry: Email not found')
        else:
            return HttpResponse('Passwords not Matching')
    except (ObjectDoesNotExist, ValueError) as e:
        return HttpResponse(str(e))
