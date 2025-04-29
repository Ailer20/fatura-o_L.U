# fatoracao_lu/urls.py

from django.contrib import admin
from django.urls import path
from app_lu import views  # certifique-se de importar a view
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # <- isso adiciona a rota "/"
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

