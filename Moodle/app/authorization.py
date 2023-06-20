from django.shortcuts import render
from .models import Role

def role_required(role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role == role:
                return view_func(request, *args, **kwargs)
            else:
                return render(request, 'forbidden.html')  # Render your custom forbidden page

        return wrapper

    return decorator

def mentor_or_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.role == Role.objects.get(name='MENTOR') or request.user.role == Role.objects.get(name='ADMIN')):
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'forbidden.html')  # Render your custom forbidden page

    return wrapper



admin_required = role_required(Role.objects.get(name='ADMIN'))
student_required = role_required(Role.objects.get(name='STUDENT'))
mentor_required = role_required(Role.objects.get(name='MENTOR'))

