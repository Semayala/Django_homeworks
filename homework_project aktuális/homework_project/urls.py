from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import get_language_from_request
from django.conf.urls.i18n import set_language
from django.shortcuts import redirect

def redirect_to_language_root(request):
    language = get_language_from_request(request)
    return redirect(f'/{language}/')

urlpatterns = [
    path('set_language/', set_language, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', redirect_to_language_root),
]

urlpatterns += i18n_patterns(
    path('', RedirectView.as_view(pattern_name='index', permanent=False)),
    path('admin/', admin.site.urls),
    path('library/', include('library.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


