import secrets
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

# Create your models here.
class Navigators(models.Model):
    nome=models.CharField(max_length=255)
    user=models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

class Mentorados(models.Model):
    estagio_choices=(
        ('E1', '10m-100m'), 
        ('E2', '100m-1Mi'), 
    )
    nome=models.CharField(max_length=255)
    foto=models.ImageField(upload_to='photos',null=True,blank=True)
    estagio=models.CharField(max_length=2,choices=estagio_choices)
    navigator=models.ForeignKey(Navigators,null=True,blank=True, on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    data_matricula=models.DateField(auto_now_add=True)
    token=models.CharField(max_length=16,null=True,blank=True)

    def save(self,*args, **kwargs):
        if not self.token:
            self.token=self.generate_unique_token()
        super().save(*args, **kwargs)

    def generate_unique_token(self):
        while True:
            token=secrets.token_urlsafe(8)
            if not Mentorados.objects.filter(token=token).exists():
                return token

    def __str__(self):
        return self.nome

class Horarios(models.Model):
    data_inicial=models.DateTimeField(null=True,blank=True)
    mentor=models.ForeignKey(User,on_delete=models.CASCADE)
    agendado=models.BooleanField(default=False)

    def data_final(self):
        return self.data_inicial+timedelta(minutes=50)
    
class Reuniao(models.Model):
    tag_choices=(
        ('G','Gestão'),
        ('M','Marketing'),
        ('RH','Recursos Humanos'),
        ('I','Impostos'),
    )

    data=models.ForeignKey(Horarios, on_delete=models.CASCADE)
    mentorado=models.ForeignKey(Mentorados, on_delete=models.CASCADE)
    tag=models.CharField(max_length=2,choices=tag_choices)
    descricao=models.TextField()
        
class Tarefa(models.Model):
    mentorado = models.ForeignKey(Mentorados, on_delete=models.DO_NOTHING)
    tarefa = models.CharField(max_length=255)
    realizada = models.BooleanField(default=False)

class Upload(models.Model):
    mentorado = models.ForeignKey(Mentorados, on_delete=models.DO_NOTHING)
    video = models.FileField(upload_to='video')