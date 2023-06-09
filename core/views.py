from django.shortcuts                   import render, redirect
from django.contrib.auth                import login as auth_login
from django.contrib.auth.decorators     import login_required

from .models    import User
from .forms     import UserCreationForm

from django.shortcuts import HttpResponse

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

    return render(request, 'registration/signup.html', {
        'form' : form,
        'title' : 'Sign up',
    })


def about(request):
    return render(request, "pages/about.html", {'title' : 'About'})