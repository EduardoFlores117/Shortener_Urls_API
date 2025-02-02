from django.contrib import admin
from django.urls import path, include
from shortener.swagger import urlpatterns as swagger_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shortener.urls')),
]

# ✅ Agregar rutas de Swagger para la documentación
urlpatterns += swagger_urls
    