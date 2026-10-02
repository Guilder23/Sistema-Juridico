from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Usuario

def index(request):
    usuarios = Usuario.objects.all().order_by('-date_joined')
    return render(request, 'usuarios/usuarios.html', {'usuarios': usuarios})

def login_view(request):
    if request.method == 'POST':
        usuario_nom = request.POST.get('username')
        clave = request.POST.get('password')
        user = authenticate(request, username=usuario_nom, password=clave)
        if user is not None:
            login(request, user)
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Credenciales incorrectas. Verifique usuario y contraseña.')
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    return redirect('usuarios:login')

def crear(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        rol = request.POST.get('rol', 'GESTOR')
        telefono = request.POST.get('telefono', '').strip()
        cargo = request.POST.get('cargo', '').strip()

        if not username or not password:
            messages.error(request, 'Usuario y contraseña son obligatorios.')
            return redirect('usuarios:index')

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya se encuentra registrado.')
            return redirect('usuarios:index')

        Usuario.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            rol=rol,
            telefono=telefono,
            cargo=cargo
        )
        messages.success(request, f'Usuario "{username}" creado exitosamente.')
    return redirect('usuarios:index')

def editar(request, id):
    user = get_object_or_404(Usuario, id=id)
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.email = request.POST.get('email', user.email).strip()
        user.rol = request.POST.get('rol', user.rol)
        user.telefono = request.POST.get('telefono', user.telefono).strip()
        user.cargo = request.POST.get('cargo', user.cargo).strip()
        
        password = request.POST.get('password', '').strip()
        if password:
            user.set_password(password)

        user.save()
        messages.success(request, f'Usuario "{user.username}" actualizado.')
    return redirect('usuarios:index')

def eliminar(request, id):
    user = get_object_or_404(Usuario, id=id)
    if request.method == 'POST':
        nombre = user.username
        user.delete()
        messages.success(request, f'Usuario "{nombre}" eliminado.')
    return redirect('usuarios:index')
