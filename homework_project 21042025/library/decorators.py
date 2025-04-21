from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse


def superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        print(view_func)
        print(request)
        print(args)
        print(kwargs)
        print(request.user)
        print('auth', request.user.is_authenticated)
        print('super', request.user.is_superuser)
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            # return HttpResponseForbidden("You are not allowed to view this page.")
            return render(request, 'registration/forbidden.html', status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def custom_permission_required(perm, login_url=None, raise_exception=True):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            print(view_func)
            print(request)
            print(args)
            print(kwargs)
            print(request.user)
            print('auth', request.user.is_authenticated)
            print('super', request.user.is_superuser)
            user_permissions = request.user.get_user_permissions()
            print(f"User permissions: {user_permissions}")

            if not request.user.is_authenticated:
                return redirect('login')
                # return redirect_to_login(request.get_full_path(), login_url)

            if not request.user.has_perm(perm):
                if raise_exception:
                    return render(request, 'registration/forbidden.html', status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator