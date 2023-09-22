from django.shortcuts                   import render, redirect, HttpResponse
from django.contrib.auth                import login as auth_login
from django.contrib.auth.decorators     import login_required

from .models    import User
from .forms     import UserCreationForm

from group.helper       import custom_render
from time               import sleep

@login_required
def home(request):
    print(request)
    return render(request, 'pages/home.html')

def signup(request):
    if request.method == 'POST':    
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()

    return custom_render(request, 'registration/signup.html', {
        'form' : form,
        'title' : 'Sign up',
    })

def about(request):
    return custom_render(request, "pages/about.html", {'title' : 'About'})