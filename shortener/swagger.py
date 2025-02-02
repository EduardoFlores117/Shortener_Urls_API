from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from django.urls import path

schema_view = get_schema_view(
    openapi.Info(
        title="API de Acortador de URLs",
        default_version="v1",
        description="Documentación de la API para el sistema de acortamiento de URLs.",
        contact=openapi.Contact(email="soporte@example.com"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
