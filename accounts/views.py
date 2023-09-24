from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import UserForm
from .models import User
from django.contrib import messages


def registerUser(request):
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
            #messages.success(request,'your account register successfully')
            #messages.error(request,'your account register successfully')
            #messages.warning(request,'your account register successfully')
            messages.primary(request,'your account register successfully')

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