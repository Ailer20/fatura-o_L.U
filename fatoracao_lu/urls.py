from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_lu.urls')),  # Incluir as URLs do seu aplicativo
]