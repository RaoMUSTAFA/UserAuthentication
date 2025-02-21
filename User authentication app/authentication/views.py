
from pyexpat.errors import messages
from userathentication import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logOut
from django.core.mail import send_mail,EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from . tokens import generate_token
# Create your views here.
def home(request):
    return HttpResponse(request, 'athentication/index.html')

def signup(request):
    if request.method == "POST":
        #username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request,"Username already exists")
            return redirect('home')
        
        if User.objects.filter(email=email):
            messages.error(request,"Email already exists")
            return redirect('home')
        
        if len(username)>10:
            messages.error(request,"Usename mustbe under 12 charactors")

        if pass1 != pass2:
            messages.error(request,"Password not match")

        if not username.isalnum():
            messages.error(request,"Usename mustbe Alpha Numeric")
            return redirect('home')
        
        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        messages.success(request, "Your Account has been successfully created. We have sent you a confirmation email,please confirm you email in order to activate your account.")

        #Welcome Email

        subject= "Welcome to User-Authentication Login"
        message = "Hello "+ myuser.first_name + "!! \n"+"Welcome to User Authentication app \n Thank you for visiting our website \n We have also sent you a confirfimation email, please confirm your email address in order to activate your account. \n\n Thank you \n Ghulam Mustafa"
        form_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject,message,form_email,to_list,failsilently=True)

        #Email Confirmation
        current_site = get_current_site(request)
        email_subject = "Confirm your email @userauthentication-django login app"
        massage2 = render_to_string("email_confirmation.html",{
            'name' : myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            massage2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect ('signin')
    return render(request, 'athentication/signup.html')

def signin(request):

    if request.method == "POST":
        #username = request.POST.get('username')
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username = username,password = pass1)

        if user is not None:
            fname = user.first_name
            login(request,user)
            return render(request,"Athentication/index.html",{'fname': fname})

        else:
            messages.error(request,"Bad Credentials")
            return redirect('home')

    return render(request, 'athentication/signin.html')

def signout(request):
    logOut(request)
    messages.success(request, "LoggedOut successfully!")
    return redirect ('home')

def activate(request,uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk = uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        myuser.save()
        login(request,myuser)
        return redirect('login')
    
    else:
        return render(request, 'activation_failed.html')