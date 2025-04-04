from datetime import datetime, timedelta
from django.shortcuts import redirect, render
from django.http import HttpResponse,Http404
from .models import Mentorados,Navigators,Horarios,Reuniao, Tarefa, Upload
from django.contrib import messages
from django.contrib.messages import constants
from .auth import validate_token
from dateutil.parser import parse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def mentorados(request):
    if not request.user.is_authenticated:
        #raise Http404
        return redirect('login')
    if request.method == 'GET':
        navigators=Navigators.objects.filter(user=request.user)
        mentorados=Mentorados.objects.filter(user=request.user)
        estagios_list=[index[1] for index in Mentorados.estagio_choices]
        estagios_amount=[]
        for row,column in Mentorados.estagio_choices:
            estagios_amount.append(Mentorados.objects.filter(estagio=row).count())
        return render(request,'mentorados.html',{'estagios':Mentorados.estagio_choices,'navigators':navigators,'mentorados':mentorados,'estagios_list':estagios_list,'estagios_amount':estagios_amount})
    elif request.method == 'POST':
        nome=request.POST.get('nome')
        foto=request.FILES.get('foto') 
        estagio=request.POST.get('estagio')
        navigator=request.POST.get('navigator')
        mentorado=Mentorados(
            nome=nome,
            foto=foto,
            estagio=estagio,
            navigator_id=navigator,
            user=request.user
        )
        mentorado.save()
        messages.add_message(request, constants.SUCCESS, 'Mentorado cadastrado com sucesso.')
        return redirect('mentorados')
    
def reunioes(request):
    if request.method=='GET':
        reunioes=Reuniao.objects.filter(data__mentor=request.user)
        return render(request,'reunioes.html',{'reunioes':reunioes})
    elif request.method=='POST':
        data=request.POST.get('data')
        data=datetime.strptime(data,'%Y-%m-%dT%H:%M')
        horarios=Horarios.objects.filter(mentor=request.user).filter(
            data_inicial__gte=(data-timedelta(minutes=50)),
            data_inicial__lte=(data+timedelta(minutes=50))
        )
        if horarios.exists():
            messages.add_message(request,constants.ERROR,'Você já tem reunião agendada para este horário.')
            return redirect('reunioes')
        horarios=Horarios(
            data_inicial=data,
            mentor=request.user
        )
        horarios.save()
        messages.add_message(request,constants.SUCCESS,'Reunião agendada com sucesso.')
        return redirect('reunioes')

def auth(request):
    if request.method=='GET':
        return render(request,'auth_mentorado.html')
    elif request.method=='POST':
        token=request.POST.get('token')
        if not Mentorados.objects.filter(token=token).exists():
            messages.add_message(request,constants.ERROR,'Token inválido.')
            return redirect('auth_mentorado')
    response = redirect('escolher_dia')
    response.set_cookie('auth_token', token, max_age=3600)
    return response

def escolher_dia(request):
    if not validate_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
    if request.method=='GET':
        horarios=Horarios.objects.filter(
            data_inicial__gte=datetime.now(),
            agendado=False
        ).values_list('data_inicial',flat=True)
        #estagios_list=[index[1] for index in Mentorados.estagio_choices]
        datas=[]
        dias=[]
        meses=[]
        for index in horarios:
            datas.append(index.date().strftime('%d-%m-%Y'))
        #TODO: Deixar Dia e Mes dinamicos - DONE!
        dates_list_dataset=list(set(datas))
        final_dataset=[]
        for date in dates_list_dataset:
            final_dataset.append(datetime.strptime(date, '%d-%m-%Y'))
        return render(request,'escolher_dia.html',{'horarios':final_dataset})
    
def agendar_reuniao(request):
    if not validate_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
    mentorado=validate_token(request.COOKIES.get('auth_token'))
    #TODO: Validar se o horario agendado pertencie ao mentor do mentorado
    if request.method == 'GET':
        data = request.GET.get("data")
        data = datetime.strptime(data, '%d-%m-%Y')
        horarios = Horarios.objects.filter(
            data_inicial__gte=data,
            data_inicial__lt=data + timedelta(days=1),
            agendado=False
        )
        return render(request, 'agendar_reuniao.html', {'horarios': horarios, 'tags': Reuniao.tag_choices})
    elif request.method == 'POST':
        horario_id=request.POST.get('horario')
        tag=request.POST.get('tag')
        descricao=request.POST.get('descricao')
        reuniao=Reuniao(
            data_id=horario_id,
            mentorado=mentorado,
            tag=tag,
            descricao=descricao
        )
        reuniao.save()
        horario=Horarios.objects.get(id=horario_id)
        horario.agendado=True
        horario.save()
        messages.add_message(request,constants.SUCCESS,'Reunião agendada.')
        return redirect('escolher_dia')

def tarefa(request, id):
    mentorado = Mentorados.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404()
    
    if request.method == 'GET':
        tarefas = Tarefa.objects.filter(mentorado=mentorado)
        videos=Upload.objects.filter(mentorado=mentorado)
        return render(request, 'tarefa.html', {'mentorado': mentorado, 'tarefas': tarefas,'videos': videos})
    elif request.method == 'POST':
        tarefa=request.POST.get('tarefa')
        t=Tarefa(
            mentorado=mentorado,
            tarefa=tarefa
        )
        t.save()
        return redirect(f'/mentorados/tarefa/{id}')
    
def upload(request, id):
    mentorado = Mentorados.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404()
    video = request.FILES.get('video')
    upload = Upload(
        mentorado=mentorado,
        video=video
    )
    upload.save()
    return redirect(f'/mentorados/tarefa/{mentorado.id}')

def tarefa_mentorado(request):
    mentorado=validate_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('auth_mentorado')
    if  request.method == 'GET':
        videos=Upload.objects.filter(mentorado=mentorado)
        tarefas=Tarefa.objects.filter(mentorado=mentorado)
        return render(request, 'tarefa_mentorado.html',{'mentorado':mentorado,'videos':videos,'tarefas':tarefas})
    
@csrf_exempt
def tarefa_alterar(request, id):
    mentorado = validate_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('auth_mentorado')

    tarefa = Tarefa.objects.get(id=id)
    if mentorado != tarefa.mentorado:
        raise Http404()
    tarefa.realizada = not tarefa.realizada
    tarefa.save()

    return HttpResponse('teste')