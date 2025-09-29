from django.shortcuts import render
from django.contrib.auth import get_user_model

def index(request):
    User = get_user_model()
    users = User.objects.all().order_by('username')
    return render(request, 'users/index.html', {'users': users})