from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib import auth

def cadastro(request):
    if request.method == 'GET':
        return render(request,'cadastro.html')
    elif request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('senha')
        c_password=request.POST.get('confirmar_senha')
        verify_user=User.objects.filter(username=username)
        if len(password)<6:
            messages.add_message(request, constants.ERROR, 'Senha inferior a 6 digitos.')
            return redirect('/usuarios/cadastro/')
        if not password==c_password:
            messages.add_message(request, constants.ERROR, 'Senhas digitdas não conferem.')
            return redirect('/usuarios/cadastro/')
        if verify_user.exists():
            messages.add_message(request, constants.ERROR, 'Nome de usuario já cadastrado.')
            return redirect('/usuarios/cadastro/')
        User.objects.create_user(
            username=username,
            password=password,
        )
        messages.add_message(request, constants.SUCCESS, 'Conta criada com sucesso.')
        return redirect('/usuarios/login/')
    
def login(request):
    if request.method == 'GET':
        return render(request,'login.html')
    elif request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('senha')
        user=authenticate(request,username=username,password=password)
        if user:
            auth.login(request,user)
            return redirect('/mentorados/')
        
        messages.add_message(request, constants.ERROR,'Nome de usuário ou senha inválidos')
        return redirect('login')