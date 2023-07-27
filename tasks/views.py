from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):  # request info.del visitante
    return render(request, 'home.html')


def singup(request):  # request info.del visitante
    if request.method == 'GET':
        print("enviando datos")  # envia al servidor el formulario
        return render(request, 'singup.html', {
            'form': UserCreationForm
        })
    else:
        if(request.POST['username']=='' or request.POST['password1']=='' or request.POST['pasword2']==''):
             return render(request, 'singup.html', {
            'form': UserCreationForm,
            'error': "ingrese campos porfavor"
             })
        else:
            if request.POST['password1'] == request.POST['password2']:
                try:
                    # registrando usuario
                    user = User.objects.create_user(username=request.POST['username'],
                                                    password=request.POST['password1'])
                    # guardar usuario
                    user.save()
                    login(request, user)
                    return redirect('tasks')
                except IntegrityError:
                    # return HttpResponse("el usuario ya existe")
                    return render(request, 'singup.html', {
                        'form': UserCreationForm,
                        'error': "El usuario ya existe"
                    })

            return render(request, 'singup.html', {
            'form': UserCreationForm,
            'error': "Contraseñas no coenciden"
             })

@login_required
def tasks(request):
    # tasks=Task.objects.all()#devuelve toodas las tareas
    tasks = Task.objects.filter(user=request.user,datecompleted__isnull=True )#,datecompleted__isnull=True
    return render(request, 'tasks.html', {
        'tasks': tasks
    })
@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user,datecompleted__isnull=False ).order_by('-datecompleted')
    return render(request, 'tasks.html', {
        'tasks': tasks
    })
@login_required
def task_detail(request,task_id):
    if( request.method=='GET'):
        task=get_object_or_404(Task,pk=task_id,user=request.user)
        form= TaskForm(instance=task)
        return render(request,'task_detail.html',{
            'task':task,
            'form':form
        })
    else:#acualizando tarea
        try:
            task=get_object_or_404(Task,pk=task_id,user=request.user)
            form    =TaskForm(request.POST,instance=task)
            form.save()#el actualziar tarea
            return redirect('tasks')
        except ValueError:
              return render(request,'task_detail.html',{
            'task':task,
            'form':form,
            'error':"error al actulizar tarea"
        })


@login_required
def completed_task(request,task_id):
    task= get_object_or_404(Task,pk=task_id,user=request.user)
    if request.method=='POST':
        task.datecompleted=timezone.now()
        #actualizar fecha
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request,task_id):
    task= get_object_or_404(Task,pk=task_id,user=request.user)
    if request.method=='POST':
        #eliminar tarea
        task.delete()
        return redirect('tasks')

@login_required
def tasks_create(request):
    if request.method == 'GET':

        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)  # devolver solo los campos no todo el formulario
            new_task.user = request.user  # agregamos el usuario rescantando de la sesion
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': "ingrese datos validos"
            })


@login_required
def singout(request):
    logout(request)
    return redirect('home')


def singin(request):
    if request.method == 'GET':
        return render(request, 'singin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'],
                            password=request.POST['password'])
        if user is None:
            return render(request, 'singin.html', {
                'form': AuthenticationForm,
                'error': 'password o usuario incorrecto'
            })
        else:
            login(request, user)
            return redirect('tasks')
