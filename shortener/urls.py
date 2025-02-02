from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShortenedURLRedirectView, AuthViewSet, ShortenedURLViewSet

# ✅ Router para organizar las rutas automáticamente en módulos
router = DefaultRouter()

# ✅ Módulo de Autenticación
router.register(r'auth', AuthViewSet, basename='auth')

# ✅ Módulo de Gestión de URLs Acortadas
router.register(r'urls', ShortenedURLViewSet, basename='urls')

urlpatterns = [
    # ✅ Incluye las rutas generadas automáticamente por el router
    path('api/', include(router.urls)),  

    # ✅ Redirección de URLs Acortadas (fuera del router porque es una ruta específica)
    path('r/<str:short_code>/', ShortenedURLRedirectView.as_view(), name='redirect_url'),
]
