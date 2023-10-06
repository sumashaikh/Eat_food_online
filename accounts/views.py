from django.shortcuts import render,redirect
from django.http import HttpResponse
from vendor.forms import VendorForm
from .forms import UserForm
from .models import User,UserProfile
from django.contrib import messages,auth
from .utils import detectUser,send_verification_email
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from vendor.models import Vendor


# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied




def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request,'you are all ready logged in')
        return redirect('my_Account')

    if request.method == 'POST':
        print(request.POST)
        form=UserForm(request.POST)
        if form.is_valid():
            #create the user using the form
            #password=form.cleaned_data['password']
            #user=form.save(commit=False)
            #user.set_password(password)
            #user.role=User.CUSTOMER
            #user.save()

            # create the user using another method create_user
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']

            user=User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.role=user.CUSTOMER
            user.save()
            # send verification email
            mail_subject='Reset your Password'
            email_template='accounts/emails/reset_password_email.html'

            send_verification_email(request,user,mail_subject,email_template)
            #messages.success(request,'your account register successfully')
            #messages.error(request,'your account register successfully')
            #messages.warning(request,'your account register successfully')
            messages.success(request,'your account register successfully')

            return redirect('registerUser')
        else:
            print("user is invaild")
            print(form.errors)


    else:
        form=UserForm()
    context={
           'form':form, 
    }
    return render(request,'accounts/registerUser.html',context)


def registervendor(request):
    if request.user.is_authenticated:
        messages.warning(request,'you are all ready logged in')
        return redirect('dashboard')

    elif request.method == 'POST':
        form=UserForm(request.POST)
        v_form=VendorForm(request.POST,request.FILES)

        if form.is_valid() and v_form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user=User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.role=User.VENDOR
            user.save()
            vendor=v_form.save(commit=False)
            vendor.user=user
            user_profile=UserProfile.objects.get(user=user)
            vendor.user_profile=user_profile
            vendor.save()
            # send verification email
            mail_subject='Reset your Password'
            email_template='accounts/emails/reset_password_email.html'

            send_verification_email(request,user,mail_subject,email_template)


            messages.success(request,'your account has been registered successfully plz wait for the approval')
            return redirect('registerVendor')
        else:
            print("invaild")
            print(form.errors)


    else:
        form=UserForm()
        v_form=VendorForm()
    context={
          'form':form,
          'v_form':v_form,
    }
    return render(request,'accounts/registervendor.html',context)


def login(request):
    if request.user.is_authenticated:
        messages.warning(request,'you are all ready logged in')
        return redirect('my_Account')

    elif request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(email=email,password=password)
        
        if user is not None:
            auth.login(request,user)
            messages.success(request,'you are now logged in')
            return redirect('my_Account')

        else:
            messages.error(request,"invaild login user")
            return redirect('login')
    return render(request,'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request,"you are logout")
    return redirect('login')

@login_required(login_url='login')
def my_Account(request):
    user=request.user
    redirectUrl=detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request,'accounts/custDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    #vendor = Vendor.objects.get(user=request.user)
    #context={
    #'vendor':vendor,
    #}


    return render(request,'accounts/vendorDashboard.html')

def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulation! Your account is activated.')
        return redirect('my_Account')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('my_Account')



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            mail_subject='Reset your Password'
            email_template='accounts/emails/reset_password_email.html'


            # send reset password email
            send_verification_email(request, user,mail_subject,email_template)

            messages.success(request,'Password reset link has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.info(request,'Plz Reset your Password')
        return redirect('reset_password')
    else:
        messages.error(request, 'this link is expired')
        return redirect('my_Account')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')

